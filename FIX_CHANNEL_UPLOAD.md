# ✅ YouTube 채널 문제 해결 - 빠른 가이드

## 현재 상황

```
설정된 채널 ID: UC2yneYUgVE2VSzRL4y1Qbdg
실제 업로드 채널: ❓ (다른 채널)
```

---

## 🎯 3단계 해결 방법

### **Step 1: 인증 정보 초기화** ✅ (완료)

```bash
rm -f config/youtube_credentials.json
```

### **Step 2: YouTube 기본 채널 설정**

**설정되기를 원하는 채널 ID: `UC2yneYUgVE2VSzRL4y1Qbdg`**

1. **YouTube.com 접속**
   ```
   https://www.youtube.com
   ```

2. **우측 상단 프로필 아이콘 클릭**

3. **채널 목록 표시**
   ```
   내 채널
   ├─ 편의점 꿀조합 ✓ 
   ├─ K-POP 분석
   └─ 여행 채널
   ```

4. **목표 채널 선택**
   - `UC2yneYUgVE2VSzRL4y1Qbdg` 채널 ID를 가진 채널 클릭
   - (정확한 채널명은 아래 명령으로 확인)

5. **확인**
   - YouTube Studio 자동 진입
   - 좌측 메뉴 > 설정 > 기본 정보에서 채널 ID 확인

### **Step 3: 테스트 업로드**

```bash
python main.py --count 1
```

**로그 확인:**
```
✓ 현재 로그인 채널: [채널명] (UC2yneYUgVE2VSzRL4y1Qbdg)
✅ 업로드 완료!
```

---

## 🔍 현재 보유한 채널 확인

### **방법 1: YouTube에서 직접 확인**

1. YouTube.com 접속
2. 우측 상단 프로필 > "채널 목록"
3. 각 채널명과 채널 ID 메모

### **방법 2: YouTube Studio에서**

1. https://studio.youtube.com 접속
2. 좌측 하단 채널 선택 드롭다운
3. 각 채널명 확인
4. 각 채널 > 설정 > 기본 정보 > "채널 ID" 복사

---

## 📋 체크리스트

### 업로드 전 확인 사항

- [ ] **YouTube 기본 채널 변경 완료**
  - 설정: `UC2yneYUgVE2VSzRL4y1Qbdg`
  - YouTube에서 이 ID의 채널을 기본 채널로 설정했음

- [ ] **인증 정보 초기화 완료**
  ```bash
  rm -f config/youtube_credentials.json
  ```

- [ ] **config.json 확인**
  ```json
  {
    "youtube": {
      "target_channel_id": "UC2yneYUgVE2VSzRL4y1Qbdg"
    }
  }
  ```

### 업로드 후 확인 사항

- [ ] **테스트 업로드 실행**
  ```bash
  python main.py --count 1
  ```

- [ ] **로그 확인**
  - ✓ 현재 로그인 채널이 `UC2yneYUgVE2VSzRL4y1Qbdg`인지 확인

- [ ] **YouTube 확인**
  - 새 영상이 올바른 채널에 업로드되었는지 확인
  - 채널명, 채널 ID 확인

---

## ⚠️ 만약 여전히 다른 채널에 업로드된다면?

### **원인 1: YouTube에서 기본 채널이 변경되지 않음**

**해결:**
1. YouTube 캐시 삭제 (Ctrl+Shift+Del)
2. 시크릿 창에서 다시 확인
3. 다시 기본 채널 설정

### **원인 2: 인증 정보가 여전히 캐시됨**

**해결:**
```bash
# 완전히 초기화
rm -f config/youtube_credentials.json
rm -rf ~/.cache/  # 시스템 캐시도 삭제

# 다시 시도
python main.py --count 1
```

### **원인 3: 다른 Google 계정으로 로그인됨**

**해결:**
1. 올바른 Google 계정으로 로그인되어 있는지 확인
2. 필요시 로그아웃 후 다시 로그인
3. `rm -f config/youtube_credentials.json` 후 재시도

---

## 💡 유용한 팁

### 현재 로그인 채널 빠르게 확인

```bash
# 한 줄 명령어
python -c "from scripts.youtube_uploader import YouTubeUploader as YT; u=YT(); u.authenticate() and print(f'현재: {u.get_authenticated_channel()[\"title\"]}')"
```

### config.json에서 채널 ID 빠르게 확인

```bash
# config.json의 채널 ID만 출력
python -c "import json; print(json.load(open('config/config.json'))['youtube']['target_channel_id'])"
```

---

## 📞 추가 도움말

### YouTube 채널 ID가 뭐예요?

- **형식**: `UC`로 시작하는 24자 문자열
- **예시**: `UC2yneYUgVE2VSzRL4y1Qbdg`
- **위치**: YouTube Studio > 설정 > 기본 정보 > "채널 ID"

### `@` 핸들과의 차이

```
채널 URL: https://www.youtube.com/channel/UC2yneYUgVE2VSzRL4y1Qbdg
                                              ^^^^^^^^^^^^^^^^^^^^^^
                                              이것이 채널 ID

채널 핸들: @mychannel (다른 것)
```

---

## 🚀 다음 단계

1. **위 체크리스트 완료**
2. **테스트 업로드 실행**
3. **YouTube에서 확인**
4. **성공하면 GitHub Actions 테스트 진행**

---

**마지막 업데이트**: 2026년 2월 13일
