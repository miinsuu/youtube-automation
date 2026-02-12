#!/usr/bin/env python3
"""
GitHub Actions 워크플로우 모니터링 스크립트
테스트 워크플로우 실행 상태를 실시간으로 확인합니다.
"""

import requests
import json
import time
from datetime import datetime
import sys

# GitHub 설정
OWNER = "miinsuu"
REPO = "youtube-automation"
WORKFLOW_NAME = "Test Schedule - Auto Run at 00:40 KST"

def get_workflow_runs(github_token=None):
    """워크플로우 실행 목록 조회"""
    headers = {}
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        workflows = response.json().get('workflows', [])
        
        # 테스트 워크플로우 찾기
        test_workflow = None
        for workflow in workflows:
            if 'test-schedule' in workflow.get('path', ''):
                test_workflow = workflow
                break
        
        if not test_workflow:
            print("❌ 테스트 워크플로우를 찾을 수 없습니다.")
            return None
        
        # 워크플로우 실행 목록 조회
        runs_url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{test_workflow['id']}/runs"
        runs_response = requests.get(runs_url, headers=headers, timeout=10)
        runs_response.raise_for_status()
        
        return runs_response.json().get('workflow_runs', [])
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def print_run_status(run):
    """워크플로우 실행 상태 출력"""
    run_id = run.get('id')
    status = run.get('status')
    conclusion = run.get('conclusion')
    created_at = run.get('created_at')
    updated_at = run.get('updated_at')
    
    # 상태 아이콘
    status_icon = {
        'queued': '⏳',
        'in_progress': '🔄',
        'completed': '✅' if conclusion == 'success' else '❌'
    }.get(status, '❓')
    
    # 결론 텍스트
    conclusion_text = {
        'success': '성공',
        'failure': '실패',
        'cancelled': '취소됨',
        'skipped': '건너뜀',
        'neutral': '중립'
    }.get(conclusion, conclusion or '진행 중')
    
    print(f"\n{status_icon} 실행 ID: {run_id}")
    print(f"   상태: {status} - {conclusion_text}")
    print(f"   생성: {created_at}")
    print(f"   업데이트: {updated_at}")
    print(f"   상세: https://github.com/{OWNER}/{REPO}/actions/runs/{run_id}")

def monitor_workflow(check_interval=30, max_wait_time=600):
    """워크플로우 모니터링"""
    print(f"""
╔════════════════════════════════════════════╗
║   🧪 GitHub Actions 테스트 모니터링        ║
╚════════════════════════════════════════════╝

📍 저장소: {OWNER}/{REPO}
🔍 워크플로우: {WORKFLOW_NAME}
⏱️  확인 간격: {check_interval}초
⏰ 현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}

waiting... (최대 {max_wait_time}초)
    """)
    
    start_time = time.time()
    found_run = False
    
    while True:
        runs = get_workflow_runs()
        
        if not runs:
            print("⏳ 워크플로우를 기다리는 중...")
            time.sleep(check_interval)
            continue
        
        latest_run = runs[0]
        status = latest_run.get('status')
        
        if not found_run:
            print_run_status(latest_run)
            found_run = True
        
        # 실행 중인 경우
        if status == 'in_progress':
            print(f"\n🔄 진행 중... ({datetime.now().strftime('%H:%M:%S')})")
        
        # 완료된 경우
        elif status == 'completed':
            conclusion = latest_run.get('conclusion')
            
            if conclusion == 'success':
                print(f"\n✅ 성공! ({datetime.now().strftime('%H:%M:%S')})")
                print(f"   총 소요 시간: {int((time.time() - start_time) / 60)}분")
                print_run_status(latest_run)
                break
            else:
                print(f"\n❌ 실패: {conclusion} ({datetime.now().strftime('%H:%M:%S')})")
                print_run_status(latest_run)
                break
        
        # 타임아웃 확인
        if time.time() - start_time > max_wait_time:
            print(f"\n⏰ 타임아웃 ({max_wait_time}초 경과)")
            break
        
        time.sleep(check_interval)
    
    print("\n✨ 모니터링 완료")
    print(f"📊 상세 정보: https://github.com/{OWNER}/{REPO}/actions")

def main():
    """메인 함수"""
    print(f"""
╔════════════════════════════════════════════╗
║   GitHub Actions 워크플로우 모니터          ║
╚════════════════════════════════════════════╝

⏰ 예상 실행 시간: KST 오전 12시 40분(00:40)
📍 현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}

🔍 실시간 모니터링을 시작합니다...
   (Ctrl+C로 중단 가능)
    """)
    
    try:
        monitor_workflow(check_interval=30)  # 30초마다 확인
    except KeyboardInterrupt:
        print("\n\n⛔ 모니터링 중단됨")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
