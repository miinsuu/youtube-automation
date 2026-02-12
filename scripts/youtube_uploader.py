"""
YouTube 업로드 모듈
Google YouTube Data API v3를 사용하여 영상을 자동으로 업로드합니다.
"""

import json
import os
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
                creds.refresh(Request())
            else:
                if not os.path.exists(self.client_secrets):
                    print("❌ client_secrets.json 파일이 필요합니다.")
                    print("   Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하세요.")
                    print("   https://console.cloud.google.com/apis/credentials")
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
    
    def upload_video(self, video_path, script_data, thumbnail_path=None, channel_id=None):
        """비디오를 YouTube에 업로드"""
        
        # 채널 ID 지정된 경우 새로운 업로더 인스턴스 생성
        if channel_id and channel_id != self.target_channel_id:
            uploader = YouTubeUploader(channel_id=channel_id)
            return uploader.upload_video(video_path, script_data, thumbnail_path)
        
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
            
            # 비디오 메타데이터
            title = script_data['title']
            description = script_data.get('description', '')
            
            # 태그: 스크립트의 5개 태그 + 기본 태그
            script_tags = script_data.get('tags', [])
            if isinstance(script_tags, list):
                tags = script_tags + self.config['upload']['default_tags']
            else:
                tags = self.config['upload']['default_tags']
            
            # 설명란 강화: 이미 풍성한 설명이 있으면 유지, 없으면 생성
            if not description or len(description) < 50:
                description = f"{script_data.get('title', '')}\n\n추천 정보를 제공하는 채널입니다.\n공감하셨다면 좋아요와 구독을 눌러주세요! 🙏"
            
            # 해시태그: 상위 5개 태그 + shorts 기본 태그
            hashtags = " ".join([f"#{tag}" for tag in tags[:5]])  # 상위 5개 태그
            description += f"\n\n{hashtags}\n#shorts"
            
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': self.config['upload']['category_id']
                },
                'status': {
                    'privacyStatus': self.config['upload']['privacy_status'],
                    'selfDeclaredMadeForKids': False
                }
            }
            
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


if __name__ == "__main__":
    uploader = YouTubeUploader()
    
    # 인증 테스트
    if uploader.authenticate():
        print("\n✅ YouTube API 연결 성공!")
        print("업로드 준비가 완료되었습니다.")
    else:
        print("\n❌ 인증에 실패했습니다.")
        print("client_secrets.json 파일을 확인해주세요.")
