"""
TTS 음성 생성 모듈
Edge TTS를 사용하여 대본을 자연스러운 음성으로 변환합니다.
"""

import json
import asyncio
import edge_tts
from pydub import AudioSegment
import os
import time


class TTSGenerator:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.language = self.config['tts']['language']
        self.speed = self.config['tts'].get('speed', 1.0)
        # 한국어 여성 음성 (자연스럽고 인기 있는 목소리)
        self.voice = self.config['tts'].get('voice', 'ko-KR-SunHiNeural')
    
    async def _generate_speech_with_timing(self, text, output_path):
        """Edge TTS로 음성 생성 + 타이밍 정보 추출 (비동기, 타임아웃 보호)"""
        # 속도 조절 문자열
        rate = f"+{int((self.speed - 1) * 100)}%" if self.speed >= 1 else f"{int((self.speed - 1) * 100)}%"
        
        max_retries = 7
        retry_delay = 3  # 초 (지수 백오프 기저)
        tts_timeout = 120  # 초 (WebSocket 무한 행 방지)
        
        for attempt in range(max_retries):
            try:
                async def _do_stream():
                    communicate = edge_tts.Communicate(text, self.voice, rate=rate)
                    sentence_timings = []
                    with open(output_path, "wb") as f:
                        async for chunk in communicate.stream():
                            if chunk["type"] == "audio":
                                f.write(chunk["data"])
                            elif chunk["type"] == "SentenceBoundary":
                                start = chunk["offset"] / 10000000
                                duration = chunk["duration"] / 10000000
                                sentence_timings.append({
                                    "text": chunk["text"],
                                    "start": start,
                                    "end": start + duration,
                                    "duration": duration
                                })
                    return sentence_timings
                
                return await asyncio.wait_for(_do_stream(), timeout=tts_timeout)
                
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = min(retry_delay * (2 ** attempt), 60)
                    print(f"⚠️  TTS 타임아웃 ({tts_timeout}초), {wait_time}초 후 재시도 ({attempt + 1}/{max_retries})...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    print(f"❌ TTS 타임아웃 계속됨 ({max_retries}회 재시도 후 실패)")
                    raise
            except Exception as e:
                if "503" in str(e) or "Invalid response status" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = min(retry_delay * (2 ** attempt), 60)
                        print(f"⚠️  TTS 서버 오류 (503), {wait_time}초 후 재시도 ({attempt + 1}/{max_retries})...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ TTS 서버 오류가 계속됨 ({max_retries}회 재시도 후 실패)")
                        raise
                else:
                    raise
    
    async def _generate_speech(self, text, output_path):
        """Edge TTS로 음성 생성 (비동기, 타임아웃 보호)"""
        # 속도 조절 문자열
        rate = f"+{int((self.speed - 1) * 100)}%" if self.speed >= 1 else f"{int((self.speed - 1) * 100)}%"
        
        max_retries = 7
        retry_delay = 3
        tts_timeout = 120  # 초
        
        for attempt in range(max_retries):
            try:
                communicate = edge_tts.Communicate(text, self.voice, rate=rate)
                await asyncio.wait_for(communicate.save(output_path), timeout=tts_timeout)
                return
                
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = min(retry_delay * (2 ** attempt), 60)
                    print(f"⚠️  TTS 타임아웃 ({tts_timeout}초), {wait_time}초 후 재시도 ({attempt + 1}/{max_retries})...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    print(f"❌ TTS 타임아웃 계속됨 ({max_retries}회 재시도 후 실패)")
                    raise
            except Exception as e:
                if "503" in str(e) or "Invalid response status" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = min(retry_delay * (2 ** attempt), 60)
                        print(f"⚠️  TTS 서버 오류 (503), {wait_time}초 후 재시도 ({attempt + 1}/{max_retries})...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ TTS 서버 오류가 계속됨 ({max_retries}회 재시도 후 실패)")
                        raise
                else:
                    raise
    
    def text_to_speech(self, text, output_path):
        """텍스트를 음성으로 변환합니다. (강화 재시도 + 음성 폴백)"""
        max_retries = 5
        # 대체 음성 (기본 음성 실패 시 폴백)
        fallback_voices = ['ko-KR-InJoonNeural', 'ko-KR-HyunsuNeural']
        
        for attempt in range(max_retries):
            try:
                # 3회 이상 실패하면 대체 음성 시도
                if attempt >= 3 and fallback_voices:
                    old_voice = self.voice
                    self.voice = fallback_voices[attempt - 3] if (attempt - 3) < len(fallback_voices) else fallback_voices[0]
                    print(f"🔄 대체 음성으로 전환: {old_voice} → {self.voice}")
                
                print(f"🎤 TTS 생성 중: {len(text)}자 (음성: {self.voice})")
                
                # Edge TTS로 음성 생성 + 타이밍 정보 (SentenceBoundary)
                sentence_timings = asyncio.run(self._generate_speech_with_timing(text, output_path))
                
                # 음성 길이 확인
                audio = AudioSegment.from_mp3(output_path)
                duration = len(audio) / 1000.0  # 초 단위
                
                # 타이밍 보정: Edge TTS SentenceBoundary 오프셋이 실제 오디오 길이와
                # 미세하게 어긋나는 문제 보정 (긴 텍스트일수록 누적 오차 커짐)
                if sentence_timings and duration > 0:
                    last_end = max(t['end'] for t in sentence_timings)
                    if last_end > 0 and abs(last_end - duration) > 0.1:
                        scale = duration / last_end
                        for t in sentence_timings:
                            t['start'] *= scale
                            t['end'] *= scale
                            t['duration'] = t['end'] - t['start']
                        print(f"   ⏱️ 타이밍 보정 적용: scale={scale:.4f} (오차 {last_end - duration:.2f}초)")
                
                print(f"✅ TTS 생성 완료: {output_path}")
                print(f"   음성 길이: {duration:.1f}초")
                print(f"   문장 타이밍: {len(sentence_timings)}개")
                
                return {
                    'path': output_path,
                    'duration': duration,
                    'sentence_timings': sentence_timings
                }
                
            except Exception as e:
                error_msg = str(e)
                is_transient = ("503" in error_msg or "Invalid response status" in error_msg
                                or "TimeoutError" in type(e).__name__)
                if is_transient:
                    if attempt < max_retries - 1:
                        wait_time = min(10 * (2 ** attempt), 120)  # 10, 20, 40, 80, 120초
                        print(f"⚠️  TTS 서버 오류, {wait_time}초 후 재시도 ({attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ TTS 생성 실패: Bing 서버 오류 - {max_retries}회 재시도 후에도 실패")
                        print("💡 팁: Bing 서버가 일시적으로 응답하지 않습니다. 잠시 후 다시 시도해주세요.")
                        return None
                else:
                    print(f"❌ TTS 생성 오류: {e}")
                    import traceback
                    traceback.print_exc()
                    return None
    
    def generate_from_script(self, script_data, output_dir="output/audio"):
        """스크립트 데이터에서 음성을 생성합니다."""
        os.makedirs(output_dir, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"audio_{timestamp}.mp3")
        
        return self.text_to_speech(script_data['script'], output_path)


if __name__ == "__main__":
    # 테스트 실행
    tts = TTSGenerator()
    
    test_script = {
        'script': '여러분은 알고 계셨나요? 인간의 뇌는 하루에 약 7만 개의 생각을 한다고 합니다. '
                 '이 중 80%가 부정적인 생각이라고 하죠. 이것은 우리 조상들이 위험으로부터 살아남기 위해 '
                 '발달시킨 생존 본능의 흔적입니다. 놀랍지 않나요?'
    }
    
    result = tts.generate_from_script(test_script)
    if result:
        print(f"\n✅ 테스트 완료: {result['path']}")
