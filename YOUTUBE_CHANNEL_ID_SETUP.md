# 📺 YouTube 채널 ID 설정 가이드

여러 YouTube 채널을 소유하고 있을 때, **특정 채널로만 업로드**하는 방법입니다.

---

## 🎯 문제 상황

"UC2yneYUgVE2VSzRL4y1Qbdg" 채널로 업로드하려는데 **다른 채널로 업로드**됨

---

## ✅ 해결 방법

### Step 1: 채널 ID 확인

**본인의 YouTube 채널 ID 찾기:**

```
1. YouTube 채널 방문: youtube.com/@your_channel
2. 채널명 클릭 → 채널 정보
3. URL에서 @뒤의 username 확인
   https://youtube.com/@minsu_channel
   
4. 또는 YouTube Studio에서:
   YouTube Studio (youtube.com/studio)
   → 설정 → 채널 정보
   → 채널 ID 복사 (UC로 시작하는 28자 문자열)
```

### Step 2: config.json 수정

**로컬 환경에서 (macOS):**

```
파일: config/config.json

{
  "youtube": {
    "client_secrets_file": "config/client_secrets.json",
    "credentials_file": "config/youtube_credentials.json",
    "target_channel_id": "UC2yneYUgVE2VSzRL4y1Qbdg"  ← 여기!
  }
}
```

**GitHub Actions 환경:**

GitHub workflow에서 실행할 때는 config.json이 자동으로 생성되므로:

1. GitHub 저장소 Settings → Secrets and variables
2. "YOUTUBE_CHANNEL_ID" Secret 생성
3. 값: UC2yneYUgVE2VSzRL4y1Qbdg

---

## 🔍 채널 ID 확인하는 다양한 방법

### 방법 1: YouTube 채널 페이지

```
1. youtube.com/channel/UC2yneYUgVE2VSzRL4y1Qbdg 접속
2. URL의 'channel/' 뒤의 문자열이 채널 ID
```

### 방법 2: YouTube Data API

```bash
# curl로 확인 (API 키 필요)
curl "https://www.googleapis.com/youtube/v3/channels?part=id&mine=true&key=YOUR_API_KEY"

응답:
{
  "items": [
    {
      "id": "UC2yneYUgVE2VSzRL4y1Qbdg"
    }
  ]
}
```

### 방법 3: Python으로 확인

```python
from scripts.youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()
if uploader.authenticate():
    channels = uploader.get_my_channels()
    for ch in channels:
        print(f"채널: {ch['title']}")
        print(f"ID: {ch['channel_id']}\n")
```

---

## ⚙️ 설정 후 작동 원리

### 실행 흐름

```
1. config.json 읽기
   ↓
2. target_channel_id 확인: "UC2yneYUgVE2VSzRL4y1Qbdg"
   ↓
3. main.py에서 YouTubeUploader에 전달
   ↓
4. youtube_uploader.py에서 사용
   ↓
5. "🎯 업로드 대상 채널: UC2yneYUgVE2VSzRL4y1Qbdg" 출력
   ↓
6. 해당 채널로 업로드!
```

### 로그 확인

```
✅ YouTube API 인증 완료
🎯 업로드 대상 채널: UC2yneYUgVE2VSzRL4y1Qbdg
📤 YouTube 업로드 중: 20대 직장인의 금융 관리법
   업로드 진행: 100%
✅ 업로드 완료!
```

---

## 🚨 주의사항

### 주의 1: OAuth 인증 계정

```
⚠️ YouTube API 인증은 채널 소유자 계정으로 해야 합니다

예:
- 계정 A: 채널 1, 채널 2 소유
- 계정 B: 채널 3 소유

계정 A로 인증했는데 채널 3으로 업로드?
→ 권한 없음 에러 발생!

해결: 계정 B로 다시 인증
```

### 주의 2: 채널 ID vs 채널명

```
❌ 틀림: target_channel_id: "@minsu_channel"
❌ 틀림: target_channel_id: "minsu_channel"

✅ 맞음: target_channel_id: "UC2yneYUgVE2VSzRL4y1Qbdg"
```

### 주의 3: 빈 문자열이면 기본 채널로 업로드

```json
{
  "youtube": {
    "target_channel_id": ""  ← 비어있음
  }
}

결과: 기본 YouTube 채널로 업로드 (원하지 않는 채널일 수 있음)
```

---

## 🔧 여러 채널로 업로드하기

### 방법 1: 수동으로 config 변경

```bash
# 채널 1로 업로드
sed -i '' 's/"target_channel_id": ".*"/"target_channel_id": "UC_CHANNEL_1"/g' config/config.json
python main.py --count 1 --no-upload

# 채널 2로 업로드
sed -i '' 's/"target_channel_id": ".*"/"target_channel_id": "UC_CHANNEL_2"/g' config/config.json
python main.py --count 1
```

### 방법 2: Python 스크립트

```python
import json

def upload_to_channel(channel_id, count=1):
    # config 수정
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    
    config['youtube']['target_channel_id'] = channel_id
    
    with open('config/config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # 업로드 실행
    from scripts.youtube_uploader import YouTubeUploader
    from main import YouTubeAutomation
    
    automation = YouTubeAutomation()
    automation.batch_create(count=count, upload=True)

# 여러 채널에 업로드
upload_to_channel("UC_CHANNEL_1", count=2)
upload_to_channel("UC_CHANNEL_2", count=1)
```

### 방법 3: GitHub Actions 파라미터화

```yaml
workflow_dispatch:
  inputs:
    channel_id:
      description: 'YouTube Channel ID'
      required: true
      default: 'UC2yneYUgVE2VSzRL4y1Qbdg'

env:
  CHANNEL_ID: ${{ github.event.inputs.channel_id }}

steps:
  - name: Update channel ID
    run: |
      python -c "
      import json
      with open('config/config.json', 'r') as f:
          config = json.load(f)
      config['youtube']['target_channel_id'] = '${{ env.CHANNEL_ID }}'
      with open('config/config.json', 'w') as f:
          json.dump(config, f, indent=2)
      "
```

---

## ✨ 코드 변경 사항

### youtube_uploader.py

**이전:**
```python
def upload_video(self, video_path, script_data, thumbnail_path=None):
    # 채널 ID 미사용
    request = self.youtube.videos().insert(...)
```

**수정:**
```python
def upload_video(self, video_path, script_data, thumbnail_path=None, channel_id=None):
    # 채널 ID 확인 및 로깅
    target_channel_id = channel_id or self.config['youtube'].get('target_channel_id')
    if target_channel_id:
        print(f"🎯 업로드 대상 채널: {target_channel_id}")
    
    request = self.youtube.videos().insert(...)
```

### main.py

**이전:**
```python
upload_result = self.uploader.upload_video(video_path, script_data)
```

**수정:**
```python
target_channel_id = self.config['youtube'].get('target_channel_id')
upload_result = self.uploader.upload_video(
    video_path, 
    script_data,
    channel_id=target_channel_id
)
```

---

## 🎯 최종 체크리스트

- [ ] 업로드하려는 채널 ID 확인됨
- [ ] config/config.json의 target_channel_id 수정됨
- [ ] 파일 저장됨
- [ ] git push 완료됨 (로컬 테스트)
- [ ] 테스트 영상 생성 시작
- [ ] 올바른 채널에 업로드됨

---

## 📞 트러블슈팅

### Q: 여전히 다른 채널로 업로드돼요

```
1. config.json에서 target_channel_id 확인
2. 채널 ID 형식 확인 (UC로 시작, 28자)
3. YouTube API 인증 계정 확인
4. 로그에서 "🎯 업로드 대상 채널" 메시지 확인
5. GitHub Actions 사용 시:
   - Secrets 확인
   - config.json이 제대로 생성되는지 확인
```

### Q: 채널 ID를 모르겠어요

```
1. youtube.com/studio 방문
2. 좌측 메뉴 → 설정 → 채널 정보
3. "채널 ID" 섹션에서 복사
```

### Q: 권한 없음 에러가 나요

```
❌ Error: 403 Forbidden

원인: 현재 인증된 계정이 그 채널의 소유자가 아님

해결:
1. 로그아웃: rm config/youtube_credentials.json
2. 채널 소유자 계정으로 다시 인증
3. 첫 실행 시 브라우저에서 로그인
```

---

**설정 완료 후 다음 업로드부터 올바른 채널로 업로드됩니다!** ✅
