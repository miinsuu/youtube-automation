# 🔧 YouTube 기본 채널 변경 방법

## 📺 현재 상황

- **설정된 채널 ID**: `UC2yneYUgVE2VSzRL4y1Qbdg` ❌ (업로드 안 됨)
- **실제 업로드되는 채널**: 다른 채널 ✓ (기본 채널)

---

## 🛠️ 해결 방법 1: 기본 채널 변경 (권장)

### **Step 1: YouTube 채널 목록 확인**

1. YouTube.com 접속
2. 우측 상단 **프로필 아이콘** 클릭
3. **채널 목록** 확인 (아래 예시)

```
내 채널
─────────────────────
✓ 편의점 꿀조합    (현재 기본 채널)
  K-POP 분석
  여행 채널
  cooking tips
```

### **Step 2: 기본 채널 변경**

1. 목표 채널 이름 클릭
   - "K-POP 분석"을 기본으로 설정하려면 클릭

2. **YouTube Studio** 진입 (자동)
3. 좌측 메뉴 > **설정** > **기본 정보**

### **Step 3: 채널 ID 확인**

**현재 채널의 ID 확인:**
- 설정 > 기본 정보
- "채널 ID" 확인 (UC로 시작)

### **Step 4: config.json 업데이트**

```json
{
  "youtube": {
    "target_channel_id": "UC2yneYUgVE2VSzRL4y1Qbdg"  // 기본 채널로 설정한 채널의 ID로 변경
  }
}
```

### **Step 5: 인증 정보 초기화 후 재시도**

```bash
# 1. 기존 인증 정보 삭제
rm config/youtube_credentials.json

# 2. 새로 인증 (새 채널로 로그인)
python main.py --count 1

# 3. 확인
# ✓ 현재 로그인 채널: [기본 채널 이름] (UC2yneYUgVE2VSzRL4y1Qbdg)
```

---

## 🔍 현재 채널 ID 확인 스크립트

현재 어느 채널로 로그인되어 있는지 확인:

```bash
python -c "
from scripts.youtube_uploader import YouTubeUploader
u = YouTubeUploader()
if u.authenticate():
    ch = u.get_authenticated_channel()
    print(f'현재 기본 채널:')
    print(f'  이름: {ch[\"title\"]}')
    print(f'  ID: {ch[\"id\"]}')
    print()
    
    chs = u.get_my_channels()
    print(f'보유한 모든 채널:')
    for c in chs:
        marker = '✓ (기본)' if c['channel_id'] == ch['id'] else ''
        print(f'  {c[\"title\"]} ({c[\"channel_id\"]}) {marker}')
"
```

### 출력 예시:

```
현재 기본 채널:
  이름: 편의점 꿀조합
  ID: UCxxxxx111

보유한 모든 채널:
  ✓ 편의점 꿀조합 (UCxxxxx111) (기본)
  K-POP 분석 (UC2yneYUgVE2VSzRL4y1Qbdg)
  여행 채널 (UCyyyyyy222)
```

---

## 📝 단계별 체크리스트

### **1단계: 채널 확인**
- [ ] YouTube 채널 목록에서 모든 채널 확인
- [ ] 목표 채널의 정확한 이름 기억

### **2단계: 기본 채널 변경**
- [ ] YouTube에서 목표 채널로 전환
- [ ] YouTube Studio 접속 (자동)
- [ ] 설정 > 기본 정보에서 채널 ID 복사

### **3단계: 설정 업데이트**
- [ ] `config/config.json` 업데이트
- [ ] 채널 ID 확인 (UC로 시작하는 24자)

### **4단계: 인증 초기화**
- [ ] `rm config/youtube_credentials.json` 실행
- [ ] Python 스크립트로 현재 채널 ID 확인
- [ ] 테스트 영상 업로드

### **5단계: 검증**
- [ ] YouTube 채널 방문
- [ ] 새 영상 확인
- [ ] 메타데이터(제목, 설명) 정상 확인

---

## ⚠️ 주의사항

### ❌ 작동하지 않는 방법

```python
# 이건 작동하지 않음:
channel_id = "UC2yneYUgVE2VSzRL4a1Qbdg"  # 설정만으로는 불가능
# YouTube API는 항상 인증된 계정의 기본 채널로 업로드
```

### ✅ 작동하는 방법

```python
# 1. 채널을 기본 채널로 설정
# 2. 그 계정으로 인증
# 3. 업로드 (자동으로 그 채널로 업로드됨)
```

---

## 🎯 빠른 해결 순서

1. **YouTube 접속**
   ```
   https://www.youtube.com
   ```

2. **우측 상단 프로필 > 목표 채널 선택**

3. **YouTube Studio 자동 진입 > 설정 > 기본 정보 > 채널 ID 복사**

4. **터미널에서:**
   ```bash
   rm config/youtube_credentials.json
   python main.py --count 1
   ```

5. **YouTube에서 새 영상 확인**

---

## 🔐 GitHub Actions에서도 동일하게 작동

```yaml
# .github/workflows/youtube-automation.yml에서도
# 같은 계정으로 인증되어야 기본 채널로 업로드됨
```

**GitHub Actions 실행 시 로그 확인:**
```
✓ 현재 로그인 채널: [목표 채널 이름] ([채널 ID])
```

---

## 💡 추가 팁

### 여러 채널 자동 관리 (향후 기능)

현재는 하나의 기본 채널로만 가능하지만, 다음과 같이 확장 가능:

```python
# 미래 업데이트: 채널별 별도 인증
channels = {
    "Channel A": "config/creds_a.json",
    "Channel B": "config/creds_b.json"
}
```

---

## 📞 문제 해결

### **Q: 여전히 다른 채널에 업로드됨**

**A:** 
1. 현재 기본 채널 ID 확인
2. YouTube에서 기본 채널이 변경되었는지 확인
3. 인증 정보 재생성 (`rm config/youtube_credentials.json`)

### **Q: 채널 ID를 어떻게 확인하나?**

**A:** YouTube Studio > 설정 > 기본 정보 > "채널 ID"

### **Q: 기본 채널을 변경해도 안 바뀜**

**A:**
1. 캐시 지우기 (Ctrl+Shift+Del)
2. 시크릿 모드에서 다시 확인
3. 인증 정보 재생성

---

**마지막 업데이트**: 2026년 2월 13일
