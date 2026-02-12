# YouTube 자동 업로드 설정 가이드

## 📋 사전 요구사항

1. **Google Cloud 프로젝트** (YouTube Data API v3 활성화)
2. **OAuth 2.0 클라이언트 ID** (데스크톱 앱)
3. **YouTube 채널** (업로드 권한 필요)

---

## 🔧 1단계: Google Cloud 프로젝트 설정

### 1.1 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 상단의 프로젝트 선택 → "새 프로젝트" 클릭
3. 프로젝트 이름 입력 (예: "YouTube Shorts Automation")
4. "만들기" 클릭

### 1.2 YouTube Data API 활성화
1. 좌측 메뉴 → "API 및 서비스" → "라이브러리"
2. "YouTube Data API v3" 검색
3. "사용" 버튼 클릭

### 1.3 OAuth 동의 화면 설정
1. 좌측 메뉴 → "API 및 서비스" → "OAuth 동의 화면"
2. 사용자 유형: "외부" 선택 (개인 사용)
3. 앱 이름, 사용자 지원 이메일, 개발자 연락처 입력
4. "저장 후 계속"

### 1.4 범위 추가
1. "범위 추가 또는 삭제" 클릭
2. `https://www.googleapis.com/auth/youtube.upload` 선택
3. "업데이트" → "저장 후 계속"

### 1.5 테스트 사용자 추가
1. "테스트 사용자" 섹션
2. "ADD USERS" 클릭
3. 본인의 Google 계정 이메일 추가
4. "저장 후 계속"

---

## 🔑 2단계: OAuth 클라이언트 ID 생성

1. 좌측 메뉴 → "API 및 서비스" → "사용자 인증 정보"
2. "+ 사용자 인증 정보 만들기" → "OAuth 클라이언트 ID"
3. 애플리케이션 유형: "데스크톱 앱"
4. 이름 입력 (예: "YouTube Shorts Desktop")
5. "만들기" 클릭
6. **JSON 다운로드** 클릭
7. 다운로드한 파일을 `config/client_secrets.json`으로 저장

---

## 🔐 3단계: 최초 인증 (한 번만 필요)

```bash
# 프로젝트 디렉토리에서 실행
cd /Users/minsu/Downloads/youtube-automation
source venv/bin/activate

# 인증 스크립트 실행
python -c "
from scripts.youtube_uploader import YouTubeUploader
uploader = YouTubeUploader()
uploader.authenticate()
print('✅ 인증 완료!')
"
```

브라우저가 열리면:
1. Google 계정으로 로그인
2. "계속" 클릭 (보안 경고 무시)
3. 권한 허용
4. 완료되면 `config/youtube_credentials.json` 파일이 생성됨

---

## ☁️ 4단계: GitHub Actions 설정 (24/7 자동화)

### 4.1 GitHub 저장소 생성
```bash
cd /Users/minsu/Downloads/youtube-automation
git init
git add .
git commit -m "Initial commit"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/youtube-automation.git
git push -u origin main
```

### 4.2 GitHub Secrets 설정
GitHub 저장소 → Settings → Secrets and variables → Actions

다음 시크릿 추가:

| Secret Name | 값 |
|------------|-----|
| `GEMINI_API_KEY` | Gemini API 키 |
| `YOUTUBE_CLIENT_SECRETS` | `client_secrets.json` 파일 전체 내용 |
| `YOUTUBE_CREDENTIALS` | `youtube_credentials.json` 파일 전체 내용 |

### 4.3 워크플로우 활성화
1. GitHub 저장소 → Actions 탭
2. "I understand my workflows, go ahead and enable them" 클릭

---

## 🖥️ 5단계: 로컬 스케줄러 실행 (대안)

맥북에서 직접 실행하려면:

### 5.1 launchd 설정 (macOS)
```bash
# LaunchAgent 파일 생성
cat > ~/Library/LaunchAgents/com.youtube.shorts.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.youtube.shorts</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/minsu/Downloads/youtube-automation/venv/bin/python</string>
        <string>/Users/minsu/Downloads/youtube-automation/scheduler.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/minsu/Downloads/youtube-automation</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/minsu/Downloads/youtube-automation/logs/scheduler.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/minsu/Downloads/youtube-automation/logs/scheduler_error.log</string>
</dict>
</plist>
EOF

# 서비스 로드
launchctl load ~/Library/LaunchAgents/com.youtube.shorts.plist

# 상태 확인
launchctl list | grep youtube
```

### 5.2 서비스 관리
```bash
# 중지
launchctl unload ~/Library/LaunchAgents/com.youtube.shorts.plist

# 시작
launchctl load ~/Library/LaunchAgents/com.youtube.shorts.plist

# 수동 실행
launchctl start com.youtube.shorts
```

---

## 📅 스케줄 요약

| 요일 | 업로드 시간 |
|-----|-----------|
| 월-금 | 07:00, 12:00, 18:00, 22:00 (4회) |
| 토-일 | 09:00, 12:00, 15:00, 18:00, 22:00 (5회) |

**주간 총 업로드: 30개 영상**

---

## 🧪 테스트 방법

```bash
# 업로드 없이 테스트
python main.py --test

# 스케줄러 테스트 (1회 실행)
python scheduler.py --run-once

# 스케줄 확인만
python scheduler.py --dry-run

# 실제 업로드 활성화
python scheduler.py --enable-upload --run-once
```

---

## ⚠️ 주의사항

1. **API 할당량**: YouTube Data API는 일일 할당량이 있습니다 (10,000 단위)
2. **업로드 제한**: 하루에 너무 많은 영상을 올리면 스팸으로 간주될 수 있습니다
3. **토큰 갱신**: OAuth 토큰은 자동으로 갱신되지만, 가끔 재인증이 필요할 수 있습니다
4. **콘텐츠 정책**: YouTube 커뮤니티 가이드라인을 준수하세요

---

## 🔄 문제 해결

### 인증 오류
```bash
# 인증 파일 삭제 후 재인증
rm config/youtube_credentials.json
python -c "from scripts.youtube_uploader import YouTubeUploader; YouTubeUploader().authenticate()"
```

### API 할당량 초과
- 다음 날까지 대기
- 또는 Google Cloud Console에서 할당량 증가 요청

### 영상 업로드 실패
- `logs/` 폴더의 로그 파일 확인
- 네트워크 연결 확인
- YouTube 계정 상태 확인
