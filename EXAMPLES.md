# 사용 예시 및 가이드 📚

## 🎯 기본 사용 시나리오

### 1. 첫 영상 생성 (테스트)

```bash
# 업로드 없이 비디오만 생성
python main.py --test
```

**결과:**
- `output/videos/video_20240215_093045.mp4` - 완성된 영상
- `output/audio/audio_20240215_093045.mp3` - 음성 파일
- `output/images/thumbnail_20240215_093045.png` - 썸네일
- `output/script_20240215_093045.json` - 생성된 대본

### 2. 실제 YouTube 업로드

```bash
python main.py
```

첫 실행 시:
1. 브라우저가 자동으로 열립니다
2. Google 계정으로 로그인
3. 권한 승인
4. 이후로는 자동 업로드

### 3. 특정 주제로 영상 생성

```bash
# 우주 관련 영상
python main.py --topic "우주의 신비"

# 건강 팁 영상
python main.py --topic "건강 관리 팁"

# 역사 이야기
python main.py --topic "역사 속 놀라운 이야기"
```

### 4. 여러 영상 자동 생성

```bash
# 3개의 영상을 연속으로 생성
python main.py --count 3

# 5개 생성 (업로드 없이)
python main.py --count 5 --no-upload
```

## 📅 자동화 스케줄 설정

### Cron 작업 예시

```bash
# 크론 에디터 열기
crontab -e
```

**매일 오전 9시에 1개 영상 자동 업로드**
```cron
0 9 * * * cd /home/user/youtube-automation && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

**하루 3번 (오전 9시, 오후 3시, 오후 9시)**
```cron
0 9,15,21 * * * cd /home/user/youtube-automation && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

**평일만 오전 10시**
```cron
0 10 * * 1-5 cd /home/user/youtube-automation && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

**주말에만 오전 11시, 오후 5시**
```cron
0 11,17 * * 0,6 cd /home/user/youtube-automation && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

## 🎨 커스터마이징 예시

### 1. 새로운 주제 추가

`config/config.json` 수정:

```json
{
  "content": {
    "topics": [
      "건강과 웰빙",
      "돈 버는 팁",
      "심리학 트릭",
      "요리 꿀팁",
      "여행 정보",
      "반려동물 지식",
      "자기계발",
      "환경과 지속가능성"
    ]
  }
}
```

### 2. 비디오 스타일 변경

```json
{
  "video": {
    "resolution": "1080x1920",
    "background_color": "#000000",  // 검정 배경
    "text_color": "#FFD700",        // 금색 텍스트
    "accent_color": "#FF1493"       // 핑크 강조색
  }
}
```

### 3. 태그 전략 변경

```json
{
  "upload": {
    "default_tags": [
      "쇼츠",
      "shorts",
      "팩트체크",
      "정보",
      "꿀팁",
      "알고가자",
      "지식"
    ]
  }
}
```

## 📊 성과 분석 활용

### 생성된 로그 분석

```bash
# 최근 10개 영상의 주제 확인
ls -lt logs/*.json | head -10 | while read -r line; do
    file=$(echo $line | awk '{print $9}')
    topic=$(jq -r '.script.topic' "$file")
    title=$(jq -r '.script.title' "$file")
    echo "$topic: $title"
done
```

### 업로드된 영상 URL 목록

```bash
# 모든 업로드된 영상의 URL 추출
jq -r '.upload.url' logs/*.json 2>/dev/null | grep -v null
```

## 🎬 영상 품질 최적화

### 1. 대본 길이 조정

스크립트가 너무 길거나 짧으면 `script_generator.py` 수정:

```python
prompt = f"""
...
요구사항:
1. 첫 3초 안에 시청자의 관심을 끌 수 있는 훅
2. 정확한 사실 기반의 정보 제공
3. 40-50초 분량 (약 100-130단어)  # ← 여기 조정
...
"""
```

### 2. TTS 속도 조정

`config/config.json`:

```json
{
  "tts": {
    "speed": 1.2  // 1.0 = 보통, 1.2 = 20% 빠르게, 0.8 = 20% 느리게
  }
}
```

### 3. 자막 스타일 변경

`video_generator.py`의 `create_subtitle_clips` 함수:

```python
txt_clip = TextClip(
    word_group,
    fontsize=100,              # 폰트 크기 증가
    color='yellow',            # 색상 변경
    stroke_color='black',
    stroke_width=4,            # 테두리 두께 증가
    ...
)
```

## 🚀 고급 활용

### 1. A/B 테스팅

같은 주제로 다른 스타일의 영상 생성:

```bash
# 스타일 1: 일반적인 팩트
python main.py --topic "심리학 팩트"

# config.json에서 배경색 변경 후
# 스타일 2: 다른 디자인
python main.py --topic "심리학 팩트"
```

### 2. 시리즈 영상 제작

```bash
#!/bin/bash
# 우주 시리즈 5편 제작

topics=(
    "블랙홀의 비밀"
    "화성 탐사의 역사"
    "은하수의 크기"
    "태양계 행성들"
    "우주 정거장 생활"
)

for topic in "${topics[@]}"; do
    python main.py --topic "$topic"
    sleep 600  # 10분 대기
done
```

### 3. 트렌드 기반 자동 주제 생성

OpenAI API를 활용한 트렌드 주제 자동 생성:

```python
# 별도 스크립트 작성
import openai

def get_trending_topics():
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": "현재 한국에서 인기있는 쇼츠 영상 주제 5가지를 추천해주세요."
        }]
    )
    return response.choices[0].message.content

# 트렌드 주제로 영상 생성
trending = get_trending_topics()
# ... 파싱 후 main.py 실행
```

## 🔍 문제 해결 가이드

### 영상이 너무 짧거나 길 때

1. TTS 속도 확인: `config.json`의 `tts.speed`
2. 대본 길이 조정: `script_generator.py`의 프롬프트 수정
3. 생성된 대본 확인: `output/script_*.json`

### 자막이 안 보일 때

1. 폰트 설치 확인:
```bash
fc-list | grep -i nanum
```

2. 폰트 경로 수정: `video_generator.py`
```python
font='Arial'  # 또는 시스템에 있는 다른 폰트
```

### YouTube 업로드 실패

1. API 할당량 확인:
   - Google Cloud Console > API 및 서비스 > 할당량
   
2. 인증 토큰 재생성:
```bash
rm config/youtube_credentials.json
python scripts/youtube_uploader.py
```

3. 영상 길이 확인:
   - 쇼츠는 60초 이하여야 함

## 💡 창의적 아이디어

### 1. 시즌별 콘텐츠

```python
# seasonal_topics.py
import datetime

def get_seasonal_topic():
    month = datetime.datetime.now().month
    
    if month in [12, 1, 2]:  # 겨울
        return "겨울철 건강 관리"
    elif month in [3, 4, 5]:  # 봄
        return "봄 알레르기 예방법"
    elif month in [6, 7, 8]:  # 여름
        return "여름 더위 극복 팁"
    else:  # 가을
        return "가을 단풍 명소"
```

### 2. 인터랙티브 요소

대본에 질문 추가:

```json
{
  "script": "여러분은 어떻게 생각하시나요? 댓글로 의견을 남겨주세요!"
}
```

### 3. 시리즈 연결

각 영상 끝에 다음 편 예고:

```json
{
  "script": "... 놀랍지 않나요? 다음 편에서는 더 놀라운 사실을 알려드리겠습니다!"
}
```

---

**더 많은 예시와 팁은 커뮤니티에서 공유해주세요!** 🎉
