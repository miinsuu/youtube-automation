"""
YouTube 업로드 모듈
Google YouTube Data API v3를 사용하여 영상을 자동으로 업로드합니다.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


class YouTubeUploader:
    # 필요한 모든 YouTube API 스코프
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',           # 비디오 업로드
        'https://www.googleapis.com/auth/youtube.readonly',         # 채널 정보 조회
        'https://www.googleapis.com/auth/youtube',                  # 전체 YouTube 관리
        'https://www.googleapis.com/auth/youtube.force-ssl',       # 댓글 작성/고정
    ]
    
    def __init__(self, config_path="config/config.json", channel_id=None):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.client_secrets = self.config['youtube']['client_secrets_file']
        self.target_channel_id = channel_id or self.config['youtube'].get('target_channel_id')
        
        # 채널별 인증 정보 파일 지정
        if self.target_channel_id:
            # 채널 ID별로 다른 인증 파일 사용
            channel_shortname = self.target_channel_id[-8:]  # 마지막 8자
            self.credentials_file = f"config/youtube_credentials_{channel_shortname}.json"
        else:
            self.credentials_file = self.config['youtube']['credentials_file']
        
        self.youtube = None
    
    def authenticate(self):
        """YouTube API 인증"""
        creds = None
        
        # 저장된 인증 정보 로드 (JSON 형식)
        if os.path.exists(self.credentials_file):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.credentials_file, self.SCOPES
                )
            except Exception as e:
                print(f"⚠️ 인증 파일 로드 실패: {e}")
                creds = None
        
        # 인증 정보가 없거나 만료된 경우
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"⚠️ 토큰 갱신 실패: {e}")
                    creds = None  # 재인증 흐름으로 전환
            
            if not creds or not creds.valid:
                if not os.path.exists(self.client_secrets):
                    print("❌ client_secrets.json 파일이 필요합니다.")
                    print("   Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하세요.")
                    print("   https://console.cloud.google.com/apis/credentials")
                    return False
                
                # CI/GitHub Actions 환경에서는 브라우저 인증 불가
                if os.environ.get('GITHUB_ACTIONS') or os.environ.get('CI'):
                    print("❌ OAuth2 토큰이 만료/취소되었습니다. CI 환경에서는 재인증이 불가합니다.")
                    print("   로컬에서 재인증 후 YOUTUBE_CREDENTIALS 시크릿을 업데이트하세요:")
                    print("   1) 로컬: python scripts/youtube_uploader.py  (브라우저 인증)")
                    print("   2) cat config/youtube_credentials_L4y1Qbdg.json")
                    print("   3) GitHub → Settings → Secrets → YOUTUBE_CREDENTIALS 업데이트")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # 인증 정보 저장 (JSON 형식)
            with open(self.credentials_file, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✅ YouTube API 인증 완료")
        return True
    
    def get_authenticated_channel(self):
        """현재 인증된 YouTube 채널 정보 조회 (기본 채널)"""
        try:
            if not self.youtube:
                return None
            
            request = self.youtube.channels().list(
                part='snippet,contentDetails',
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                return {
                    'id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet'].get('description', '')
                }
            return None
        except Exception as e:
            err_msg = str(e).lower()
            # SSL/연결 오류 시 API 클라이언트 재생성 후 재시도
            if 'eof' in err_msg or 'ssl' in err_msg or 'connection' in err_msg or 'broken pipe' in err_msg:
                print(f"⚠️ 연결 만료 감지: {e}")
                print("🔄 API 클라이언트 재생성 중...")
                self.youtube = None
                if self.authenticate():
                    try:
                        request = self.youtube.channels().list(
                            part='snippet,contentDetails',
                            mine=True
                        )
                        response = request.execute()
                        if response.get('items'):
                            channel = response['items'][0]
                            print("✅ 재연결 성공!")
                            return {
                                'id': channel['id'],
                                'title': channel['snippet']['title'],
                                'description': channel['snippet'].get('description', '')
                            }
                    except Exception as e2:
                        print(f"❌ 재연결 후에도 채널 조회 실패: {e2}")
            else:
                print(f"❌ 현재 채널 조회 오류: {e}")
            return None
    
    def get_my_channels(self):
        """내 모든 YouTube 채널 목록 조회"""
        try:
            if not self.youtube:
                if not self.authenticate():
                    return None
            
            request = self.youtube.channels().list(
                part='snippet,contentDetails',
                mine=True,
                maxResults=10
            )
            response = request.execute()
            
            channels = []
            for channel in response.get('items', []):
                channels.append({
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet'].get('description', '')
                })
            
            return channels
        except Exception as e:
            print(f"❌ 채널 조회 오류: {e}")
            return None
    
    def get_recent_videos(self, max_results=None):
        """채널의 전체 업로드 영상 제목 목록 조회 (중복 방지용)
        
        Args:
            max_results: 최대 조회 수 (None이면 전체 조회)
        """
        if not self.youtube:
            if not self.authenticate():
                return []

        try:
            # 채널의 uploads playlist ID 가져오기
            channel_resp = self.youtube.channels().list(
                part='contentDetails',
                mine=True
            ).execute()

            if not channel_resp.get('items'):
                print("⚠️ 채널 정보를 가져올 수 없습니다")
                return []

            uploads_id = channel_resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # 전체 영상 목록 가져오기 (모든 페이지)
            videos = []
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_id,
                maxResults=50  # API 최대값 50
            )

            while request:
                response = request.execute()
                for item in response.get('items', []):
                    snippet = item['snippet']
                    videos.append({
                        'title': snippet.get('title', ''),
                        'published_at': snippet.get('publishedAt', ''),
                    })
                # max_results 지정 시 초과하면 중단
                if max_results and len(videos) >= max_results:
                    break
                request = self.youtube.playlistItems().list_next(request, response)

            print(f"📺 채널 영상 {len(videos)}개 전체 조회 완료 (중복 방지용)")
            return videos

        except Exception as e:
            print(f"⚠️ 채널 영상 목록 조회 실패: {e}")
            return []

    def get_popular_videos(self, top_n=15):
        """채널 영상의 조회수/좋아요 통계를 가져와 인기 순으로 정렬하여 반환

        Args:
            top_n: 상위 N개 반환 (기본 15)

        Returns:
            list of dict: [{'title': str, 'views': int, 'likes': int, 'id': str}, ...]
        """
        if not self.youtube:
            if not self.authenticate():
                return []

        try:
            # 채널의 uploads playlist ID 가져오기
            channel_resp = self.youtube.channels().list(
                part='contentDetails',
                mine=True
            ).execute()

            if not channel_resp.get('items'):
                print("⚠️ 채널 정보를 가져올 수 없습니다")
                return []

            uploads_id = channel_resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # 모든 비디오 ID 수집
            video_ids = []
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_id,
                maxResults=50
            )
            while request:
                response = request.execute()
                for item in response.get('items', []):
                    video_ids.append(item['snippet']['resourceId']['videoId'])
                request = self.youtube.playlistItems().list_next(request, response)

            if not video_ids:
                return []

            # 50개씩 배치로 통계 조회
            all_stats = []
            for i in range(0, len(video_ids), 50):
                batch = video_ids[i:i+50]
                stats_resp = self.youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(batch)
                ).execute()
                for item in stats_resp.get('items', []):
                    stats = item.get('statistics', {})
                    snippet = item.get('snippet', {})
                    all_stats.append({
                        'id': item['id'],
                        'title': snippet.get('title', ''),
                        'views': int(stats.get('viewCount', 0)),
                        'likes': int(stats.get('likeCount', 0)),
                    })

            # 조회수 + 좋아요 가중 점수로 정렬 (좋아요 1개 = 조회수 10)
            all_stats.sort(key=lambda x: x['views'] + x['likes'] * 10, reverse=True)
            top = all_stats[:top_n]

            print(f"📊 인기 영상 TOP {len(top)} 조회 완료 (총 {len(all_stats)}개 중)")
            for v in top[:5]:
                print(f"   {v['views']:>6} views | {v['likes']:>3} likes | {v['title'][:40]}")

            return top

        except Exception as e:
            print(f"⚠️ 인기 영상 통계 조회 실패: {e}")
            return []

    def upload_video(self, video_path, script_data, thumbnail_path=None,
                     channel_id=None, metadata=None, add_pinned_comment=True,
                     publish_at='', longform_url=''):
        """비디오를 YouTube에 업로드

        Args:
            metadata: script_generator에서 생성된 구조화 데이터 dict
                      (title, description, hashtags, tags, pinned_comment)
                      None이면 script_data에서 직접 추출
            publish_at: 예약 공개 시간 (ISO 8601, 비어있으면 즉시 공개)
            longform_url: 롱폼 영상 URL (쇼츠 설명란/고정댓글에 삽입)
        """

        # 채널 ID 지정된 경우 새로운 업로더 인스턴스 생성
        if channel_id and channel_id != self.target_channel_id:
            uploader = YouTubeUploader(channel_id=channel_id)
            return uploader.upload_video(video_path, script_data, thumbnail_path,
                                         metadata=metadata,
                                         add_pinned_comment=add_pinned_comment,
                                         publish_at=publish_at,
                                         longform_url=longform_url)

        if not self.youtube:
            if not self.authenticate():
                return None

        try:
            # 현재 인증된 채널 확인
            current_channel = self.get_authenticated_channel()

            if not current_channel:
                print("❌ 현재 채널을 확인할 수 없습니다.")
                return None

            # 목표 채널과 현재 채널 비교
            if self.target_channel_id:
                print(f"🎯 업로드 대상 채널: {self.target_channel_id}")
                print(f"✓ 현재 로그인 채널: {current_channel['title']} ({current_channel['id']})")

                if current_channel['id'] == self.target_channel_id:
                    print(f"✅ 채널 일치! 해당 채널로 업로드됩니다.")
                else:
                    print(f"⚠️  채널 불일치!")
                    print(f"   대상: {self.target_channel_id}")
                    print(f"   현재: {current_channel['id']}")
                    print(f"   다른 계정으로 로그인하거나 기본 채널을 변경해주세요.")
                    return None
            else:
                print(f"✓ 업로드 채널: {current_channel['title']} ({current_channel['id']})")

            # 메타데이터 사용 (metadata 우선, 없으면 script_data에서 추출)
            if metadata:
                title = self._strip_markdown(metadata.get('title', script_data.get('title', '')))
                description = self._strip_markdown(metadata.get('description', ''))
                tags = metadata.get('tags', [])
                pinned_text = self._strip_markdown(metadata.get('pinned_comment', ''))
            else:
                title = self._strip_markdown(script_data.get('title', ''))
                description = script_data.get('description', '')
                tags = script_data.get('tags', [])
                pinned_text = script_data.get('pinned_comment', '')

            # 롱폼 URL 연동 (쇼츠 설명란/고정댓글에 롱폼 링크 삽입)
            # 설명란: URL을 맨 앞에 배치 (Shorts 플레이어는 설명 축약 표시 → 맨 앞이 가장 잘 보임)
            if longform_url:
                url_header = f"📺 풀영상 보러가기 👇\n{longform_url}\n\n"
                description = url_header + description.lstrip()
                # Gemini가 생성한 고정댓글에서 중복 풀영상 문구 제거
                import re as _re2
                pinned_text = _re2.sub(
                    r'📺[^\n]*풀영상 보러가기[^\n]*\n?',
                    '',
                    pinned_text
                ).lstrip()
                if pinned_text:
                    pinned_text = f"📺 풀영상 보러가기 👇\n{longform_url}\n\n{pinned_text}"
                else:
                    pinned_text = f"📺 풀영상 보러가기 👇\n{longform_url}\n\n💬 감상평을 댓글로 남겨주세요!"
                print(f"🔗 롱폼 URL 연동: {longform_url}")

            # 태그: 스크립트 태그 + 기본 태그
            shorts_config = self.config.get('upload', {}).get('shorts', {})
            default_tags = shorts_config.get('tags', ['쇼츠', '팩트', '정보', 'shorts'])
            if isinstance(tags, list):
                tags = tags + [t for t in default_tags if t not in tags]
            else:
                tags = default_tags

            # 제목에 해시태그 추가 (#shorts 필수 포함, 최대 5개)
            title_hashtags = ['#shorts']
            hashtag_source = metadata.get('hashtags', []) if metadata else []
            if isinstance(hashtag_source, str):
                import re as _re
                hashtag_source = _re.findall(r'#\S+', hashtag_source)
            # 태그에서 해시태그 보충 (공백 제거: "재테크 꿀팁" → "#재테크꿀팁")
            for t in tags:
                t_clean = t.replace(' ', '') if isinstance(t, str) else t
                ht = f'#{t_clean}' if not t_clean.startswith('#') else t_clean
                if ht not in title_hashtags and ht != '#shorts':
                    title_hashtags.append(ht)
                if len(title_hashtags) >= 5:
                    break
            # hashtag_source에서 추가 보충 (공백 제거)
            for ht in hashtag_source:
                ht = ht.replace(' ', '') if isinstance(ht, str) else ht
                if ht not in title_hashtags:
                    title_hashtags.append(ht)
                if len(title_hashtags) >= 5:
                    break
            title_hashtag_str = ' '.join(title_hashtags[:5])

            # 설명글 강화
            if not description or len(description) < 50:
                description = f"{title}\n\n📌 추천 정보를 제공하는 채널입니다.\n❤️ 공감하셨다면 좋아요와 구독을 눌러주세요! 🙏"

            # 설명글 하단에 해시태그 추가 (기존 해시태그 제거 후 재추가)
            import re as _re
            description = _re.sub(r'\n*#\S+(\s+#\S+)*\s*$', '', description).rstrip()
            desc_hashtags = ['#shorts']
            for t in tags:
                t_clean = t.replace(' ', '') if isinstance(t, str) else t
                ht = f'#{t_clean}' if not t_clean.startswith('#') else t_clean
                if ht not in desc_hashtags:
                    desc_hashtags.append(ht)
                if len(desc_hashtags) >= 10:
                    break
            description += f"\n\n{' '.join(desc_hashtags)}"

            # 제목에 해시태그 붙이기 (총 100자 제한 고려)
            title_with_tags = f"{title} {title_hashtag_str}"
            if len(title_with_tags) > 100:
                # 해시태그 수 줄이기
                while len(title_with_tags) > 100 and len(title_hashtags) > 1:
                    title_hashtags.pop()
                    title_hashtag_str = ' '.join(title_hashtags)
                    title_with_tags = f"{title} {title_hashtag_str}"
            title = title_with_tags

            # 예약 공개 검증 (시간이 이미 지났으면 즉시 공개로 전환)
            scheduled_publish_at = ''
            if publish_at:
                scheduled_publish_at = self._validate_publish_at(publish_at)

            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': shorts_config.get('category_id', '22')
                },
                'status': {
                    # 예약 공개 시: unlisted로 업로드 → 댓글 추가 → private+publishAt 전환
                    'privacyStatus': 'unlisted' if scheduled_publish_at else shorts_config.get('privacy_status', 'public'),
                    'selfDeclaredMadeForKids': False
                }
            }

            if scheduled_publish_at:
                print(f"⏰ 예약 공개 예정: {scheduled_publish_at} (댓글 추가 후 전환)")

            # 미디어 파일 업로드
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True
            )

            print(f"📤 YouTube 업로드 중: {title}")

            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"   업로드 진행: {int(status.progress() * 100)}%")

            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            print(f"✅ 업로드 완료!")
            print(f"   비디오 ID: {video_id}")
            print(f"   URL: {video_url}")

            # 썸네일 업로드
            if thumbnail_path and os.path.exists(thumbnail_path):
                self.upload_thumbnail(video_id, thumbnail_path)

            # 고정 댓글 추가
            if add_pinned_comment and pinned_text:
                self.add_pinned_comment(video_id, pinned_text)

            # 예약 공개로 전환 (unlisted → private + publishAt)
            if scheduled_publish_at:
                self._set_scheduled_publish(video_id, scheduled_publish_at)

            return {
                'video_id': video_id,
                'url': video_url,
                'title': title
            }
            
        except Exception as e:
            print(f"❌ 업로드 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def upload_thumbnail(self, video_id, thumbnail_path):
        """썸네일 업로드 (권한 없으면 YouTube 자동 생성 썸네일 사용)"""
        try:
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print(f"✅ 썸네일 업로드 완료")
        except Exception as e:
            # 권한 없으면 자동 생성 썸네일 사용하므로 무시
            if "insufficient" in str(e).lower() or "permission" in str(e).lower() or "forbidden" in str(e).lower():
                print(f"ℹ️  커스텀 썸네일 업로드 불가 - YouTube 자동 생성 썸네일 사용 중")
            else:
                print(f"⚠️  썸네일 업로드 실패: {e}")
    
    def create_longform_metadata(self, script_data):
        """롱폼 비디오 메타데이터 생성"""
        title = script_data.get('title', '새로운 이야기')
        topic = script_data.get('topic', '')
        
        # 길이 조정: 쇼츠보다 더 설명적
        longform_config = self.config.get('upload', {}).get('longform', {})
        tags = longform_config.get('tags', [])
        
        # 설명 작성
        description = f"""{title}

🎬 오늘의 주제: {topic}

이 영상은 10-15분에 걸쳐 깊이 있는 스토리를 다룹니다.
따뜻한 마음으로 시청해주세요.

📌 주요 포인트:
• 실제 이야기와 교훈
• 감정이 담긴 메시지
• 영감과 희망

💬 댓글로 당신의 이야기를 나눠주세요!
❤️ 공감이 되셨다면 좋아요 눌러주세요
🔔 더 좋은 콘텐츠를 위해 구독 부탁드립니다

---
#스토리 #감동 #영감 #일상 #성공 #{' #'.join(t.replace(' ', '') for t in tags[:5])}"""
        
        hashtags = " ".join([f"#{tag.replace(' ', '')}" for tag in tags[:5]])
        
        return {
            'title': f"{title}",
            'description': description,
            'tags': tags,
            'hashtags': hashtags,
            'category_id': longform_config.get('category_id', '27'),  # Shorts 카테고리 = 15, 일반 = 27
            'privacy': longform_config.get('privacy_status', 'public')
        }
    
    def add_pinned_comment(self, video_id, comment_text):
        """고정 댓글 추가"""
        try:
            if not self.youtube:
                if not self.authenticate():
                    return None
            
            # 댓글 삽입
            request = self.youtube.commentThreads().insert(
                part='snippet',
                body={
                    'snippet': {
                        'videoId': video_id,
                        'topLevelComment': {
                            'snippet': {
                                'textOriginal': comment_text
                            }
                        }
                    }
                }
            )
            
            response = request.execute()
            comment_id = response['id']
            print(f"✅ 댓글 추가 완료: {comment_id}")
            
            # 댓글 고정 (채널 소유자만 가능)
            try:
                self.youtube.commentThreads().update(
                    part='snippet',
                    body={
                        'id': comment_id,
                        'snippet': {
                            'canPin': True,
                            'isPublic': True
                        }
                    }
                ).execute()
                print(f"✅ 댓글 고정 완료")
            except:
                print(f"ℹ️  댓글 고정은 수동으로 진행해주세요 (채널에서 직접 고정 가능)")
            
            return comment_id
        
        except Exception as e:
            print(f"⚠️  댓글 추가 실패: {e}")
            return None
    
    def upload_longform_video(self, video_path, script_data, thumbnail_path=None,
                              add_pinned_comment=True, metadata=None, publish_at=''):
        """롱폼 비디오 업로드 (메타데이터 자동 최적화)
        
        Args:
            metadata: generate_metadata()로 생성된 메타데이터 dict
                      (title, description, tags, hashtags, pinned_comment)
            publish_at: 예약 공개 시간 (ISO 8601, 비어있으면 즉시 공개)
        """
        
        if not self.youtube:
            if not self.authenticate():
                return None
        
        try:
            # 현재 인증된 채널 확인
            current_channel = self.get_authenticated_channel()
            
            if not current_channel:
                print("❌ 현재 채널을 확인할 수 없습니다.")
                return None
            
            # 목표 채널과 현재 채널 비교
            if self.target_channel_id:
                if current_channel['id'] != self.target_channel_id:
                    print(f"⚠️  채널 불일치! 업로드할 수 없습니다.")
                    return None
            
            # 외부에서 제공된 메타데이터 사용, 없으면 기본 생성
            if metadata:
                title = self._strip_markdown(metadata.get('title', script_data.get('title', '')))
                description = self._strip_markdown(metadata.get('description', ''))
                tags = metadata.get('tags', [])
                pinned_text = self._strip_markdown(metadata.get('pinned_comment', ''))
            else:
                meta = self.create_longform_metadata(script_data)
                title = meta['title']
                description = meta['description']
                tags = meta['tags']
                pinned_text = ''
            
            longform_config = self.config.get('upload', {}).get('longform', {})
            category_id = longform_config.get('category_id', '27')
            privacy = longform_config.get('privacy_status', 'public')
            
            # 예약 공개 검증 (시간이 이미 지났으면 즉시 공개로 전환)
            scheduled_publish_at = ''
            if publish_at:
                scheduled_publish_at = self._validate_publish_at(publish_at)

            # 비디오 body
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': category_id
                },
                'status': {
                    # 예약 공개 시: unlisted로 업로드 → 댓글 추가 → private+publishAt 전환
                    'privacyStatus': 'unlisted' if scheduled_publish_at else privacy,
                    'selfDeclaredMadeForKids': False,
                    'embeddable': True
                }
            }

            if scheduled_publish_at:
                print(f"⏰ 예약 공개 예정: {scheduled_publish_at} (댓글 추가 후 전환)")
            
            # 미디어 파일 업로드
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True
            )
            
            print(f"📤 롱폼 비디오 YouTube 업로드 중...")
            print(f"   제목: {title}")
            print(f"   설명: {len(description)}자")
            print(f"   태그: {', '.join(tags[:5])}")
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"   업로드 진행: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"✅ 업로드 완료!")
            print(f"   비디오 ID: {video_id}")
            print(f"   URL: {video_url}")
            
            # 썸네일 업로드
            if thumbnail_path and os.path.exists(thumbnail_path):
                self.upload_thumbnail(video_id, thumbnail_path)
            
            # 고정 댓글 추가
            if add_pinned_comment and pinned_text:
                self.add_pinned_comment(video_id, pinned_text)

            # 예약 공개로 전환 (unlisted → private + publishAt)
            if scheduled_publish_at:
                self._set_scheduled_publish(video_id, scheduled_publish_at)
            
            return {
                'video_id': video_id,
                'url': video_url,
                'title': title,
                'type': 'longform'
            }
        
        except Exception as e:
            print(f"❌ 롱폼 업로드 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _set_scheduled_publish(self, video_id, publish_at):
        """업로드 완료 후 예약 공개로 전환 (unlisted → private + publishAt)"""
        try:
            self.youtube.videos().update(
                part='status',
                body={
                    'id': video_id,
                    'status': {
                        'privacyStatus': 'private',
                        'publishAt': publish_at,
                        'selfDeclaredMadeForKids': False
                    }
                }
            ).execute()
            print(f"✅ 예약 공개 전환 완료: {publish_at}")
            return True
        except Exception as e:
            print(f"⚠️  예약 공개 전환 실패: {e}")
            print(f"   비디오가 unlisted 상태로 남아있습니다. YouTube Studio에서 수동 설정하세요.")
            return False

    def _validate_publish_at(self, publish_at):
        """예약 공개 시간 검증 — 이미 지났거나 5분 이내면 즉시 공개로 전환"""
        try:
            # ISO 8601 파싱 (예: 2026-02-20T22:00:00+09:00)
            target = datetime.fromisoformat(publish_at)
            now = datetime.now(timezone.utc)
            remaining = (target - now).total_seconds()

            if remaining < 300:  # 5분 미만 남았거나 이미 지남
                if remaining < 0:
                    print(f"⚠️  예약 시간({publish_at})이 이미 지났습니다 → 즉시 공개로 전환")
                else:
                    print(f"⚠️  예약 시간까지 {remaining:.0f}초 남음 (5분 미만) → 즉시 공개로 전환")
                return ''  # 빈 문자열 → publishAt 미설정 → 즉시 공개
            
            mins = remaining / 60
            print(f"✅ 예약 공개까지 {mins:.0f}분 남음")
            return publish_at
        except Exception as e:
            print(f"⚠️  예약 시간 파싱 오류({publish_at}): {e} → 즉시 공개로 전환")
            return ''

    @staticmethod
    def _strip_markdown(text):
        """마크다운 서식 제거 유틸리티"""
        import re
        if not text:
            return text
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', text)
        text = re.sub(r'^[-=]{3,}$', '', text, flags=re.MULTILINE)
        text = re.sub(
            r'^\[(?:오프닝|스토리\s*\d*|본론\s*\d*|클로징|엔딩)\].*$',
            '', text, flags=re.MULTILINE | re.IGNORECASE
        )
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


if __name__ == "__main__":
    uploader = YouTubeUploader()
    
    # 인증 테스트
    if uploader.authenticate():
        print("\n✅ YouTube API 연결 성공!")
        print("업로드 준비가 완료되었습니다.")
    else:
        print("\n❌ 인증에 실패했습니다.")
        print("client_secrets.json 파일을 확인해주세요.")
