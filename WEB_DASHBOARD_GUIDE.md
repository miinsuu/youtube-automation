# 📱 웹 대시보드 - 휴대폰에서 영상 생성 제어

## 🚀 시작하기

### 1단계: 웹 서버 시작
```bash
cd /Users/minsu/Downloads/youtube-automation
source venv/bin/activate
python web_dashboard.py
```

터미널에 다음과 같은 메시지가 나타납니다:
```
============================================================
🌐 웹 대시보드 시작!
============================================================

📱 휴대폰에서 접속:
   http://[컴퓨터IP]:5000

💻 이 컴퓨터에서:
   http://localhost:5000

🔍 IP 확인:
   macOS: networksetup -getinfo Wi-Fi | grep 'IP Address'
============================================================
```

### 2단계: 컴퓨터 IP 확인 (macOS)
```bash
networksetup -getinfo Wi-Fi | grep 'IP Address'
```

예: `IP Address: 192.168.1.100`

### 3단계: 휴대폰에서 접속
브라우저 주소창에 입력:
```
http://192.168.1.100:5000
```

---

## 📊 대시보드 기능

### 시스템 정보
- **CPU**: 현재 CPU 사용률
- **메모리**: RAM 사용률
- **디스크**: 저장공간 사용률

### 생성 제어
1. **생성할 영상 수**: 1~10개 선택
2. **자동 업로드**: 생성 후 자동으로 YouTube에 업로드 (체크박스)
3. **🚀 영상 생성 시작**: 생성 시작
4. **⏹ 생성 중단**: 진행 중인 생성 중단

### 실시간 모니터링
- 진행률 바: 0~100% 실시간 표시
- 상태 뱃지: 준비 중/생성 중/완료/오류
- 최근 생성된 비디오/스크립트 목록

---

## 💡 사용 시나리오

### 외출했을 때 영상 생성
1. 집의 컴퓨터에서 `python web_dashboard.py` 실행
2. 휴대폰으로 `http://[IP]:5000` 접속
3. 영상 수 입력 후 생성 시작
4. 진행률 실시간 확인

### 자동 업로드
- 생성 후 자동으로 YouTube에 업로드
- 업로드 완료 후 자동으로 최신 비디오 목록에 표시

---

## 🔧 고급 설정

### 포트 변경
`web_dashboard.py`의 마지막 줄 수정:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

### 비밀번호 보호 추가 (선택사항)
```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    return username == "admin" and password == "your_password"

@app.route('/')
@auth.login_required
def index():
    ...
```

### SSL/HTTPS 활성화 (보안)
```bash
# 자체 서명 인증서 생성
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# app.run 수정
app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))
```

---

## ⚠️ 주의사항

1. **같은 WiFi 필요**: 컴퓨터와 휴대폰이 같은 네트워크에 연결되어야 합니다
2. **방화벽**: 필요한 경우 방화벽에서 포트 5000 허용
3. **IP 변동**: WiFi 재접속 시 IP가 변경될 수 있음
4. **백그라운드 실행**: 컴퓨터를 켜둬야 합니다

---

## 🆘 문제 해결

### "연결할 수 없음" 오류
1. 컴퓨터와 휴대폰이 같은 WiFi에 연결되었는지 확인
2. 컴퓨터의 IP 주소가 올바른지 확인
3. 방화벽 설정 확인

### 생성이 진행되지 않음
1. 터미널에서 에러 메시지 확인
2. 설정 파일(`config.json`) 확인
3. API 키 유효성 확인

### 페이지가 새로고침되지 않음
1. 휴대폰 브라우저 캐시 삭제
2. 페이지 전체 새로고침 (Ctrl+Shift+R 또는 Cmd+Shift+R)

---

## 📞 지원되는 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 메인 대시보드 |
| GET | `/api/status` | 현재 상태 조회 |
| POST | `/api/generate` | 영상 생성 시작 |
| POST | `/api/stop` | 생성 중단 |
| GET | `/api/recent-videos` | 최근 비디오 |
| GET | `/api/recent-scripts` | 최근 스크립트 |
| GET | `/api/config` | 설정 정보 |
| GET | `/api/system-info` | 시스템 정보 |

---

**버전**: 1.0  
**마지막 업데이트**: 2026년 2월 12일
