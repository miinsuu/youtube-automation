#!/bin/bash
# YouTube 자동화 헬퍼 스크립트

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

# 명령어 처리
case "$1" in
    "shorts")
        echo "🎬 쇼츠 생성 중..."
        $PYTHON "$SCRIPT_DIR/main.py" --type shorts --no-upload
        ;;
    
    "longform")
        echo "📺 롱폼 비디오 생성 중..."
        $PYTHON "$SCRIPT_DIR/main.py" --type longform --no-upload
        ;;
    
    "both")
        echo "🎥 쇼츠 + 롱폼 생성 중..."
        $PYTHON "$SCRIPT_DIR/main.py" --type both --no-upload
        ;;
    
    "upload-shorts")
        echo "🎬 쇼츠 생성 및 업로드..."
        $PYTHON "$SCRIPT_DIR/main.py" --type shorts
        ;;
    
    "upload-longform")
        echo "📺 롱폼 생성 및 업로드..."
        $PYTHON "$SCRIPT_DIR/main.py" --type longform
        ;;
    
    "scheduler-test")
        echo "🧪 스케줄러 테스트 (한 번만 실행)..."
        $PYTHON "$SCRIPT_DIR/scheduler.py" --run-once --enable-upload
        ;;
    
    "scheduler-dry-run")
        echo "📋 스케줄 확인 (실행 안함)..."
        $PYTHON "$SCRIPT_DIR/scheduler.py" --dry-run
        ;;
    
    "scheduler")
        echo "🚀 스케줄러 시작..."
        $PYTHON "$SCRIPT_DIR/scheduler.py" --enable-upload
        ;;
    
    "help"|"--help"|"-h")
        echo "📖 YouTube 자동화 헬퍼"
        echo ""
        echo "사용법: $0 <명령어>"
        echo ""
        echo "명령어 (생성만, 업로드 안함):"
        echo "  shorts              - 쇼츠 생성"
        echo "  longform            - 롱폼 비디오 생성"
        echo "  both                - 쇼츠 + 롱폼 생성"
        echo ""
        echo "명령어 (생성 + 업로드):"
        echo "  upload-shorts       - 쇼츠 생성 및 YouTube 업로드"
        echo "  upload-longform     - 롱폼 생성 및 YouTube 업로드"
        echo ""
        echo "명령어 (스케줄러):"
        echo "  scheduler           - 정기 스케줄러 시작 (실시간)"
        echo "  scheduler-test      - 스케줄러 테스트 (한 번만 실행)"
        echo "  scheduler-dry-run   - 스케줄 목록 확인 (실행 안함)"
        echo ""
        echo "예시:"
        echo "  $0 shorts              # 쇼츠 테스트"
        echo "  $0 upload-longform     # 롱폼 생성 및 업로드"
        echo "  $0 scheduler-dry-run   # 스케줄 확인"
        ;;
    
    *)
        echo "❌ 알 수 없는 명령어: $1"
        echo "도움말: $0 help"
        exit 1
        ;;
esac
