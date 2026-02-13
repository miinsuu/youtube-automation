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
from longform_script_generator import LongformScriptGenerator
from tts_generator import TTSGenerator
from video_generator import VideoGenerator
from longform_video_generator import LongformVideoGenerator
from youtube_uploader import YouTubeUploader
from thumbnail_generator import ThumbnailGenerator


class YouTubeAutomation:
    def __init__(self, config_path="config/config.json"):
        self.config_path = config_path
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 모듈 초기화
        self.script_gen = ScriptGenerator(config_path)
        self.longform_script_gen = LongformScriptGenerator(config_path)
        self.tts_gen = TTSGenerator(config_path)
        self.video_gen = VideoGenerator(config_path)
        self.longform_video_gen = LongformVideoGenerator(config_path)
        self.thumbnail_gen = ThumbnailGenerator(config_path)
        self.uploader = YouTubeUploader(config_path)
        
        # 출력 디렉토리 생성
        os.makedirs("output/videos", exist_ok=True)
        os.makedirs("output/longform_videos", exist_ok=True)
        os.makedirs("output/audio", exist_ok=True)
        os.makedirs("output/longform_audio", exist_ok=True)
        os.makedirs("output/images", exist_ok=True)
        os.makedirs("output/longform_images", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def create_video(self, topic=None, upload=True):
        """쇼츠 영상 생성 및 업로드 (구조화 메타데이터 + 5장 AI 이미지)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("\n" + "="*60)
        print("🎬 YouTube 쇼츠 자동 제작 시작")
        print("="*60)

        # 1. 스크립트 + 메타데이터 + 이미지 프롬프트 생성
        print("\n[1/6] 📝 스크립트 + 메타데이터 생성 중...")
        script_data = self.script_gen.generate_script(topic)
        if not script_data:
            print("❌ 스크립트 생성 실패")
            return None

        print(f"✅ 제목: {script_data['title']}")
        print(f"✅ 주제: {script_data['topic']}")
        print(f"✅ 이미지 프롬프트: {len(script_data.get('image_prompts', []))}개")

        # 스크립트 저장
        script_path = f"output/script_{timestamp}.json"
        self.script_gen.save_script(script_data, script_path)

        # 2. TTS 생성
        print("\n[2/6] 🎤 음성 생성 중...")
        audio_path = f"output/audio/audio_{timestamp}.mp3"
        audio_result = self.tts_gen.text_to_speech(script_data['script'], audio_path)
        if not audio_result:
            print("❌ 음성 생성 실패")
            return None

        # 3. 비디오 생성 (5장 AI 이미지 + 음성 타이밍 자막)
        print("\n[3/6] 🎬 비디오 생성 중...")
        video_path = f"output/videos/video_{timestamp}.mp4"
        sentence_timings = audio_result.get('sentence_timings', None)
        use_ai_bg = self.config.get('video', {}).get('shorts', {}).get('use_ai_background', True)
        final_video = self.video_gen.create_video(
            script_data,
            audio_path,
            video_path,
            sentence_timings=sentence_timings,
            use_ai_background=use_ai_bg
        )
        if not final_video:
            print("❌ 비디오 생성 실패")
            return None

        # 4. 썸네일 확인
        print("\n[4/6] 🖼️  썸네일 확인 중...")
        thumbnail_path = self.video_gen.get_thumbnail_path()
        if thumbnail_path and os.path.exists(thumbnail_path):
            print(f"✅ 후킹 썸네일: {thumbnail_path}")
        else:
            thumbnail_path = None
            print("⚠️ 썸네일 없음")

        # 5. YouTube 업로드
        result = {
            'script': script_data,
            'audio_path': audio_path,
            'video_path': video_path,
            'thumbnail_path': thumbnail_path,
            'timestamp': timestamp,
            'type': 'shorts'
        }

        if upload and self.config.get('upload', {}).get('shorts', {}).get('auto_upload', True):
            print("\n[5/6] 📤 YouTube 업로드 중...")

            # 현재 인증된 채널 확인
            current_channel = self.uploader.get_authenticated_channel()
            if current_channel:
                print(f"✓ 현재 로그인 채널: {current_channel['title']} ({current_channel['id']})")

            target_channel_id = self.config['youtube'].get('target_channel_id')
            if target_channel_id and current_channel and current_channel['id'] != target_channel_id:
                print(f"⚠️  주의: 대상 채널({target_channel_id})이 현재 로그인 채널과 다릅니다!")

            # 구조화 메타데이터 전달 (제목, 설명, 해시태그, 고정댓글 포함)
            upload_result = self.uploader.upload_video(
                video_path,
                script_data,
                thumbnail_path=thumbnail_path,
                channel_id=target_channel_id,
                metadata=script_data,  # title, description, tags, pinned_comment 포함
                add_pinned_comment=True
            )
            if upload_result:
                result['upload'] = upload_result
                print(f"\n🎉 모든 작업 완료!")
                print(f"📺 YouTube URL: {upload_result['url']}")
            else:
                print("\n⚠️  비디오는 생성되었지만 업로드에 실패했습니다.")
        else:
            print("\n[5/6] ⏭️  업로드 건너뛰기")
            print(f"\n✅ 비디오 생성 완료: {video_path}")

        # 6. 로그 저장
        print("\n[6/6] 📋 로그 저장 중...")
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
    
    def create_longform_video(self, topic=None, upload=True):
        """롱폼 영상 생성 및 업로드 (10-15분)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("\n" + "="*60)
        print("🎬 YouTube 롱폼 비디오 자동 제작 시작")
        print("="*60)
        
        # 1. 롱폼 스크립트 생성
        print("\n[1/7] 📚 롱폼 스크립트 생성 중...")
        script_data = self.longform_script_gen.generate_script(topic)
        if not script_data:
            print("❌ 스크립트 생성 실패")
            return None
        
        print(f"✅ 제목: {script_data['title']}")
        print(f"✅ 주제: {script_data['topic']}")
        print(f"✅ 길이: {script_data['estimated_duration']}")
        
        # 스크립트 저장
        script_path = f"output/longform_script_{timestamp}.json"
        self.longform_script_gen.save_script(script_data, script_path)
        
        # 2. YouTube 메타데이터 생성 (제목/설명/해시태그/고정댓글)
        print("\n[2/7] 📋 YouTube 메타데이터 생성 중...")
        metadata = self.longform_script_gen.generate_metadata(script_data)
        
        # 메타데이터 저장
        meta_path = f"output/longform_metadata_{timestamp}.json"
        try:
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print(f"✅ 메타데이터 저장: {meta_path}")
        except Exception:
            pass
        
        # 3. TTS 생성 (롱폼용)
        print("\n[3/7] 🎤 음성 생성 중...")
        audio_path = f"output/longform_audio/audio_{timestamp}.mp3"
        audio_result = self.tts_gen.text_to_speech(script_data['script'], audio_path)
        if not audio_result:
            print("❌ 음성 생성 실패")
            return None
        
        duration = audio_result.get('duration', 0)
        sentence_timings = audio_result.get('sentence_timings', [])
        print(f"✅ 음성 길이: {duration:.0f}초 ({duration/60:.1f}분)")
        
        # 4. 롱폼 비디오 생성
        print("\n[4/7] 🎬 비디오 생성 중...")
        video_path = f"output/longform_videos/longform_{timestamp}.mp4"
        use_ai_bg = self.config.get('video', {}).get('longform', {}).get('use_ai_background', True)
        
        final_video = self.longform_video_gen.create_video(
            script_data,
            audio_path,
            video_path,
            sentence_timings=sentence_timings,
            use_ai_background=use_ai_bg
        )
        
        if not final_video:
            print("❌ 비디오 생성 실패")
            return None
        
        # 5. 썸네일 (비디오 생성 시 자동 생성된 후킹 화면 캡처 사용)
        print("\n[5/7] 🖼️  썸네일 확인 중...")
        thumbnail_path = self.longform_video_gen.get_thumbnail_path()
        thumb = thumbnail_path if thumbnail_path and os.path.exists(thumbnail_path) else None
        if thumb:
            print(f"✅ 후킹 썸네일 사용: {thumbnail_path}")
        else:
            print("⚠️ 썸네일 없음 (업로드 시 YouTube 자동 썸네일 사용)")
        
        # 6. YouTube 업로드
        result = {
            'script': script_data,
            'metadata': metadata,
            'audio_path': audio_path,
            'video_path': video_path,
            'thumbnail_path': thumbnail_path if thumb else None,
            'timestamp': timestamp,
            'type': 'longform'
        }
        
        if upload and self.config['upload']['longform'].get('auto_upload', True):
            print("\n[6/7] 📤 YouTube 업로드 중...")
            
            # 롱폼 비디오 업로드 (Gemini 생성 메타데이터 + 썸네일)
            upload_result = self.uploader.upload_longform_video(
                video_path,
                script_data,
                thumbnail_path=thumbnail_path if thumb else None,
                add_pinned_comment=True,
                metadata=metadata
            )
            
            if upload_result:
                result['upload'] = upload_result
                print(f"\n🎉 모든 작업 완료!")
                print(f"📺 YouTube URL: {upload_result['url']}")
            else:
                print("\n⚠️  비디오는 생성되었지만 업로드에 실패했습니다.")
        else:
            print("\n[6/7] ⏭️  업로드 건너뛰기")
            print(f"\n✅ 비디오 생성 완료: {video_path}")
        
        print("\n[7/7] 📋 로그 저장 중...")
        self.save_log(result)
        
        return result


def main():
    parser = argparse.ArgumentParser(description='YouTube 자동 제작 시스템')
    parser.add_argument('--type', type=str, choices=['shorts', 'longform', 'both'], 
                       default='shorts', help='생성할 비디오 타입')
    parser.add_argument('--topic', type=str, help='영상 주제 (선택사항)')
    parser.add_argument('--count', type=int, default=1, help='생성할 영상 개수')
    parser.add_argument('--no-upload', action='store_true', help='업로드하지 않고 비디오만 생성')
    parser.add_argument('--test', action='store_true', help='테스트 모드 (업로드 없음)')
    
    args = parser.parse_args()
    
    # 자동화 시스템 초기화
    automation = YouTubeAutomation()
    
    # 업로드 여부
    upload = not args.no_upload and not args.test
    
    # 비디오 타입에 따라 생성
    if args.type == 'shorts':
        if args.count == 1:
            automation.create_video(topic=args.topic, upload=upload)
        else:
            automation.batch_create(count=args.count, upload=upload)
    
    elif args.type == 'longform':
        automation.create_longform_video(topic=args.topic, upload=upload)
    
    elif args.type == 'both':
        print("🎥 쇼츠와 롱폼 영상을 모두 생성합니다.\n")
        
        # 쇼츠 생성
        print("1️⃣  쇼츠 생성 중...")
        automation.create_video(topic=args.topic, upload=upload)
        
        # 잠시 대기
        import time
        time.sleep(5)
        
        # 롱폼 생성
        print("\n2️⃣  롱폼 비디오 생성 중...")
        automation.create_longform_video(topic=args.topic, upload=upload)


if __name__ == '__main__':
    main()
