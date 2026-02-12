# 🧪 GitHub Actions 워크플로우 테스트 가이드

## 테스트 워크플로우란?

스케줄 기반 자동 실행이 제대로 작동하는지 확인하기 위한 테스트 워크플로우입니다.

---

## 📋 현재 구성

### 1. **메인 워크플로우** (`.github/workflows/youtube-automation.yml`)
- **목적**: 정기적으로 자동 영상 생성 및 업로드
- **스케줄**: 평일/주말 특정 시간에 자동 실행
- **업로드**: 활성화됨

### 2. **테스트 워크플로우** (`.github/workflows/test-schedule.yml`) ⭐ NEW
- **목적**: 1회성 영상 생성으로 전체 파이프라인 검증
- **실행 방식**: 자동 스케줄링 (오늘 오전 12시 40분)
- **업로드**: 활성화됨
- **영상 개수**: 1개

---

## 🚀 테스트 실행 방법

### **자동 실행 (자동 스케줄링)**

⏰ **실행 시간**: 오늘 오전 12시 40분(KST 00:40)
- **현재 시간 기준**: 약 10분 후 자동 실행
- **실행 위치**: GitHub Actions (자동)
- **별도 조작 불필요**: 시간 되면 자동 시작

#### **모니터링 방법:**

1. **GitHub Actions 페이지 방문**
   ```
   https://github.com/miinsuu/youtube-automation/actions
   ```

2. **"Test Schedule - Auto Run at 00:40 KST" 확인**
   - 워크플로우 목록에서 확인
   - 00:40 시간이 되면 자동으로 실행 시작

3. **실시간 진행 상황 모니터링**
   - 워크플로우 클릭
   - 각 Step별 진행 상황 확인
   - 약 5-10분 소요

---

### **방법 2: GitHub 웹 UI에서 수동 실행 (선택사항)**

시간을 기다리지 않고 즉시 테스트하고 싶다면:

1. **GitHub 저장소 방문**
   ```
   https://github.com/miinsuu/youtube-automation
   ```

2. **Actions 탭 클릭**
   - 상단 메뉴에서 `Actions` 탭 선택

3. **"Test Schedule - Auto Run at 00:40 KST" 선택**
   - 좌측 워크플로우 목록에서 클릭

4. **"Run workflow" 버튼 클릭**
   - 우측 상단의 드롭다운 메뉴
   - "Run workflow" 버튼 클릭
   - main 브랜치 선택 후 실행

5. **즉시 시작**
   - 클릭 후 즉시 실행 시작

---

## 📊 실행 결과 확인

### **성공 여부 확인**

```
✅ 체크마크 = 성공
❌ 엑스마크 = 실패
```

### **생성된 결과물 확인**

1. **"Upload artifacts" 섹션 확인**
   - 워크플로우 상세 페이지 하단
   - `test-video-{run_number}` 다운로드 가능

2. **다운로드 파일**
   ```
   output/
   ├── videos/
   │   └── video_*.mp4         # 생성된 영상
   ├── images/
   │   └── *.png              # 배경 이미지
   └── logs/
       └── log_*.json         # 실행 로그
   ```

### **YouTube 확인**

1. [YouTube 채널](https://www.youtube.com/channel/UC2yneYUgVE2VSzRL4y1Qbdg) 방문
2. 최신 업로드 확인
3. 업로드 시간 = 워크플로우 완료 시간

---

## 🔍 트러블슈팅

### **문제: 워크플로우가 실행되지 않음**

**해결책:**
1. Secrets 설정 확인
   - Settings > Secrets and variables > Actions
   - 다음 항목 확인:
     - `GEMINI_API_KEY`
     - `YOUTUBE_CLIENT_SECRETS`
     - `YOUTUBE_CREDENTIALS`

2. 권한 확인
   - Settings > Actions > General
   - "Workflow permissions" = "Read and write permissions"

### **문제: 워크플로우 실패**

**확인 사항:**
1. 워크플로우 로그 확인
   - 실행 페이지 > 각 Step의 "Run" 섹션
   - 에러 메시지 확인

2. 일반적 원인:
   - API 키 만료
   - YouTube 인증 토큰 만료
   - 네트워크 오류
   - 시스템 리소스 부족

### **문제: 영상이 생성되었는데 업로드가 안 됨**

**확인 사항:**
1. YouTube 인증 토큰 갱신
   ```bash
   rm config/youtube_credentials.json
   python main.py --count 1  # 로컬에서 먼저 테스트
   ```

2. YouTube 채널 확인
   - 영상 업로드 권한 확인
   - 채널 설정 확인

---

## 📅 스케줄 시간 변경

### **테스트 시간 변경하기**

`.github/workflows/test-schedule.yml` 수정:

```yaml
on:
  schedule:
    # cron 형식: minute hour day month dayofweek
    # 예: 매주 월요일 09:00 KST
    - cron: '0 0 * * 1'  # UTC 기준 = KST -9시간
```

**UTC to KST 변환표:**
```
KST 08:00 = UTC 23:00 (전날)
KST 12:00 = UTC 03:00
KST 15:00 = UTC 06:00
KST 18:00 = UTC 09:00
KST 22:00 = UTC 13:00
KST 00:40 = UTC 15:40 (전날)
```

---

## 🔄 원본 워크플로우 (자동 스케줄)

정기적 자동 실행 워크플로우: `.github/workflows/youtube-automation.yml`

**자동 실행 일정:**
- **평일 (월-금)**
  - 08:00, 12:00, 15:00, 18:00, 22:00 KST

- **주말 (토-일)**
  - 09:00, 12:00, 15:00, 18:00, 22:00 KST

---

## ✅ 테스트 체크리스트

테스트 실행 후 다음 항목 확인:

- [ ] 워크플로우 성공 여부 확인
- [ ] 영상 생성 (output/videos/*.mp4)
- [ ] YouTube 채널 업로드 확인
- [ ] 영상 메타데이터 올바른지 확인
- [ ] 한글 자막 정상 표시 여부
- [ ] 음성 생성 정상 여부

---

## 📝 로그 분석

### **로그 파일 위치**
```
logs/log_YYYYMMDD_HHMMSS.json
```

### **확인할 항목**
```json
{
  "status": "completed",
  "video_path": "output/videos/video_*.mp4",
  "upload_status": "success",
  "upload_id": "dQw4w9WgXcQ",
  "timestamp": "2026-02-14T00:40:00"
}
```

---

## 🎯 다음 단계

1. **자동 실행 대기** (오전 12시 40분)
2. **Actions 페이지에서 진행 상황 모니터링**
3. **완료 후 결과 확인** (YouTube 업로드 확인)
4. **필요시 즉시 재테스트** (수동 실행)
5. **프로덕션 배포** (안정성 확인 후)

---

## 📞 도움말

**워크플로우 상태 확인:**
- GitHub Actions 페이지: https://github.com/miinsuu/youtube-automation/actions

**에러 해결:**
- 로그 확인 > 에러 메시지 분석 > 해당 스크립트 수정 > 재테스트

---

**마지막 업데이트:** 2026년 2월 13일
