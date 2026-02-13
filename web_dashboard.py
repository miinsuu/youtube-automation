"""
웹 대시보드 - 휴대폰에서 스크립트 생성/실행 제어
Flask를 사용한 간단한 웹 UI
"""

from flask import Flask, render_template, request, jsonify
import json
import subprocess
import threading
import os
from datetime import datetime
import psutil

app = Flask(__name__)

# 전역 상태 저장
generation_state = {
    'running': False,
    'current_task': None,
    'progress': 0,
    'status': 'Ready',
    'last_video': None,
    'error': None
}

def load_config():
    """설정 파일 로드"""
    with open('config/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_recent_videos(limit=5):
    """최근 생성된 비디오 목록"""
    videos = []
    video_dir = 'output/videos'
    if os.path.exists(video_dir):
        files = sorted(
            [f for f in os.listdir(video_dir) if f.endswith('.mp4')],
            key=lambda x: os.path.getctime(os.path.join(video_dir, x)),
            reverse=True
        )
        for f in files[:limit]:
            path = os.path.join(video_dir, f)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            mtime = datetime.fromtimestamp(os.path.getctime(path))
            videos.append({
                'name': f,
                'size': f'{size_mb:.1f}MB',
                'created': mtime.strftime('%m-%d %H:%M'),
                'path': path
            })
    return videos

def get_recent_scripts(limit=5):
    """최근 생성된 스크립트 목록"""
    scripts = []
    script_dir = 'output'
    if os.path.exists(script_dir):
        files = sorted(
            [f for f in os.listdir(script_dir) if f.startswith('script_') and f.endswith('.json')],
            key=lambda x: os.path.getctime(os.path.join(script_dir, x)),
            reverse=True
        )
        for f in files[:limit]:
            path = os.path.join(script_dir, f)
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            mtime = datetime.fromtimestamp(os.path.getctime(path))
            scripts.append({
                'name': f,
                'title': data.get('title', 'N/A'),
                'topic': data.get('topic', 'N/A'),
                'created': mtime.strftime('%m-%d %H:%M'),
                'path': path
            })
    return scripts

def run_generation(count, upload):
    """백그라운드에서 생성 실행"""
    global generation_state
    
    try:
        generation_state['running'] = True
        generation_state['status'] = f'생성 중... ({count}개)'
        generation_state['progress'] = 0
        generation_state['error'] = None
        
        # 명령어 구성
        cmd = ['python', 'main.py', '--count', str(count)]
        if not upload:
            cmd.append('--no-upload')
        
        # 프로세스 실행
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        generation_state['current_task'] = process.pid
        
        # 출력 스트림 읽기
        for line in process.stdout:
            if '✅' in line:
                generation_state['progress'] += (100 // count if count > 0 else 100)
        
        process.wait()
        
        if process.returncode == 0:
            generation_state['status'] = '완료!'
            generation_state['last_video'] = get_recent_videos(1)
            generation_state['progress'] = 100
        else:
            error_msg = process.stderr.read() if process.stderr else 'Unknown error'
            generation_state['error'] = error_msg
            generation_state['status'] = '실패'
        
    except Exception as e:
        generation_state['error'] = str(e)
        generation_state['status'] = '오류 발생'
    finally:
        generation_state['running'] = False
        generation_state['current_task'] = None

@app.route('/')
def index():
    """메인 대시보드"""
    config = load_config()
    videos = get_recent_videos()
    scripts = get_recent_scripts()
    
    return render_template('dashboard.html', 
                         config=config,
                         videos=videos,
                         scripts=scripts,
                         state=generation_state)

@app.route('/api/status', methods=['GET'])
def get_status():
    """현재 상태 조회"""
    return jsonify({
        'running': generation_state['running'],
        'progress': generation_state['progress'],
        'status': generation_state['status'],
        'error': generation_state['error'],
        'last_video': generation_state['last_video']
    })

@app.route('/api/generate', methods=['POST'])
def generate():
    """영상 생성 시작"""
    global generation_state
    
    if generation_state['running']:
        return jsonify({'error': '이미 생성 중입니다'}), 400
    
    data = request.json
    count = int(data.get('count', 1))
    upload = data.get('upload', False)
    
    # 백그라운드 스레드에서 실행
    thread = threading.Thread(target=run_generation, args=(count, upload), daemon=True)
    thread.start()
    
    return jsonify({'status': 'started', 'count': count, 'upload': upload})

@app.route('/api/stop', methods=['POST'])
def stop_generation():
    """생성 중단"""
    global generation_state
    
    if generation_state['current_task']:
        try:
            os.kill(generation_state['current_task'], 15)  # SIGTERM
            generation_state['running'] = False
            generation_state['status'] = '중단됨'
            return jsonify({'status': 'stopped'})
        except:
            return jsonify({'error': '중단 실패'}), 500
    
    return jsonify({'error': '실행 중인 작업이 없습니다'}), 400

@app.route('/api/recent-videos', methods=['GET'])
def recent_videos():
    """최근 비디오 목록"""
    return jsonify(get_recent_videos())

@app.route('/api/recent-scripts', methods=['GET'])
def recent_scripts():
    """최근 스크립트 목록"""
    return jsonify(get_recent_scripts())

@app.route('/api/config', methods=['GET'])
def get_config():
    """설정 조회"""
    config = load_config()
    shorts_topics_count = len(config['content']['shorts']['topics'])
    longform_topics_count = len(config['content']['longform']['topics'])
    return jsonify({
        'shorts_topics_count': shorts_topics_count,
        'longform_topics_count': longform_topics_count,
        'total_topics_count': shorts_topics_count + longform_topics_count,
        'tts_voice': config['tts']['voice'],
        'upload_enabled': config['upload']['auto_upload'],
        'scheduler_enabled': config['scheduler']['enabled']
    })

@app.route('/api/system-info', methods=['GET'])
def system_info():
    """시스템 정보"""
    return jsonify({
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    })

if __name__ == '__main__':
    # 폰에서 접속 가능하도록 0.0.0.0으로 바인딩
    print("=" * 60)
    print("🌐 웹 대시보드 시작!")
    print("=" * 60)
    print("\n📱 휴대폰에서 접속:")
    print("   http://[컴퓨터IP]:5000")
    print("\n💻 이 컴퓨터에서:")
    print("   http://localhost:5000")
    print("\n🔍 IP 확인:")
    print("   macOS: networksetup -getinfo Wi-Fi | grep 'IP Address'")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
