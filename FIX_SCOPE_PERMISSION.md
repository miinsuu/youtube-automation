# 🔧 YouTube API 권한 (Scope) 문제 해결

## 문제
```
❌ 현재 채널 조회 오류: Insufficient Permission
   "Request had insufficient authentication scopes"
```

## 원인

기존 인증 정보가 **채널 정보 조회 권한**이 없는 스코프로 생성되었습니다.

### 이전 스코프
```python
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']  # 업로드만 가능
```

### 새로운 스코프
```python
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',    # 비디오 업로드
    'https://www.googleapis.com/auth/youtube.readonly',  # 채널 정보 조회
    'https://www.googleapis.com/auth/youtube',           # 전체 YouTube 관리
]
```

---

## ✅ 해결 방법

### **Step 1: 기존 인증 정보 초기화**

```bash
rm config/youtube_credentials*.json
```

이 명령어로 모든 저장된 인증 정보를 삭제합니다.

### **Step 2: 채널 정보 확인 (새 스코프로 재인증)**

```bash
python check_channels.py
```

### **Step 3: 브라우저 로그인**

1. 브라우저 팝업 표시
2. 해당 Google 계정으로 로그인
3. **권한 승인** (새로운 권한 추가)
   - "YouTube 채널 정보 보기" 권한 추가 됨

### **Step 4: 완료**

이제 다음이 정상 작동합니다:
```
✓ 현재 기본 채널: [채널명] ([채널ID])
✓ 보유한 모든 채널: [목록]
```

---

## 🔑 필요한 스코프 설명

| 스코프 | 용도 |
|--------|------|
| `youtube.upload` | 비디오 업로드, 썸네일 설정 |
| `youtube.readonly` | **채널 정보 조회** (이전에 없음) |
| `youtube` | 전체 YouTube 관리 (포괄적) |

---

## 📋 단계별 체크리스트

- [ ] **기존 인증 정보 삭제**
  ```bash
  rm config/youtube_credentials*.json
  ```

- [ ] **새 스코프로 재인증**
  ```bash
  python check_channels.py
  ```

- [ ] **브라우저 팝업에서 권한 승인**
  - "이 앱에 다음 권한 제공 허용"
  - ✓ YouTube 채널 정보 보기
  - ✓ 계정 이메일 주소 보기

- [ ] **완료 확인**
  ```
  ✓ 현재 기본 채널: [채널명]
  ✓ 보유한 모든 채널: [목록]
  ```

---

## 🚀 이제 작동하는 명령어들

### 채널 정보 확인
```bash
python check_channels.py
```

### 영상 업로드
```bash
python main.py --count 1
```

### 여러 채널 관리
```python
from scripts.youtube_uploader import YouTubeUploader

# 채널 1
uploader1 = YouTubeUploader(channel_id="UC2yneYUgVE2VSzRL4y1Qbdg")
uploader1.authenticate()

# 채널 2
uploader2 = YouTubeUploader(channel_id="UC_다른채널ID")
uploader2.authenticate()
```

---

## ⚠️ 주의사항

### 인증 정보 파일 위치

```
config/
├── youtube_credentials_Rl4y1Qbdg.json    (채널 1)
├── youtube_credentials_xxxyyy222.json    (채널 2)
└── youtube_credentials_zzz9gg33.json     (채널 3)
```

각 채널마다 별도의 인증 정보가 저장됩니다.

### 권한 변경 시

새로운 권한이 필요하면:
1. 인증 정보 삭제
2. 재인증 (권한 승인)

---

## 🔐 Google OAuth 권한 확인

### 앱 권한 확인 방법

1. Google Account 방문
   ```
   https://myaccount.google.com/permissions
   ```

2. "YouTube Automation" 앱 확인

3. 권한 확인:
   - ✓ YouTube 채널 정보 보기
   - ✓ YouTube 콘텐츠 업로드

### 권한 재설정

권한에 문제가 있으면:
1. 앱 삭제 (해제)
2. 인증 정보 삭제
3. 다시 실행 (새 권한으로 재인증)

---

## 🆘 여전히 안 되면?

### 1단계: 완전 초기화

```bash
# 모든 인증 정보 삭제
rm -f config/youtube_credentials*.json
rm -f ~/.cache/google-auth-*  # 시스템 캐시도 삭제

# 앱 권한 제거
# https://myaccount.google.com/permissions > YouTube Automation 삭제
```

### 2단계: 재인증

```bash
python check_channels.py
```

### 3단계: 권한 재승인

브라우저에서 모든 권한 승인

---

## 📝 코드 변경 사항

### youtube_uploader.py

```python
# 이전
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# 현재
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube',
]
```

---

## ✅ 완료!

이제 모든 기능이 정상 작동합니다:

- ✓ 채널 정보 조회
- ✓ 영상 업로드
- ✓ 채널별 관리
- ✓ 썸네일 업로드

---

**마지막 업데이트**: 2026년 2월 13일
