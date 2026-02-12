# 🚀 Groq API 설정 가이드 (완전 무료!)

## ✨ Groq의 장점

- ✅ **완전 무료** - 신용카드 없음
- ⚡ **초고속** - 응답 시간 <1초
- 📊 **무제한** - 사용 제한 없음
- 🔑 **즉시 발급** - 몇 초만에 API 키 획득

---

## 1단계: Groq 회원가입

1. https://console.groq.com 방문
2. **"Sign up"** 클릭
3. 이메일로 가입 (Google/GitHub 계정도 가능)
4. 이메일 인증 완료

---

## 2단계: API 키 발급

1. Groq Console 로그인
2. 왼쪽 사이드바에서 **"API Keys"** 클릭
3. **"Create New API Key"** 클릭
4. 키 이름 입력 (예: "youtube-automation")
5. **"Generate Key"** 클릭
6. API 키 복사 (시작: `gsk_...`)

---

## 3단계: config.json 설정

`config/config.json` 파일을 열어서:

```json
{
  "ai_provider": "groq",
  "groq_api_key": "gsk_YOUR_API_KEY_HERE",
  ...
}
```

발급받은 API 키를 `gsk_YOUR_API_KEY_HERE` 자리에 붙여넣기

---

## 4단계: 테스트

```bash
# 스크립트 생성 테스트
python main.py --count 1 --no-upload

# 또는 직접 테스트
python -c "
from scripts.script_generator import ScriptGenerator
gen = ScriptGenerator()
script = gen.generate_script()
print(script)
"
```

---

## 환경변수 설정 (선택사항)

`.env` 파일 생성:

```bash
echo "GROQ_API_KEY=gsk_YOUR_API_KEY_HERE" > .env
```

그러면 `config.json`에 API 키를 저장하지 않아도 됩니다.

---

## 🎉 모두 완료!

이제 완전 무료로 무제한으로 스크립트를 생성할 수 있습니다! 🚀

### 문제 해결

**"GROQ_API_KEY가 필요합니다" 에러:**
- config.json에서 groq_api_key 확인
- 또는 환경변수 GROQ_API_KEY 설정

**"API 응답이 느림" 증상:**
- Groq는 매우 빠르므로, 네트워크 확인
- 모델: llama-3.1-70b-versatile (최적화됨)
