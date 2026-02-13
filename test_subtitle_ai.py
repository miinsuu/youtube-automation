#!/usr/bin/env python3
"""자막 스타일 + 무료 AI 일러스트 생성 테스트"""
import os
import sys
import time
import requests
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.makedirs("output/longform_images", exist_ok=True)
os.makedirs("output/longform_videos", exist_ok=True)

print("=" * 60)
print("🧪 자막 스타일 + AI 일러스트 테스트")
print("=" * 60)

# ── 테스트 1: 자막 배경박스 (텍스트 맞춤 너비 + 충분한 높이) ──
print("\n🔹 테스트 1: 자막 배경박스 스타일")
try:
    from moviepy import TextClip, ImageClip, CompositeVideoClip

    font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

    test_subs = [
        (0, 3, "짧은 자막"),
        (3, 7, "중간 길이의 자막 테스트입니다"),
        (7, 10, "긴 문장의 자막입니다 이렇게 되면\n두 줄로 나뉘어야 합니다"),
    ]

    bg_path = "output/longform_images/test_pexels_0.jpg"
    if os.path.exists(bg_path):
        bg_clip = ImageClip(bg_path).with_duration(10)
    else:
        from moviepy import ColorClip
        bg_clip = ColorClip(size=(1920, 1080), color=(20, 30, 60)).with_duration(10)

    text_clips = []
    for start, end, text in test_subs:
        kw = {
            "text": text,
            "font_size": 48,
            "color": "white",
            "bg_color": "black",
            "method": "label",
            "margin": (30, 15),
            "transparent": False,
            "duration": end - start,
        }
        if font_path and os.path.exists(font_path):
            kw["font"] = font_path

        tc = TextClip(**kw)
        print(f"  자막: '{text[:20]}...' → 크기: {tc.size}")
        tc = tc.with_start(start).with_position(("center", 900))
        text_clips.append(tc)

    composite = CompositeVideoClip([bg_clip] + text_clips, size=(1920, 1080)).with_duration(10)
    preview_path = "output/longform_videos/preview_subtitle_test.mp4"
    t0 = time.time()
    composite.write_videofile(preview_path, fps=30, codec="libx264", audio_codec="aac")
    elapsed = time.time() - t0
    composite.close()
    fsize = os.path.getsize(preview_path) / 1024
    print(f"  ✅ 미리보기: {preview_path} ({fsize:.0f}KB, {elapsed:.1f}초)")
except Exception as e:
    print(f"  ❌ 자막 테스트 실패: {e}")
    import traceback
    traceback.print_exc()


# ── 테스트 2: 무료 AI 일러스트 생성 API 시도 ──
print("\n" + "=" * 60)
print("🔹 테스트 2: 무료 AI 일러스트 생성 API")
print("=" * 60)

# 2-1. Pollinations AI
print("\n[1] Pollinations AI (flux-realism)")
try:
    prompt = "peaceful mountain landscape, soft illustration style, pastel colors, no text, digital art"
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1920&height=1080&nologo=true&model=flux-realism"
    resp = requests.get(url, timeout=60, allow_redirects=True)
    ct = resp.headers.get("content-type", "")
    if resp.status_code == 200 and "image" in ct:
        path = "output/longform_images/test_pollinations.jpg"
        with open(path, "wb") as f:
            f.write(resp.content)
        img = Image.open(path)
        print(f"    ✅ 성공: {img.size}, 파일: {path}")
    else:
        print(f"    ❌ 실패: status={resp.status_code}, ct={ct}")
except Exception as e:
    print(f"    ❌ 에러: {e}")

# 2-2. Hugging Face Inference API (무료, 인증 불필요)
print("\n[2] Hugging Face Inference API (stabilityai/stable-diffusion-xl-base-1.0)")
try:
    hf_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    payload = {"inputs": "soft illustration of a peaceful sunrise over mountains, pastel colors, digital art style, no text, calming mood"}
    resp = requests.post(hf_url, json=payload, timeout=60)
    ct = resp.headers.get("content-type", "")
    print(f"    상태: {resp.status_code}, ct: {ct}")
    if resp.status_code == 200 and "image" in ct:
        path = "output/longform_images/test_hf_sdxl.png"
        with open(path, "wb") as f:
            f.write(resp.content)
        img = Image.open(path)
        print(f"    ✅ 성공: {img.size}, 파일: {path}")
    elif resp.status_code == 503:
        print(f"    ⏳ 모델 로딩 중 (콜드 스타트). 재시도 필요.")
        body = resp.json() if resp.headers.get("content-type","").startswith("application/json") else {}
        est = body.get("estimated_time", "?")
        print(f"    예상 대기: {est}초")
    else:
        print(f"    ❌ body: {resp.text[:200]}")
except Exception as e:
    print(f"    ❌ 에러: {e}")

# 2-3. Hugging Face - FLUX.1-dev (무료)
print("\n[3] Hugging Face - FLUX.1-schnell (빠른 무료 모델)")
try:
    hf_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    payload = {"inputs": "warm illustration of two friends walking in autumn park, soft watercolor style, peaceful mood, no text"}
    resp = requests.post(hf_url, json=payload, timeout=60)
    ct = resp.headers.get("content-type", "")
    print(f"    상태: {resp.status_code}, ct: {ct}")
    if resp.status_code == 200 and "image" in ct:
        path = "output/longform_images/test_hf_flux.png"
        with open(path, "wb") as f:
            f.write(resp.content)
        img = Image.open(path)
        print(f"    ✅ 성공: {img.size}, 파일: {path}")
    elif resp.status_code == 503:
        body = resp.json() if "json" in ct else {}
        est = body.get("estimated_time", "?")
        print(f"    ⏳ 모델 로딩 중. 예상: {est}초")
    else:
        print(f"    body: {resp.text[:200]}")
except Exception as e:
    print(f"    ❌ 에러: {e}")

# 2-4. Together AI 무료 체험
print("\n[4] Together AI (FLUX-schnell)")
print("    → 가입 필요: https://api.together.xyz")
print("    → 무료 $1 크레딧 제공 (약 100장 생성 가능)")

# 2-5. Segmind API
print("\n[5] Segmind API (SDXL)")
print("    → 가입 시 100 크레딧 무료: https://www.segmind.com")

print("\n" + "=" * 60)
print("🧪 테스트 완료!")
print("=" * 60)
