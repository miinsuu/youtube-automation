# 🎯 target_channel_id로 특정 채널에 업로드하기

## 문제
- **Q**: `target_channel_id`를 사용해서 직접 특정 채널에 업로드할 수 있을까?
- **A**: YouTube API 제한으로 직접은 불가능하지만, **채널별 독립 인증**으로 가능합니다!

---

## 🔧 해결책: 채널별 인증 정보 분리

### 방식 변경

| 이전 | 현재 |
|------|------|
| 단일 인증 정보 | 채널별 독립 인증 정보 |
| 항상 기본 채널로 업로드 | `target_channel_id`의 채널로 업로드 |
| `youtube_credentials.json` | `youtube_credentials_[채널ID].json` |

---

## 📋 설정 방법

### **Step 1: config.json에서 채널 ID 지정**

```json
{
  "youtube": {
    "target_channel_id": "UC2yneYUgVE2VSzRL4y1Qbdg"
  }
}
```

### **Step 2: 해당 채널 계정으로 인증**

```bash
python main.py --count 1
```

**처음 실행 시 자동으로:**
1. 브라우저에서 Google 로그인 팝업 표시
2. **`target_channel_id` 채널의 소유자 계정으로 로그인**
3. 인증 정보 저장: `config/youtube_credentials_Rl4y1Qbdg.json` (채널 ID의 마지막 8자)
4. 해당 채널로 자동 업로드

### **Step 3: 업로드 확인**

```
✓ 업로드 대상 채널: UC2yneYUgVE2VSzRL4y1Qbdg
✓ 현재 로그인 채널: [채널명] (UC2yneYUgVE2VSzRL4y1Qbdg)
✅ 채널 일치! 해당 채널로 업로드됩니다.
✅ 업로드 완료!
```

---

## 🔐 여러 채널로 업로드하기

### **여러 채널을 관리하는 경우**

각 채널마다 다른 `config.json`을 사용하거나, 프로그래밍으로 제어할 수 있습니다:

```python
from scripts.youtube_uploader import YouTubeUploader

# 채널 1로 업로드
uploader1 = YouTubeUploader(channel_id="UC2yneYUgVE2VSzRL4y1Qbdg")
uploader1.upload_video("video.mp4", script_data)

# 채널 2로 업로드
uploader2 = YouTubeUploader(channel_id="UC_다른채널ID")
uploader2.upload_video("video.mp4", script_data)
```

---

## 💾 채널별 인증 정보 파일

자동으로 생성되는 인증 정보 파일:

```
config/
├── youtube_credentials_Rl4y1Qbdg.json  (채널 1)
├── youtube_credentials_xxxyyy222.json  (채널 2)
└── youtube_credentials_zzz9gg33.json   (채널 3)
```

각 파일은 해당 채널의 인증 정보를 보관합니다.

---

## ✅ 체크리스트

### 채널별 업로드 설정

- [ ] **각 채널의 ID 확인**
  - YouTube Studio > 설정 > 기본 정보 > "채널 ID"

- [ ] **config.json 업데이트**
  ```json
  "target_channel_id": "UC2yneYUgVE2VSzRL4y1Qbdg"
  ```

- [ ] **인증 정보 초기화** (새로운 채널일 경우)
  ```bash
  rm config/youtube_credentials_*.json
  ```

- [ ] **테스트 업로드**
  ```bash
  python main.py --count 1
  ```

- [ ] **로그 확인**
  - `✅ 채널 일치!` 메시지 확인
  - YouTube에서 해당 채널에 업로드되었는지 확인

---

## 🔄 채널 변경하기

### 다른 채널로 업로드하려면?

```bash
# 1. config.json에서 target_channel_id 변경
# 2. 인증 정보 초기화
rm config/youtube_credentials_*.json

# 3. 새 채널로 인증 (다른 계정으로 로그인)
python main.py --count 1

# 4. 자동으로 새 채널의 인증 정보 생성됨
# config/youtube_credentials_[새채널ID].json
```

---

## ⚠️ 문제 해결

### **문제: "채널 불일치!" 오류**

```
⚠️  채널 불일치!
   대상: UC2yneYUgVE2VSzRL4y1Qbdg
   현재: UC_다른채널ID
```

**원인**: 다른 계정으로 로그인됨

**해결**:
```bash
# 1. 인증 정보 삭제
rm config/youtube_credentials_*.json

# 2. 올바른 계정으로 다시 인증
python main.py --count 1

# 3. 로그인 팝업에서 target_channel_id의 소유자 계정으로 로그인
```

### **문제: 인증 팝업이 안 나옴**

**해결**:
```bash
# 1. 저장된 인증 정보 모두 삭제
rm config/youtube_credentials_*.json

# 2. 다시 시도 (팝업 자동 표시)
python main.py --count 1
```

### **문제: "Insufficient Permission" 오류**

**원인**: 이전 인증 정보가 만료됨

**해결**:
```bash
# 1. 모든 인증 정보 삭제
rm config/youtube_credentials_*.json

# 2. 재인증
python main.py --count 1
```

---

## 🎯 GitHub Actions에서 사용하기

### 채널별로 다른 Secrets 설정

```yaml
# .github/workflows/youtube-automation.yml

- name: Setup credentials for Channel 1
  env:
    CHANNEL_ID: UC2yneYUgVE2VSzRL4y1Qbdg
  run: |
    python -c "
    import json
    config = json.load(open('config/config.json'))
    config['youtube']['target_channel_id'] = '${{ env.CHANNEL_ID }}'
    json.dump(config, open('config/config.json', 'w'), indent=2)
    "
```

---

## 📝 예제 시나리오

### 시나리오 1: 단일 채널 (일반적)

```bash
# 1. config.json 설정
# target_channel_id: "UC2yneYUgVE2VSzRL4y1Qbdg"

# 2. 한 번 인증 후 계속 사용
python main.py --count 1  # 자동 업로드

# 계속 동작...
python main.py --count 1  # 또 자동 업로드
```

### 시나리오 2: 다중 채널 (고급)

```python
# multi_channel_upload.py
from scripts.youtube_uploader import YouTubeUploader

channels = [
    "UC2yneYUgVE2VSzRL4y1Qbdg",  # 채널 1
    "UC_채널2ID",
    "UC_채널3ID"
]

for channel_id in channels:
    print(f"\n📤 {channel_id}로 업로드 중...")
    uploader = YouTubeUploader(channel_id=channel_id)
    uploader.upload_video("video.mp4", script_data)
    print("✅ 완료!")
```

---

## 🔑 핵심 정리

### ❌ 과거 방식 (불가능)
```
config.json의 target_channel_id만으로는 불가능
→ 항상 기본 채널로 업로드됨
```

### ✅ 새로운 방식 (가능)
```
config.json: target_channel_id 지정
      ↓
Python 실행: 채널별 인증 정보 자동 생성
      ↓
해당 채널로 자동 업로드
```

---

## 🚀 시작하기

```bash
# 1. config.json에 target_channel_id 설정
# 2. 실행
python main.py --count 1

# 3. 브라우저 팝업에서 해당 채널의 계정으로 로그인
# 4. 완료!
```

---

**마지막 업데이트**: 2026년 2월 13일  
**상태**: ✅ 채널별 독립 인증 기능 구현 완료
