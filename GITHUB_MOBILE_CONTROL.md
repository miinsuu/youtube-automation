# 🎬 GitHub 모바일 컨트롤 가이드

맥북이 꺼져있어도 **폰 브라우저에서 GitHub를 통해** 영상 생성을 제어할 수 있습니다!

---

## 🚀 빠른 시작 (30초)

### 1️⃣ 폰에서 GitHub 저장소 열기
```
https://github.com/miinsuu/youtube-automation
```

### 2️⃣ "Actions" 탭 클릭
![GitHub Actions Tab](https://github.com/miinsuu/youtube-automation/actions)

### 3️⃣ "YouTube Shorts Auto Upload" 워크플로우 선택

### 4️⃣ "Run workflow" 버튼 클릭
- **upload**: `true` (유튜브 자동 업로드) 또는 `false` (생성만)
- **Branch**: main 선택

### 5️⃣ "Run workflow" 확인
✅ 몇 초 후 Ubuntu 서버에서 자동 실행 시작!

---

## 📊 실시간 진행 상황 확인

### 실행 중인 워크플로우 모니터링

1. **Actions 탭** → "YouTube Shorts Auto Upload" 클릭
2. 최신 실행 항목 클릭 (맨 위)
3. **Logs** 탭에서 실시간 진행 상황 확인:
   ```
   ✅ Checkout repository
   ✅ Set up Python
   ✅ Install FFmpeg
   ✅ Install dependencies
   ✅ Setup credentials
   📝 Create video (시간이 걸림 - 3-5분)
   ```

### 진행 상황 해석

```
🔄 Creating video...
   📌 고정 주제 선택: 비트코인의 실제 가치
   📝 스크립트 생성 중...
   🎤 음성 생성 중...
   🖼️ 이미지 다운로드 중...
   🎬 영상 생성 중...
   ✅ output/video_20260212_143025.mp4

✅ 영상 생성 완료! (소요시간: 4분 32초)
```

---

## 📱 모바일에서의 최적 동작

### 스마트폰 화면 크기 최적화

```
┌─────────────────────┐
│ GitHub.com          │  ← 주소창
├─────────────────────┤
│ 🏠 YouTube Shorts   │
│    Auto Upload      │
│                     │
│ ━━━━━━━━━━━━━━━━   │
│ ✅ youtube-automa.. │  ← 최신 실행
│    3분 전           │     (초록색 = 성공)
│                     │
│ ━━━━━━━━━━━━━━━━   │
│ 🟡 youtube-automa.. │  ← 이전 실행
│    1시간 전         │     (황색 = 진행중)
│                     │
│ [Run workflow ▼]    │  ← 터치하기 쉬운 버튼
└─────────────────────┘
```

### 터치하기 좋은 위치
- ✅ "Run workflow" 버튼 (아래쪽)
- ✅ 실행 항목 리스트 (스크롤 가능)
- ✅ Logs 탭 (실시간 진행 상황)

---

## ⚙️ 워크플로우 파라미터 설정

### "Run workflow" 클릭 후 설정 화면

```
┌────────────────────────────────┐
│ Run workflow                   │
├────────────────────────────────┤
│ Upload:  ┌─────────────────┐  │
│          │ ⊕ true  ○ false │  │
│          └─────────────────┘  │
│                                │
│ Branch:  ┌─────────────────┐  │
│          │ main         ⊗ │  │
│          └─────────────────┘  │
│                                │
│        [Run workflow]          │
│        [Cancel]                │
└────────────────────────────────┘
```

### 파라미터 설명

| 파라미터 | 옵션 | 설명 |
|---------|------|------|
| **Upload** | `true` | ✅ 영상 생성 + YouTube 자동 업로드 |
| | `false` | 📝 영상만 생성 (업로드 안 함) |
| **Branch** | `main` | 항상 main 선택 |

### 추천 설정

**📱 빠른 테스트 (2-3분)**
```
upload: false  ← 업로드 시간 절약
```

**📤 완전 자동화 (5-7분)**
```
upload: true   ← 생성 후 자동 업로드
```

---

## 🔍 결과 확인

### 1. GitHub에서 파일 확인

**생성된 영상 다운로드:**
```
github.com/miinsuu/youtube-automation
→ output 폴더
→ video_*.mp4 (최신 영상)
```

**생성된 스크립트 확인:**
```
github.com/miinsuu/youtube-automation
→ output 폴더
→ script_*.json
```

### 2. 폰에서 영상 재생

```
output 폴더 → video_*.mp4
→ 파일 클릭 → "Preview" 또는 다운로드
```

### 3. YouTube에서 확인 (업로드한 경우)

```
https://www.youtube.com/@your_channel
→ 최신 영상 확인 (1-2분 후)
```

---

## 🚨 문제 해결

### Q: "Run workflow" 버튼이 안 보여요

**해결:**
1. 로그인되어 있나요? 
   - 우측 상단 프로필 클릭 → "Sign in" (또는 이미 로그인 상태)
2. Repository 권한이 있나요?
   - Owner 계정으로 로그인해야 함

### Q: 워크플로우가 실패했어요 (빨간 ❌)

**로그 확인:**
1. 최신 실행 항목 클릭
2. 실패한 작업 클릭 (예: "Create video")
3. 에러 메시지 확인

**일반적인 원인:**
- ❌ API 키 만료 (config.json 확인)
- ❌ YouTube OAuth 토큰 만료 (재인증 필요)
- ❌ Pexels API 할당량 초과 (다음 날 재시도)

### Q: Logs가 너무 길어요

**필터링:**
```
Logs 입력창에 검색어 입력:
- "✅" → 성공한 항목만
- "⚠️" → 경고만
- "error" → 오류만
```

### Q: 폰에서 자동 새로고침이 안 돼요

**수동 새로고침:**
```
iOS Safari:  아래쪽 새로고침 아이콘 ↻
Android Chrome: 위쪽 새로고침 아이콘 ↻
```

또는 자동 새로고침 (Chrome):
```
1. 개발자 도구 (F12)
2. ... 메뉴 → Settings
3. "Auto-reload page" 체크
```

---

## 📈 모니터링 팁

### 1. 북마크 저장
```
폰 브라우저:
1. github.com/miinsuu/youtube-automation/actions
2. 공유 → 북마크에 추가
3. "YouTube Shorts 생성" (단축 이름)
```

### 2. 홈 화면에 추가 (PWA)
```
iOS Safari:
1. 공유 → 홈 화면에 추가
2. 앱처럼 사용 가능

Android Chrome:
1. 메뉴 → 앱 설치
2. 앱 드로어에서 실행
```

### 3. 알림 설정 (GitHub 앱)
```
GitHub 모바일 앱 설치:
1. App Store / Play Store → "GitHub"
2. Actions 탭 → 워크플로우 클릭
3. 🔔 알림 활성화
4. 완료/실패 시 알림 받음
```

---

## 🎯 워크플로우 상태 코드

| 상태 | 아이콘 | 의미 |
|------|--------|------|
| 성공 | ✅ | 영상 생성/업로드 완료 |
| 실패 | ❌ | 오류 발생 (로그 확인) |
| 진행 중 | 🟡 | 현재 실행 중 |
| 취소됨 | ⏹ | 수동 중단됨 |
| 대기 중 | ⏳ | 대기열에서 대기 |

---

## 💡 Best Practices

### ✅ DO

- ✅ 정해진 시간대에 실행 (트래픽 분산)
- ✅ 한 번에 1-2개만 생성 (서버 부하 방지)
- ✅ 업로드 전에 `false`로 테스트
- ✅ Logs에서 이모티콘 제거 여부 확인
- ✅ 매주 1-2번 정도 수동 트리거

### ❌ DON'T

- ❌ 동시에 여러 워크플로우 실행 (대기열 오버플로우)
- ❌ 자동 업로드 테스트 반복 (YouTube 제한)
- ❌ 5분 이내 재시도 (서버 쿨다운)
- ❌ 밤 10시 이후 트리거 (GitHub Actions 부하)

---

## 🔗 빠른 링크

| 링크 | 설명 |
|------|------|
| [저장소](https://github.com/miinsuu/youtube-automation) | GitHub 저장소 메인 |
| [Actions](https://github.com/miinsuu/youtube-automation/actions) | 워크플로우 실행 현황 |
| [Output 폴더](https://github.com/miinsuu/youtube-automation/tree/main/output) | 생성된 파일들 |
| [Config](https://github.com/miinsuu/youtube-automation/blob/main/config/config.json) | 설정 파일 (웹 에디터로 수정 가능) |

---

## 🔐 보안 주의

### Secrets 관리

GitHub Secrets에 저장되는 민감 정보:
- 🔑 `GEMINI_API_KEY` - Google Gemini API
- 🔑 `YOUTUBE_CLIENT_SECRETS` - YouTube OAuth
- 🔑 `YOUTUBE_CREDENTIALS` - YouTube 인증 토큰

⚠️ **절대 공개하지 마세요!**

### Workflow 로그 보안

- 🔐 로그에는 민감 정보가 마스킹됨
- 🔐 API 키는 표시되지 않음
- ✅ 안전하게 모니터링 가능

---

## 📞 FAQ

**Q: 몇 개 영상을 한 번에 만들 수 있나요?**
```
A: count 파라미터로 1-10개 설정 가능
   (현재 워크플로우는 1개 고정, 
    필요시 main.py --count N으로 수정 가능)
```

**Q: 만들어진 영상은 자동으로 삭제되나요?**
```
A: 아니오. output 폴더에 영구 저장됨
   용량 초과 시 수동으로 정리 필요
```

**Q: 스케줄된 자동 실행 + 수동 실행을 동시에?**
```
A: GitHub Actions가 자동으로 대기열 관리
   동시 실행 최대 20개까지 가능
```

**Q: 업로드 없이 생성만 하고 나중에 업로드할 수 있나요?**
```
A: 네! upload=false로 생성 후
   나중에 output 폴더의 MP4를 YouTube에 수동 업로드
```

---

## 🎉 축하합니다!

이제 **폰 한 대**로 언제 어디서나:
- ✅ 영상 생성 트리거
- ✅ 진행 상황 실시간 모니터링
- ✅ 생성된 파일 확인 및 다운로드
- ✅ 자동 업로드 설정

**모두 가능합니다!** 🚀

---

## 📝 마지막 팁

### 자주 사용할 URL들을 정리해두세요:

```
📱 모바일 홈 화면:
1. GitHub Actions: github.com/miinsuu/youtube-automation/actions
2. Output 폴더: github.com/miinsuu/youtube-automation/tree/main/output
3. YouTube 채널: youtube.com/@your_channel

🔗 북마크 저장:
- "🎬 영상 생성"
- "📁 결과 확인"
- "📺 내 채널"
```

**Happy creating! 🎬✨**
