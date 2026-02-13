#!/usr/bin/env python3
"""
YouTube 쇼츠 자동 업로드 스케줄러
설정된 시간에 자동으로 영상을 생성하고 업로드합니다.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
import schedule
import argparse

# 모듈 임포트
sys.path.append('scripts')
from main import YouTubeAutomation


class YouTubeScheduler:
    def __init__(self, config_path="config/config.json"):
        self.config_path = config_path
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.automation = YouTubeAutomation(config_path)
        self.upload_enabled = self.config.get('scheduler', {}).get('upload_enabled', False)
        
        # 스케줄 설정
        self.schedule_config = self.config.get('scheduler', {})
        
    def create_and_upload(self, video_type='shorts'):
        """영상 생성 및 업로드 (플래그에 따라)"""
        now = datetime.now()
        print(f"\n{'='*60}")
        print(f"⏰ 스케줄 실행: {now.strftime('%Y-%m-%d %H:%M:%S')} (KST)")
        print(f"🎬 타입: {video_type.upper()}")
        print(f"{'='*60}")
        
        try:
            # 비디오 타입에 따라 생성
            if video_type == 'longform':
                result = self.automation.create_longform_video(upload=self.upload_enabled)
            else:  # shorts
                result = self.automation.create_video(upload=self.upload_enabled)
            
            if result:
                print(f"✅ 작업 완료!")
                if self.upload_enabled:
                    print(f"📺 YouTube 업로드 완료")
                else:
                    print(f"📁 비디오 저장됨: {result['video_path']}")
            else:
                print(f"❌ 작업 실패")
                
        except Exception as e:
            print(f"❌ 스케줄 실행 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_schedule(self):
        """스케줄 설정"""
        # Config에서 매일 실행 시간 읽기
        shorts_times = self.schedule_config.get('shorts', {}).get('daily_times', 
            ['08:00', '12:00', '15:00', '18:00', '22:00'])
        longform_times = self.schedule_config.get('longform', {}).get('daily_times', 
            ['12:00', '15:00', '18:00', '22:00'])
        
        print("📅 스케줄 설정 중...")
        print(f"\n📱 쇼츠 (매일): {', '.join(shorts_times)}")
        print(f"📺 롱폼 (매일): {', '.join(longform_times)}")
        print(f"   업로드 활성화: {'✅ 예' if self.upload_enabled else '❌ 아니오 (테스트 모드)'}")
        
        # 쇼츠 스케줄 - 매일 실행
        for time_str in shorts_times:
            schedule.every().day.at(time_str).do(self.create_and_upload, video_type='shorts')
        
        # 롱폼 스케줄 - 매일 실행
        for time_str in longform_times:
            schedule.every().day.at(time_str).do(self.create_and_upload, video_type='longform')
        
        print(f"\n✅ 총 {len(schedule.get_jobs())}개의 스케줄이 설정되었습니다.")
        
    def run(self):
        """스케줄러 실행"""
        self.setup_schedule()
        
        print("\n🚀 스케줄러가 시작되었습니다. (Ctrl+C로 종료)")
        print(f"   다음 실행: {schedule.next_run()}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    
    def run_once(self):
        """한 번만 실행 (테스트용)"""
        print("\n🧪 테스트 모드: 한 번 실행")
        self.create_and_upload()


def main():
    parser = argparse.ArgumentParser(description='YouTube 쇼츠 자동 업로드 스케줄러')
    parser.add_argument('--run-once', action='store_true', help='한 번만 실행 (테스트)')
    parser.add_argument('--enable-upload', action='store_true', help='실제 업로드 활성화')
    parser.add_argument('--dry-run', action='store_true', help='스케줄만 확인 (실행 안함)')
    
    args = parser.parse_args()
    
    scheduler = YouTubeScheduler()
    
    if args.enable_upload:
        scheduler.upload_enabled = True
        print("⚠️  실제 업로드가 활성화되었습니다!")
    
    if args.dry_run:
        scheduler.setup_schedule()
        print("\n📋 스케줄 목록:")
        for job in schedule.get_jobs():
            print(f"   - {job}")
        return
    
    if args.run_once:
        scheduler.run_once()
    else:
        scheduler.run()


if __name__ == "__main__":
    main()
