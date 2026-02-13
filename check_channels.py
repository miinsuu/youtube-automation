#!/usr/bin/env python3
"""
YouTube 채널 정보 확인 및 검증 스크립트
현재 인증된 채널과 보유한 모든 채널을 확인할 수 있습니다.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from youtube_uploader import YouTubeUploader  # type: ignore
import json

def print_header(text):
    """헤더 출력"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_channels():
    """채널 정보 확인"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║     🎬 YouTube 채널 정보 확인 도구                        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    uploader = YouTubeUploader()
    
    # 인증
    print("🔐 YouTube API 인증 중...")
    if not uploader.authenticate():
        print("❌ 인증 실패!")
        return False
    
    # 현재 기본 채널 확인
    print_header("📍 현재 기본 채널")
    current_channel = uploader.get_authenticated_channel()
    
    if not current_channel:
        print("❌ 현재 채널 정보를 가져올 수 없습니다.")
        return False
    
    print(f"""
채널명: {current_channel['title']}
채널ID: {current_channel['id']}
설명: {current_channel.get('description', '(없음)')[:80]}...
    """)
    
    # 모든 채널 확인
    print_header("📺 보유한 모든 채널")
    channels = uploader.get_my_channels()
    
    if not channels:
        print("❌ 채널 목록을 가져올 수 없습니다.")
        return False
    
    print(f"\n총 {len(channels)}개의 채널을 찾았습니다:\n")
    
    for i, ch in enumerate(channels, 1):
        marker = "✓ [기본]" if ch['channel_id'] == current_channel['id'] else "  "
        print(f"{marker} {i}. {ch['title']}")
        print(f"      ID: {ch['channel_id']}")
        if ch.get('description'):
            desc_preview = ch['description'][:50] + ("..." if len(ch['description']) > 50 else "")
            print(f"      설명: {desc_preview}")
        print()
    
    # config 파일 확인
    print_header("⚙️  설정 파일 확인")
    
    config_path = "config/config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        target_channel_id = config.get('youtube', {}).get('target_channel_id')
        print(f"\n설정된 대상 채널 ID: {target_channel_id}")
        
        # 설정된 채널과 현재 채널 비교
        if target_channel_id == current_channel['id']:
            print("✅ 설정된 채널 = 현재 기본 채널 (일치함)")
        else:
            print("⚠️  설정된 채널 ≠ 현재 기본 채널 (불일치)")
            
            # 설정된 채널을 보유한 채널에서 찾기
            found = False
            for ch in channels:
                if ch['channel_id'] == target_channel_id:
                    print(f"\n설정된 채널: {ch['title']} ({target_channel_id})")
                    print(f"현재 기본 채널: {current_channel['title']} ({current_channel['id']})")
                    print("\n💡 해결 방법:")
                    print(f"   1. YouTube에서 '{ch['title']}' 채널로 전환")
                    print(f"   2. 터미널에서 실행: rm config/youtube_credentials.json")
                    print(f"   3. 다시 업로드: python main.py --count 1")
                    found = True
                    break
            
            if not found:
                print(f"\n⚠️  설정된 채널 ID({target_channel_id})를 찾을 수 없습니다.")
                print("   이 계정에서 찾을 수 있는 채널 ID로 config.json 업데이트:")
                print("\n   \"youtube\": {")
                print(f"     \"target_channel_id\": \"{channels[0]['channel_id']}\"")
                print("   }")
    
    # 요약
    print_header("✅ 체크리스트")
    print(f"""
□ 현재 기본 채널: {current_channel['title']} ({current_channel['id']})
□ 설정된 대상 채널: {target_channel_id if target_channel_id else '(미설정)'}
□ 보유한 채널 수: {len(channels)}개

다음 단계:
{'✓ 설정이 일치하므로 업로드를 진행하세요.' if target_channel_id == current_channel['id'] else '⚠️  기본 채널을 변경한 후 다시 인증하세요.'}
    """)
    
    return True

def main():
    """메인 함수"""
    try:
        success = check_channels()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⛔ 중단됨")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
