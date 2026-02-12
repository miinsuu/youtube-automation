"""
스크립트 생성 모듈
Groq API (LLaMA 3.1)를 사용하여 흥미로운 팩트 영상 대본을 자동 생성합니다.
완전 무료 + 무제한 사용 가능
"""

import json
import random
import re
import os
from datetime import datetime

try:
    from groq import Groq
except ImportError:
    print("⚠️ groq 패키지를 설치해주세요: pip install groq")
    raise


class ScriptGenerator:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Groq API 설정
        self.groq_api_key = self.config.get('groq_api_key') or os.environ.get('GROQ_API_KEY')
        if not self.groq_api_key or 'YOUR_GROQ_API_KEY' in self.groq_api_key:
            raise ValueError("❌ Groq API 키가 필요합니다.\n"
                           "1. https://console.groq.com 에서 무료 회원가입\n"
                           "2. API 키 발급 받기\n"
                           "3. config.json에서 groq_api_key 입력하거나\n"
                           "4. GROQ_API_KEY 환경변수 설정")
        
        self.client = Groq(api_key=self.groq_api_key)
        self.topics = self.config['content']['topics']
        print(f"✅ Groq API 초기화 완료 (LLaMA 3.1 - 완전 무료!)")
    
    def get_trending_topic(self):
        """Groq LLaMA 3.1로 요즘 조회수/구독이 잘 되는 트렌디한 주제를 추천받습니다."""
        try:
            prompt = """현재 유튜브 쇼츠에서 조회수와 구독이 잘 나오는 한국 주제 3개를 추천해주세요.

요구사항:
- 한국인을 타겟으로 하는 고-조회수 주제만
- 각 주제는 한 줄씩만 (30자 이내)

다음 JSON 형식으로만 답변하세요:
{"topics":["주제1","주제2","주제3"]}"""
            
            message = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                max_tokens=150,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.choices[0].message.content.strip()
            
            # JSON 추출
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
        
        except Exception as e:
            print(f"⚠️ 트렌디한 주제 추천 실패: {str(e)[:100]}")
        
        print("⚠️ 트렌디한 주제 추천 실패 - 고정 주제 사용으로 전환")
        return None
    
    def generate_script(self, topic=None):
        """팩트 영상 대본을 생성합니다."""
        if topic is None:
            # 50% 확률로 트렌디한 주제 추천, 50% 확률로 고정 주제 사용
            use_trending = random.random() < 0.5
            
            if use_trending:
                trending = self.get_trending_topic()
                if trending:
                    topic = random.choice(trending)
                    print(f"✅ 트렌디한 주제 선택: {topic}")
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
        
        try:
            message = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                max_tokens=2500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.choices[0].message.content.strip()
            
            # JSON 파싱 (마크다운 코드블록 제거)
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
                print(f"✅ 스크립트 생성 완료: {result.get('title', 'N/A')}")
                return result
            else:
                print(f"⚠️ JSON 형식을 찾을 수 없습니다")
                print(f"응답: {content[:200]}...")
                return None
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {str(e)[:100]}")
            print(f"응답 미리보기: {content[:150]}...")
            return None
        except Exception as e:
            error_msg = str(e)[:150]
            print(f"❌ 스크립트 생성 실패: {error_msg}")
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
