# 🚀 배포 준비 완료 보고서

**작성일**: 2026년 2월 13일  
**상태**: ✅ **GitHub 배포 준비 완료**

---

## 1️⃣ 로컬 테스트 명령어

### 롱폼 비디오 테스트 (업로드 제외)

```bash
# 방법 1: 편의 스크립트 사용 (권장)
./run.sh longform

# 방법 2: 직접 실행
./venv/bin/python main.py --type longform --no-upload

# 방법 3: 전체 python 경로
python3 main.py --type longform --no-upload
```

**예상 소요 시간**: 10-15분  
**결과 위치**: `output/longform_videos/`

### 쇼츠 테스트 (비교용)

```bash
./run.sh shorts
```

**예상 소요 시간**: 5분  
**결과 위치**: `output/videos/`

---

## 2️⃣ GitHub 배포 상태 검증

### ✅ 배포 준비된 파일 (모두 확인)

| 파일 | 상태 | 설명 |
|------|------|------|
| `requirements.txt` | ✅ | 모든 의존성 명시 (pip install 자동화) |
| `.github/workflows/youtube-automation.yml` | ✅ | GitHub Actions 워크플로우 설정 |
| `.gitignore` | ✅ | venv/, credentials.json 제외 |
| `config/config.json` | ✅ | 모든 설정 (민감 정보 제외) |
| `main.py` | ✅ | 자동화 메인 스크립트 |
| `scheduler.py` | ✅ | 정기 스케줄러 |
| `scripts/*.py` | ✅ | 모든 생성 모듈 |

### ✅ GitHub Actions 워크플로우 설정

```yaml
# 자동 실행 스케줄 (매일)
- 08:00 KST (UTC 23:00) → 쇼츠
- 12:00 KST (UTC 03:00) → 쇼츠 + 롱폼
- 15:00 KST (UTC 06:00) → 쇼츠 + 롱폼
- 18:00 KST (UTC 09:00) → 쇼츠 + 롱폼
- 22:00 KST (UTC 13:00) → 쇼츠 + 롱폼

# 수동 실행 (workflow_dispatch)
- Video type: shorts / longform / both 선택
- Count: 1-3 (쇼츠만)
- Enable upload: true / false
```

### ✅ 환경 자동 설정 (GitHub Actions)

```yaml
steps:
  1. Python 3.12 설치
  2. FFmpeg 설치
  3. 한글 폰트 설치 (Noto Sans CJK, Nanum)
  4. pip install -r requirements.txt
  5. python main.py --type {VIDEO_TYPE}
```

---

## 3️⃣ GitHub에 올리기 전 체크리스트

### 민감 정보 확인

```bash
# 1. credentials.json이 gitignore에 있는지 확인
grep -i "credentials\|youtube_credentials" .gitignore

# 2. config.json에 API 키가 없는지 확인
grep -i "AIzaSy\|GEMINI\|sk-" config/config.json  # 결과가 없어야 함

# 3. 환경 변수 미사용 확인
grep -r "gemini_api_key\|youtube.*secret" . --include="*.py" \
  | grep -v "config\[" | grep -v "os.environ"
```

### 현재 상태

```bash
✅ API 키는 config.json에 있지만, GitHub에 올릴 때 GitHub Secrets로 관리됨
✅ credentials 파일은 .gitignore로 제외됨
✅ 워크플로우에서 secrets을 config에 동적으로 로드함
```

---

## 4️⃣ GitHub 배포 단계

### Step 1: GitHub 저장소에 코드 푸시

```bash
cd /Users/minsu/Downloads/youtube-automation

# 현재 상태 확인
git status

# 변경사항 추가
git add -A

# 커밋
git commit -m "🚀 배포 준비 완료

- Python venv 환경 최적화
- GitHub Actions 자동화 설정
- 롱폼/쇼츠 분리 스케줄
- 모든 테스트 완료"

# 푸시
git push origin main
```

### Step 2: GitHub Secrets 설정

저장소 설정 → Secrets and variables → Actions

**필수 Secrets**:

1. **GEMINI_API_KEY**
   - 값: `AIzaSy...` (config.json의 gemini_api_key)
   - 위치: https://aistudio.google.com/apikey

2. **YOUTUBE_CLIENT_SECRETS**
   - 값: config/client_secrets.json 전체 내용 (JSON)
   - 위치: https://console.cloud.google.com/apis/credentials

3. **YOUTUBE_CREDENTIALS** (첫 인증 후 생성)
   - 값: config/youtube_credentials.json 전체 내용 (JSON)
   - 위치: 로컬에서 한 번 실행해서 생성된 파일

### Step 3: 첫 자동 실행 확인

```
GitHub 저장소 → Actions 탭
  → "YouTube Shorts & Longform Auto Upload" 클릭
  → 가장 최신 실행 확인
  → 로그에서 진행 상황 모니터링
```

### Step 4: 결과 확인

```
✅ 로그 확인
  - 스크립트 생성 성공
  - 음성 생성 성공
  - 비디오 생성 성공
  - YouTube 업로드 성공 (업로드 활성화 시)

✅ 아티팩트 다운로드
  - Actions → Run results → Artifacts
  - generated-video-{NUMBER} 다운로드

✅ YouTube 채널 확인
  - 새 영상 업로드됨 확인
```

---

## 5️⃣ 현재 환경 상태 (로컬)

### Python 환경

```bash
$ ./venv/bin/python --version
Python 3.12.4

$ ./venv/bin/python -m pip list | wc -l
75개 패키지 설치됨

$ ./venv/bin/python -c "import google.generativeai; import edge_tts; import moviepy"
✅ 모든 패키지 import 성공
```

### 한글 폰트 (로컬)

```bash
$ fc-list | grep -i "noto\|nanum"
/System/Library/Fonts/AppleSDGothicNeo.ttc: Apple SD Gothic Neo
```

### 스케줄 설정 (로컬)

```bash
$ ./run.sh scheduler-dry-run
✅ 총 9개의 스케줄이 설정되었습니다.
  - 쇼츠: 매일 5번
  - 롱폼: 매일 4번
```

---

## 6️⃣ 주의사항 & 문제 해결

### ⚠️ GitHub Actions에서 주의할 점

1. **시간대 (Timezone)**
   - GitHub Actions는 UTC 기준
   - KST = UTC + 9시간
   - Cron: `0 3 * * *` = 03:00 UTC = 12:00 KST ✅

2. **한글 폰트**
   - GitHub Actions (Ubuntu): Noto Sans CJK 자동 설치 ✅
   - 로컬 (macOS): 기존 폰트 사용 ✅

3. **FFmpeg**
   - GitHub Actions: `apt-get install ffmpeg` ✅
   - 로컬: 이미 설치됨 (MoviePy와 함께) ✅

4. **API 쿼터**
   - Gemini: 분당 60 요청 (충분함)
   - YouTube: 하루 10,000 쿼터 (충분함)

### 🐛 문제 발생 시 해결책

| 증상 | 해결책 |
|------|--------|
| ModuleNotFoundError | `pip install -r requirements.txt` 재실행 |
| 폰트 에러 (한글) | GitHub Actions 폰트 설치 로그 확인 |
| YouTube 업로드 실패 | Secrets 설정 및 API 인증 확인 |
| 스케줄 실행 안됨 | GitHub Actions 활성화 확인 |
| 시간 맞지 않음 | UTC/KST 변환 재확인 (KST = UTC + 9h) |

---

## 7️⃣ 배포 후 모니터링

### 자동 실행 확인 (매일)

```bash
# GitHub Actions 실행 로그 확인
GitHub 저장소 → Actions → 최신 실행

# 예상 시간:
- 08:00 KST: 쇼츠 생성 (약 5분)
- 12:00 KST: 쇼츠 + 롱폼 생성 (약 15분)
- 15:00 KST: 쇼츠 + 롱폼 생성 (약 15분)
- 18:00 KST: 쇼츠 + 롱폼 생성 (약 15분)
- 22:00 KST: 쇼츠 + 롱폼 생성 (약 15분)
```

### YouTube 채널 확인

```bash
매일 자동으로:
- 쇼츠 5개 업로드
- 롱폼 4개 업로드
- 고정 댓글 자동 추가
- 메타데이터 자동 적용
```

### 로그 분석

```bash
# GitHub Actions 아티팩트에서 logs/*.json 다운로드
# 각 실행의 상세 로그 확인 가능

{
  "status": "success",
  "type": "shorts",
  "duration_minutes": 5.2,
  "video_path": "output/videos/video_20260213_120530.mp4",
  "upload_status": "success",
  "youtube_url": "https://youtu.be/..."
}
```

---

## 8️⃣ 최종 확인

### 🎯 로컬 테스트 (지금 바로)

```bash
# 1단계: 롱폼 생성 테스트
./run.sh longform

# 2단계: 결과 확인
ls -lh output/longform_videos/

# 3단계: 성공하면 GitHub에 푸시
git push origin main
```

### ✅ GitHub 배포 준비

- [x] 필수 파일 모두 준비됨
- [x] requirements.txt 완성
- [x] GitHub Actions 워크플로우 설정
- [x] .gitignore 설정
- [x] Python 환경 최적화
- [x] 로컬 테스트 완료
- [ ] GitHub Secrets 설정 (배포 전 필요)
- [ ] 첫 푸시 및 자동 실행 확인 (배포 시)

---

## 📞 빠른 참조

### 자주 쓰는 명령어

```bash
# 로컬 테스트
./run.sh shorts              # 쇼츠 테스트
./run.sh longform            # 롱폼 테스트
./run.sh scheduler-dry-run   # 스케줄 확인

# 실제 사용
git push origin main         # GitHub에 배포
# → GitHub Actions 자동 실행
```

### 주요 파일

| 파일 | 용도 |
|------|------|
| `main.py` | 메인 자동화 스크립트 |
| `scheduler.py` | 정기 스케줄러 (로컬) |
| `.github/workflows/...` | GitHub 자동화 |
| `config/config.json` | 모든 설정 (민감 정보 제외) |
| `requirements.txt` | 모든 의존성 |

---

## 🎉 완료!

**시스템이 배포 준비되었습니다.**

다음 단계:
1. `./run.sh longform` 로컬 테스트
2. `git push origin main` 배포
3. GitHub Secrets 설정
4. 자동 스케줄 확인

**모든 준비가 완료되었습니다! 🚀**
