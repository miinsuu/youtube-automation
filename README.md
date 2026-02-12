# YouTube 쇼츠 자동화 시스템 📹

팩트/정보 쇼츠 영상을 자동으로 생성하고 YouTube에 업로드하는 완전 자동화 시스템입니다.

## ⚠️ 보안 주의사항

**🔒 이 프로젝트를 GitHub에 올릴 때는 반드시 Private 저장소로 설정하세요!**

민감한 정보가 포함되어 있습니다:
- API 키 (Gemini, Pexels)
- YouTube OAuth 인증 정보
- `config/config.json` - 실제 API 키 포함
- `config/client_secrets.json` - YouTube OAuth 클라이언트 시크릿
- `config/youtube_credentials.json` - YouTube 액세스 토큰

`.gitignore`가 이 파일들을 자동으로 제외하지만, **절대 Public 저장소로 만들지 마세요!**

---

## 🌟 주요 기능

✅ **AI 대본 자동 생성** - OpenAI GPT를 사용한 바이럴 스크립트 생성  
✅ **TTS 음성 생성** - 한국어 음성 자동 생성  
✅ **자막 자동 생성** - 단어별로 타이밍에 맞춰 나타나는 자막  
✅ **YouTube 자동 업로드** - 생성된 영상을 자동으로 업로드  
✅ **썸네일 자동 생성** - 눈길을 끄는 썸네일 이미지 생성  

## 📋 사전 준비사항

### 1. 필수 프로그램 설치
```bash
# Python 3.8 이상
python --version

# FFmpeg (비디오 처리에 필요)
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows - https://ffmpeg.org/download.html 에서 다운로드
```

### 2. API 키 발급

#### OpenAI API 키
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. 생성된 키를 복사 (sk-로 시작)

#### YouTube API 설정
1. https://console.cloud.google.com/ 접속
2. 새 프로젝트 생성
3. "API 및 서비스" > "라이브러리" 이동
4. "YouTube Data API v3" 검색 후 활성화
5. "사용자 인증 정보" > "OAuth 2.0 클라이언트 ID" 생성
6. 애플리케이션 유형: "데스크톱 앱"
7. client_secrets.json 다운로드

## 🚀 설치 방법

### 1. 의존성 설치
```bash
cd youtube-automation
pip install -r requirements.txt
```

### 2. 설정 파일 구성

#### config/config.json 수정
```bash
nano config/config.json
```

다음 항목을 수정하세요:
- `openai_api_key`: OpenAI API 키 입력
- `youtube.client_secrets_file`: 다운로드한 client_secrets.json 경로

#### YouTube 인증 파일 배치
```bash
# Google Cloud Console에서 다운로드한 파일을 config 폴더에 복사
cp ~/Downloads/client_secrets_*.json config/client_secrets.json
```

### 3. 한글 폰트 설치 (자막용)
```bash
# Ubuntu/Debian
sudo apt-get install fonts-nanum fonts-nanum-coding fonts-nanum-extra

# macOS는 기본 설치되어 있음

# Windows - 나눔고딕체 설치 필요
```

## 💻 사용 방법

### 기본 사용법

#### 영상 1개 생성 및 업로드
```bash
python main.py
```

#### 특정 주제로 영상 생성
```bash
python main.py --topic "우주의 신비"
```

#### 여러 영상 일괄 생성
```bash
python main.py --count 3
```

#### 업로드 없이 비디오만 생성 (테스트용)
```bash
python main.py --no-upload
```

### 고급 사용법

#### 개별 모듈 테스트

**1. 스크립트 생성 테스트**
```bash
cd scripts
python script_generator.py
```

**2. TTS 테스트**
```bash
python tts_generator.py
```

**3. YouTube 인증 테스트**
```bash
python youtube_uploader.py
```

## 📁 프로젝트 구조

```
youtube-automation/
├── config/
│   ├── config.json              # 설정 파일
│   └── client_secrets.json      # YouTube OAuth 인증 정보
├── scripts/
│   ├── script_generator.py      # AI 대본 생성
│   ├── tts_generator.py         # 음성 생성
│   ├── video_generator.py       # 비디오 합성
│   └── youtube_uploader.py      # YouTube 업로드
├── output/
│   ├── videos/                  # 생성된 비디오 파일
│   ├── audio/                   # 생성된 오디오 파일
│   └── images/                  # 썸네일 이미지
├── logs/                        # 작업 로그
├── main.py                      # 메인 실행 파일
└── requirements.txt             # Python 패키지 목록
```

## ⚙️ 설정 커스터마이징

### config/config.json 주요 설정

```json
{
  "content": {
    "topics": [
      "여기에 원하는 주제를 추가하세요"
    ]
  },
  "video": {
    "resolution": "1080x1920",  // 세로 영상 (쇼츠용)
    "fps": 30,
    "background_color": "#1a1a2e"  // 배경색 변경 가능
  },
  "upload": {
    "privacy_status": "public",  // public, unlisted, private
    "default_tags": ["쇼츠", "팩트"]  // 기본 태그
  }
}
```

## 🤖 자동화 설정 (크론잡)

### 매일 자동으로 영상 업로드

```bash
# 크론 편집
crontab -e

# 매일 오전 9시에 영상 1개 자동 생성 및 업로드
0 9 * * * cd /path/to/youtube-automation && python main.py

# 매일 오전 9시, 오후 3시, 오후 9시에 각각 1개씩 (총 3개)
0 9,15,21 * * * cd /path/to/youtube-automation && python main.py
```

## 📊 생성 결과 예시

각 실행마다 다음 파일들이 생성됩니다:

1. **스크립트** - `output/script_20240215_093045.json`
2. **음성** - `output/audio/audio_20240215_093045.mp3`
3. **썸네일** - `output/images/thumbnail_20240215_093045.png`
4. **비디오** - `output/videos/video_20240215_093045.mp4`
5. **로그** - `logs/log_20240215_093045.json`

## 🎯 최적화 팁

### 조회수를 높이기 위한 설정

1. **매력적인 주제 선택**
   - config.json의 topics 배열에 트렌딩 주제 추가
   - 시즌별 이슈 반영 (예: 겨울철 건강 팁)

2. **업로드 타이밍**
   - 오후 6-9시가 조회수가 높은 시간대
   - 크론잡으로 이 시간에 업로드 예약

3. **태그 최적화**
   - 인기 검색어를 default_tags에 추가
   - 각 주제별 관련 태그 자동 생성됨

## ⚠️ 주의사항

1. **API 비용**
   - OpenAI API는 사용량에 따라 과금됩니다
   - GPT-4o-mini 사용으로 비용 최소화 (영상 1개당 약 $0.01)

2. **YouTube 정책**
   - 저작권이 있는 배경 음악 사용 금지
   - 부적절한 콘텐츠 생성 방지
   - YouTube 커뮤니티 가이드라인 준수

3. **업로드 제한**
   - YouTube는 일일 업로드 제한이 있을 수 있음
   - 처음에는 1-2개로 시작 권장

## 🔧 문제 해결

### 1. FFmpeg 오류
```bash
# FFmpeg가 설치되어 있는지 확인
ffmpeg -version

# 없다면 설치
sudo apt-get install ffmpeg  # Ubuntu
brew install ffmpeg          # macOS
```

### 2. 한글 폰트 오류
```bash
# 나눔 폰트 설치
sudo apt-get install fonts-nanum
```

### 3. YouTube 업로드 실패
- client_secrets.json 파일 경로 확인
- Google Cloud Console에서 API가 활성화되어 있는지 확인
- OAuth 동의 화면 설정 완료 여부 확인

### 4. OpenAI API 오류
- API 키가 올바른지 확인
- 계정에 충분한 크레딧이 있는지 확인

## 📈 성과 모니터링

생성된 로그 파일을 통해 다음을 추적할 수 있습니다:
- 어떤 주제가 가장 많이 생성되었는지
- 영상 길이 분포
- 업로드 성공률

```bash
# 로그 확인
ls -lh logs/
cat logs/log_latest.json
```

## 🎓 확장 아이디어

1. **A/B 테스팅**
   - 같은 주제로 다른 스타일의 영상 생성
   - 조회수 비교 후 효과적인 스타일 선택

2. **분석 연동**
   - YouTube Analytics API 연동
   - 조회수가 높은 영상 패턴 분석

3. **다양한 포맷**
   - 뉴스 요약형
   - 퀴즈형
   - 스토리텔링형

## 📞 지원

문제가 발생하면:
1. logs/ 폴더의 최신 로그 확인
2. 에러 메시지 복사
3. 각 모듈별 개별 테스트 실행

---

**만든 이**: AI 자동화 전문가  
**버전**: 1.0.0  
**라이센스**: MIT

즐거운 유튜브 활동 되세요! 🎉
