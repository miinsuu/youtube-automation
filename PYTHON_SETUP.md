# 🐍 Python 명령어 설정 가이드

macOS에서 `python` 명령어가 없는 경우 해결 방법입니다.

---

## 🔍 현재 상태 확인

```bash
# Python3 경로 확인
which python3
# 결과: /opt/homebrew/bin/python3

# Python3 버전 확인
python3 --version
# 결과: Python 3.12.4
```

---

## ✅ 방법 1: 편의 스크립트 사용 (추천)

가장 간단한 방법입니다. 이미 준비된 `run.sh` 파일을 사용하세요:

```bash
# 쇼츠 생성 (테스트)
./run.sh shorts

# 롱폼 생성 (테스트)
./run.sh longform

# 쇼츠 생성 + 업로드
./run.sh upload-shorts

# 롱폼 생성 + 업로드
./run.sh upload-longform

# 스케줄러 시작
./run.sh scheduler

# 도움말
./run.sh help
```

**장점**: 
- ✅ 가장 간단함
- ✅ 모든 명령어 자동 관리
- ✅ 추가 설정 없음

---

## ✅ 방법 2: Python3 직접 사용

터미널에서 직접 Python3를 호출합니다:

```bash
# 쇼츠 생성
python3 main.py --type shorts --no-upload

# 롱폼 생성
python3 main.py --type longform --no-upload

# 쇼츠 + 업로드
python3 main.py --type shorts

# 롱폼 + 업로드
python3 main.py --type longform

# 스케줄러 시작
python3 scheduler.py --enable-upload
```

---

## ✅ 방법 3: Alias 설정 (영구적)

`python` 명령어를 `python3`으로 자동 매핑합니다.

### Step 1: Shell 설정 파일 열기

```bash
# zsh 사용 (기본값)
nano ~/.zshrc

# 또는 bash 사용 중이면
nano ~/.bash_profile
```

### Step 2: Alias 추가

파일 끝에 다음을 추가하세요:

```bash
# Python alias
alias python=python3
```

### Step 3: 설정 적용

```bash
# zsh인 경우
source ~/.zshrc

# bash인 경우
source ~/.bash_profile
```

### Step 4: 확인

```bash
python --version
# 결과: Python 3.12.4
```

이제 `python` 명령어를 직접 사용 가능합니다:

```bash
python main.py --type shorts --no-upload
```

---

## ✅ 방법 4: Homebrew 심링크 생성

또 다른 방법은 심링크를 생성하는 것입니다:

```bash
# python3을 python으로 심링크
ln -s /opt/homebrew/bin/python3 /opt/homebrew/bin/python

# 확인
python --version
```

---

## 📋 권장 사항

| 상황 | 추천 방법 |
|------|---------|
| 처음 사용자 | **방법 1** (run.sh) |
| Python 개발자 | **방법 3** (Alias) |
| 빠른 테스트 | **방법 2** (python3) |
| 영구 해결 | **방법 3 또는 4** |

---

## 🚀 즉시 테스트

편의 스크립트로 즉시 테스트하세요:

```bash
cd /Users/minsu/Downloads/youtube-automation

# 쇼츠 생성 테스트 (약 5분)
./run.sh shorts

# 또는
python3 main.py --type shorts --no-upload
```

---

## 🐛 문제 해결

**Q: "./run.sh: Permission denied" 오류**

```bash
chmod +x run.sh
./run.sh shorts
```

**Q: "python3: command not found"**

```bash
# Python3 재설치
brew install python3

# 경로 확인
which python3
```

**Q: "ModuleNotFoundError" 오류**

```bash
# 의존성 설치
pip3 install -r requirements.txt
```

---

## ✅ 확인 체크리스트

- [x] Python3 설치 확인 (`which python3`)
- [x] 버전 확인 (`python3 --version`)
- [x] run.sh 실행 권한 (`ls -lh run.sh`)
- [x] 의존성 설치 (`pip3 install -r requirements.txt`)
- [ ] 쇼츠 테스트 실행 (`./run.sh shorts`)
- [ ] 롱폼 테스트 실행 (`./run.sh longform`)

---

**다음 단계**: `./run.sh shorts` 또는 `python3 main.py --type shorts --no-upload` 실행! 🚀
