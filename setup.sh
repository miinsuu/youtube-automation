#!/bin/bash
# YouTube 쇼츠 자동화 시스템 - 빠른 시작 스크립트

echo "================================================"
echo "  YouTube 쇼츠 자동화 시스템 설치"
echo "================================================"
echo ""

# 1. Python 버전 확인
echo "1️⃣  Python 버전 확인 중..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   ✅ Python $python_version 감지됨"
echo ""

# 2. FFmpeg 확인
echo "2️⃣  FFmpeg 확인 중..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg_version=$(ffmpeg -version 2>&1 | head -n 1 | awk '{print $3}')
    echo "   ✅ FFmpeg $ffmpeg_version 설치됨"
else
    echo "   ❌ FFmpeg가 설치되어 있지 않습니다."
    echo "   설치 방법:"
    echo "   - Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Windows: https://ffmpeg.org/download.html"
    exit 1
fi
echo ""

# 3. 가상환경 생성 (선택사항)
echo "3️⃣  가상환경을 생성하시겠습니까? (권장) [y/N]"
read -r create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "   가상환경 생성 중..."
    python3 -m venv venv
    source venv/bin/activate
    echo "   ✅ 가상환경 활성화됨"
else
    echo "   ⏭️  가상환경 건너뛰기"
fi
echo ""

# 4. 패키지 설치
echo "4️⃣  Python 패키지 설치 중..."
pip install -r requirements.txt
echo "   ✅ 패키지 설치 완료"
echo ""

# 5. 설정 확인
echo "5️⃣  설정 파일 확인 중..."
if [ ! -f "config/config.json" ]; then
    echo "   ❌ config/config.json이 없습니다!"
    exit 1
fi

# OpenAI API 키 확인
if grep -q "YOUR_OPENAI_API_KEY_HERE" config/config.json; then
    echo "   ⚠️  OpenAI API 키가 설정되지 않았습니다."
    echo "   config/config.json 파일을 열어서 openai_api_key를 입력하세요."
    echo ""
    echo "   API 키 발급: https://platform.openai.com/api-keys"
    echo ""
fi

# YouTube 인증 파일 확인
if [ ! -f "config/client_secrets.json" ]; then
    echo "   ⚠️  YouTube 인증 파일이 없습니다."
    echo "   Google Cloud Console에서 OAuth 클라이언트 ID를 생성하고"
    echo "   client_secrets.json을 config/ 폴더에 저장하세요."
    echo ""
    echo "   설정 방법: https://console.cloud.google.com/apis/credentials"
    echo ""
fi
echo ""

# 6. 한글 폰트 확인
echo "6️⃣  한글 폰트 확인 중..."
if fc-list | grep -i "nanum" &> /dev/null; then
    echo "   ✅ 나눔 폰트가 설치되어 있습니다."
else
    echo "   ⚠️  나눔 폰트가 설치되어 있지 않습니다."
    echo "   설치 방법:"
    echo "   - Ubuntu/Debian: sudo apt-get install fonts-nanum"
    echo "   - macOS: 기본 설치됨"
fi
echo ""

# 7. 테스트 실행 안내
echo "================================================"
echo "  설치가 완료되었습니다!"
echo "================================================"
echo ""
echo "다음 단계:"
echo ""
echo "1️⃣  config/config.json 파일을 열어서 API 키를 입력하세요"
echo "   nano config/config.json"
echo ""
echo "2️⃣  테스트 실행 (업로드 없이 비디오만 생성):"
echo "   python main.py --test"
echo ""
echo "3️⃣  실제 업로드 (YouTube 인증 필요):"
echo "   python main.py"
echo ""
echo "4️⃣  여러 영상 일괄 생성:"
echo "   python main.py --count 3"
echo ""
echo "자세한 사용법은 README.md를 참고하세요."
echo ""
