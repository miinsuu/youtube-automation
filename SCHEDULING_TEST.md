# 🕐 스케줄링 테스트 (오전 1시 20분)

## 📋 개요

YouTube 쇼츠 자동 제작 시스템의 **GitHub Actions 스케줄링** 테스트입니다.
**매일 자동으로** 오전 1시 20분(KST)에 1개의 영상을 생성하고 업로드합니다.

---

## ⏰ 스케줄 설정

### 🔥 메인 스케줄 (매일 자동실행)
- **실행 시간**: 매일 **오전 1시 20분 (KST)**
- **UTC 시간**: 매일 **오후 4시 20분 (UTC 16:20, 전날)**
- **Cron 표현식**: `20 16 * * *`
- **빈도**: 매일 자동 실행 ✅
- **수동 개입 필요**: **없음** (완전 자동)
- **테스트 규모**: 1개 영상 생성 및 업로드

### 📅 추가 스케줄 (연간 1회)
- **실행 시간**: 매년 **2월 12일 오전 12시 40분 (KST)**
- **UTC 시간**: 매년 **2월 12일 오후 3시 40분 (UTC 15:40, 전날)**
- **Cron 표현식**: `40 15 12 2 *`
- **빈도**: 연간 1회만 자동 실행
- **목적**: 연간 신뢰성 테스트
- **테스트 규모**: 1개 영상 생성 및 업로드

---

## 🔐 자동실행 vs 수동실행

### ✅ 자동실행 (스케줄대로)
```yaml
on:
  schedule:
    - cron: '20 16 * * *'  # ← 이것만으로 자동 실행됩니다!
```

**특징:**
- ✅ 수동 개입 불필요
- ✅ 설정 후 자동으로 지정된 시간에 실행
- ✅ GitHub Actions가 자동으로 트리거
- ✅ 저장소에 푸시만 하면 활성화
- ⏳ 첫 실행 시간까지 대기

### 🖱️ 수동실행 (Run workflow)
```yaml
on:
  ...
  workflow_dispatch:  # ← 수동 실행 기능
```

**특징:**
- 🖱️ GitHub 웹에서 수동으로 "Run workflow" 클릭
- 💡 스케줄과 무관하게 언제든 실행 가능
- 🔄 테스트/디버깅할 때 유용
- ⚡ 즉시 실행 (클릭 후 1-2초 안에 시작)

---

## 📊 타임존 변환

| 지역 | 시간 | 설명 |
|------|------|------|
| **KST (한국)** | 🌅 오전 1:20 | ← 원하는 시간 |
| **UTC** | 🌆 오후 4:20 (전날) | GitHub Actions 서버 시간 |
| **EST (미국 동부)** | 🌃 오후 11:20 (전날) | 참고용 |
| **PST (미국 서부)** | 🌌 오전 8:20 (전날) | 참고용 |

---

## 🚀 작동 흐름

### 자동실행 시 프로세스
```
GitHub Actions 자동 트리거 (매일 KST 01:20)
    ↓
Python 3.12 환경 설정
    ↓
FFmpeg, 한글 폰트 자동 설치
    ↓
의존성 자동 설치
    ↓
스크립트 생성 (Gemini 2.5 Flash)
    ↓
음성 생성 (Edge TTS)
    ↓
비디오 생성 (MoviePy)
    ↓
YouTube 업로드 (채널 자동 검증)
    ↓
로그 저장
```

### 환경 변수
```yaml
UPLOAD_ENABLED: true      # 실제 업로드 활성화
VIDEO_COUNT: 1            # 1개 영상만 생성
TEST_MODE: false          # 실제 모드 (테스트 스킵)
```

### 처리 순서
1. ✅ Python 3.12 설정
2. ✅ FFmpeg 및 한글 폰트 설치
3. ✅ 의존성 설치 (pip install -r requirements.txt)
4. ✅ 스크립트 생성
5. ✅ 음성 생성
6. ✅ 비디오 생성
7. ✅ YouTube 업로드
8. ✅ 로그 생성

### 결과 저장
```
output/
├─ videos/          # 생성된 영상
├─ audio/           # 음성 파일
├─ images/          # 배경 이미지
└─ script_*.json    # 스크립트 데이터

logs/
└─ log_*.json       # 실행 로그
```

---

## 📈 모니터링 및 확인

### GitHub Actions 상태 확인
1. 저장소 접속: https://github.com/miinsuu/youtube-automation
2. **Actions** 탭 클릭
3. **"Test Schedule - Auto Run at 00:40 KST"** 워크플로우 선택
4. 최근 실행 결과 확인
   - ✅ 초록색 체크마크 = 성공
   - ❌ 빨간색 X = 실패
   - ⏳ 노란색 동그라미 = 실행 중

### YouTube 채널 확인
- 업로드된 새 영상 자동 확인
- 제목: `[AUTO] YYYY-MM-DD HH:MM 자동 생성 영상` (또는 설정된 제목)
- 설명: 자동 생성 영상임을 명시

### 로컬에서 로그 확인
```bash
# 최신 로그 확인
tail -f logs/log_*.json

# 모든 로그 목록
ls -lh logs/
```

### GitHub Actions 로그 상세 확인
1. Actions 탭 > 워크플로우 선택
2. 최신 실행 > "test-schedule" 클릭
3. 각 단계별 로그 확인
4. 오류 메시지 상세 조회

---

## 🔄 수동 실행 방법

### 1️⃣ GitHub 웹에서 수동 실행
```
1. GitHub 저장소 접속
2. Actions 탭 클릭
3. "Test Schedule - Auto Run at 00:40 KST" 선택
4. "Run workflow" 버튼 클릭 (우측 상단)
5. 브랜치 선택 (main 권장)
6. "Run workflow" 클릭 ✅
→ 1-2초 후 실행 시작
```

### 2️⃣ 터미널에서 로컬 테스트
```bash
# 1개 영상 생성 (업로드 포함)
python main.py --count 1

# 1개 영상 생성 (업로드 미포함 - 테스트용)
python main.py --count 1 --no-upload

# 로그 확인
tail -f logs/log_*.json
```

---

## 🔐 필수 요구사항

### GitHub 저장소 설정
- ✅ 공개 저장소 (또는 private도 가능)
- ✅ GitHub Actions 활성화
- ✅ 워크플로우 파일 존재

### config.json 설정
- ✅ `gemini_api_key` 설정됨
- ✅ `youtube.client_secrets_file` 설정됨
- ✅ `youtube.credentials_file` 설정됨
- ✅ `youtube.target_channel_id` 설정됨

### GitHub Actions Secrets (필요시)
환경 변수로 민감한 정보 관리 시:
- `GEMINI_API_KEY`
- `YOUTUBE_CREDENTIALS`

---

## ⚠️ 주의사항

### 첫 실행 시
- ⏳ 첫 번째 자동 실행까지 대기 필요
- 🕐 스케줄 설정 후 다음 지정 시간에 자동 실행
- 💡 기다리는 동안 "Run workflow"로 수동 테스트 가능

### API 할당량 관리
- 📊 매일 실행되므로 API 할당량 모니터링 필수
- 🔍 Gemini API 콘솔에서 할당량 확인
- 📈 YouTube API 할당량 체크

### 권한 갱신
- 🔐 90일마다 YouTube 자격증명 갱신 필요
- ⏰ 자격증명 만료 전에 재인증
- 🔔 만료 예정 알림 설정 권장

### 오류 모니터링
- 📝 GitHub Actions 로그 정기 확인
- 🔴 실패 시 즉시 확인 및 수정
- 📧 메일 알림 설정 (GitHub Actions 설정에서)

---

## 🔄 스케줄 변경 방법

### 시간만 변경 (매일 실행)
```yaml
# .github/workflows/test-schedule.yml
- cron: 'MM HH * * *'  # MM = 분, HH = 시간 (UTC)

예시:
- cron: '20 16 * * *'  # 매일 UTC 16:20 (KST 01:20)
- cron: '0 6 * * *'    # 매일 UTC 06:00 (KST 15:00)
- cron: '30 8 * * *'   # 매일 UTC 08:30 (KST 17:30)
```

### 요일별로 실행
```yaml
- cron: '20 16 * * 1-5'  # 월~금요일만 (UTC)
- cron: '20 16 * * 0,6'  # 토요일, 일요일만 (UTC)
- cron: '20 16 * * 0'    # 일요일만 (UTC)
```

### 특정 날짜만 실행
```yaml
- cron: '20 16 15 * *'   # 매월 15일 UTC 16:20
- cron: '20 16 1 1 *'    # 매년 1월 1일 UTC 16:20
- cron: '20 16 12 2 *'   # 매년 2월 12일 UTC 16:20
```

### 시간대 변환 팁
```
원하는 KST 시간 - 9시간 = UTC 시간

예시:
KST 18:00 - 9:00 = UTC 09:00
KST 15:00 - 9:00 = UTC 06:00
KST 22:00 - 9:00 = UTC 13:00
KST 23:00 - 9:00 = UTC 14:00
KST 00:40 - 9:00 = UTC 15:40 (전날)
KST 01:20 - 9:00 = UTC 16:20 (전날)
```

---

## ✅ 체크리스트

### 설정 확인
- [ ] `.github/workflows/test-schedule.yml` 파일 존재
- [ ] `on: schedule:` 섹션에 cron 설정 있음
- [ ] config.json에 API 키 설정됨
- [ ] YouTube 자격증명 파일 존재

### 실행 확인
- [ ] GitHub Actions 탭에서 워크플로우 확인
- [ ] "Run workflow" 수동 실행 테스트 (선택)
- [ ] 로그 확인
- [ ] YouTube 채널에서 영상 확인

### 모니터링 설정
- [ ] GitHub Actions 실패 알림 설정 (선택)
- [ ] API 할당량 모니터링 시작
- [ ] 로그 저장소 정리 계획

---

## 📞 문제 해결

### Q: 스케줄이 실행되지 않음
**A:**
```
확인사항:
1. GitHub Actions 메뉴에서 워크플로우 활성화 확인
2. Repository > Settings > Actions > General
   → "Allow all actions and reusable workflows" 확인
3. 저장소 Settings > Workflows 권한 확인
4. Cron 문법 검증: https://crontab.guru/ 확인
```

### Q: 업로드 실패
**A:**
```
확인사항:
1. YouTube 자격증명 갱신 (90일 만료)
2. API 할당량 확인
3. 채널 권한 확인
4. logs/log_*.json에서 오류 메시지 확인
5. 인증 파일 삭제 후 재인증
```

### Q: 음성/영상 생성 실패
**A:**
```
확인사항:
1. Gemini API 키 확인
2. FFmpeg 설치 확인 (GitHub Actions에서는 자동)
3. 한글 폰트 설치 확인
4. 로그에서 상세 오류 메시지 확인
```

### Q: 언제부터 자동 실행되나요?
**A:**
```
✅ 설정 후 즉시 활성화
- 워크플로우 파일을 저장소에 푸시하면
- GitHub Actions가 즉시 감시 시작
- 다음 스케줄 시간에 자동 실행
```

---

## 📞 지원

문제 발생 시:
1. GitHub Issues에 문제 보고
2. 로그 파일 첨부 (`logs/log_*.json`)
3. 타임존 정보 포함
4. 예상 vs 실제 결과 비교

---

**마지막 업데이트**: 2026년 2월 13일  
**상태**: ✅ 활성화  
**자동실행**: ✅ 매일 오전 1시 20분 (KST)  
**수동실행**: ✅ "Run workflow" 언제든 가능

---

## ⏰ 스케줄 설정

### 메인 테스트 스케줄
- **실행 시간**: 매일 **오전 1시 20분 (KST)**
- **UTC 시간**: 매일 **오후 4시 20분 (UTC 16:20, 전날)**
- **Cron 표현식**: `20 16 * * *`
- **빈도**: 매일 자동 실행
- **테스트 규모**: 1개 영상 생성 및 업로드

### 추가 테스트 (연간)
- **실행 시간**: 매년 **2월 12일 오전 12시 40분 (KST)**
- **UTC 시간**: 매년 **2월 12일 오후 3시 40분 (UTC 15:40, 전날)**
- **Cron 표현식**: `40 15 12 2 *`
- **빈도**: 연간 1회만 실행
- **테스트 규모**: 1개 영상 생성 및 업로드

---

## 🔧 설정 파일 위치

### GitHub Actions 워크플로우
```
.github/workflows/test-schedule.yml
```

### 설정 파일
```
config/config.json
  ├─ scheduler.enabled: true (스케줄러 활성화)
  ├─ scheduler.upload_enabled: true (업로드 활성화)
  └─ scheduler.test_schedules: 테스트 스케줄 정보
```

---

## 📊 테스트 데이터 상세

### 타임존 변환 참고

| 지역 | 시간 | 상태 |
|------|------|------|
| **KST (한국)** | 오전 1:20 | ✅ 실행 시작 |
| **UTC** | 오후 4:20 (전날) | ⏳ GitHub Actions 서버 실행 |
| **EST (미국 동부)** | 오후 11:20 (전날) | 📍 참고용 |
| **PST (미국 서부)** | 오전 8:20 (전날) | 📍 참고용 |

---

## 🚀 작동 흐름

### 1️⃣ GitHub Actions 트리거 (KST 01:20)
```
매일 자동으로 워크플로우 시작
↓
```

### 2️⃣ 환경 설정
```yaml
UPLOAD_ENABLED: true      # 실제 업로드 활성화
VIDEO_COUNT: 1            # 1개 영상만 생성
TEST_MODE: false          # 실제 모드 (테스트 스킵 가능)
```

### 3️⃣ 처리 단계
- ✅ Python 3.12 설정
- ✅ FFmpeg 및 한글 폰트 설치
- ✅ 의존성 설치
- ✅ 스크립트 생성 (Gemini 2.5 Flash)
- ✅ 음성 생성 (Edge TTS)
- ✅ 비디오 생성 (MoviePy)
- ✅ YouTube 업로드 (채널 자동 검증)
- ✅ 로그 생성

### 4️⃣ 결과 저장
```
output/
├─ videos/          # 생성된 영상
├─ audio/           # 음성 파일
├─ images/          # 배경 이미지
└─ script_*.json    # 스크립트 데이터

logs/
└─ log_*.json       # 실행 로그
```

---

## 📈 모니터링

### GitHub Actions 상태 확인
1. 저장소의 **Actions** 탭 클릭
2. **"Test Schedule - Auto Run at 00:40 KST"** 워크플로우 선택
3. 최근 실행 결과 확인

### 업로드 확인
- YouTube 채널에서 새로운 영상 확인
- 제목: `[AUTO] YYYY-MM-DD HH:MM 자동 생성 영상`
- 설명: 자동 생성 영상임을 명시

### 로그 확인
```bash
# 로컬 테스트
tail -f logs/log_*.json

# GitHub Actions 로그
- 워크플로우 실행 > 해당 Job 클릭 > 로그 확인
```

---

## 🔐 필수 요구사항

### GitHub Actions Secrets
- `GEMINI_API_KEY` ✅ (설정됨)
- `YOUTUBE_CLIENT_SECRETS` ✅ (설정됨)
- `YOUTUBE_CREDENTIALS` ✅ (설정됨)

### config.json
- `gemini_api_key` 설정됨
- `youtube.client_secrets_file` 설정됨
- `youtube.credentials_file` 설정됨
- `youtube.target_channel_id` 설정됨

---

## 🔄 수동 실행

### 1️⃣ GitHub 웹에서 수동 실행
```
Actions > Test Schedule - Auto Run at 00:40 KST > Run workflow
```

### 2️⃣ 터미널에서 로컬 테스트
```bash
# 1개 영상 생성 (업로드 포함)
python main.py --count 1

# 1개 영상 생성 (업로드 미포함 - 테스트용)
python main.py --count 1 --no-upload
```

---

## ⚠️ 주의사항

### 테스트 실행 시 고려사항
1. **API 할당량**: 매일 실행되므로 Gemini/YouTube API 할당량 모니터링
2. **YouTube 제한**: 신채널은 초기 제한이 있을 수 있음
3. **권한 갱신**: 90일마다 YouTube 자격증명 갱신 필요
4. **오류 추적**: GitHub Actions 로그에서 모든 오류 기록

### 비용 고려
- **Gemini API**: 일부 할당량 무료 (모니터링 필요)
- **YouTube API**: 무료 (할당량 제한 있음)
- **GitHub Actions**: 무료 (공개 저장소는 무한)

---

## 📝 문제 해결

### 스케줄이 실행되지 않음
```
해결책:
1. GitHub Actions 메뉴에서 워크플로우 활성화 확인
2. Cron 문법 검증: https://crontab.guru/
3. Repository Settings > Actions > General > Allow all actions and reusable workflows 확인
```

### 업로드 실패
```
해결책:
1. YouTube 자격증명 갱신 (90일 만료)
2. API 할당량 확인
3. 채널 권한 확인
4. logs/log_*.json에서 오류 메시지 확인
```

### 음성/영상 생성 실패
```
해결책:
1. Gemini API 키 확인
2. FFmpeg 설치 확인 (GitHub Actions에서는 자동 설치)
3. 한글 폰트 설치 확인
4. 로그에서 상세 오류 메시지 확인
```

---

## 📅 스케줄 변경 방법

### 시간 변경
```yaml
# .github/workflows/test-schedule.yml
- cron: 'MM HH * * *'  # MM = 분, HH = 시간 (UTC)

예시:
- cron: '20 16 * * *'  # 매일 UTC 16:20 (KST 01:20)
- cron: '0 6 * * *'    # 매일 UTC 06:00 (KST 15:00)
```

### 요일별 실행
```yaml
- cron: '20 16 * * 1-5'  # 월~금요일만 (UTC)
- cron: '20 16 * * 0,6'  # 주말만 (UTC)
```

### 시간대 변환 팁
```
원하는 KST 시간 - 9시간 = UTC 시간
예: KST 18:00 - 9:00 = UTC 09:00
```

---

## 📞 지원

문제 발생 시:
1. GitHub Issues에 문제 보고
2. 로그 파일 첨부
3. 타임존 정보 포함
4. 예상 vs 실제 결과 비교

---

**마지막 업데이트**: 2026년 2월 13일  
**상태**: ✅ 활성화  
**테스트 빈도**: 매일 오전 1시 20분 (KST)
