"""
비디오 생성 모듈
MoviePy를 사용하여 음성, 배경, 자막을 합성하여 최종 영상을 생성합니다.
"""

import json
import os
import requests
import subprocess
from moviepy import (
    ColorClip, AudioFileClip, CompositeVideoClip, 
    TextClip, concatenate_videoclips, ImageClip, VideoClip
)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np


class VideoGenerator:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 비디오 설정
        res = self.config['video']['resolution'].split('x')
        self.width = int(res[0])
        self.height = int(res[1])
        self.fps = self.config['video']['fps']
        self.bg_color = self.config['video']['background_color']
        self.text_color = self.config['video']['text_color']
        self.accent_color = self.config['video']['accent_color']
        
        # 한글 폰트 찾기
        self.font_path = self._find_korean_font()
    
    def _find_korean_font(self):
        """시스템에서 한글 폰트 찾기"""
        # macOS 폰트 경로들
        font_paths = [
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/Library/Fonts/AppleGothic.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            # Linux 폰트 경로들
            "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
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
        pexels_api_key = "***REMOVED***"
        
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

    def create_background_video(self, images, duration):
        """배경 이미지들로 비디오 클립 생성 (Ken Burns 효과)"""
        if not images:
            return ColorClip(
                size=(self.width, self.height),
                color=(26, 26, 46),
                duration=duration
            ).with_fps(self.fps)
        
        clips = []
        time_per_image = duration / len(images)
        
        for i, img in enumerate(images):
            # PIL 이미지를 numpy 배열로 변환
            img_array = np.array(img)
            
            # ImageClip 생성
            clip = ImageClip(img_array).with_duration(time_per_image)
            clip = clip.with_start(i * time_per_image)
            clips.append(clip)
        
        return CompositeVideoClip(clips, size=(self.width, self.height)).with_fps(self.fps)
    
    def _create_subtitle_image(self, text, font_size=80):
        """PIL로 자막 이미지 생성 (한글 지원)"""
        # 투명 배경 이미지
        img = Image.new('RGBA', (self.width, 400), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 폰트 로드
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 텍스트 줄바꿈 처리 (최대 2줄)
        max_width = self.width - 120
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
                # 최대 2줄까지만
                if len(lines) >= 2:
                    break
        if current_line and len(lines) < 2:
            lines.append(current_line)
        
        # 텍스트 그리기 (그림자 + 외곽선 + 흰색 본문)
        y_offset = 30
        line_height = font_size + 25
        
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
            
            # 흰색 본문
            draw.text((x, y_offset), line, font=font, fill=(255, 255, 255, 255))
            y_offset += line_height
        
        return np.array(img)
    
    def create_subtitle_clips(self, script_text, audio_duration, sentence_timings=None):
        """자막 클립 생성 (PIL 기반, 한글 지원, 음성 타이밍 기반)"""
        import re
        
        # 음성 타이밍 정보가 있으면 그것을 사용
        if sentence_timings and len(sentence_timings) > 0:
            print(f"   📝 음성 타이밍 기반 자막 생성 ({len(sentence_timings)}개 문장)")
            clips = []
            
            for i, timing in enumerate(sentence_timings):
                text = timing["text"]
                start_time = timing["start"]
                # 다음 문장 시작까지 또는 오디오 끝까지
                if i < len(sentence_timings) - 1:
                    end_time = sentence_timings[i + 1]["start"]
                else:
                    end_time = audio_duration
                
                duration = end_time - start_time
                
                # 너무 긴 문장은 분리
                if len(text) > 40:
                    # 쉼표나 조사 위치에서 분리하여 별도 표시
                    pass  # 한 자막으로 표시하되 줄바꿈 처리
                
                # PIL로 자막 이미지 생성
                subtitle_img = self._create_subtitle_image(text)
                
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
        
        # 한글 폰트 로드
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, 100)
            else:
                font = ImageFont.load_default()
        except:
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
    
    def create_video(self, script_data, audio_path, output_path, sentence_timings=None):
        """최종 비디오 생성"""
        try:
            print("🎬 비디오 생성 중...")
            
            # 오디오 로드
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # 대본 텍스트로 키워드 기반 배경 이미지 다운로드
            script_text = script_data.get('script', '')
            topic = script_data.get('topic', '흥미로운 사실')
            print(f"📷 대본 키워드 기반 배경 이미지 검색 중...")
            background_images = self.download_background_images(topic, count=5, script_text=script_text)
            
            # 배경 비디오 생성
            background = self.create_background_video(background_images, duration)
            
            # 자막 생성 (음성 타이밍 기반)
            subtitle_clips = self.create_subtitle_clips(script_data['script'], duration, sentence_timings=sentence_timings)
            
            # 모든 클립 합성
            final_video = CompositeVideoClip(
                [background] + subtitle_clips,
                size=(self.width, self.height)
            ).with_duration(duration).with_audio(audio)
            
            # 비디오 저장
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='medium'
            )
            
            print(f"✅ 비디오 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 비디오 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return None


if __name__ == "__main__":
    # 테스트
    generator = VideoGenerator()
    
    # 간단한 테스트 스크립트
    test_script = {
        'script': '이것은 테스트 영상입니다. 자막이 잘 나타나는지 확인해봅시다.',
        'thumbnail_text': '테스트 영상'
    }
    
    print("비디오 생성기가 준비되었습니다.")
