"""
비디오 생성 모듈
MoviePy를 사용하여 음성, 배경, 자막을 합성하여 최종 영상을 생성합니다.
AI 이미지 생성: HuggingFace FLUX.1-schnell (1순위) → Together AI (2순위) → Pexels (3순위)
"""

import json
import os
import requests
import sys
import time
import io
from contextlib import redirect_stdout
try:
    from moviepy import (
        ColorClip, AudioFileClip, CompositeVideoClip,
        TextClip, concatenate_videoclips, ImageClip, VideoClip
    )
except ImportError:
    print("⚠️ moviepy 2.x import 실패, moviepy.editor에서 시도...")
    from moviepy.editor import (  # type: ignore
        ColorClip, AudioFileClip, CompositeVideoClip,
        TextClip, concatenate_videoclips, ImageClip, VideoClip
    )
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np


class VideoGenerator:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 쇼츠 비디오 설정
        shorts_config = self.config['video']['shorts']
        res = shorts_config['resolution'].split('x')
        self.width = int(res[0])
        self.height = int(res[1])
        self.fps = shorts_config['fps']
        self.bg_color = shorts_config['background_color']
        self.text_color = shorts_config['text_color']
        self.accent_color = shorts_config['accent_color']

        # AI 이미지 생성 설정
        self.hf_token = self.config.get('huggingface_token', '')
        self.together_api_key = self.config.get('together_api_key', '')
        self.pexels_api_key = self.config.get('pexels_api_key', '')

        # 한글 폰트 찾기
        self.font_path = self._find_korean_font()

    # ──────────────────────────────────────────────────
    # AI 이미지 생성 (3-tier 폴백)
    # ──────────────────────────────────────────────────
    def generate_ai_image_huggingface(self, prompt, retry_count=2):
        """HuggingFace FLUX.1-schnell로 이미지 생성 (9:16 세로)"""
        if not self.hf_token:
            return None

        url = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json",
        }
        # 9:16 비율 → 768x1344
        payload = {
            "inputs": prompt,
            "parameters": {"width": 768, "height": 1344},
        }

        for attempt in range(retry_count):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                if resp.status_code == 200 and resp.headers.get('content-type', '').startswith('image'):
                    img = Image.open(io.BytesIO(resp.content))
                    if img.size[0] > 100:
                        return img
                print(f"   ⚠️ HF 응답 코드 {resp.status_code}, 재시도 {attempt+1}/{retry_count}")
                time.sleep(3)
            except Exception as e:
                print(f"   ⚠️ HF 오류: {str(e)[:80]}, 재시도 {attempt+1}/{retry_count}")
                time.sleep(3)
        return None

    def generate_ai_image_together(self, prompt, retry_count=2):
        """Together AI FLUX.1-schnell로 이미지 생성 (9:16 세로)"""
        if not self.together_api_key:
            return None

        url = "https://api.together.xyz/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell-Free",
            "prompt": prompt,
            "width": 768,
            "height": 1344,
            "n": 1,
        }

        for attempt in range(retry_count):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()
                    img_data = data.get('data', [{}])[0]
                    if 'b64_json' in img_data:
                        import base64
                        img_bytes = base64.b64decode(img_data['b64_json'])
                        img = Image.open(io.BytesIO(img_bytes))
                        return img
                    elif 'url' in img_data:
                        img_resp = requests.get(img_data['url'], timeout=30)
                        if img_resp.status_code == 200:
                            img = Image.open(io.BytesIO(img_resp.content))
                            return img
                print(f"   ⚠️ Together 응답 코드 {resp.status_code}, 재시도 {attempt+1}/{retry_count}")
                time.sleep(3)
            except Exception as e:
                print(f"   ⚠️ Together 오류: {str(e)[:80]}, 재시도 {attempt+1}/{retry_count}")
                time.sleep(3)
        return None

    def generate_ai_image(self, prompt, section_name="image"):
        """3-tier 폴백: HuggingFace → Together AI → Pexels"""
        # 프롬프트에서 --ar 9:16 등 제거 (API는 width/height 파라미터 사용)
        import re
        clean_prompt = re.sub(r'--\w+\s+\S+', '', prompt).strip()

        # 1차: HuggingFace FLUX.1-schnell
        print(f"   🎨 [{section_name}] HuggingFace 이미지 생성 중...")
        img = self.generate_ai_image_huggingface(clean_prompt)
        if img:
            print(f"   ✅ [{section_name}] HuggingFace 성공")
            return img

        # 2차: Together AI
        if self.together_api_key:
            print(f"   🎨 [{section_name}] Together AI 폴백...")
            img = self.generate_ai_image_together(clean_prompt)
            if img:
                print(f"   ✅ [{section_name}] Together AI 성공")
                return img

        # 3차: Pexels 키워드 검색
        print(f"   📷 [{section_name}] Pexels 폴백...")
        # 프롬프트에서 영어 키워드 추출
        keywords = ' '.join(clean_prompt.split()[:5])
        pexels_images = self.download_background_images(keywords, count=1, script_text="")
        if pexels_images:
            print(f"   ✅ [{section_name}] Pexels 성공")
            return pexels_images[0]

        # 최종 폴백: 그라디언트
        print(f"   🎨 [{section_name}] 그라디언트 폴백")
        return self._create_gradient_image()

    def generate_ai_background_images(self, script_data, use_ai=True):
        """script_data의 image_prompts를 사용해 5개 AI 배경 이미지 생성"""
        if not use_ai:
            print("ℹ️ AI 이미지 생성 비활성화, 기존 방식 사용")
            return None

        image_prompts = script_data.get('image_prompts', [])
        if not image_prompts or len(image_prompts) < 5:
            print("⚠️ image_prompts가 5개 미만, 기존 방식 사용")
            return None

        try:
            print("🎨 AI 배경 이미지 생성 시작 (5장)...")
            section_names = ["intro", "section1", "section2", "section3", "outro"]
            ai_images = []

            for i, (section, prompt) in enumerate(zip(section_names, image_prompts)):
                img = self.generate_ai_image(prompt, section_name=section)
                img = self._resize_and_crop(img)
                ai_images.append((section, img))
                # API 속도 제한 방지 (마지막 이미지 후에는 대기 불필요)
                if i < 4:
                    time.sleep(1.5)

            print(f"✅ 총 {len(ai_images)}개 AI 배경 이미지 생성 완료!")
            return ai_images

        except Exception as e:
            print(f"❌ AI 배경 이미지 생성 실패: {e}")
            return None
    
    def _find_korean_font(self):
        """시스템에서 한글 폰트 찾기 (GitHub Actions 지원)"""
        # macOS 폰트 경로들
        font_paths = [
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/Library/Fonts/AppleGothic.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            # Linux 폰트 경로들 (GitHub Actions)
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            # 추가 Linux 경로
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                print(f"✅ 한글 폰트 발견: {path}")
                return path
        
        print("⚠️ 한글 폰트를 찾지 못했습니다. 기본 폰트 사용")
        return None
    
    def extract_keywords_from_script(self, script_text):
        """대본에서 키워드 추출 - 다양성 증가"""
        import re
        import random
        
        # 한글-영어 키워드 매핑 (각 키워드별로 여러 검색 쿼리 옵션)
        keyword_map = {
            # 금융/재테크 (다양한 쿼리)
            "돈": ["money finance", "cash wealth", "coins gold", "financial success"],
            "주식": ["stock market", "trading chart", "investment growth", "financial data"],
            "암호": ["cryptocurrency", "bitcoin blockchain", "digital currency"],
            "투자": ["investment portfolio", "business growth", "wealth building"],
            "부동산": ["real estate", "house property", "building architecture"],
            "이직": ["career change", "job interview", "business opportunity"],
            "절약": ["saving money", "budgeting finance", "piggy bank"],
            "금융": ["banking finance", "economy growth", "financial planning"],
            
            # 심리/성공
            "심리": ["psychology mind", "brain thinking", "mental health"],
            "성공": ["success winner", "achievement trophy", "business growth"],
            "자존감": ["confidence self", "empowerment motivation", "personal growth"],
            "관계": ["relationship people", "friendship together", "communication"],
            "스트레스": ["stress relief", "meditation peace", "relaxation calm"],
            "집중": ["focus concentration", "meditation brain", "mindfulness"],
            "수면": ["sleep rest", "bedroom night", "peaceful calm"],
            "습관": ["habit routine", "lifestyle healthy", "self improvement"],
            
            # 뷰티/건강
            "얼굴": ["face beauty", "skin care", "skincare routine"],
            "피부": ["skin dermatology", "beauty cosmetics", "skincare"],
            "헬스": ["gym fitness", "exercise workout", "weight training"],
            "건강": ["health wellness", "nutrition healthy", "fitness lifestyle"],
            "살": ["weight loss", "diet healthy", "body fitness"],
            "연예인": ["celebrity fame", "entertainment fashion", "glamour"],
            
            # 커리어/학습
            "유튜브": ["youtube content", "video production", "streaming media"],
            "알고리즘": ["data algorithm", "artificial intelligence", "technology"],
            "직업": ["career profession", "job workplace", "business"],
            "면접": ["job interview", "business meeting", "interview"],
            "커리어": ["career growth", "professional development", "business"],
            "입시": ["graduation school", "education campus", "university"],
            "공무원": ["government office", "civil service", "administration"],
            "영어": ["english language", "learning education", "language study"],
            
            # 과학/기술
            "뇌": ["brain neuroscience", "thinking intelligence", "mind science"],
            "우주": ["space galaxy", "universe stars", "astronomy cosmos"],
            "행성": ["planet solar", "space universe", "astronomy"],
            "블랙홀": ["black hole space", "universe physics", "astronomy"],
            "태양": ["sun solar", "star bright", "astronomy"],
            "달": ["moon lunar", "night sky", "space"],
            "별": ["stars night", "constellation sky", "astronomy"],
            "과학": ["science laboratory", "research experiment", "technology"],
            "실험": ["experiment laboratory", "science research", "chemical"],
            "DNA": ["DNA genetics", "biology science", "microscope"],
            "세포": ["cell biology", "microscope science", "medical"],
            "원자": ["atom physics", "molecule science", "quantum"],
            "에너지": ["energy power", "electricity", "solar power"],
            "전기": ["electricity lightning", "power energy", "electrical"],
            "로봇": ["robot technology", "artificial intelligence", "automation"],
            "인공지능": ["artificial intelligence AI", "technology future", "robot"],
            "컴퓨터": ["computer technology", "digital gadget", "electronics"],
            
            # 자연/동물
            "바다": ["ocean underwater", "sea beach", "marine life"],
            "산": ["mountain nature", "landscape hiking", "wilderness"],
            "숲": ["forest trees", "nature woodland", "green landscape"],
            "동물": ["animals wildlife", "nature fauna", "wildlife photography"],
            "새": ["birds flying", "wildlife nature", "bird photography"],
            "물고기": ["fish underwater", "aquatic marine", "ocean life"],
            "고래": ["whale ocean", "marine mammal", "underwater"],
            "상어": ["shark ocean", "marine predator", "underwater"],
            "사자": ["lion wildlife", "safari animals", "wildlife africa"],
            "호랑이": ["tiger wildlife", "nature stripes", "big cats"],
            "공룡": ["dinosaur prehistoric", "extinct animals", "fossil"],
            "곤충": ["insects macro", "nature detail", "close up"],
            "꽃": ["flowers nature", "garden bloom", "colorful plants"],
            "나무": ["trees forest", "nature leaves", "woodland"],
            
            # 인체/건강
            "심장": ["heart medical", "cardiac health", "anatomy"],
            "눈": ["eye vision", "sight optical", "eyeball"],
            "귀": ["ear hearing", "audio sound", "auditory"],
            "피": ["blood medical", "vein anatomy", "healthcare"],
            "근육": ["muscle fitness", "body workout", "exercise"],
            "뼈": ["skeleton bones", "anatomy structure", "medical"],
            "인체": ["human body", "anatomy medical", "health"],
            
            # 역사/문화
            "역사": ["history ancient", "civilization culture", "historical"],
            "전쟁": ["war battle", "history conflict", "military"],
            "왕": ["king royal", "castle monarchy", "palace"],
            "피라미드": ["pyramid egypt", "ancient architecture", "monument"],
            "로마": ["rome ancient", "roman empire", "ancient civilization"],
            "그리스": ["greece ancient", "greek temple", "antique"],
            "중세": ["medieval castle", "knight history", "ancient times"],
            "문명": ["civilization ancient", "culture history", "society"],
            
            # 세계/지리
            "세계": ["world globe", "earth travel", "international"],
            "지구": ["earth planet", "world geography", "globe"],
            "나라": ["countries travel", "flags world", "international"],
            "도시": ["city skyline", "urban landscape", "metropolis"],
            "사막": ["desert landscape", "sand nature", "arid"],
            "북극": ["arctic ice", "polar region", "snow"],
            "화산": ["volcano lava", "eruption nature", "geological"],
            "지진": ["earthquake disaster", "seismic", "natural disaster"],
            
            # 감정/기타
            "감정": ["emotions feeling", "expression face", "psychology"],
            "기억": ["memory brain", "remembering thought", "mind"],
            "꿈": ["dream sleep", "nighttime rest", "subconscious"],
            "행복": ["happiness joy", "smile success", "celebration"],
            "공포": ["fear horror", "dark scary", "thriller"],
            "사랑": ["love romance", "heart relationship", "passion"],
            "기록": ["record achievement", "trophy winner", "success"],
            "숫자": ["numbers data", "statistics chart", "mathematics"],
        }
        
        # 대본에서 매칭되는 키워드 찾기
        found_keywords = []
        for kr, queries in keyword_map.items():
            if kr in script_text:
                # 각 키워드마다 여러 쿼리 중 하나를 랜덤으로 선택
                if isinstance(queries, list):
                    found_keywords.append(random.choice(queries))
                else:
                    found_keywords.append(queries)
        
        # 키워드가 없으면 다양한 기본값 중 선택
        if not found_keywords:
            default_queries = [
                "abstract dark background",
                "cinematic lighting", 
                "dramatic background",
                "modern minimal",
                "professional wallpaper",
                "inspirational poster",
                "creative design",
                "geometric pattern"
            ]
            found_keywords = [random.choice(default_queries)]
        
        return found_keywords

    def download_background_images(self, keywords, count=3, script_text=""):
        """Pexels API로 배경 이미지 다운로드 (다양성 증가)"""
        import random
        
        images = []
        pexels_api_key = self.config.get('pexels_api_key', '')
        
        try:
            # 대본에서 키워드 추출 (매번 다른 결과)
            if script_text:
                search_queries = self.extract_keywords_from_script(script_text)
            else:
                # 토픽 기반 폴백 (기존 호환성)
                keyword_map = {
                    "돈": ["money finance", "wealth"],
                    "주식": ["stock market", "trading"],
                    "심리": ["psychology mind", "brain thinking"],
                    "건강": ["health wellness", "fitness"],
                    "역사": ["history ancient", "civilization"],
                    "우주": ["space galaxy", "astronomy"],
                    "기술": ["technology future", "innovation"],
                }
                search_queries = ["abstract dark background"]
                for kr, qs in keyword_map.items():
                    if kr in keywords:
                        search_queries = qs if isinstance(qs, list) else [qs]
                        break
            
            headers = {"Authorization": pexels_api_key}
            
            # 랜덤 페이지 오프셋으로 다양한 이미지 가져오기
            page_offset = random.randint(1, 10)
            
            # 각 키워드별로 이미지 검색
            for query in search_queries[:8]:  # 최대 8개 키워드
                if len(images) >= count:
                    break
                
                try:
                    # 랜덤 페이지 사용으로 매번 다른 이미지 가져오기
                    page = page_offset + random.randint(0, 5)
                    per_page = max(5, count - len(images) + 2)
                    
                    url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}&page={page}&orientation=portrait"
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        photos = data.get('photos', [])
                        
                        # 여러 사진 중에서 랜덤 선택으로 다양성 증가
                        if len(photos) > 0:
                            random.shuffle(photos)
                            for photo in photos:
                                if len(images) >= count:
                                    break
                                try:
                                    img_url = photo['src']['large2x']
                                    img_response = requests.get(img_url, timeout=10)
                                    if img_response.status_code == 200:
                                        from io import BytesIO
                                        img = Image.open(BytesIO(img_response.content))
                                        img = self._resize_and_crop(img)
                                        images.append(img)
                                        print(f"✅ 배경 이미지 다운로드 ({query}): {len(images)}/{count}")
                                except:
                                    continue
                except Exception as e:
                    print(f"⚠️  쿼리 실패 ({query}): {e}")
                    continue
            
        except Exception as e:
            print(f"⚠️ 배경 이미지 다운로드 실패: {e}")
        
        # 이미지 부족 시 - 다양한 폴백 쿼리로 추가 검색
        if len(images) < count:
            fallback_queries = [
                "dark abstract modern",
                "night sky stars",
                "nature landscape scenic",
                "cinematic dramatic lighting",
                "urban city modern",
                "technology digital future",
                "professional business",
                "creative artistic",
                "minimalist design",
                "colorful vibrant",
                "moody atmospheric",
                "energy power",
                "success achievement",
                "growth development",
                "motion dynamic",
                "bright sunny"
            ]
            
            # 랜덤으로 섞어서 순회
            random.shuffle(fallback_queries)
            
            for query in fallback_queries:
                if len(images) >= count:
                    break
                
                try:
                    # 매번 다른 페이지에서 가져오기
                    page = random.randint(1, 15)
                    print(f"📷 추가 배경 검색 ({query}) - page {page}...")
                    
                    url = f"https://api.pexels.com/v1/search?query={query}&per_page=5&page={page}&orientation=portrait"
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        photos = data.get('photos', [])
                        
                        if len(photos) > 0:
                            random.shuffle(photos)
                            for photo in photos:
                                if len(images) >= count:
                                    break
                                try:
                                    img_url = photo['src']['large2x']
                                    img_response = requests.get(img_url, timeout=10)
                                    if img_response.status_code == 200:
                                        from io import BytesIO
                                        img = Image.open(BytesIO(img_response.content))
                                        img = self._resize_and_crop(img)
                                        images.append(img)
                                        print(f"✅ 추가 배경: {len(images)}/{count}")
                                except:
                                    continue
                except:
                    continue
        
        # 그래도 부족하면 인기 이미지에서 추가 (다양한 페이지)
        if len(images) < count:
            try:
                print("📷 인기 이미지에서 추가 검색...")
                page = random.randint(1, 50)
                url = f"https://api.pexels.com/v1/curated?per_page={count - len(images) + 3}&page={page}&orientation=portrait"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    photos = data.get('photos', [])
                    
                    if len(photos) > 0:
                        random.shuffle(photos)
                        for photo in photos:
                            if len(images) >= count:
                                break
                            try:
                                img_url = photo['src']['large2x']
                                img_response = requests.get(img_url, timeout=10)
                                if img_response.status_code == 200:
                                    from io import BytesIO
                                    img = Image.open(BytesIO(img_response.content))
                                    img = self._resize_and_crop(img)
                                    images.append(img)
                                    print(f"✅ 인기 이미지 추가: {len(images)}/{count}")
                            except:
                                continue
            except:
                pass
        
        return images
    
    def _resize_and_crop(self, img):
        """이미지를 세로 형식으로 크롭 및 리사이즈"""
        target_ratio = self.height / self.width
        img_ratio = img.height / img.width
        
        if img_ratio > target_ratio:
            # 이미지가 더 세로로 김 - 위아래 자르기
            new_height = int(img.width * target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))
        else:
            # 이미지가 더 가로로 김 - 좌우 자르기
            new_width = int(img.height / target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        
        img = img.resize((self.width, self.height), Image.LANCZOS)
        
        # 어둡게 처리 (자막이 잘 보이도록)
        enhancer = Image.new('RGBA', img.size, (0, 0, 0, 150))
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, enhancer)
        
        return img.convert('RGB')
    
    def _create_gradient_image(self):
        """그라디언트 배경 이미지 생성"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # 그라디언트 색상
        colors = [
            ((26, 26, 46), (46, 46, 86)),
            ((20, 30, 48), (36, 59, 85)),
            ((15, 32, 39), (32, 58, 67)),
        ]
        
        import random
        c1, c2 = random.choice(colors)
        
        for i in range(self.height):
            ratio = i / self.height
            r = int(c1[0] + (c2[0] - c1[0]) * ratio)
            g = int(c1[1] + (c2[1] - c1[1]) * ratio)
            b = int(c1[2] + (c2[2] - c1[2]) * ratio)
            draw.line([(0, i), (self.width, i)], fill=(r, g, b))
        
        return img

    def create_background_video(self, images, duration, section_times=None):
        """배경 이미지들로 비디오 클립 생성 (섹션 타이밍 동기화)"""
        if not images:
            return ColorClip(
                size=(self.width, self.height),
                color=(26, 26, 46),
                duration=duration
            ).with_fps(self.fps)
        
        clips = []
        
        # 섹션 타이밍이 있으면 섹션별로 이미지 배치
        if section_times and len(section_times) == len(images) + 1:
            print(f"   🖼️  섹션 타이밍 기반 이미지 배치 ({len(images)}장)")
            for i, img in enumerate(images):
                start = section_times[i]
                end = section_times[i + 1]
                dur = max(0.1, end - start)  # 최소 0.1초
                
                img_array = np.array(img)
                clip = ImageClip(img_array).with_duration(dur)
                clip = clip.with_start(start)
                clips.append(clip)
                print(f"      이미지 {i+1}: {start:.1f}s ~ {end:.1f}s ({dur:.1f}s)")
        else:
            # 균등 분배 (폴백)
            time_per_image = duration / len(images)
            for i, img in enumerate(images):
                img_array = np.array(img)
                clip = ImageClip(img_array).with_duration(time_per_image)
                clip = clip.with_start(i * time_per_image)
                clips.append(clip)
        
        return CompositeVideoClip(clips, size=(self.width, self.height)).with_fps(self.fps)
    
    def _create_subtitle_image(self, text, font_size=80, text_color=(255, 255, 255, 255), is_bold=False):
        """PIL로 자막 이미지 생성 (한글 지원, 단어 단위 줄바꿈, 색상/볼드 지원)"""
        # 일단 임시 이미지로 텍스트 크기 측정
        temp_img = Image.new('RGBA', (self.width, 400), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 폰트 로드 (GitHub Actions 호환)
        font = None
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                # GitHub Actions에서 폴백
                fallback_fonts = [
                    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                ]
                for font_path in fallback_fonts:
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, font_size)
                            break
                        except:
                            continue
        except:
            pass
        
        if not font:
            font = ImageFont.load_default()
        
        # 텍스트 줄바꿈 처리 - 단어 단위로 줄바꿈 (문자 단위 아님)
        # 최대 2줄이 기본이지만, 문장이 길면 3줄 이상까지 허용 (문장이 잘리지 않도록)
        max_width = self.width - 120
        lines = []
        current_line = ""
        
        # 공백 단위로 단어 분할 (띄어쓰기 기준)
        words = text.split(' ')
        
        for word in words:
            # 현재 줄에 단어 추가 시도
            test_line = current_line + (' ' if current_line else '') + word
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            
            if bbox[2] - bbox[0] <= max_width:
                # 단어가 들어감
                current_line = test_line
            else:
                # 단어가 들어가지 않음
                if current_line:
                    # 현재 줄 저장하고 새로운 줄에 단어 추가
                    lines.append(current_line)
                    current_line = word
                else:
                    # 현재 줄이 비어있는데도 단어가 너무 긴 경우
                    # 어쩔 수 없이 단어 자체를 줄로 추가
                    lines.append(word)
                    current_line = ""
        
        if current_line:
            lines.append(current_line)
        
        # 필요한 이미지 높이 계산 (줄 수에 따라 동적 조정)
        line_height = font_size + 25
        padding = 20
        text_bg_height = len(lines) * line_height + (padding * 2)
        img_height = text_bg_height + 40  # 위아래 여유
        
        # 최종 이미지 생성 (높이는 동적)
        img = Image.new('RGBA', (self.width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 검정색 배경 박스 그리기 (시인성 개선)
        # 텍스트 영역을 포함하는 검정색 박스
        box_top = 20
        box_bottom = box_top + text_bg_height
        box_left = 40
        box_right = self.width - 40
        
        # 검정색 박스 (약간의 투명도 포함)
        box_img = Image.new('RGBA', (self.width, img_height), (0, 0, 0, 0))
        box_draw = ImageDraw.Draw(box_img)
        box_draw.rectangle(
            [(box_left, box_top), (box_right, box_bottom)],
            fill=(0, 0, 0, 220)  # 검정색, 약간 투명
        )
        # 테두리 (진한 검정)
        box_draw.rectangle(
            [(box_left, box_top), (box_right, box_bottom)],
            outline=(0, 0, 0, 255),
            width=3
        )
        
        # 박스 이미지 합성
        img = Image.alpha_composite(img, box_img)
        draw = ImageDraw.Draw(img)
        
        # 텍스트 그리기 (그림자 + 외곽선 + 흰색 본문)
        y_offset = box_top + padding
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            
            # 그림자 효과
            for offset in [(4, 4), (3, 3), (2, 2)]:
                draw.text((x + offset[0], y_offset + offset[1]), line, font=font, fill=(0, 0, 0, 200))
            
            # 외곽선
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y_offset + dy), line, font=font, fill=(0, 0, 0, 255))
            
            # 본문 텍스트 (지정 색상)
            draw.text((x, y_offset), line, font=font, fill=text_color)
            if is_bold:
                # Faux-bold: 1px, 2px 오프셋으로 중복 그리기
                draw.text((x + 1, y_offset), line, font=font, fill=text_color)
                draw.text((x + 2, y_offset), line, font=font, fill=text_color)
            y_offset += line_height
        
        return np.array(img)
    
    def create_subtitle_clips(self, script_text, audio_duration, sentence_timings=None):
        """자막 클립 생성 (PIL 기반, 한글 지원, 음성 타이밍 기반)"""
        import re
        
        # 음성 타이밍 정보가 있으면 그것을 사용
        if sentence_timings and len(sentence_timings) > 0:
            print(f"   📝 음성 타이밍 기반 자막 생성 ({len(sentence_timings)}개 문장)")
            clips = []
            
            # ── 1단계: TTS 타이밍을 개별 문장으로 분리 ──
            # Edge TTS SentenceBoundary가 "첫째, ~~~. 그래서~~~." 을 하나로 묶는 경우 분리
            split_timings = []
            for i, timing in enumerate(sentence_timings):
                text = timing["text"].strip()
                start_time = timing["start"]
                if i < len(sentence_timings) - 1:
                    end_time = sentence_timings[i + 1]["start"]
                else:
                    end_time = audio_duration
                total_dur = end_time - start_time
                
                # 문장 부호(. ! ?)로 분리 시도 (부호 포함)
                sub_sents = re.split(r'(?<=[.!?])\s+', text)
                sub_sents = [s.strip() for s in sub_sents if s.strip()]
                
                if len(sub_sents) > 1:
                    # 글자 수 비례로 시간 분배
                    total_chars = sum(len(s) for s in sub_sents)
                    cur_start = start_time
                    for j, sub in enumerate(sub_sents):
                        ratio = len(sub) / total_chars if total_chars > 0 else 1.0 / len(sub_sents)
                        sub_dur = total_dur * ratio
                        split_timings.append({
                            "text": sub,
                            "start": cur_start,
                            "end": cur_start + sub_dur,
                            "original_index": i
                        })
                        cur_start += sub_dur
                else:
                    split_timings.append({
                        "text": text,
                        "start": start_time,
                        "end": end_time,
                        "original_index": i
                    })
            
            total_split = len(split_timings)
            print(f"   📝 문장 분리 후 자막 {total_split}개")
            
            # ── 2단계: 각 분리된 문장에 색상/볼드 결정 + 클립 생성 ──
            for idx, st in enumerate(split_timings):
                text = st["text"]
                start_time = st["start"]
                duration = st["end"] - st["start"]
                orig_i = st["original_index"]
                
                if duration < 0.05:
                    continue
                
                # 문장 유형에 따라 색상/볼드 결정
                RED = (255, 0, 0, 255)
                WHITE = (255, 255, 255, 255)
                tc = WHITE
                bold = False
                
                if orig_i == 0 and idx == 0:  # 인트로 (첫 문장)
                    tc = RED
                elif re.search(r'\d+가지', text):  # N가지
                    tc = RED
                    bold = True
                elif re.match(r'^(첫째|둘째|셋째)', text):  # 순서 문장 (해당 문장만)
                    tc = RED
                elif orig_i == len(sentence_timings) - 1 and idx == total_split - 1:  # 아웃트로 (마지막)
                    tc = RED
                
                # PIL로 자막 이미지 생성
                subtitle_img = self._create_subtitle_image(text, text_color=tc, is_bold=bold)
                
                # ImageClip으로 변환
                clip = ImageClip(subtitle_img)
                clip = clip.with_duration(duration)
                clip = clip.with_start(start_time)
                clip = clip.with_position(('center', int(self.height * 0.25)))
                
                clips.append(clip)
            
            return clips
        
        # 타이밍 정보가 없으면 기존 방식 (균등 분배)
        print("   📝 균등 분배 방식 자막 생성")
        
        # 문맥상 자연스러운 위치에서 자막 분리
        # 1. 먼저 문장 부호로 분리
        # 2. 긴 문장은 조사/어미 위치에서 추가 분리
        
        # 문장 부호로 1차 분리 (부호 유지)
        raw_segments = re.split(r'([.!?]+\s*)', script_text)
        segments = []
        
        for i in range(0, len(raw_segments) - 1, 2):
            text = raw_segments[i]
            punct = raw_segments[i + 1] if i + 1 < len(raw_segments) else ""
            if text.strip():
                segments.append(text.strip() + punct.strip())
        
        # 마지막 세그먼트 처리
        if len(raw_segments) % 2 == 1 and raw_segments[-1].strip():
            segments.append(raw_segments[-1].strip())
        
        # 너무 긴 문장은 쉼표나 자연스러운 위치에서 분리
        final_segments = []
        for seg in segments:
            if len(seg) > 35:  # 35자 이상이면 분리 시도
                # 쉼표로 분리
                if ',' in seg:
                    parts = seg.split(',')
                    for j, part in enumerate(parts):
                        part = part.strip()
                        if part:
                            if j < len(parts) - 1:
                                final_segments.append(part + ',')
                            else:
                                final_segments.append(part)
                # 조사 위치에서 분리 (는, 은, 이, 가, 를, 을, 에서, 으로 등)
                elif len(seg) > 40:
                    # 중간 지점 근처에서 조사 찾기
                    mid = len(seg) // 2
                    split_patterns = ['는 ', '은 ', '이 ', '가 ', '를 ', '을 ', '에서 ', '으로 ', '에 ', '도 ', '만 ']
                    best_split = -1
                    
                    for pattern in split_patterns:
                        idx = seg.find(pattern, mid - 15)
                        if idx != -1 and idx < mid + 15:
                            best_split = idx + len(pattern)
                            break
                    
                    if best_split > 0:
                        final_segments.append(seg[:best_split].strip())
                        final_segments.append(seg[best_split:].strip())
                    else:
                        final_segments.append(seg)
                else:
                    final_segments.append(seg)
            else:
                final_segments.append(seg)
        
        # 빈 세그먼트 제거
        final_segments = [s for s in final_segments if s.strip()]
        
        if not final_segments:
            final_segments = [script_text]
        
        clips = []
        time_per_segment = audio_duration / len(final_segments)
        
        # 자막이 음성보다 살짝 빨리 나오도록 (싱크 맞추기)
        sync_offset = -0.2  # 0.3초 먼저 나오게
        
        for i, segment in enumerate(final_segments):
            start_time = max(0, i * time_per_segment + sync_offset)
            duration = time_per_segment
            
            # PIL로 자막 이미지 생성
            subtitle_img = self._create_subtitle_image(segment)
            
            # ImageClip으로 변환
            clip = ImageClip(subtitle_img)
            clip = clip.with_duration(duration)
            clip = clip.with_start(start_time)
            # 자막 위치: 상단에서 1/4 지점 (높이 25%)
            clip = clip.with_position(('center', int(self.height * 0.25)))
            
            clips.append(clip)
        
        return clips
    
    def create_thumbnail(self, text, output_path, background_img=None):
        """썸네일 이미지 생성"""
        if background_img:
            img = background_img.copy()
        else:
            img = Image.new('RGB', (self.width, self.height), color='#1a1a2e')
        
        draw = ImageDraw.Draw(img)
        
        # 한글 폰트 로드 (GitHub Actions 호환)
        font = None
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, 100)
            else:
                # GitHub Actions에서 폴백
                fallback_fonts = [
                    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                ]
                for font_path in fallback_fonts:
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, 100)
                            break
                        except:
                            continue
        except:
            pass
        
        if not font:
            font = ImageFont.load_default()
        
        # 텍스트 줄바꿈
        max_width = self.width - 100
        lines = []
        current_line = ""
        
        for char in text:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        
        # 총 텍스트 높이 계산
        line_height = 120
        total_height = len(lines) * line_height
        y_start = (self.height - total_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = y_start + i * line_height
            
            # 그림자
            draw.text((x+4, y+4), line, font=font, fill='black')
            draw.text((x+2, y+2), line, font=font, fill='#333333')
            # 메인 텍스트 (형광 녹색)
            draw.text((x, y), line, font=font, fill='#00ff88')
        
        img.save(output_path)
        print(f"✅ 썸네일 생성: {output_path}")
        return output_path
    
    def get_thumbnail_path(self):
        """마지막 create_video 호출 시 생성된 썸네일 경로 반환"""
        return getattr(self, '_thumbnail_path', None)

    def _create_hook_thumbnail(self, pil_image, hook_text, output_path):
        """인트로 배경 이미지 + 후킹 문장 오버레이로 썸네일 생성 (쇼츠 9:16)"""
        try:
            bg = pil_image.copy().convert('RGB')
            draw = ImageDraw.Draw(bg)

            font_size = 72
            font = None
            try:
                if self.font_path:
                    font = ImageFont.truetype(self.font_path, font_size)
            except:
                pass
            if not font:
                font = ImageFont.load_default()

            # 단어 단위 줄바꿈
            max_width = self.width - 150
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
            y_start = int(self.height * 0.25)  # 상단 1/4 지점 (자막 위치)

            # 반투명 배경 박스
            pad = 25
            overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [(40, y_start - pad), (self.width - 40, y_start + total_text_h + pad)],
                fill=(0, 0, 0, 180)
            )
            bg = Image.alpha_composite(bg.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(bg)

            RED = (255, 0, 0)
            for idx, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                tw = bbox[2] - bbox[0]
                x = (self.width - tw) // 2
                y = y_start + idx * line_height

                for ox, oy in [(4, 4), (3, 3), (2, 2)]:
                    draw.text((x + ox, y + oy), line, font=font, fill=(0, 0, 0))
                for dx in [-3, -2, -1, 0, 1, 2, 3]:
                    for dy in [-3, -2, -1, 0, 1, 2, 3]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
                draw.text((x, y), line, font=font, fill=RED)
                draw.text((x + 1, y), line, font=font, fill=RED)
                draw.text((x + 2, y), line, font=font, fill=RED)

            bg.save(output_path, 'JPEG', quality=95)
            print(f"   ✅ 쇼츠 후킹 썸네일 생성: {output_path}")
            return output_path
        except Exception as e:
            print(f"   ⚠️ 썸네일 생성 실패: {e}")
            return None
    
    def _detect_section_boundaries(self, sentence_timings, duration):
        """문장 타이밍에서 섹션 경계 시간 감지 (인트로/첫째/둘째/셋째/아웃트로)"""
        import re
        if not sentence_timings or len(sentence_timings) == 0:
            return None
        
        # 첫째/둘째/셋째 시작 시간 찾기
        ordinal_times = []
        for timing in sentence_timings:
            text = timing['text']
            if re.match(r'^(첫째|둘째|셋째)', text):
                ordinal_times.append(timing['start'])
        
        if len(ordinal_times) < 3:
            print(f"   ⚠️  섹션 경계 부족 ({len(ordinal_times)}개 발견), 균등 분배 사용")
            return None
        
        # 마지막 문장 = 아웃트로 시작
        outro_start = sentence_timings[-1]['start']
        
        # 경계: [0, 첫째, 둘째, 셋째, 아웃트로, 끝]
        boundaries = [0] + ordinal_times[:3] + [outro_start, duration]
        
        # 중복 제거 및 정렬
        boundaries = sorted(list(set(boundaries)))
        
        if len(boundaries) != 6:
            print(f"   ⚠️  경계 수 불일치 ({len(boundaries)}개), 균등 분배 사용")
            return None
        
        print(f"   🎯 섹션 경계 감지 완료:")
        sections = ["인트로", "첫째", "둘째", "셋째", "아웃트로"]
        for i in range(5):
            print(f"      {sections[i]}: {boundaries[i]:.1f}s ~ {boundaries[i+1]:.1f}s")
        
        return boundaries
    
    def create_video(self, script_data, audio_path, output_path, sentence_timings=None, use_ai_background=True):
        """최종 비디오 생성 (AI 배경 이미지 옵션, 썸네일 자동 생성)"""
        self._thumbnail_path = None  # 썸네일 경로
        audio = None
        final_video = None
        try:
            print("🎬 비디오 생성 중...")
            
            # 오디오 로드
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # AI 배경 이미지 생성 시도
            ai_images = None
            if use_ai_background:
                ai_images = self.generate_ai_background_images(script_data, use_ai=True)
            
            # AI 이미지가 없으면 기존 방식 사용
            if not ai_images:
                print("📷 기존 방식: 대본 키워드 기반 배경 이미지 검색 중...")
                script_text = script_data.get('script', '')
                topic = script_data.get('topic', '흥미로운 사실')
                background_images = self.download_background_images(topic, count=5, script_text=script_text)
            else:
                # AI 이미지 사용 (섹션 순서로 정렬)
                section_order = ["intro", "section1", "section2", "section3", "outro"]
                background_images = []
                for section in section_order:
                    for sec, img in ai_images:
                        if sec == section:
                            background_images.append(img)
                            break
            
            # 섹션 경계 감지 (이미지 타이밍 동기화)
            section_times = self._detect_section_boundaries(sentence_timings, duration) if sentence_timings else None
            
            # 배경 비디오 생성 (섹션 타이밍 적용)
            background = self.create_background_video(background_images, duration, section_times=section_times)
            
            # 자막 생성 (음성 타이밍 기반)
            subtitle_clips = self.create_subtitle_clips(script_data['script'], duration, sentence_timings=sentence_timings)
            
            # 썸네일 생성: 인트로 배경 + 후킹 문장 (N가지) 오버레이
            if sentence_timings and background_images:
                import re
                hook_text = None
                for timing in sentence_timings:
                    if re.search(r'\d+가지', timing['text']):
                        hook_text = timing['text']
                        break
                if hook_text and len(background_images) > 0:
                    thumb_path = output_path.replace('.mp4', '_thumb.jpg')
                    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                    self._thumbnail_path = self._create_hook_thumbnail(
                        background_images[0], hook_text, thumb_path
                    )
            
            # 모든 클립 합성
            final_video = CompositeVideoClip(
                [background] + subtitle_clips,
                size=(self.width, self.height)
            ).with_duration(duration).with_audio(audio)
            
            # 비디오 저장 (MoviePy 출력을 캡처하여 한 줄로 표시)
            captured_output = io.StringIO()
            
            with redirect_stdout(captured_output):
                final_video.write_videofile(
                    output_path,
                    fps=self.fps,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    preset='medium'
                )
            
            # 캡처된 출력에서 progress bar 라인들만 추출
            output_lines = captured_output.getvalue().split('\n')
            last_progress_line = ""
            
            for line in output_lines:
                # frame_index나 chunk를 포함한 진행 라인 찾기
                if 'frame_index' in line or 'chunk' in line or '|' in line:
                    # 한 줄에 덮어씌우기
                    sys.stdout.write(f'\r{line}')
                    sys.stdout.flush()
                    last_progress_line = line
                elif line.strip() and 'MoviePy' in line:
                    # 완료 메시지는 새 줄로 출력
                    print(f"\n{line}")
            
            # 마지막에 새 줄 추가
            if last_progress_line:
                print()
            
            print(f"✅ 비디오 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 비디오 생성 오류: {e}")
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
            if audio:
                try:
                    audio.close()
                except Exception:
                    pass


if __name__ == "__main__":
    # 테스트
    generator = VideoGenerator()
    
    # 간단한 테스트 스크립트
    test_script = {
        'script': '이것은 테스트 영상입니다. 자막이 잘 나타나는지 확인해봅시다.',
        'thumbnail_text': '테스트 영상'
    }
    
    print("비디오 생성기가 준비되었습니다.")
