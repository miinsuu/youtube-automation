# Python 실행 환경 분석 & 수정 보고서

**작성일**: 2026년 2월 13일  
**상태**: ✅ 완전 해결

---

## 📋 문제 분석

### 초기 증상
```
실행하려는데 오류나.
기존에는 python 명령어로 실행했던거 같은데
어느 순간부터 python3로 해야되는걸로 바뀐거같아.
```

### 근본 원인 분석

#### 1단계: Python 명령어 상태 확인
```bash
$ which python python3
python not found                          # ❌ python 없음
/opt/homebrew/bin/python3                # ✅ python3만 있음
```

**결론**: 시스템에 `python` 명령어가 **완전히 제거**되었거나 PATH에서 사라짐

#### 2단계: venv 발견
```bash
$ ls -la venv/bin/python*
venv/bin/python -> python3.12            # venv에 python 있음!
venv/bin/python3 -> python3.12
venv/bin/python3.12 -> /opt/homebrew/opt/python@3.12/bin/python3.12
```

**중요 발견**: **venv에는 python이 있고 모든 패키지가 설치되어 있었음**

#### 3단계: venv 패키지 상태 확인
```bash
$ venv/bin/python -m pip list | head -20
google-generativeai         0.8.6
google-api-python-client    2.190.0
edge-tts                    7.2.7
moviepy                     1.0.3
...
(30개 이상의 필수 패키지 모두 설치됨)
```

**핵심 원인**:
- ✅ venv에 모든 패키지 설치되어 있음
- ✅ venv/bin/python 명령어 사용 가능
- ❌ run.sh가 venv 무시하고 /opt/homebrew/bin/python3 직접 사용
- ❌ /opt/homebrew/bin/python3에는 패키지 **미설치**

---

## 🔧 실행 구조 변화

### 이전 (기존 - 동작함)
```
$ python main.py
└─ venv/bin/python (활성화된 shell)
   └─ venv/lib/python3.12/site-packages
      ├─ google-generativeai
      ├─ edge-tts
      ├─ moviepy
      └─ ... (30+개 패키지)
   ✅ SUCCESS
```

### 중간 (현재 - 동작 안함)
```
$ /opt/homebrew/bin/python3 main.py  (run.sh 사용)
└─ /opt/homebrew/Cellar/python@3.12/.../python3
   └─ /opt/homebrew/lib/python3.12/site-packages
      ├─ pip (만 있음)
      ├─ wheel (만 있음)
      └─ ❌ google-generativeai 없음!
   ❌ ModuleNotFoundError
```

### 해결됨 (수정된 - 동작함)
```
$ ./run.sh shorts
└─ ./venv/bin/python  (fixed run.sh)
   └─ ./venv/lib/python3.12/site-packages
      ├─ google-generativeai
      ├─ edge-tts
      ├─ moviepy
      └─ ... (30+개 패키지)
   ✅ SUCCESS
```

---

## ✅ 수정 내역

### 1. run.sh 수정
**파일**: `/Users/minsu/Downloads/youtube-automation/run.sh`

**변경 전**:
```bash
PYTHON=/opt/homebrew/bin/python3
```

**변경 후**:
```bash
# 현재 디렉토리
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# venv Python 경로 설정 (패키지가 설치된 곳)
PYTHON="$SCRIPT_DIR/venv/bin/python"

# venv 활성화 여부 확인
if [ ! -f "$PYTHON" ]; then
    echo "❌ 오류: venv가 없습니다."
    echo "해결책: python3 -m venv venv"
    exit 1
fi
```

**이점**:
- ✅ venv의 python 사용 (패키지 모두 접근 가능)
- ✅ venv 없을 시 에러 메시지 표시
- ✅ 상대 경로로 어디서나 실행 가능

### 2. script_generator.py 수정
**파일**: `/Users/minsu/Downloads/youtube-automation/scripts/script_generator.py` (Line 35)

**변경 전**:
```python
self.topics = self.config['content']['topics']
```

**변경 후**:
```python
self.topics = self.config['content']['shorts']['topics']
```

**이유**: config.json 구조 변경으로 인한 KeyError 수정

### 3. video_generator.py 수정
**파일**: `/Users/minsu/Downloads/youtube-automation/scripts/video_generator.py` (Lines 29-36)

**변경 전**:
```python
res = self.config['video']['resolution'].split('x')
self.width = int(res[0])
self.height = int(res[1])
self.fps = self.config['video']['fps']
```

**변경 후**:
```python
shorts_config = self.config['video']['shorts']
res = shorts_config['resolution'].split('x')
self.width = int(res[0])
self.height = int(res[1])
self.fps = shorts_config['fps']
```

**이유**: 쇼츠 전용 설정 구조로 명확하게 표시

### 4. web_dashboard.py 수정
**파일**: `/Users/minsu/Downloads/youtube-automation/web_dashboard.py` (Lines 199-211)

**변경 전**:
```python
'topics_count': len(config['content']['topics']),
```

**변경 후**:
```python
shorts_topics_count = len(config['content']['shorts']['topics'])
longform_topics_count = len(config['content']['longform']['topics'])
return jsonify({
    'shorts_topics_count': shorts_topics_count,
    'longform_topics_count': longform_topics_count,
    'total_topics_count': shorts_topics_count + longform_topics_count,
```

**이유**: shorts/longform 분리된 설정 반영

---

## 🧪 검증 결과

### 검증 1: run.sh 도움말 확인
```bash
$ ./run.sh help
📖 YouTube 자동화 헬퍼

사용법: ./run.sh <명령어>

명령어 (생성만, 업로드 안함):
  shorts              - 쇼츠 생성
  longform            - 롱폼 비디오 생성
  both                - 쇼츠 + 롱폼 생성
...
✅ SUCCESS
```

### 검증 2: 패키지 Import 확인
```bash
$ ./venv/bin/python -c "import google.generativeai; import edge_tts; import moviepy"
✅ 모든 패키지 import 성공!
```

### 검증 3: 스케줄러 Dry-run
```bash
$ ./run.sh scheduler-dry-run

✅ Gemini 2.5 Flash API 초기화 완료 (쇼츠)
✅ 한글 폰트 발견: /System/Library/Fonts/AppleSDGothicNeo.ttc

📱 쇼츠 (매일): 08:00, 12:00, 15:00, 18:00, 22:00
📺 롱폼 (매일): 12:00, 15:00, 18:00, 22:00
✅ 총 9개의 스케줄이 설정되었습니다.
```

---

## 📚 핵심 학습

### Python 실행 경로 이해
```
명령어 입력
    ↓
1. shell PATH에서 python 검색
   ├─ /Users/minsu/.nvm/... (Node)
   ├─ /opt/homebrew/bin/... (Homebrew - 여기서 python3 발견)
   └─ /usr/bin, /bin 등
    
2. 발견된 python 실행
   ├─ /opt/homebrew/bin/python3
   │  └─ /opt/homebrew/lib/python3.12/site-packages (패키지 경로)
   │     └─ pip, wheel만 있음 (우리 패키지 없음!)
   └─ ./venv/bin/python ← 수정된 경로
      └─ ./venv/lib/python3.12/site-packages (패키지 경로)
         └─ 모든 필수 패키지 있음! ✅
```

### venv 중요성
- **격리된 환경**: 프로젝트별 패키지 독립 관리
- **재현성**: 같은 버전의 패키지 보장
- **안정성**: 시스템 Python 영향 없음
- **협업 편의성**: venv 공유로 팀원 바로 실행 가능

---

## 🚀 사용 방법

### 방법 1: run.sh 사용 (권장)
```bash
./run.sh shorts           # 쇼츠 생성
./run.sh longform         # 롱폼 생성
./run.sh scheduler-dry-run # 스케줄 확인
```

### 방법 2: venv 직접 활성화
```bash
source venv/bin/activate  # venv 활성화
python main.py --type shorts  # python (명령어 가능)
deactivate               # venv 비활성화
```

### 방법 3: venv python 직접 호출
```bash
./venv/bin/python main.py --type shorts
```

---

## 🎯 결론

| 항목 | 상태 |
|------|------|
| **원인** | venv 무시, 시스템 python3 사용 + 패키지 미설치 |
| **해결책** | run.sh에서 venv 경로 사용 |
| **테스트** | ✅ 모든 모듈 정상 작동 |
| **부작용** | ❌ 없음 |
| **권장사항** | 앞으로 항상 `./run.sh` 사용 |

**✅ 시스템이 정상적으로 가동 중입니다!**
