# 📱 모바일 컨트롤 설정 (macOS 꺼져있을 때)

맥북이 꺼져있어도 **폰 한 대로 GitHub를 통해** YouTube 쇼츠를 만들 수 있습니다! 🚀

---

## 🎯 3가지 방법

### 방법 1️⃣: **가장 쉬운 방법** (수동 클릭)
```
1. 폰 브라우저: github.com/miinsuu/youtube-automation/actions
2. "YouTube Shorts Auto Upload" 워크플로우 클릭
3. "Run workflow" ▼ 클릭
4. count, upload 설정
5. "Run workflow" 확인
```
⏱️ **소요 시간**: 10초

---

### 방법 2️⃣: **HTML 페이지 사용** (한 번에!)
```
폰 브라우저에서 이 URL 열기:
https://github.com/miinsuu/youtube-automation/raw/main/templates/mobile-control.html
```

**기능:**
- ✅ 개수 선택 (1-5개)
- ✅ 업로드 여부 선택
- ✅ GitHub Token 없이도 수동 실행 가능
- ✅ 한 번에 GitHub Actions 실행

⏱️ **소요 시간**: 3초

---

### 방법 3️⃣: **자동 트리거** (가장 빠름 - GitHub Token 필요)
```
1. GitHub Token 생성
   https://github.com/settings/tokens
   
2. "Personal access tokens" → "Tokens (classic)"
3. "Generate new token (classic)"
4. Scopes: repo, workflow 체크
5. Token 복사 (ghp_로 시작)

6. 모바일 페이지에 Token 입력
   설정 → GitHub Token입력
   
7. "🚀 영상 생성 시작" 클릭
```

⏱️ **소요 시간**: 1초

---

## 📱 모바일 페이지 (권장!)

### 빠른 접근
```
폰 북마크 추가:
https://github.com/miinsuu/youtube-automation/raw/main/templates/mobile-control.html
```

### PWA 앱처럼 사용
```
iOS:  공유 → 홈 화면에 추가
Android: 메뉴 → 앱 설치
```

---

## ⚙️ 파라미터 설정

### Count (생성할 영상 개수)
```
1 = 3분 (빠른 테스트)
2 = 6분
3 = 9분
4 = 12분
5 = 15분
```

### Upload (YouTube 업로드)
```
false = 생성만 (나중에 수동 업로드)
true  = 자동 업로드 (생성 후 바로 업로드)
```

---

## 📊 실행 상황 확인

### 실시간 모니터링
```
GitHub Actions 페이지:
github.com/miinsuu/youtube-automation/actions

✅ 녹색 체크 = 성공
❌ 빨강 X = 실패
🟡 황색 동그라미 = 진행 중
```

### 로그 확인
```
최신 실행 항목 클릭
→ Create video 스텝 클릭
→ 실시간 진행 상황 보기
```

### 파일 확인
```
생성된 영상:
github.com/miinsuu/youtube-automation/tree/main/output/videos

생성된 스크립트:
github.com/miinsuu/youtube-automation/tree/main/output
```

---

## 🔐 GitHub Token 생성하기

### 1단계: 설정 페이지 열기
```
https://github.com/settings/tokens
```

### 2단계: "Tokens (classic)" 클릭

### 3단계: "Generate new token (classic)" 클릭

### 4단계: 설정
```
Token name: "YouTube Automation Mobile"

Expiration: 90일 (또는 무제한)

Scopes:
  ☑️ repo (저장소 접근)
  ☑️ workflow (Actions 실행)
```

### 5단계: Token 복사
```
ghp_... 형태로 시작하는 긴 문자열

⚠️ 절대 누구에게도 알려주지 마세요!
```

---

## 🚨 문제 해결

### Token 오류
```
❌ "401 Unauthorized"
→ Token이 만료됨
→ 새 Token 생성

❌ "404 Not Found"
→ Repository 이름 확인
→ 소유자 계정으로 로그인
```

### Workflow 실행 안 됨
```
1. GitHub 로그인 확인
2. Token 유효 기간 확인
3. Scopes 확인 (repo, workflow)
4. 수동으로 시도해보기
```

### 자동 스케줄 vs 수동 실행
```
자동 스케줄 (정해진 시간):
- 평일: 08:00, 12:00, 15:00, 18:00, 22:00 (한국 시간)
- 주말: 09:00, 12:00, 15:00, 18:00, 22:00 (한국 시간)

수동 실행:
- 언제든 실행 가능 (24시간)
- 동시에 여러 개 가능 (20개까지)
```

---

## 💡 추천 사용법

### 매일 자동 생성
```
자동 스케줄 활용
→ 정해진 시간에 자동으로 1개씩 생성
→ YouTube에 자동 업로드
```

### 긴급 콘텐츠 생성
```
수동 실행 (모바일 페이지)
→ 1-5개 추가 생성
→ 바로 업로드
```

### 테스트
```
count: 1
upload: false
→ 빠른 생성 (3분)
→ 결과 확인 후 업로드
```

---

## 🎯 모바일 페이지 기능

### 생성 개수 선택
```
드롭다운에서 1-5개 선택
(많을수록 시간 증가)
```

### 업로드 옵션
```
🔘 생성만 (빠름)
🔘 자동 업로드 (완전 자동)
```

### GitHub Token 입력
```
없으면:
→ "수동으로 실행" 버튼 사용
→ GitHub에서 직접 실행

있으면:
→ 입력 후 "시작" 버튼
→ 1초에 시작됨
```

### 진행 상황
```
버튼 클릭
→ "생성 중..." 표시
→ GitHub Actions 자동 열림
→ 실시간 로그 확인 가능
```

---

## 📈 성능 팁

### 빠르게 하기
```
✅ count=1 선택 (3분)
✅ upload=false 선택 (업로드 시간 절약)
✅ 자동 스케줄 활용 (대기 없음)
```

### 안정적으로 하기
```
✅ 5분 이상 간격으로 실행
✅ 동시에 여러 개 안 하기
✅ 로그에서 에러 확인
```

### 효율적으로 하기
```
✅ 자동 스케줄 + 수동 실행 조합
✅ 야간에 자동 생성 (리소스 여유)
✅ 긴급 때만 수동 트리거
```

---

## 🔗 빠른 링크

| 목적 | 링크 |
|------|------|
| **모바일 페이지** | [open](https://github.com/miinsuu/youtube-automation/raw/main/templates/mobile-control.html) |
| **Actions 모니터링** | [github.com/miinsuu/youtube-automation/actions](https://github.com/miinsuu/youtube-automation/actions) |
| **결과 확인** | [output 폴더](https://github.com/miinsuu/youtube-automation/tree/main/output) |
| **Token 생성** | [settings/tokens](https://github.com/settings/tokens) |
| **저장소** | [youtube-automation](https://github.com/miinsuu/youtube-automation) |

---

## ✨ 요약

| 방법 | 난이도 | 속도 | 추천도 |
|------|--------|------|--------|
| 수동 실행 | ⭐ 쉬움 | 10초 | ⭐⭐⭐⭐ |
| HTML 페이지 | ⭐⭐ 보통 | 3초 | ⭐⭐⭐⭐⭐ |
| Token 자동화 | ⭐⭐⭐ 어려움 | 1초 | ⭐⭐⭐⭐ |

---

**시작하세요! 🚀**

가장 쉬운 "수동 실행" 방법부터 시작해보세요. 익숙해지면 HTML 페이지나 Token을 추가하세요!
