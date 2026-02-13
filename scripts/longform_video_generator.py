"""
롱폼 비디오 생성 모듈 (10-15분)
음성 기반의 롱폼 콘텐츠를 자막과 함께 생성합니다.
- HuggingFace AI 일러스트 생성 (FLUX.1-schnell) + Pexels 폴백
- TextClip으로 자막 생성 (PNG 없이 메모리 효율적)
- sentence_timings 기반 음성 싱크 자막
"""

import json
import os
import random
import requests
import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    from moviepy import (
        ColorClip, AudioFileClip, CompositeVideoClip,
        TextClip, concatenate_videoclips, ImageClip
    )
except ImportError:
    from moviepy.editor import (
        ColorClip, AudioFileClip, CompositeVideoClip,
        TextClip, concatenate_videoclips, ImageClip
    )


class LongformVideoGenerator:
    # Pexels 검색에 사용할 영문 키워드 (순환 사용)
    IMAGE_KEYWORDS = [
        "peaceful nature landscape",
        "city skyline sunset",
        "ocean waves calm",
        "mountain scenery fog",
        "forest path morning light",
        "starry night sky",
        "sunrise horizon clouds",
        "rain window mood",
        "autumn leaves path",
        "cloud sky dramatic",
        "lake reflection peaceful",
        "desert sand dunes",
    ]

    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 비디오 설정
        cfg = self.config.get('video', {}).get('longform', {})
        res = cfg.get('resolution', '1920x1080').split('x')
        self.width = int(res[0])
        self.height = int(res[1])
        self.fps = cfg.get('fps', 30)
        self.bg_color = cfg.get('background_color', '#000000')
        self.text_color = cfg.get('text_color', '#ffffff')
        self.accent_color = cfg.get('accent_color', '#00d4ff')
        self.font_size = cfg.get('text_font_size', 48)

        # Pexels API 키
        self.pexels_api_key = self.config.get('pexels_api_key', '')

        # HuggingFace API
        self.hf_token = self.config.get('huggingface_token', '')
        self.hf_model_url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

        # 한글 폰트 찾기
        self.font_path = self._find_korean_font()

        # 출력 디렉토리 생성
        os.makedirs("output/longform_images", exist_ok=True)
        os.makedirs("output/longform_videos", exist_ok=True)

    def _find_korean_font(self):
        """한글 폰트 찾기"""
        possible_paths = [
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/System/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/NotoSansCJK.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/nanum/NanumGothic.ttf",
            "/Windows/Fonts/malgun.ttf",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def create_video(self, script_data, audio_path, video_output_path,
                     sentence_timings=None, use_ai_background=True):
        """롱폼 비디오 생성 메인 메서드 (thumbnail_path 함께 반환)"""
        print("\n🎬 롱폼 비디오 생성 시작")
        self._thumbnail_path = None  # 썸네일 경로 저장용

        audio_clip = None
        final_video = None
        try:
            # 1. 오디오 로드
            print("📊 오디오 분석 중...")
            audio_clip = AudioFileClip(audio_path)
            total_duration = audio_clip.duration
            print(f"✓ 오디오 길이: {total_duration:.1f}초 ({total_duration/60:.1f}분)")

            if total_duration < 600:
                print(f"⚠️ 경고: 목표(10-15분)보다 짧음 ({total_duration/60:.1f}분)")

            # 2. 비디오 클립 생성 (AI 배경 + PIL 자막)
            print("🎬 비디오 클립 생성 중...")
            video_clips = self._create_video_clips_with_subtitles(
                script_data.get('title', ''),
                total_duration,
                sentence_timings
            )

            # 3. 최종 비디오 합성
            print("🔗 비디오 합성 중...")
            final_video = concatenate_videoclips(video_clips)
            final_video = final_video.with_audio(audio_clip)

            # 4. 저장
            print(f"💾 비디오 저장 중: {video_output_path}")
            os.makedirs(os.path.dirname(video_output_path), exist_ok=True)

            final_video.write_videofile(
                video_output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac'
            )

            print(f"✅ 비디오 생성 완료: {video_output_path}")

            return video_output_path

        except Exception as e:
            print(f"❌ 비디오 생성 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 리소스 정리
            if final_video:
                try:
                    final_video.close()
                except Exception:
                    pass
            if audio_clip:
                try:
                    audio_clip.close()
                except Exception:
                    pass

    def get_thumbnail_path(self):
        """마지막 create_video 호출 시 생성된 썸네일 경로 반환"""
        return self._thumbnail_path

    def _create_video_clips_with_subtitles(self, title, total_duration, sentence_timings):
        """Pexels 배경 이미지 + 음성 싱크 자막으로 비디오 클립 생성"""

        # ── 1. 배경 이미지 생성 (30초마다 교체) ──
        num_images = max(1, int(total_duration / 30) + 1)
        print(f"🎨 배경 이미지 {num_images}장 준비 중 (30초 간격)...")

        # 자막 텍스트에서 AI 프롬프트 생성용 키워드 추출
        scene_texts = self._extract_scene_keywords(sentence_timings, total_duration, num_images)

        bg_images = []
        used_prompts = set()  # 중복 프롬프트 방지
        for i in range(num_images):
            img_path = None

            # 1순위: HuggingFace AI 일러스트
            if self.hf_token:
                prompt = self._build_illustration_prompt(
                    scene_texts[i] if i < len(scene_texts) else "",
                    used_prompts=used_prompts
                )
                img_path = self._generate_ai_illustration(prompt, i + 1)

            # 2순위: Pexels 사진
            if not img_path:
                keyword = self.IMAGE_KEYWORDS[i % len(self.IMAGE_KEYWORDS)]
                img_path = self._download_pexel_image(keyword, i + 1)

            # 3순위: 그라디언트 배경
            if not img_path:
                img_path = self._create_gradient_background(i)

            bg_images.append(img_path)

        # ── 2. 배경 이미지 → ImageClip (30초마다 교체) ──
        bg_clips = []
        for i, bg_path in enumerate(bg_images):
            start_time = i * 30
            end_time = min((i + 1) * 30, total_duration)
            dur = end_time - start_time

            if dur > 0:
                bg_clip = ImageClip(bg_path).with_duration(dur).with_start(start_time)
                bg_clips.append(bg_clip)

        # ── 3. 자막 생성 (PIL 기반, 색상/볼드 지원) ──
        text_clips = []
        hook_text = None  # 썸네일용 후킹 문장 저장
        first_bg_path = bg_images[0] if bg_images else None
        if sentence_timings:
            import re
            print(f"💬 자막 {len(sentence_timings)}개 생성 중 (PIL 기반, 색상 강조)...")
            success_count = 0
            RED = (255, 0, 0, 255)
            WHITE = (255, 255, 255, 255)

            # 인트로/아웃트로 경계 감지
            # 첫 문장 = 인사말 (RED), 두 번째 문장 = 후킹 (RED+BOLD) → 썸네일 사용
            # 마지막 2문장 = 아웃트로 (RED)
            total_sents = len(sentence_timings)

            for i, timing in enumerate(sentence_timings):
                try:
                    start = timing['start']
                    end = timing['end']
                    text = timing['text'].strip()

                    if not text or start >= total_duration:
                        continue

                    # 자막 지속 시간
                    if i + 1 < len(sentence_timings):
                        next_start = sentence_timings[i + 1]['start']
                        duration = next_start - start
                    else:
                        duration = min(end, total_duration) - start

                    if duration < 0.05:
                        continue

                    # 색상/볼드 결정
                    tc = WHITE
                    bold = False
                    if i == 0:  # 첫 문장 = 인사말 (RED)
                        tc = RED
                    elif i == 1:  # 두 번째 문장 = 진짜 후킹 (RED + BOLD)
                        tc = RED
                        bold = True
                        hook_text = text
                    elif i >= total_sents - 2:  # 마지막 2문장 = 아웃트로 RED
                        tc = RED

                    # PIL로 자막 이미지 생성
                    subtitle_img = self._create_subtitle_image(
                        text[:80], text_color=tc, is_bold=bold
                    )

                    clip = ImageClip(subtitle_img)
                    clip = clip.with_duration(duration)
                    clip = clip.with_start(start)
                    clip = clip.with_position(('center', self.height - 300))
                    text_clips.append(clip)
                    success_count += 1

                except Exception as e:
                    if i < 3:
                        print(f"  ⚠️ 자막 #{i+1} 에러: {e}")
                    continue

            print(f"  ✓ 자막 {success_count}/{len(sentence_timings)}개 생성 완료")

            # 썸네일 생성: 첫 배경 이미지 + 후킹 문장 오버레이
            if hook_text and first_bg_path:
                thumb_path = f"output/thumbnails/longform_thumb_{int(time.time())}.jpg"
                os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                self._thumbnail_path = self._create_hook_thumbnail(first_bg_path, hook_text, thumb_path)
        else:
            print("⚠️ sentence_timings 없음 → 자막 생략")

        # ── 4. 모든 클립 합성 ──
        all_clips = bg_clips + text_clips

        if all_clips:
            try:
                composite = CompositeVideoClip(
                    all_clips, size=(self.width, self.height)
                ).with_duration(total_duration)
                return [composite]
            except Exception as e:
                print(f"⚠️ 합성 에러: {e}")

        # 폴백: 검정 배경
        return [ColorClip(
            size=(self.width, self.height), color=(0, 0, 0)
        ).with_duration(total_duration)]

    # ─────────────────────────────────────────────
    #  AI 일러스트 생성 (HuggingFace)
    # ─────────────────────────────────────────────

    def _extract_scene_keywords(self, sentence_timings, total_duration, num_images):
        """각 30초 구간의 자막 전체 텍스트 수집 (AI 프롬프트용)"""
        scene_texts = []
        if not sentence_timings:
            return [""] * num_images

        for i in range(num_images):
            start_time = i * 30
            end_time = min((i + 1) * 30, total_duration)

            # 해당 시간대의 자막 텍스트 전체 수집
            segment_text = ""
            for timing in sentence_timings:
                t_start = timing.get('start', 0)
                if start_time <= t_start < end_time:
                    segment_text += timing.get('text', '') + " "

            scene_texts.append(segment_text.strip())

        return scene_texts

    def _build_illustration_prompt(self, scene_text, used_prompts=None):
        """자막 내용 기반 3D 렌더 스타일 일러스트 프롬프트 생성"""
        base_style = (
            "3D render, cinematic lighting, detailed scene, "
            "modern digital art, high quality, "
            "dramatic composition, vivid colors, "
            "storytelling scene, emotional atmosphere, "
            "horizontal 16:9 aspect ratio, no text"
        )

        # 한국어 → 영어 키워드 매핑 (장면/대상 묘사 중심)
        keyword_map = {
            # 사람/관계
            "사랑": "two people in love, romantic scene",
            "행복": "happy person smiling, warm atmosphere",
            "슬픔": "person feeling sad, melancholy mood, tears",
            "희망": "person looking at hopeful horizon, light breaking through",
            "꿈": "dreamy fantasy world, person dreaming",
            "우정": "two friends together, warm friendship",
            "가족": "family gathering, warm home scene",
            "엄마": "mother and child together, maternal love",
            "아빠": "father figure, family bond",
            "아이": "young child playing, innocent childhood",
            "청년": "young adult facing the world, determination",
            "할머니": "elderly grandmother, wisdom and warmth",
            "할아버지": "elderly grandfather, gentle wisdom",
            "친구": "close friends sharing moment together",
            "연인": "couple in love, romantic scene",
            "부부": "married couple, warm domestic scene",
            "선생님": "teacher and student, learning moment",
            "학생": "student studying hard, school life",
            "직장": "person at work, office scene",
            "동료": "coworkers together, workplace bond",
            "이별": "person saying farewell, bittersweet parting",
            "만남": "two people meeting for first time",
            "눈물": "person with tears, emotional crying scene",
            "웃음": "person laughing joyfully, bright smile",
            "포옹": "two people embracing warmly, heartfelt hug",
            # 감정/상태
            "고민": "person deep in thought, contemplative",
            "후회": "person feeling regret, looking back",
            "용기": "person standing brave, courageous pose",
            "성공": "person achieving goal, celebration moment",
            "실패": "person fallen but getting back up, resilience",
            "외로": "person alone, solitude scene",
            "스트레스": "person overwhelmed, pressure",
            "위로": "person comforting another, consolation",
            "감사": "person expressing gratitude, thankful moment",
            "분노": "person frustrated, angry emotion",
            "화해": "two people reconciling, making peace",
            # 장소/환경
            "바다": "ocean waves, coastal scenery, sea horizon",
            "산": "mountain landscape, hiking path, mountain peak",
            "하늘": "vast sky with clouds, atmospheric sky",
            "별": "starry night sky, constellation, night landscape",
            "비": "rainy scene, rain drops, umbrella in rain",
            "눈": "snowy winter scene, falling snowflakes",
            "봄": "spring cherry blossoms, flowers blooming",
            "여름": "summer sunshine, bright blue sky",
            "가을": "autumn red and golden leaves falling",
            "겨울": "winter cold landscape, warm cozy indoor",
            "도시": "city street scene, urban landscape",
            "숲": "forest path, trees and green nature",
            "밤": "night scene with moonlight, dark atmosphere",
            "아침": "morning sunrise, dawn light, fresh start",
            "노을": "beautiful sunset, golden hour sky",
            "꽃": "flowers in bloom, garden scene",
            "집": "cozy house interior, warm home",
            "학교": "school building, campus, classroom",
            "병원": "hospital scene, medical setting",
            "카페": "cozy cafe interior, coffee shop",
            "길": "long road ahead, path stretching forward",
            "다리": "bridge crossing over water, connection",
            # 상황/행동
            "여행": "person traveling, adventure journey",
            "공부": "person studying with books, learning",
            "일": "person working hard, dedication",
            "음악": "person playing music, musical instrument",
            "편지": "person writing or reading a letter",
            "전화": "person making a phone call, conversation",
            "선물": "gift giving moment, wrapped present",
            "약속": "two people making a promise, pinky promise",
            "기다": "person waiting patiently, anticipation",
            "달리": "person running forward, determination",
            "걸어": "person walking along a path",
            "앉아": "person sitting peacefully, contemplation",
            # 추상/기타
            "시간": "clock, time passing, hourglass, seasons changing",
            "미래": "futuristic hopeful horizon, path ahead",
            "과거": "nostalgic vintage scene, old memories, sepia tone",
            "인생": "life journey, path from young to old",
            "마음": "heart symbol, emotional inner world",
            "기억": "faded photos, memories floating, nostalgia",
            "변화": "transformation scene, caterpillar to butterfly",
            "선택": "person at crossroads, making a choice",
            "돈": "coins and savings, financial scene",
            "건강": "person exercising, healthy lifestyle",
        }

        # 자막에서 매칭되는 키워드 찾기 (최대 5개)
        matched_themes = []
        for ko, en in keyword_map.items():
            if ko in scene_text:
                matched_themes.append(en)

        # 사람 관련 키워드가 있으면 사람을 포함하도록 강조
        people_keywords = ["사람", "남자", "여자", "그", "그녀", "나", "우리", "저", "너",
                          "엄마", "아빠", "아이", "친구", "선생", "학생", "부모", "형", "누나",
                          "동생", "언니", "오빠", "할머니", "할아버지", "아저씨", "아줌마"]
        has_people = any(kw in scene_text for kw in people_keywords)

        if matched_themes:
            # 중복 방지: used_prompts에 이미 있는 테마 제외
            unique_themes = matched_themes[:5]
            theme = ", ".join(unique_themes)
            people_note = ", people characters prominently featured" if has_people else ""
            prompt = f"{theme}{people_note}, {base_style}"
        else:
            # 매칭 없으면 장면 텍스트 일부를 직접 사용
            # 자막에서 명사/키워드 느낌으로 앞부분 추출
            hint = scene_text[:80].replace('\n', ' ').strip()
            people_note = ", with people characters" if has_people else ""
            default_scenes = [
                "peaceful village at sunset, warm community",
                "cozy room with window light, person reading",
                "forest clearing with sunbeams, magical atmosphere",
                "ocean cliff overlooking vast sea, contemplation",
                "city rooftop at twilight, person gazing at skyline",
                "flower garden in gentle breeze, peaceful moment",
                "mountain path at dawn, person hiking upward",
                "rain falling on window, person inside warm room",
                "ancient tree in meadow, person sitting beneath",
                "train platform, person waiting for departure",
                "library filled with books, quiet study scene",
                "riverside at golden hour, person fishing peacefully",
            ]
            scene = default_scenes[hash(hint) % len(default_scenes)]
            prompt = f"{scene}{people_note}, {base_style}"

        # 중복 프롬프트 방지
        if used_prompts is not None:
            if prompt in used_prompts:
                # 변형 추가로 중복 회피
                variations = [
                    "wide angle view, ", "close up view, ",
                    "bird eye view, ", "from behind, ",
                    "evening version, ", "morning version, ",
                    "different perspective, ", "profile view, ",
                ]
                for v in variations:
                    new_prompt = v + prompt
                    if new_prompt not in used_prompts:
                        prompt = new_prompt
                        break
            used_prompts.add(prompt)

        return prompt

    def _generate_ai_illustration(self, prompt, index):
        """HuggingFace FLUX.1-schnell로 AI 일러스트 생성"""
        try:
            headers = {
                "Authorization": f"Bearer {self.hf_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "inputs": prompt,
                "parameters": {"width": 1344, "height": 768}
            }

            print(f"  [{index}] AI 일러스트 생성 중...")
            response = requests.post(
                self.hf_model_url,
                json=payload,
                headers=headers,
                timeout=60,
            )

            ct = response.headers.get("content-type", "")
            if response.status_code == 200 and "image" in ct:
                from io import BytesIO
                img = Image.open(BytesIO(response.content))

                # Center crop으로 비율 유지하며 리사이즈
                img_cropped = self._center_crop_resize(img)
                output_path = f"output/longform_images/bg_ai_{index}_{int(time.time())}.jpg"
                img_cropped.save(output_path, "JPEG", quality=90)

                fsize = os.path.getsize(output_path) // 1024
                print(f"  ✓ [{index}] AI 일러스트 완료 ({fsize}KB)")
                return output_path
            elif response.status_code == 503:
                print(f"  ⚠️ [{index}] 모델 로딩 중... Pexels 폴백")
            else:
                print(f"  ⚠️ [{index}] AI 생성 실패 ({response.status_code}) → Pexels 폴백")

            return None

        except Exception as e:
            print(f"  ⚠️ [{index}] AI 생성 에러: {e} → Pexels 폴백")
            return None

    # ─────────────────────────────────────────────
    #  배경 이미지 관련 (Pexels 폴백)
    # ─────────────────────────────────────────────

    def _download_pexel_image(self, keyword, index):
        """Pexels API에서 배경 이미지 다운로드"""

        if not self.pexels_api_key:
            print(f"  [{index}] ⚠️ Pexels API 키 없음 → 그라디언트 배경 사용")
            return None

        try:
            headers = {"Authorization": self.pexels_api_key}
            params = {
                "query": keyword,
                "per_page": 15,
                "orientation": "landscape",
                "size": "large",
            }

            print(f"  [{index}] Pexels 검색: {keyword}...")
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params=params,
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])

                if photos:
                    photo = random.choice(photos)
                    img_url = photo["src"]["landscape"]

                    img_resp = requests.get(img_url, timeout=20)
                    if img_resp.status_code == 200:
                        output_path = f"output/longform_images/bg_pexel_{index}_{int(time.time())}.jpg"
                        with open(output_path, 'wb') as f:
                            f.write(img_resp.content)

                        # Center crop으로 비율 유지하며 리사이즈
                        try:
                            img = Image.open(output_path)
                            img = self._center_crop_resize(img)
                            img.save(output_path, 'JPEG', quality=90)
                        except Exception:
                            pass

                        print(f"  ✓ [{index}] 다운로드 완료")
                        return output_path
                    else:
                        print(f"  ⚠️ [{index}] 이미지 다운로드 실패: {img_resp.status_code}")
                else:
                    print(f"  ⚠️ [{index}] 검색 결과 없음: {keyword}")
            elif response.status_code == 401:
                print(f"  ⚠️ [{index}] Pexels API 키가 올바르지 않습니다")
            else:
                print(f"  ⚠️ [{index}] API 에러: {response.status_code}")

            return None

        except Exception as e:
            print(f"  ⚠️ [{index}] 다운로드 에러: {e}")
            return None

    def _create_gradient_background(self, index):
        """그라디언트 배경 이미지 생성 (Pexels 실패 시 폴백)"""
        colors = [
            ((15, 25, 50), (40, 70, 130)),   # 진한 파랑
            ((30, 15, 45), (80, 40, 120)),   # 진한 보라
            ((45, 30, 15), (120, 80, 40)),   # 진한 갈색
            ((15, 40, 30), (40, 110, 80)),   # 진한 청록
            ((40, 15, 25), (110, 40, 70)),   # 진한 분홍
            ((10, 10, 30), (30, 30, 90)),    # 짙은 남색
        ]

        c1, c2 = colors[index % len(colors)]

        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)

        for y in range(self.height):
            r = y / self.height
            color = tuple(int(c1[j] + (c2[j] - c1[j]) * r) for j in range(3))
            draw.line([(0, y), (self.width, y)], fill=color)

        path = f"output/longform_images/bg_grad_{index}_{int(time.time())}.jpg"
        img.save(path, 'JPEG', quality=90)
        print(f"  ✓ [{index+1}] 그라디언트 배경 생성")
        return path

    # ─────────────────────────────────────────────
    #  PIL 자막 + 썸네일
    # ─────────────────────────────────────────────

    def _load_font(self, font_size):
        """한글 폰트 로드"""
        font = None
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                fallback_fonts = [
                    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                ]
                for fp in fallback_fonts:
                    if os.path.exists(fp):
                        try:
                            font = ImageFont.truetype(fp, font_size)
                            break
                        except:
                            continue
        except:
            pass
        if not font:
            font = ImageFont.load_default()
        return font

    def _create_subtitle_image(self, text, font_size=48, text_color=(255, 255, 255, 255), is_bold=False):
        """PIL로 자막 이미지 생성 (한글 지원, 색상/볼드)"""
        temp_img = Image.new('RGBA', (self.width, 300), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        font = self._load_font(font_size)

        # 단어 단위 줄바꿈
        max_width = self.width - 200
        lines = []
        current_line = ""
        words = text.split(' ')

        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
                    current_line = ""
        if current_line:
            lines.append(current_line)

        line_height = font_size + 20
        padding = 15
        text_bg_height = len(lines) * line_height + (padding * 2)
        img_height = text_bg_height + 30

        img = Image.new('RGBA', (self.width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 반투명 검정 박스
        box_top = 15
        box_bottom = box_top + text_bg_height
        box_left = 60
        box_right = self.width - 60

        box_img = Image.new('RGBA', (self.width, img_height), (0, 0, 0, 0))
        box_draw = ImageDraw.Draw(box_img)
        box_draw.rectangle([(box_left, box_top), (box_right, box_bottom)], fill=(0, 0, 0, 200))
        box_draw.rectangle([(box_left, box_top), (box_right, box_bottom)], outline=(0, 0, 0, 255), width=2)
        img = Image.alpha_composite(img, box_img)
        draw = ImageDraw.Draw(img)

        y_offset = box_top + padding
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2

            # 그림자
            for offset in [(3, 3), (2, 2)]:
                draw.text((x + offset[0], y_offset + offset[1]), line, font=font, fill=(0, 0, 0, 200))
            # 외곽선
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y_offset + dy), line, font=font, fill=(0, 0, 0, 255))
            # 본문
            draw.text((x, y_offset), line, font=font, fill=text_color)
            if is_bold:
                draw.text((x + 1, y_offset), line, font=font, fill=text_color)
                draw.text((x + 2, y_offset), line, font=font, fill=text_color)
            y_offset += line_height

        return np.array(img)

    def _create_hook_thumbnail(self, bg_image_path, hook_text, output_path):
        """배경 이미지 + 후킹 문장 오버레이로 썸네일 생성"""
        try:
            bg = Image.open(bg_image_path).convert('RGB')
            bg = bg.resize((self.width, self.height), Image.LANCZOS)
            draw = ImageDraw.Draw(bg)

            font_size = 72
            font = self._load_font(font_size)

            # 단어 단위 줄바꿈
            max_width = self.width - 200
            lines = []
            current_line = ""
            for word in hook_text.split(' '):
                test_line = current_line + (' ' if current_line else '') + word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            line_height = font_size + 25
            total_text_h = len(lines) * line_height
            y_start = (self.height - total_text_h) // 2

            # 반투명 배경 박스
            pad = 30
            box_top = y_start - pad
            box_bottom = y_start + total_text_h + pad
            overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [(80, box_top), (self.width - 80, box_bottom)],
                fill=(0, 0, 0, 160)
            )
            bg = Image.alpha_composite(bg.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(bg)

            # 후킹 문장 그리기 (#FF0000 + 볼드)
            RED = (255, 0, 0)
            for idx, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                tw = bbox[2] - bbox[0]
                x = (self.width - tw) // 2
                y = y_start + idx * line_height

                # 그림자 + 외곽선
                for ox, oy in [(4, 4), (3, 3), (2, 2)]:
                    draw.text((x + ox, y + oy), line, font=font, fill=(0, 0, 0))
                for dx in [-3, -2, -1, 0, 1, 2, 3]:
                    for dy in [-3, -2, -1, 0, 1, 2, 3]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
                # 빨간 본문 + 볼드
                draw.text((x, y), line, font=font, fill=RED)
                draw.text((x + 1, y), line, font=font, fill=RED)
                draw.text((x + 2, y), line, font=font, fill=RED)

            bg.save(output_path, 'JPEG', quality=95)
            print(f"  ✅ 후킹 썸네일 생성: {output_path}")
            return output_path
        except Exception as e:
            print(f"  ⚠️ 썸네일 생성 실패: {e}")
            return None

    # ─────────────────────────────────────────────
    #  유틸리티
    # ─────────────────────────────────────────────

    def _hex_to_rgb(self, hex_color):
        """Hex 색상을 RGB 튜플로 변환"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _center_crop_resize(self, img):
        """Center crop 방식으로 비율 유지하며 target 해상도에 맞게 리사이즈"""
        target_w, target_h = self.width, self.height
        target_ratio = target_w / target_h  # 16:9 = 1.778
        img_w, img_h = img.size
        img_ratio = img_w / img_h

        if img_ratio > target_ratio:
            # 이미지가 더 넓음 → 좌우 크롭
            new_w = int(img_h * target_ratio)
            left = (img_w - new_w) // 2
            img = img.crop((left, 0, left + new_w, img_h))
        else:
            # 이미지가 더 높음 → 상하 크롭
            new_h = int(img_w / target_ratio)
            top = (img_h - new_h) // 2
            img = img.crop((0, top, img_w, top + new_h))

        return img.resize((target_w, target_h), Image.LANCZOS)


if __name__ == "__main__":
    gen = LongformVideoGenerator()
    print(f"✓ 해상도: {gen.width}x{gen.height}")
    print(f"✓ 폰트: {gen.font_path}")
    print(f"✓ Pexels API: {'설정됨' if gen.pexels_api_key else '미설정'}")
    print(f"✓ HuggingFace: {'설정됨' if gen.hf_token else '미설정'}")
