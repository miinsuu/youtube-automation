"""
스크립트 생성 모듈
Google Gemini API를 사용하여 흥미로운 팩트 영상 대본을 자동 생성합니다.
"""

import json
import random
import requests
from datetime import datetime


class ScriptGenerator:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.api_key = self.config['gemini_api_key']
        self.topics = self.config['content']['topics']
    
    def generate_script(self, topic=None, max_retries=3):
        """팩트 영상 대본을 생성합니다."""
        if topic is None:
            topic = random.choice(self.topics)
        
        prompt = f"""유튜브 쇼츠 대본 작성. 주제: {topic}

요구사항:
- 첫 문장: 충격적인 훅 (반드시 "?" 또는 "!" 포함)
- 50초 분량 (약 100-120단어)
- 짧고 강렬한 문장
- 모든 문장 끝에 "!", "?", "..." 등 감정을 담은 문장부호 적극 사용
- 시청자의 호기심을 자극하는 질문형 문장 2-3개 포함
- 끝: 강렬한 감탄형 마무리 (예: "정말 놀랍지 않나요?!", "믿기 힘들죠?!")

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
- 예: #쇼츠 #팩트 #꿀팁 같은 검색량 많은 태그 포함

JSON 출력:
{{"hook":"훅 문장","script":"전체 대본","title":"영상 제목","description":"이모티콘 포함 풍성한 설명 200자 이상","tags":["태그1","태그2","태그3","태그4","태그5"],"thumbnail_text":"썸네일 3단어"}}

JSON만 출력."""
        
        for attempt in range(max_retries):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 4096,
                    }
                }
                
                response = requests.post(url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                
                # 응답이 완료되었는지 확인
                if data.get('candidates', [{}])[0].get('finishReason') == 'MAX_TOKENS':
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
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    content = json_match.group()
                
                result = json.loads(content)
                result['topic'] = topic
                result['generated_at'] = datetime.now().isoformat()
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON 파싱 오류, 재시도 {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    print(f"원본 응답: {content[:300]}...")
            except Exception as e:
                print(f"⚠️ 오류, 재시도 {attempt + 1}/{max_retries}: {e}")
        
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
