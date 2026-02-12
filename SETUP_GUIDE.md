# YouTube 자동 업로드 설정 가이드

## 📋 사전 요구사항

1. **Google Cloud 프로젝트** (YouTube Data API v3 활성화)
2. **OAuth 2.0 클라이언트 ID** (데스크톱 앱)
3. **YouTube 채널** (업로드 권한 필요)

---

## 🔧 1단계: Google Cloud 프로젝트 설정

### 1.1 프로젝트 생성
1. [Google Cloud Console](https://---

## 🚀 실전 운영 시작하기

### 🎯 여러 채널에 업로드하기 (채널 선택)

2개 이상의 YouTube 채널이 있다면:

#### 📌 채널 ID 찾기 (추천)

1. **YouTube Studio** 방문
   https://youtube.com/studio

2. 좌측 메뉴 → **설정** → **채널 정보** 클릭

3. **채널 ID** 찾기
   ```
   형식: UC로 시작하는 24자 코드
   예: UCxxxxxxxxxxxxxxxx
   ```

4. 모든 채널에 대해 1-3 반복 (채널마다 다른 ID)

#### 설정 방법

**config.json 수정:**
```bash
vim config/config.json
# 또는
code config/config.json
```

원하는 채널의 ID를 입력:
```json
"youtube": {
    "client_secrets_file": "config/client_secrets.json",
    "credentials_file": "config/youtube_credentials.json",
    "target_channel_id": "UCxxxxxxxxxxxxxxxx"  // ← 여기에 채널 ID 입력
}
```

**저장 후 GitHub 푸시:**
```bash
git add config/config.json
git commit -m "Set target YouTube channel: [채널 이름]"
git push
```

**채널 변경하려면:**
- `target_channel_id` 값만 바꾼 후 다시 push하면 됨
- 각 채널별로 다른 `config.json` 파일을 사용하려면 GitHub에서 별도 branch 생성 가능

---

### 1단계: 로컬에서 최종 테스트le.cloud.google.com/) 접속
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

⚠️ **중요: 반드시 Private 저장소로 생성하세요!**
- API 키와 인증 정보가 포함되어 있으므로 절대 Public으로 하면 안됩니다

1. GitHub에서 새 저장소 생성
   - Repository name: `youtube-automation`
   - **Visibility: Private** ✅
   - "Create repository" 클릭

2. 로컬에서 push
```bash
cd /Users/minsu/Downloads/youtube-automation

# .gitignore에 민감한 파일이 포함되어 있는지 확인
cat .gitignore

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/youtube-automation.git
git push -u origin main
```

### 4.2 GitHub Secrets 설정

GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

다음 시크릿을 하나씩 추가:

#### Secret 1: GEMINI_API_KEY
```
Name: GEMINI_API_KEY
Secret: ***REMOVED***
```

#### Secret 2: YOUTUBE_CLIENT_SECRETS
```bash
# 파일 내용 복사
cat config/client_secrets.json
```
복사한 JSON 전체를 Secret 값으로 붙여넣기

#### Secret 3: YOUTUBE_CREDENTIALS
```bash
# 파일 내용 복사
cat config/youtube_credentials.json
```
복사한 JSON 전체를 Secret 값으로 붙여넣기

#### Secret 4: PEXELS_API_KEY
```
Name: PEXELS_API_KEY
Secret: ***REMOVED***
```

### 4.3 워크플로우 확인

push 후 GitHub 저장소에서:
1. **Actions** 탭 클릭
2. 워크플로우가 보이면 정상
3. "I understand my workflows, go ahead and enable them" 버튼이 보이면 클릭
   - (이 버튼은 첫 push 후에만 나타나며, 안 보이면 이미 활성화된 것)

### 4.4 자동 업로드 활성화

GitHub Actions가 설정되면 **자동으로 스케줄대로 실행**됩니다!

#### 현재 상태 확인
```bash
# config.json에서 upload_enabled 확인
cat config/config.json | grep upload_enabled
```

#### 실제 업로드 활성화 (테스트 완료 후)
```bash
# config.json 수정
# "upload_enabled": false → true 로 변경
```

또는 직접 수정:
```json
"scheduler": {
    "upload_enabled": true,  // false → true로 변경
    "weekday_times": ["07:00", "12:00", "18:00", "22:00"],
    "weekend_times": ["09:00", "12:00", "15:00", "18:00", "22:00"]
}
```

수정 후 GitHub에 push:
```bash
git add config/config.json
git commit -m "Enable YouTube upload"
git push
```

#### 🎯 자동화 동작 방식

**GitHub Actions가 자동으로:**
1. ⏰ **스케줄대로 실행** (월-금 4회, 토-일 5회)
2. 📝 **스크립트 자동 생성** (Gemini AI)
3. 🎤 **음성 자동 생성** (Edge TTS)
4. 🎬 **비디오 자동 생성** (배경+자막)
5. 📤 **YouTube 자동 업로드** (upload_enabled: true일 때)

#### 확인 방법
- GitHub 저장소 → **Actions** 탭
- 각 실행 결과 확인 가능
- 생성된 비디오는 Artifacts에 저장됨

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

## � 실전 운영 시작하기

### 1단계: 로컬에서 최종 테스트

```bash
cd /Users/minsu/Downloads/youtube-automation
source venv/bin/activate

# 1. 업로드 없이 비디오만 생성 테스트
python main.py --test

# 2. 생성된 비디오 확인
open output/videos/video_*.mp4

# 3. 실제 YouTube 업로드 테스트 (1개만)
# config.json에서 upload_enabled: true로 변경 후
python main.py
```

### 2단계: GitHub에서 자동화 활성화

#### 2.1 config.json 수정
```bash
# upload_enabled를 true로 변경
vim config/config.json
# 또는
code config/config.json
```

```json
"scheduler": {
    "upload_enabled": true,  // ← 여기를 true로
    "weekday_times": ["07:00", "12:00", "18:00", "22:00"],
    "weekend_times": ["09:00", "12:00", "15:00", "18:00", "22:00"]
}
```

#### 2.2 GitHub에 push
```bash
git add config/config.json
git commit -m "Enable automatic YouTube upload"
git push
```

#### 2.3 GitHub Actions 확인
1. GitHub 저장소 → **Actions** 탭
2. 다음 실행 시간 확인
3. 실행 결과 로그 확인

### 3단계: 모니터링

#### GitHub Actions에서 확인
- **Actions** 탭 → 각 워크플로우 실행 클릭
- 로그에서 성공/실패 확인
- Artifacts에서 생성된 비디오 다운로드 가능

#### YouTube에서 확인
- YouTube Studio → 콘텐츠
- 업로드된 영상 확인
- 조회수, 댓글 등 모니터링

### 4단계: 스케줄 조정 (선택사항)

스케줄을 변경하려면:

```bash
# config.json 수정
vim config/config.json
```

```json
"scheduler": {
    "upload_enabled": true,
    "weekday_times": ["08:00", "14:00", "20:00"],  // 원하는 시간으로
    "weekend_times": ["10:00", "16:00", "22:00"]   // 변경 가능
}
```

```bash
git add config/config.json
git commit -m "Update schedule times"
git push
```

또는 `.github/workflows/youtube-automation.yml` 수정:
```yaml
on:
  schedule:
    - cron: '0 23 * * 0-4'  # 월-금 08:00 KST
    - cron: '0 5 * * 0-4'   # 월-금 14:00 KST
    # ... 원하는 cron 추가
```

---

## �📅 스케줄 요약

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
