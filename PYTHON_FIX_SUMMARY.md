# 🔧 Python 실행 환경 수정 완료

**수정 완료**: 2026년 2월 13일 ✅

---

## 📊 문제 요약

| 단계 | 상태 |
|------|------|
| **문제** | `python` 명령어 없음, `python3`로 변경 필요 → 모듈 Import 오류 |
| **원인** | venv 무시하고 시스템 python3 사용 (패키지 미설치) |
| **해결** | run.sh 수정하여 venv/bin/python 사용 |
| **결과** | ✅ 모든 시스템 정상 작동 |

---

## 🔍 원인 분석 과정

### Step 1: Python 상태 확인
```bash
$ which python python3
python not found
/opt/homebrew/bin/python3
```
→ `python` 명령어 완전히 제거됨

### Step 2: 실제 패키지 위치 확인
```bash
# /opt/homebrew/bin/python3 (패키지 없음!)
$ /opt/homebrew/bin/python3 -m pip list
pip         24.0
wheel       0.43.0

# ./venv/bin/python (모든 패키지 있음!)
$ ./venv/bin/python -m pip list
google-generativeai    0.8.6  ✅
edge-tts               7.2.7  ✅
moviepy                1.0.3  ✅
...총 75개
```

### Step 3: 구조 문제 발견
```
config.json 구조:
  content
    ├─ shorts
    │  └─ topics: [...]  ✅
    ├─ longform
       └─ topics: [...]  ✅

코드에서 찾는 위치:
  config['content']['topics']  ❌ (없음!)
```

---

## ✅ 수정 내용

### 1️⃣ run.sh
```bash
# Before (패키지 없는 시스템 python3 사용)
PYTHON=/opt/homebrew/bin/python3

# After (패키지 있는 venv python 사용)
PYTHON="$SCRIPT_DIR/venv/bin/python"
```

### 2️⃣ script_generator.py
```python
# Before
self.topics = self.config['content']['topics']

# After
self.topics = self.config['content']['shorts']['topics']
```

### 3️⃣ video_generator.py
```python
# Before
res = self.config['video']['resolution'].split('x')

# After
shorts_config = self.config['video']['shorts']
res = shorts_config['resolution'].split('x')
```

### 4️⃣ web_dashboard.py
```python
# Before
'topics_count': len(config['content']['topics'])

# After
'shorts_topics_count': len(config['content']['shorts']['topics'])
'longform_topics_count': len(config['content']['longform']['topics'])
```

---

## ✨ 최종 상태

```bash
$ ./run.sh scheduler-dry-run

✅ Gemini 2.5 Flash API 초기화 완료 (쇼츠)
✅ 한글 폰트 발견: /System/Library/Fonts/AppleSDGothicNeo.ttc

📱 쇼츠 (매일): 08:00, 12:00, 15:00, 18:00, 22:00
📺 롱폼 (매일): 12:00, 15:00, 18:00, 22:00
✅ 총 9개의 스케줄이 설정되었습니다.
```

### 시스템 상태
- ✅ Python 경로: `./venv/bin/python`
- ✅ 설치된 패키지: 75개
- ✅ 모든 모듈 Import 성공
- ✅ 스케줄러 정상 작동

---

## 🚀 사용 방법

### 쇼츠 생성
```bash
./run.sh shorts
```

### 롱폼 생성
```bash
./run.sh longform
```

### 스케줄 확인
```bash
./run.sh scheduler-dry-run
```

### 스케줄러 시작
```bash
./run.sh scheduler
```

---

## 📌 중요 포인트

1. **venv 우선**: 앞으로는 항상 `./run.sh` 사용
2. **패키지 관리**: venv 내에 모든 패키지 설치
3. **경로 문제**: 절대 경로 대신 상대 경로 사용
4. **config 구조**: shorts/longform 분리된 설정 사용

---

**✅ 모든 문제 해결 완료!**
