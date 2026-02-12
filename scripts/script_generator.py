"""
스크립트 생성 모듈
Google Gemini API를 사용하여 흥미로운 팩트 영상 대본을 자동 생성합니다.
"""

import json
import random
import requests
import re
import time
from datetime import datetime


class ScriptGenerator:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.api_key = self.config['gemini_api_key']
        self.topics = self.config['content']['topics']
    
    def get_trending_topic(self, max_retries=5):
        """Gemini API에서 요즘 조회수/구독이 잘 되는 트렌디한 주제를 추천받습니다."""
        try:
            prompt = """현재 유튜브 쇼츠에서 조회수와 구독이 잘 나오는 한국 주제 3개를 추천해주세요.

요구사항:
- 한국인을 타겟으로 하는 고-조회수 주제만
- 각 주제는 한 줄씩만 (30자 이내)

다음 JSON 형식으로만 답변하세요:
{{"topics":["주제1","주제2","주제3"]}}"""
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
            
            for attempt in range(max_retries):
                try:
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }],
                        "generationConfig": {
                            "temperature": 0.5,
                            "maxOutputTokens": 100,
                        }
                    }
                    
                    response = requests.post(url, json=payload, timeout=10)
                    
                    # 429 Too Many Requests 처리 - Retry-After 헤더 우선 사용
                    if response.status_code == 429:
                        # Retry-After 헤더에서 대기 시간 가져오기 (초 단위)
                        retry_after = response.headers.get('Retry-After', None)
                        if retry_after:
                            wait_time = int(retry_after) + 2  # 여유 시간 추가
                        else:
                            # Retry-After 없으면 지수 백오프
                            wait_time = min(2 ** attempt + random.uniform(0, 2), 60)
                        
                        print(f"⏳ API 레이트 제한 (429). {wait_time}초 대기 후 재시도 ({attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # 응답 파싱
                    if not data.get('candidates'):
                        print(f"⚠️ 빈 응답, 재시도 {attempt + 1}/{max_retries}")
                        continue
                    
                    content = data['candidates'][0]['content']['parts'][0]['text']
                    
                    # JSON 추출
                    content = content.strip()
                    json_match = re.search(r'\{[^{}]*"topics"[^{}]*\}', content)
                    if not json_match:
                        json_match = re.search(r'\{[\s\S]*?\}', content)
                    
                    if json_match:
                        json_str = json_match.group()
                        result = json.loads(json_str)
                        trending_topics = result.get('topics', [])
                        trending_topics = [t.strip() for t in trending_topics if t and isinstance(t, str) and len(t.strip()) > 0]
                        
                        if trending_topics:
                            print(f"🔥 트렌디한 주제 {len(trending_topics)}개 추천받음!")
                            return trending_topics
                    else:
                        print(f"⚠️ JSON 찾지 못함, 재시도 {attempt + 1}/{max_retries}")
                        continue
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON 파싱 실패, 재시도 {attempt + 1}/{max_retries}: {str(e)[:50]}")
                except requests.exceptions.Timeout:
                    print(f"⏱️ 요청 타임아웃, 재시도 {attempt + 1}/{max_retries}")
                    time.sleep(2)
                except requests.exceptions.RequestException as e:
                    print(f"⚠️ API 요청 오류, 재시도 {attempt + 1}/{max_retries}: {str(e)[:50]}")
                    time.sleep(1)
            
            print("⚠️ 트렌디한 주제 추천 실패 - 고정 주제 사용으로 전환")
        
        except Exception as e:
            print(f"⚠️ 트렌디한 주제 생성 실패: {str(e)[:100]}")
        
        return None
    
    def generate_script(self, topic=None, max_retries=5):
        """팩트 영상 대본을 생성합니다."""
        if topic is None:
            # 50% 확률로 트렌디한 주제 추천, 50% 확률로 고정 주제 사용 (레이트 제한 완화)
            use_trending = random.random() < 0.5
            
            if use_trending:
                trending = self.get_trending_topic()
                if trending:
                    topic = random.choice(trending)
                    print(f"✅ 트렌디한 주제 선택: {topic}")
                    # 트렌디한 주제 사용 후 3초 대기 (두 API 호출 사이의 레이트 제한 완화)
                    time.sleep(3)
                else:
                    topic = random.choice(self.topics)
                    print(f"📌 고정 주제 선택: {topic}")
            else:
                topic = random.choice(self.topics)
                print(f"📌 고정 주제 선택: {topic}")
        
        prompt = f"""유튜브 쇼츠 대본 작성. 주제: {topic}

요구사항:
- 첫 문장: 충격적인 훅 (반드시 "?" 또는 "!" 포함)
- 50초 분량 (약 100-120단어)
- 짧고 강렬한 문장
- 시청자의 호기심을 자극하는 질문형 문장 2-3개 포함
- 끝: 주제를 정리하는 마무리 문장과 구독 유도 문장 ("!" 포함)
- 주의: 대본에는 절대 이모티콘을 포함하지 마세요

설명 작성 요구사항:
- 3~5줄의 풍성한 설명 (총 200자 이상)
- 이모티콘 5개 이상 활용 (💰 🧠 📚 🎯 ✨ 등)
- 첫줄: 영상 요약 (한 문장)
- 둘째줄: 왜 봐야하는지 (한 문장)
- 셋째줄: 주요 포인트 (한 문장 또는 2줄)
- 마지막줄: 행동 유도 (댓글, 구독, 공유 독려)

태그 요구사항:
- 정확히 5개의 태그 생성
- 조회수 잘 나오는 인기 태그 위주
- 영상 주제와 정확히 관련된 태그만
- 예: #shorts #팩트 #꿀팁 같은 검색량 많은 태그 포함

JSON 출력:
{{"hook":"훅 문장","script":"전체 대본 (이모티콘 제외)","title":"영상 제목 (이모티콘 제외)","description":"이모티콘 포함 풍성한 설명 200자 이상","tags":["태그1","태그2","태그3","태그4","태그5"]}}

JSON만 출력."""
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        
        for attempt in range(max_retries):
            try:
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 2048,
                    }
                }
                
                response = requests.post(url, json=payload, timeout=15)
                
                # 429 Too Many Requests 처리 - Retry-After 헤더 우선 사용
                if response.status_code == 429:
                    # Retry-After 헤더에서 대기 시간 가져오기 (초 단위)
                    retry_after = response.headers.get('Retry-After', None)
                    if retry_after:
                        wait_time = int(retry_after) + 2  # 여유 시간 추가
                    else:
                        # Retry-After 없으면 지수 백오프 (더 긴 대기)
                        wait_time = min(2 ** attempt + random.uniform(0, 3), 120)
                    
                    print(f"⏳ API 레이트 제한 (429). {wait_time}초 대기 후 재시도 ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                
                data = response.json()
                
                # 응답이 비어있는지 확인
                if not data.get('candidates'):
                    print(f"⚠️ 빈 응답, 재시도 {attempt + 1}/{max_retries}")
                    time.sleep(1)
                    continue
                
                # 응답이 완료되었는지 확인
                finish_reason = data['candidates'][0].get('finishReason', 'UNKNOWN')
                if finish_reason == 'MAX_TOKENS':
                    print(f"⚠️ 응답이 잘림, 재시도 {attempt + 1}/{max_retries}")
                    continue
                
                content = data['candidates'][0]['content']['parts'][0]['text']
                
                # JSON 파싱 (마크다운 코드블록 제거)
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                # JSON 추출 시도 (중괄호 사이의 내용만 추출)
                json_match = re.search(r'\{[\s\S]*?\}', content)
                if json_match:
                    json_str = json_match.group()
                    result = json.loads(json_str)
                    result['topic'] = topic
                    result['generated_at'] = datetime.now().isoformat()
                    return result
                else:
                    print(f"⚠️ JSON 형식 찾지 못함, 재시도 {attempt + 1}/{max_retries}")
                    continue
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON 파싱 오류, 재시도 {attempt + 1}/{max_retries}: {str(e)[:50]}")
                if attempt == max_retries - 1:
                    print(f"   응답 미리보기: {content[:100]}...")
            except requests.exceptions.Timeout:
                print(f"⏱️ 요청 타임아웃, 재시도 {attempt + 1}/{max_retries}")
                time.sleep(2)
            except requests.exceptions.RequestException as e:
                error_msg = str(e)[:100]
                print(f"⚠️ API 요청 오류, 재시도 {attempt + 1}/{max_retries}: {error_msg}")
                time.sleep(1)
            except Exception as e:
                error_msg = str(e)[:100]
                print(f"⚠️ 예기치 않은 오류, 재시도 {attempt + 1}/{max_retries}: {error_msg}")
                time.sleep(1)
        
        print("❌ 최대 재시도 횟수 초과")
        return None
    
    def save_script(self, script_data, filename=None):
        """생성된 스크립트를 파일로 저장합니다."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/script_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 스크립트 저장 완료: {filename}")
        return filename


if __name__ == "__main__":
    # 테스트 실행
    generator = ScriptGenerator()
    
    print("📝 스크립트 생성 중...")
    script = generator.generate_script()
    
    if script:
        print("\n=== 생성된 스크립트 ===")
        print(f"제목: {script['title']}")
        print(f"주제: {script['topic']}")
        print(f"\n대본:\n{script['script']}")
        print(f"\n썸네일 텍스트: {script['thumbnail_text']}")
        
        # 저장
        generator.save_script(script)
