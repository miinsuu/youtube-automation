"""
롱폼 비디오 썸네일 생성 모듈
AI 일러스트 배경 + 텍스트 오버레이로 클릭을 유도하는 썸네일을 생성합니다.
"""

import json
import os
import re
import requests
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class ThumbnailGenerator:
    # 썸네일 해상도 (YouTube 권장: 1280x720)
    WIDTH = 1280
    HEIGHT = 720

    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.hf_token = self.config.get('huggingface_token', '')
        self.hf_model_url = (
            "https://router.huggingface.co/hf-inference/models/"
            "black-forest-labs/FLUX.1-schnell"
        )
        self.font_path = self._find_korean_font()
        os.makedirs("output/thumbnails", exist_ok=True)

    # ─────────────────────────────────────────────
    # 공개 API
    # ─────────────────────────────────────────────
    def generate_thumbnail(self, title, script_text="", output_path=None):
        """썸네일 생성 메인 메서드
        Returns: 저장된 썸네일 파일 경로 (실패 시 None)
        """
        if not output_path:
            ts = int(time.time())
            output_path = f"output/thumbnails/thumb_{ts}.jpg"

        print("🖼️  썸네일 생성 중...")

        # 1. 배경 이미지 생성 (AI > 그라디언트 폴백)
        bg = self._generate_background(title, script_text)

        # 2. 배경 어둡게 + 블러 (텍스트 가독성)
        bg = self._apply_overlay(bg)

        # 3. 제목 텍스트 그리기
        clean_title = self._strip_markdown(title)
        bg = self._draw_title(bg, clean_title)

        # 4. 저장
        bg.save(output_path, "JPEG", quality=95)
        fsize = os.path.getsize(output_path) // 1024
        print(f"✅ 썸네일 생성 완료: {output_path} ({fsize}KB)")
        return output_path

    # ─────────────────────────────────────────────
    # 배경 이미지
    # ─────────────────────────────────────────────
    def _generate_background(self, title, script_text):
        """AI 일러스트 배경 생성 (폴백: 그라디언트)"""
        if self.hf_token:
            prompt = self._build_prompt(title, script_text)
            img = self._hf_generate(prompt)
            if img:
                return self._center_crop(img)

        return self._gradient_bg()

    def _build_prompt(self, title, script_text):
        """썸네일용 AI 프롬프트"""
        hint = (title + " " + script_text[:200]).replace('\n', ' ').strip()
        return (
            f"YouTube thumbnail background, cinematic dramatic lighting, "
            f"vibrant colors, emotional atmosphere, "
            f"related to: {hint[:120]}, "
            f"studio ghibli inspired art style, anime illustration, "
            f"wide shot, highly detailed, 4k quality, no text"
        )

    def _hf_generate(self, prompt):
        """HuggingFace API로 이미지 생성"""
        try:
            headers = {
                "Authorization": f"Bearer {self.hf_token}",
                "Content-Type": "application/json",
            }
            resp = requests.post(
                self.hf_model_url,
                json={"inputs": prompt},
                headers=headers,
                timeout=60,
            )
            ct = resp.headers.get("content-type", "")
            if resp.status_code == 200 and "image" in ct:
                return Image.open(BytesIO(resp.content))
            else:
                print(f"  ⚠️ AI 썸네일 배경 실패 ({resp.status_code}), 그라디언트 폴백")
        except Exception as e:
            print(f"  ⚠️ AI 배경 오류: {e}")
        return None

    def _center_crop(self, img):
        """16:9 비율로 center crop + 리사이즈"""
        tw, th = self.WIDTH, self.HEIGHT
        target_ratio = tw / th
        iw, ih = img.size
        img_ratio = iw / ih

        if img_ratio > target_ratio:
            new_w = int(ih * target_ratio)
            left = (iw - new_w) // 2
            img = img.crop((left, 0, left + new_w, ih))
        else:
            new_h = int(iw / target_ratio)
            top = (ih - new_h) // 2
            img = img.crop((0, top, iw, top + new_h))

        return img.resize((tw, th), Image.LANCZOS)

    def _gradient_bg(self):
        """그라디언트 폴백 배경"""
        import numpy as np
        arr = np.zeros((self.HEIGHT, self.WIDTH, 3), dtype=np.uint8)

        # 진한 남색 → 보라 그라디언트
        for y in range(self.HEIGHT):
            r = int(15 + (60 - 15) * y / self.HEIGHT)
            g = int(10 + (20 - 10) * y / self.HEIGHT)
            b = int(60 + (120 - 60) * y / self.HEIGHT)
            arr[y, :] = [r, g, b]

        return Image.fromarray(arr)

    # ─────────────────────────────────────────────
    # 오버레이 + 텍스트
    # ─────────────────────────────────────────────
    def _apply_overlay(self, img):
        """배경 어둡게 + 하단 비네팅"""
        # 살짝 블러
        img = img.filter(ImageFilter.GaussianBlur(radius=2))

        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # 하단 그라디언트 어둡게 (텍스트 영역)
        for y in range(self.HEIGHT):
            alpha = 0
            if y > self.HEIGHT * 0.3:
                progress = (y - self.HEIGHT * 0.3) / (self.HEIGHT * 0.7)
                alpha = int(180 * progress)
            draw.rectangle([(0, y), (self.WIDTH, y + 1)], fill=(0, 0, 0, alpha))

        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        return img.convert('RGB')

    def _draw_title(self, img, title):
        """제목 텍스트 그리기 — 2~3줄, 굵은 흰색, 좌하단"""
        draw = ImageDraw.Draw(img)

        # 폰트 크기 (제목 길이에 따라 조절)
        if len(title) <= 15:
            font_size = 72
        elif len(title) <= 25:
            font_size = 62
        else:
            font_size = 52

        font = self._get_font(font_size)

        # 줄바꿈 (12~15자 단위)
        chars_per_line = 13 if font_size >= 62 else 15
        lines = self._wrap_text(title, chars_per_line)
        lines = lines[:3]  # 최대 3줄

        # 텍스트 위치 (좌하단, 패딩 60px)
        line_height = font_size + 16
        total_text_h = line_height * len(lines)
        y_start = self.HEIGHT - total_text_h - 60
        x_start = 60

        for i, line in enumerate(lines):
            y = y_start + i * line_height

            # 그림자 (검정)
            for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4)]:
                draw.text((x_start + dx, y + dy), line, font=font, fill=(0, 0, 0))

            # 메인 텍스트 (흰색)
            draw.text((x_start, y), line, font=font, fill=(255, 255, 255))

        # 우상단에 이모지 악센트 (시선 유도)
        accent_font = self._get_font(48)
        draw.text(
            (self.WIDTH - 120, 30), "🔥", font=accent_font,
            fill=(255, 200, 50)
        )

        return img

    def _wrap_text(self, text, max_chars):
        """한글 텍스트 줄바꿈"""
        words = text
        lines = []
        current = ""

        for ch in words:
            if len(current) >= max_chars and ch == ' ':
                lines.append(current.strip())
                current = ""
            else:
                current += ch

        if current.strip():
            lines.append(current.strip())

        return lines

    # ─────────────────────────────────────────────
    # 유틸리티
    # ─────────────────────────────────────────────
    def _find_korean_font(self):
        """한글 폰트 찾기"""
        paths = [
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/System/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/NotoSansCJK.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return None

    def _get_font(self, size):
        """PIL 폰트 반환"""
        if self.font_path:
            try:
                return ImageFont.truetype(self.font_path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def _strip_markdown(self, text):
        """마크다운 서식 제거"""
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', text)
        text = re.sub(r'[-=]{3,}', '', text)
        return text.strip()


if __name__ == "__main__":
    gen = ThumbnailGenerator()
    path = gen.generate_thumbnail(
        "감정 소모 없이 스마트하게 화내는 법",
        "옛날 깊은 산속에 작은 마을이 있었습니다."
    )
    if path:
        print(f"테스트 썸네일: {path}")
