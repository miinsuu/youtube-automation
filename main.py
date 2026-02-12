#!/usr/bin/env python3
"""
YouTube 쇼츠 자동화 메인 파이프라인
스크립트 생성 → TTS → 비디오 생성 → 업로드까지 전체 프로세스를 자동화합니다.
"""

import os
import sys
import json
from datetime import datetime
import argparse

# 모듈 임포트
sys.path.append('scripts')
from script_generator import ScriptGenerator
from tts_generator import TTSGenerator
from video_generator import VideoGenerator
from youtube_uploader import YouTubeUploader


class YouTubeAutomation:
    def __init__(self, config_path="config/config.json"):
        self.config_path = config_path
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 모듈 초기화
        self.script_gen = ScriptGenerator(config_path)
        self.tts_gen = TTSGenerator(config_path)
        self.video_gen = VideoGenerator(config_path)
        self.uploader = YouTubeUploader(config_path)
        
        # 출력 디렉토리 생성
        os.makedirs("output/videos", exist_ok=True)
        os.makedirs("output/audio", exist_ok=True)
        os.makedirs("output/images", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def create_video(self, topic=None, upload=True):
        """단일 영상 생성 및 업로드"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("\n" + "="*60)
        print("🎬 YouTube 쇼츠 자동 제작 시작")
        print("="*60)
        
        # 1. 스크립트 생성
        print("\n[1/5] 📝 스크립트 생성 중...")
        script_data = self.script_gen.generate_script(topic)
        if not script_data:
            print("❌ 스크립트 생성 실패")
            return None
        
        print(f"✅ 제목: {script_data['title']}")
        print(f"✅ 주제: {script_data['topic']}")
        
        # 스크립트 저장
        script_path = f"output/script_{timestamp}.json"
        self.script_gen.save_script(script_data, script_path)
        
        # 2. TTS 생성
        print("\n[2/4] 🎤 음성 생성 중...")
        audio_path = f"output/audio/audio_{timestamp}.mp3"
        audio_result = self.tts_gen.text_to_speech(script_data['script'], audio_path)
        if not audio_result:
            print("❌ 음성 생성 실패")
            return None
        
        # 3. 비디오 생성 (음성 타이밍 정보 전달)
        print("\n[3/4] 🎬 비디오 생성 중...")
        video_path = f"output/videos/video_{timestamp}.mp4"
        sentence_timings = audio_result.get('sentence_timings', None)
        final_video = self.video_gen.create_video(script_data, audio_path, video_path, sentence_timings=sentence_timings)
        if not final_video:
            print("❌ 비디오 생성 실패")
            return None
        
        # 4. YouTube 업로드
        result = {
            'script': script_data,
            'audio_path': audio_path,
            'video_path': video_path,
            'timestamp': timestamp
        }
        
        if upload and self.config['upload']['auto_upload']:
            print("\n[4/4] 📤 YouTube 업로드 중...")
            upload_result = self.uploader.upload_video(
                video_path, 
                script_data
            )
            if upload_result:
                result['upload'] = upload_result
                print(f"\n🎉 모든 작업 완료!")
                print(f"📺 YouTube URL: {upload_result['url']}")
            else:
                print("\n⚠️  비디오는 생성되었지만 업로드에 실패했습니다.")
        else:
            print("\n[4/4] ⏭️  업로드 건너뛰기")
            print(f"\n✅ 비디오 생성 완료: {video_path}")
        
        # 로그 저장
        self.save_log(result)
        
        return result
    
    def save_log(self, result):
        """작업 로그 저장"""
        log_path = f"logs/log_{result['timestamp']}.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"📋 로그 저장: {log_path}")
    
    def batch_create(self, count=3, upload=True):
        """여러 영상 일괄 생성"""
        print(f"\n🚀 {count}개의 영상을 일괄 생성합니다...\n")
        
        results = []
        for i in range(count):
            print(f"\n{'='*60}")
            print(f"영상 {i+1}/{count} 생성 중...")
            print(f"{'='*60}")
            
            result = self.create_video(upload=upload)
            if result:
                results.append(result)
            
            # 잠시 대기 (API 제한 방지)
            if i < count - 1:
                import time
                print("\n⏱️  다음 영상 생성까지 10초 대기...")
                time.sleep(10)
        
        print(f"\n{'='*60}")
        print(f"✅ 총 {len(results)}/{count}개 영상 생성 완료!")
        print(f"{'='*60}")
        
        return results


def main():
    parser = argparse.ArgumentParser(description='YouTube 쇼츠 자동 제작 시스템')
    parser.add_argument('--topic', type=str, help='영상 주제 (선택사항)')
    parser.add_argument('--count', type=int, default=1, help='생성할 영상 개수')
    parser.add_argument('--no-upload', action='store_true', help='업로드하지 않고 비디오만 생성')
    parser.add_argument('--test', action='store_true', help='테스트 모드 (업로드 없음)')
    
    args = parser.parse_args()
    
    # 자동화 시스템 초기화
    automation = YouTubeAutomation()
    
    # 업로드 여부
    upload = not args.no_upload and not args.test
    
    # 영상 생성
    if args.count == 1:
        automation.create_video(topic=args.topic, upload=upload)
    else:
        automation.batch_create(count=args.count, upload=upload)


if __name__ == "__main__":
    main()
