# 🔧 GitHub Actions Schedule 설정 가이드

GitHub Actions의 schedule이 작동하지 않는 경우를 해결하는 가이드입니다.

---

## ⚠️ 문제: Schedule이 실행되지 않음

"10시를 지났는데 workflow 항목이 없다"는 경우의 원인과 해결방법:

---

## 🔍 원인 진단

### 원인 1: GitHub Actions가 비활성화됨
```
GitHub 저장소 설정에서 Actions가 꺼져있을 수 있습니다.
```

**확인 방법:**
1. GitHub 저장소 열기
2. Settings → Actions → General
3. "Allow all actions and reusable workflows" 선택되어 있는지 확인

### 원인 2: 저장소가 Private
```
Private 저장소에서는 schedule이 제한될 수 있습니다.
(GitHub Pro/Enterprise 필요)
```

### 원인 3: Workflow 파일 경로 오류
```
.github/workflows/ 폴더에 YAML 파일이 있어야 합니다.
```

### 원인 4: Default Branch가 다름
```
Workflow는 Default Branch에서만 실행됩니다.
(보통 main 또는 master)
```

---

## ✅ 해결 방법

### Step 1: Actions 활성화 확인

```
1. GitHub 저장소 열기
2. Settings (우측 상단)
3. "Actions" → "General" 클릭
4. "Actions permissions" 섹션:
   ✓ "Allow all actions and reusable workflows"
   선택되어 있나요?

아니면:
   ✓ "Allow select actions and reusable workflows"
   를 선택하고 "YouTube Shorts Auto Upload" 허용
```

### Step 2: Default Branch 확인

```
1. Settings → "Branches"
2. "Default branch"가 "main"인가요?
3. 아니면 변경하거나 workflow 파일 위치 확인
```

### Step 3: Workflow 파일 확인

```
저장소 구조:
youtube-automation/
├─ .github/
│  └─ workflows/
│     └─ youtube-automation.yml  ✓ 이 파일이 있나요?
```

### Step 4: Workflow 문법 확인

```
GitHub Actions 페이지에서:
1. https://github.com/miinsuu/youtube-automation/actions
2. "Workflows" 왼쪽 사이드바
3. "YouTube Shorts Auto Upload" 클릭
4. 빨간 경고 표시 있나요?
   → 있으면 YAML 문법 오류
```

---

## 🚀 Schedule이 작동하도록 확인하기

### 방법 1: Schedule 상태 확인

```
GitHub Actions 페이지:
https://github.com/miinsuu/youtube-automation/actions

각 workflow 옆에 "🔄" 아이콘이 있으면:
→ Schedule이 설정됨

"Run workflow" 버튼만 있으면:
→ Schedule 미설정 또는 비활성화
```

### 방법 2: 수동 테스트

```
1. GitHub Actions 페이지
2. "YouTube Shorts Auto Upload" 클릭
3. "Run workflow" 버튼 클릭
4. 정상 실행되나요?

되면: Workflow는 정상, schedule 설정 문제
안 되면: Workflow 자체 문제
```

### 방법 3: 강제 실행으로 Schedule 활성화

```
Schedule을 활성화하려면:

1. 한 번 "Run workflow"로 수동 실행
2. 성공적으로 완료될 때까지 기다림
3. 그 후 Schedule 자동 활성화됨
```

---

## 📝 Workflow Schedule 설명

### 현재 설정된 시간

**평일 (월-금):**
```
08:00 KST (23:00 UTC)  - 아침
12:00 KST (03:00 UTC)  - 점심
15:00 KST (06:00 UTC)  - 오후
18:00 KST (09:00 UTC)  - 저녁
22:00 KST (13:00 UTC)  - 밤
```

**주말 (토-일):**
```
09:00 KST (00:00 UTC)  - 아침
12:00 KST (03:00 UTC)  - 점심
15:00 KST (06:00 UTC)  - 오후
18:00 KST (09:00 UTC)  - 저녁
22:00 KST (13:00 UTC)  - 밤
```

### Cron 문법

```
분 시 일 월 요일
0   23  *  *  1-5    = 평일 23:00 (월~금)
0   0   *  *  0,6    = 주말 00:00 (토,일)

요일: 0=일 1=월 2=화 3=수 4=목 5=금 6=토
```

---

## 🔧 수정된 내용

### 이전 (작동 안 함):
```yaml
- cron: '0 23 * * 0-4'  # 0-4 (일~목)
- cron: '0 3 * * 1-5'   # 1-5 (월~금)
```

### 수정 후 (안정적):
```yaml
- cron: '0 23 * * 1-5'  # 1-5 (월~금) ✓
- cron: '0 0 * * 0,6'   # 0,6 (토,일) ✓
```

**왜 수정했나:**
- `0-4`는 일~목 (목까지만)
- `1-5`는 월~금 (월부터)
- 표준 cron은 `0,6`이 더 안정적

---

## ✨ 최종 체크리스트

### GitHub 저장소 설정
- [ ] Settings → Actions → "Allow all actions" 체크됨
- [ ] Default Branch가 "main"
- [ ] `.github/workflows/youtube-automation.yml` 파일 존재

### Workflow 파일
- [ ] YAML 문법 정상 (GitHub Actions에서 경고 없음)
- [ ] `schedule:` 섹션 있음
- [ ] `workflow_dispatch:` 섹션 있음

### 테스트
- [ ] "Run workflow" 버튼으로 수동 실행 성공
- [ ] 약 3-5분 후 완료됨
- [ ] 그 후 자동 schedule 실행 기대

---

## 🎯 자동 Schedule 활성화되는 시점

**GitHub의 자동 Schedule 활성화 조건:**

1. ✅ Workflow 파일이 default branch에 있음
2. ✅ Actions가 활성화됨
3. ✅ 최소 1회 이상 성공적 실행 기록
4. ✅ 저장소가 Public 또는 Pro 구독

**보통 3-24시간 내에 자동 활성화됨**

---

## 🚨 Emergency: 수동 Schedule 설정

만약 자동 schedule이 안 된다면, **매일 수동으로 실행**하세요:

```
매일 08:00 KST에 폰에서:
1. GitHub 저장소 열기
2. Actions → "Run workflow"
3. count: 1, upload: false 선택
4. 실행
```

또는 **다른 automation 도구** 사용:
- IFTTT
- Zapier
- 다른 CI/CD (GitLab CI, Jenkins 등)

---

## 📞 디버깅 팁

### 로그 확인

```
1. GitHub Actions 페이지
2. 최신 실행 항목 클릭
3. "Setup" 스텝 확인
   → 이 부분에서 schedule 정보 표시
```

### GitHub CLI로 확인

```bash
# GitHub CLI 설치 필요
gh auth login
gh workflow list -R miinsuu/youtube-automation
gh workflow view youtube-automation.yml -R miinsuu/youtube-automation
```

### Event 로그

```
Actions 페이지에서:
Filters → "Scheduled" 선택
→ 스케줄된 실행만 표시
```

---

## ✅ 최종 확인

**schedule이 정상 작동하려면:**

1. 저장소 Settings에서 Actions 활성화 ✓
2. Workflow 파일이 main branch에 있음 ✓
3. 최소 1회 수동 실행으로 workflow 활성화 ✓
4. 설정된 시간이 지남 (보통 다음 날) ✓

**그러면 자동으로 실행됩니다!** 🚀

---

## 📊 Schedule 상태 확인 URL

```
https://github.com/miinsuu/youtube-automation/actions

이 페이지에서:
- "All workflows" 탭 확인
- "YouTube Shorts Auto Upload" 있는지 확인
- 최신 실행 항목의 "trigger" 확인:
  * "schedule" = 자동 실행됨 ✓
  * "manual" = 수동 실행
  * "push" = 코드 푸시 시 실행
```

---

**모든 설정을 완료했다면, 다음 스케줄 시간에 자동으로 실행될 것입니다!** ⏰
