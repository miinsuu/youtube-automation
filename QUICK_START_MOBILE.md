# 🎬 YouTube 자동 생성 - 모바일 제어 완벽 가이드

**맥북이 꺼져있어도 폰으로 영상을 만들고 YouTube에 올릴 수 있습니다!** 🚀

---

## ⚡ 30초 시작하기

### 1️⃣ 폰에서 이 링크 열기
```
https://github.com/miinsuu/youtube-automation/raw/main/templates/mobile-control.html
```

### 2️⃣ 설정 후 "🚀 영상 생성 시작" 클릭
- 개수: 1개 추천 (3분)
- 업로드: 선택

### 3️⃣ 완료! ✅
- 자동으로 GitHub Actions 실행
- 3-5분 후 영상 생성 완료

---

## 📱 3가지 사용 방법

### **방법 1: 가장 쉬움 (수동 클릭)** ⭐⭐⭐⭐⭐

```
폰 브라우저:
github.com/miinsuu/youtube-automation/actions
→ "Run workflow" 버튼
→ 설정 후 실행
```

**장점:** 가장 간단, 추가 설정 없음  
**단점:** 매번 GitHub 웹사이트 방문  
**시간:** 10초

---

### **방법 2: HTML 페이지 (권장)** ⭐⭐⭐⭐⭐

```
폰 북마크에 저장:
https://github.com/miinsuu/youtube-automation/raw/main/templates/mobile-control.html
```

**기능:**
- 개수 선택 (1-5개)
- 업로드 여부 선택
- 한 번에 클릭으로 실행

**장점:** 가장 편함, 한 번에!  
**단점:** GitHub Token으로 업그레이드 가능  
**시간:** 3초

---

### **방법 3: GitHub Token (가장 빠름)** ⭐⭐⭐

```
1. https://github.com/settings/tokens
2. "Generate new token (classic)"
3. scopes: repo, workflow 체크
4. Token 복사
5. HTML 페이지에 입력
```

**기능:**
- 1초에 실행
- GitHub 페이지 방문 불필요

**장점:** 가장 빠름, 자동화  
**단점:** 초기 설정 필요  
**시간:** 1초

---

## 🎯 각 상황별 추천

| 상황 | 추천 방법 | 이유 |
|------|---------|------|
| 처음 사용 | 방법 1 (수동) | 가장 이해하기 쉬움 |
| 자주 사용 | 방법 2 (HTML) | 편하고 간단 |
| 매일 사용 | 방법 3 (Token) | 가장 빠름 |
| 긴급 상황 | 방법 2 또는 3 | 1-3초 |

---

## 📊 파라미터 이해하기

### Count (생성할 영상 개수)
```
1개 → 약 3분
2개 → 약 6분
3개 → 약 9분
4개 → 약 12분
5개 → 약 15분

팁: 처음엔 1개로 테스트!
```

### Upload (YouTube 업로드)
```
📝 생성만
  - 영상만 만들고 업로드 안 함
  - 나중에 수동으로 업로드 가능
  - 빠름 (업로드 시간 절약)

✅ 자동 업로드
  - 영상 만든 후 YouTube에 자동 업로드
  - 설정된 채널에 바로 올라감
  - 시간 추가 필요 (1-2분)
```

---

## 🔐 GitHub Token 얻기 (선택사항)

### Step 1: 설정 페이지 열기
```
https://github.com/settings/tokens
```

### Step 2: "Tokens (classic)" 클릭

### Step 3: "Generate new token (classic)" 버튼

### Step 4: 정보 입력
```
Token name: "YouTube Automation Mobile"
Expiration: 90일 (또는 무제한)
```

### Step 5: Scopes 체크
```
☑️ repo
☑️ workflow
```

### Step 6: Token 생성 & 복사
```
ghp_... 형태의 긴 문자열
⚠️ 절대 공유하지 마세요!
```

### Step 7: HTML 페이지에 입력
```
1. mobile-control.html 열기
2. "GitHub Token" 입력 란에 붙여넣기
3. "🚀 영상 생성 시작" 클릭
```

---

## 📱 모바일 페이지 사용법

### 홈 화면에 추가 (앱처럼 사용)

**iOS (Safari):**
```
1. mobile-control.html 페이지 열기
2. 공유 아이콘 (↗️) 누르기
3. "홈 화면에 추가" 탭
4. "추가" 누르기
5. 홈 화면에서 앱처럼 실행 가능
```

**Android (Chrome):**
```
1. mobile-control.html 페이지 열기
2. 메뉴 (⋮) → "앱 설치"
3. "설치" 누르기
4. 앱 드로어에서 실행 가능
```

### 북마크로 저장

**모든 브라우저:**
```
1. mobile-control.html 페이지 열기
2. 즐겨찾기/북마크 추가
3. "🎬 영상 생성" 이름으로 저장
4. 북마크에서 한 번에 접근
```

---

## ✨ 사용 예시

### 예시 1: 빠른 테스트
```
1. Count: 1
2. Upload: 📝 생성만
3. 클릭
→ 3분 후 결과 확인
```

### 예시 2: 자동 업로드
```
1. Count: 1
2. Upload: ✅ 자동 업로드
3. 클릭
→ 5분 후 YouTube에 자동 올라감
```

### 예시 3: 대량 생성
```
1. Count: 5
2. Upload: ✅ 자동 업로드
3. 클릭
→ 15분 후 5개 영상 모두 업로드
```

---

## 🔍 실행 상황 확인

### 실시간 로그 보기
```
1. "🚀 영상 생성 시작" 클릭
2. 자동으로 GitHub Actions 페이지 열림
3. 최신 실행 항목 클릭
4. "Create video" 스텝 클릭
5. 실시간 진행 상황 확인
```

### 로그 내용 읽기
```
✅ Checkout repository
   → 코드 다운로드 완료

✅ Set up Python
   → Python 설정 완료

✅ Install dependencies
   → 필요한 라이브러리 설치

📝 Create video
   → 영상 생성 중 (시간이 걸림!)
   
   📌 고정 주제 선택: ...
   📝 스크립트 생성 중...
   🎤 음성 생성 중...
   🖼️ 이미지 다운로드 중...
   🎬 영상 생성 중...
   ✅ output/video_*.mp4

✅ 완료!
```

### 상태 아이콘
```
✅ 녹색 체크 = 완료/성공
❌ 빨강 X = 실패
🟡 황색 동그라미 = 진행 중
⏹️ 회색 정사각형 = 취소됨
```

---

## 📁 결과 확인

### 생성된 영상
```
GitHub 저장소
→ output 폴더
→ videos 폴더
→ video_*.mp4 (최신 영상)
```

### 생성된 스크립트
```
GitHub 저장소
→ output 폴더
→ script_*.json (스크립트 데이터)
```

### YouTube 확인
```
업로드 활성화하면:
→ youtube.com/@your_channel
→ "커뮤니티" 탭에서 최신 업로드 확인
→ 1-2분 후 공개
```

---

## 🚨 문제 해결

### Q: HTML 페이지가 안 열려요
```
A: 올바른 링크 확인:
https://github.com/miinsuu/youtube-automation/raw/main/templates/mobile-control.html

Safari/Chrome 캐시 지우기:
설정 → 브라우저 설정 → 캐시 지우기
```

### Q: "Run workflow" 버튼이 안 보여요
```
A: GitHub에 로그인했나요?
1. 우측 상단 프로필 아이콘
2. 로그인 상태 확인
3. Owner 계정으로 로그인 필요
```

### Q: Token 입력해도 안 되요
```
A: Token 확인 사항:
1. ghp_로 시작하나요?
2. 만료되지 않았나요?
3. Scopes에 repo, workflow 있나요?
4. 공백이 없나요?

없으면 "수동으로 실행" 버튼 사용
```

### Q: 워크플로우 실패했어요 (❌)
```
A: 로그 확인하기:
1. 최신 실행 항목 클릭
2. 실패한 스텝 클릭
3. 에러 메시지 읽기
4. 일반적인 원인:
   - API 키 만료
   - YouTube 토큰 만료
   - Pexels 할당량 초과
```

### Q: 3분 지났는데 안 끝났어요
```
A: 정상입니다!
- 첫 시작: 5-7분 소요 (라이브러리 설치)
- 이후: 3-4분
- 업로드 활성화: 5-7분

로그에서 진행 상황 확인!
```

---

## 💡 꿀팁

### Tip 1: 자동 스케줄 + 수동 실행 조합
```
자동 스케줄:
- 정해진 시간에 자동으로 1개씩 생성

수동 실행:
- 추가로 필요할 때 1-5개 생성

효율적! 😎
```

### Tip 2: 야간에 대량 생성
```
밤 11시-아침 7시:
- GitHub Actions 부하 적음
- 빠르게 실행
```

### Tip 3: 업로드 전 검수
```
1. upload: false로 생성
2. output/videos에서 확인
3. 문제 없으면 수동 업로드
```

### Tip 4: 에러 로그 저장
```
실패한 경우:
1. 로그 전체 복사
2. 메모에 저장
3. 나중에 분석/수정
```

---

## 📈 자동 스케줄 시간표

### 평일 (월-금)
```
08:00 KST - 자동 생성
12:00 KST - 자동 생성
15:00 KST - 자동 생성
18:00 KST - 자동 생성
22:00 KST - 자동 생성
```

### 주말 (토-일)
```
09:00 KST - 자동 생성
12:00 KST - 자동 생성
15:00 KST - 자동 생성
18:00 KST - 자동 생성
22:00 KST - 자동 생성
```

### 추가 수동 실행
```
언제든 추가로 실행 가능!
동시 최대 20개까지 가능
```

---

## 🎯 완벽한 워크플로우

```
아침 (6:00)
├─ 자동 스케줄 완료 (1개 생성)
└─ YouTube에 자동 업로드

점심 (12:00)
├─ 자동 스케줄 완료 (1개 생성)
└─ YouTube에 자동 업로드

오후 수동 (15:30)
├─ 모바일로 추가 2개 생성
├─ count: 2
└─ upload: true
   → YouTube에 추가 2개 올라감

저녁 (18:00)
├─ 자동 스케줄 완료 (1개 생성)
└─ YouTube에 자동 업로드

밤 (22:00)
├─ 자동 스케줄 완료 (1개 생성)
└─ YouTube에 자동 업로드

결과: 하루 5-7개 영상 자동 생성 & 업로드 ✨
```

---

## ✅ 체크리스트

### 처음 설정 시
- [ ] mobile-control.html 페이지 확인
- [ ] 북마크/홈 화면에 추가
- [ ] count: 1로 테스트
- [ ] upload: false로 시작
- [ ] 결과 확인

### 정상 작동 확인
- [ ] 스크립트 생성됨
- [ ] 이모티콘 없음 (중요!)
- [ ] 음성 생성됨
- [ ] 영상 생성됨
- [ ] GitHub에 파일 저장됨

### 업로드 준비
- [ ] YouTube 채널 확인
- [ ] OAuth 토큰 유효한지 확인
- [ ] upload: true로 변경
- [ ] 첫 업로드 테스트
- [ ] YouTube에 올라갔는지 확인

### 자동화 완성
- [ ] 자동 스케줄 활성화
- [ ] 수동 실행 준비
- [ ] 매일 모니터링
- [ ] 통계 확인

---

## 🎉 축하합니다!

이제 **폰 한 대로:**
- ✅ 언제 어디서나 영상 생성
- ✅ 원클릭 YouTube 자동 업로드
- ✅ 24/7 자동 생성
- ✅ 완전 자동화 시스템

**모두 가능합니다!** 🚀

---

## 📞 더 알아보기

| 주제 | 문서 |
|------|------|
| GitHub Actions 상세 | GITHUB_MOBILE_CONTROL.md |
| 로컬 웹 대시보드 | WEB_DASHBOARD_GUIDE.md |
| 전체 설정 가이드 | SETUP_GUIDE.md |
| 저장소 | github.com/miinsuu/youtube-automation |

---

**Happy creating! 🎬✨**

문제 발생 시 로그를 확인하고, GitHub Issues에 보고해주세요!
