# 🔧 GitHub Actions 스케줄 자동실행 문제 해결 가이드

## ✅ 단계별 확인 및 수정

### 1️⃣ GitHub 저장소 설정 확인

**설정 경로**: Settings > Actions > General

다음 항목들을 확인하세요:

```
☑️ Actions permissions:
   ○ Allow all actions and reusable workflows
   ○ Allow Microsoft-owned actions and reusable workflows
   ○ Allow Actions by GitHub
   ○ Allow specified actions and reusable workflows
   ✅ 권장: "Allow all actions and reusable workflows" 선택

☑️ Workflow permissions:
   ○ Read and write permissions
   ○ Read-only permissions
   ✅ 권장: "Read and write permissions" 선택

☑️ Default permissions:
   ○ Permissive
   ○ Restrictive
   ✅ 권장: "Permissive" 선택
```

---

### 2️⃣ 워크플로우 파일 확인

**파일 위치**: `.github/workflows/test-schedule.yml`

✅ 다음 항목들이 올바른지 확인:

```yaml
# ✅ schedule 섹션 확인
on:
  schedule:
    - cron: '20 16 * * *'  # 매일 UTC 16:20
  
# ✅ workflow_dispatch 있는지 확인
  workflow_dispatch:

# ✅ jobs 섹션 있는지 확인
jobs:
  test-schedule:
    runs-on: ubuntu-latest
    steps:
      # ... 스텝들
```

---

### 3️⃣ 저장소 분기(Branch) 확인

스케줄은 **기본 분기(main/master)에만 작동**합니다.

```bash
# 현재 분기 확인
git branch

# 기본 분기 확인 (GitHub 웹에서)
Settings > Default branch > main 설정되어 있는지 확인
```

---

### 4️⃣ 워크플로우 활성화 확인

**경로**: Actions 탭 > 워크플로우 선택

```
✅ 워크플로우가 활성화 상태인지 확인
❌ "This workflow is disabled" 메시지 없는지 확인
```

---

### 5️⃣ 최신 커밋이 푸시되었는지 확인

```bash
# 로컬 커밋이 GitHub에 푸시되었는지 확인
git log --oneline -1           # 로컬 최신 커밋
git log --oneline -1 origin    # GitHub 최신 커밋
```

---

## 🚀 즉시 해결 방법

### 방법 1: 워크플로우 파일 재푸시 (권장)

```bash
# 작은 변경사항 추가 및 푸시
git add .github/workflows/test-schedule.yml
git commit --amend --no-edit
git push -f origin main
```

### 방법 2: 워크플로우 비활성화 후 활성화

```
GitHub > Actions 탭
  > 좌측에서 "Test Schedule - Auto Run at 00:40 KST" 클릭
  > "..." 메뉴 > "Enable workflow" 클릭
```

### 방법 3: 새 이벤트 트리거로 테스트

```bash
# 새 커밋 생성 및 푸시
git commit --allow-empty -m "trigger workflow"
git push origin main
```

---

## 🔍 GitHub Actions 실행 로그 확인

### 1. GitHub 웹에서 확인

```
저장소 > Actions 탭
  > 좌측 "Test Schedule - Auto Run at 00:40 KST" 클릭
  > 실행 이력 확인
  > 각 실행 클릭하여 로그 확인
```

### 2. 실행 안 됨 상태 확인

```
- 회색 동그라미: 아직 예약됨
- 노란색 동그라미: 현재 실행 중
- 녹색 체크마크: 성공
- 빨간색 X: 실패
- 아무것도 없음: 아직 스케줄된 시간 도래하지 않음
```

---

## ⚙️ 스케줄이 정확한지 재검증

### 1. Cron 문법 검증

https://crontab.guru 방문

```
field: 20 16 * * *

입력값:
At 16:20 (4:20 PM), every day
```

확인: ✅ 매일 UTC 16:20 = KST 01:20

### 2. 시간대 변환 재확인

```
UTC 16:20 - 9시간 = KST 01:20 ✅

다른 예시:
UTC 16:20 (2월 12일) - 9시간 = KST 01:20 (2월 13일)
→ 정확히 1시간 20분 ✅
```

---

## 🆘 여전히 안 되면 확인할 사항

### 체크리스트

- [ ] Actions 탭에서 워크플로우 보이는지 확인
- [ ] "Allow all actions" 권한 설정 되어 있는지 확인
- [ ] 파일이 main 브랜치에 있는지 확인
- [ ] 최신 푸시가 GitHub에 반영되었는지 확인
- [ ] Cron 문법이 정확한지 확인
- [ ] 워크플로우 파일 들여쓰기 정확한지 확인 (YAML 형식)

### 시간대 확인

```
현재 로컬 시간: KST 1:21
GitHub 서버 시간: UTC 16:21
다음 스케줄 실행 시간: KST 01:20 (다음날)
```

---

## 🔄 강제 트리거로 테스트

즉시 테스트하려면 수동 실행:

```
GitHub > Actions > "Test Schedule - Auto Run at 00:40 KST"
> "Run workflow" 버튼 클릭
> "Run workflow" 확인
```

---

**마지막 업데이트**: 2026년 2월 13일 01:30  
**문제**: GitHub Actions 스케줄 자동실행 안 됨  
**해결**: 저장소 설정 및 워크플로우 재검증
