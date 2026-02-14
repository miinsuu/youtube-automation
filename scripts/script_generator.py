"""
쇼츠 스크립트 + 메타데이터 + 이미지 프롬프트 통합 생성 모듈
Google Gemini API 2.5 Flash를 사용하여
구조화된 쇼츠 데이터(제목, 설명, 해시태그, 고정댓글, 5장 이미지 프롬프트, TTS 대본)를 생성합니다.
"""

import json
import random
import re
import os
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    print("⚠️ google-generativeai 패키지를 설치해주세요: pip install google-generativeai")
    raise


class ScriptGenerator:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # Gemini API 설정
        self.api_key = self.config.get('gemini_api_key') or os.environ.get('GOOGLE_API_KEY')
        if not self.api_key or 'YOUR_GEMINI_API_KEY' in self.api_key:
            raise ValueError("❌ Gemini API 키가 필요합니다.\n"
                           "1. https://aistudio.google.com/apikey 에서 API 키 발급\n"
                           "2. config.json에서 gemini_api_key 입력하거나\n"
                           "3. GOOGLE_API_KEY 환경변수 설정")

        # Warning 억제
        import warnings
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.filterwarnings('ignore', category=FutureWarning)

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.topics = self.config['content']['shorts']['topics']
        print(f"✅ Gemini 2.5 Flash API 초기화 완료 (쇼츠)")

    # ──────────────────────────────────────────────────
    # 트렌디한 주제 추천
    # ──────────────────────────────────────────────────
    def get_trending_topic(self):
        """Gemini API에서 요즘 조회수/구독이 잘 되는 트렌디한 주제를 추천받습니다."""
        try:
            prompt = """현재 유튜브 쇼츠에서 조회수와 구독이 잘 나오는 한국 주제 3개를 추천해주세요.

요구사항:
- 한국인을 타겟으로 하는 고-조회수 주제만
- 각 주제는 한 줄씩만 (30자 이내)

다음 JSON 형식으로만 답변하세요:
{"topics":["주제1","주제2","주제3"]}"""

            response = self.model.generate_content(prompt)
            content = response.text.strip()

            json_match = re.search(r'\{[^{}]*"topics"[^{}]*\}', content)
            if not json_match:
                json_match = re.search(r'\{[\s\S]*?\}', content)

            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                trending_topics = result.get('topics', [])
                trending_topics = [t.strip() for t in trending_topics
                                   if t and isinstance(t, str) and len(t.strip()) > 0]
                if trending_topics:
                    print(f"🔥 트렌디한 주제 {len(trending_topics)}개 추천받음!")
                    return trending_topics

        except Exception as e:
            print(f"⚠️ 트렌디한 주제 추천 실패: {str(e)[:100]}")

        print("⚠️ 트렌디한 주제 추천 실패 - 고정 주제 사용으로 전환")
        return None

    # ──────────────────────────────────────────────────
    # 메인 생성: 스크립트 + 메타데이터 + 이미지 프롬프트
    # ──────────────────────────────────────────────────
    def generate_script(self, topic=None):
        """구조화된 쇼츠 데이터를 한 번에 생성합니다.

        Returns:
            dict with keys:
                title, hashtags, description, pinned_comment,
                image_prompts (list of 5), script (TTS용),
                tags, topic, hook, generated_at
        """
        if not self.model:
            print("❌ Gemini 모델이 초기화되지 않았습니다.")
            return None

        if topic is None:
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

        prompt = self._build_prompt(topic)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                raw = response.text.strip()
                result = self._parse_response(raw, topic)
                if result:
                    print(f"✅ 쇼츠 데이터 생성 완료: {result.get('title', 'N/A')}")
                return result

            except Exception as e:
                err_msg = str(e)
                if attempt < max_retries - 1 and ('500' in err_msg or 'internal' in err_msg.lower() or 'unavailable' in err_msg.lower()):
                    import time
                    wait = (attempt + 1) * 5
                    print(f"⚠️ Gemini API 오류 (시도 {attempt+1}/{max_retries}): {err_msg[:100]}")
                    print(f"🔄 {wait}초 후 재시도...")
                    time.sleep(wait)
                else:
                    print(f"❌ 스크립트 생성 실패: {str(e)[:150]}")
                    return None
        return None

    # ──────────────────────────────────────────────────
    # Gemini 프롬프트 빌드
    # ──────────────────────────────────────────────────
    def _build_prompt(self, topic):
        """쇼츠 통합 데이터를 생성하는 Gemini 프롬프트"""
        return f"""당신은 유튜브 쇼츠 전문 크리에이터이자 AI 이미지 프롬프트 엔지니어입니다.
아래 주제로 한국인 대상 유튜브 쇼츠를 위한 완전한 데이터 패키지를 만들어주세요.

주제: {topic}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[규칙 — 반드시 지켜주세요]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 마크다운 서식(**, *, #, ##, [], ---)을 절대 사용하지 마세요.
2. 모든 텍스트는 순수 텍스트 + 이모지만 사용합니다.
3. TTS 대본에는 이모지, 특수기호, 마크다운을 절대 넣지 마세요.
4. TTS 대본에서 숫자는 아라비아 숫자 그대로 쓰세요 (예: 3가지, 100만 원 등). 한글 숫자 금지.
5. 이미지 프롬프트는 영어로 작성하세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[출력 형식 — 정확히 이 형식으로 출력]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[TITLE]
이모지 포함 매력적인 제목 (40자 이내, 클릭 유도, 시청자의 호기심 자극)

[HASHTAGS]
#태그1 #태그2 #태그3 ... (7-10개, 공백 구분, 조회수 잘 나오는 인기 해시태그)

[DESCRIPTION]
3~5줄의 풍성한 영상 설명 (총 200자 이상)
- 첫줄: 영상 핵심 요약 + 이모지 (호기심 자극)
- 둘째줄: 왜 봐야 하는지 + 이모지
- 셋째줄: 주요 포인트 요약
- 마지막줄: 행동 유도 (좋아요/구독/댓글 독려) + 이모지

[PINNED_COMMENT]
고정댓글 내용 (이모지 포함, 공감 유도 + 체크리스트 형태의 행동 유도)
예시 형식:
여러분은 이 중 몇 개나 해보셨나요? 🤔
✅ 첫 번째 포인트
✅ 두 번째 포인트
✅ 세 번째 포인트
댓글로 알려주세요! 👇

[IMAGE_PROMPTS]
인트로부터 아웃트로까지 총 5장의 이미지 프롬프트를 각각 한 줄씩 작성하세요.
각 프롬프트는 영어, 3D render 스타일, 세로 비율(9:16) 최적화, 텍스트 없이 시각만으로 내용을 전달.
구조: 인트로(임팩트 있는 도입) / 섹션1 / 섹션2 / 섹션3 / 아웃트로(마무리 + 행동유도 느낌)
각 프롬프트 형식: PROMPT_N: 프롬프트 내용
PROMPT_1: (인트로 이미지 프롬프트)
PROMPT_2: (섹션1 이미지 프롬프트)
PROMPT_3: (섹션2 이미지 프롬프트)
PROMPT_4: (섹션3 이미지 프롬프트)
PROMPT_5: (아웃트로 이미지 프롬프트)

[TAGS]
태그1,태그2,태그3,... (쉼표 구분, 10-15개, YouTube 검색 키워드)

[SCRIPT]
TTS로 읽혀질 전체 대본 (한 덩어리 텍스트, 줄바꿈 없이 연속)
- 50~60초 분량 (약 100-150 단어)
- 첫 문장: 충격적인 훅 (반드시 ? 또는 ! 포함)
- 짧고 강렬한 문장
- 시청자의 호기심을 자극하는 질문형 문장 2-3개 포함
- 마무리: 핵심 정리 + 구독 유도 (! 포함)
- 이모지, 특수기호, 마크다운 절대 금지
- 숫자는 아라비아 숫자 그대로 사용 (예: 3가지, 5개, 100만 원)
- 포인트 나열 시 반드시 "첫째," "둘째," "셋째," 형태로 쉼표 포함
- 한 줄로 이어서 작성 (줄바꿈 금지)"""

    # ──────────────────────────────────────────────────
    # 응답 파싱
    # ──────────────────────────────────────────────────
    def _parse_response(self, text, topic):
        """Gemini 응답을 구조화된 dict로 파싱"""

        def extract_section(label):
            pattern = rf'\[{label}\]\s*\n(.*?)(?=\n\[|$)'
            m = re.search(pattern, text, re.DOTALL)
            return m.group(1).strip() if m else ''

        title = extract_section('TITLE') or topic
        hashtags_raw = extract_section('HASHTAGS')
        description = extract_section('DESCRIPTION')
        pinned_comment = extract_section('PINNED_COMMENT')
        image_prompts_raw = extract_section('IMAGE_PROMPTS')
        tags_raw = extract_section('TAGS')
        script = extract_section('SCRIPT')

        # 마크다운 필터링
        title = self._clean_markdown(title)
        description = self._clean_markdown(description)
        pinned_comment = self._clean_markdown(pinned_comment)

        # 해시태그 파싱
        hashtags = re.findall(r'#\S+', hashtags_raw)
        if not hashtags:
            hashtags = ['#쇼츠', '#꿀팁', '#정보', '#shorts', '#facts']

        # 태그 배열 파싱
        if tags_raw:
            tags = [t.strip() for t in tags_raw.replace('#', '').split(',') if t.strip()]
        else:
            tags = ['쇼츠', '팩트', '정보', 'shorts', 'facts']

        # 이미지 프롬프트 파싱 (PROMPT_1: ... 형태)
        image_prompts = []
        prompt_pattern = re.findall(r'PROMPT_\d+:\s*(.+)', image_prompts_raw)
        if prompt_pattern:
            image_prompts = [p.strip() for p in prompt_pattern]

        # 프롬프트가 5개 미만이면 줄 단위로도 시도
        if len(image_prompts) < 5:
            lines = [l.strip() for l in image_prompts_raw.split('\n')
                     if l.strip() and not l.strip().startswith('[')]
            # PROMPT_N: 이미 파싱된 것 제외하고 남은 줄 추가
            for line in lines:
                cleaned = re.sub(r'^PROMPT_\d+:\s*', '', line).strip()
                if cleaned and cleaned not in image_prompts:
                    image_prompts.append(cleaned)
                if len(image_prompts) >= 5:
                    break

        # 그래도 5개 미만이면 기본 프롬프트 추가
        default_prompts = [
            f"3D render, dramatic intro scene, eye-catching visual about {topic}, dark cinematic lighting, vertical composition 9:16, no text",
            f"3D render, educational infographic style, key fact visualization about {topic}, modern design, vertical 9:16, no text",
            f"3D render, detailed explanation scene, important information about {topic}, professional look, vertical 9:16, no text",
            f"3D render, surprising reveal moment about {topic}, dynamic composition, glowing elements, vertical 9:16, no text",
            f"3D render, conclusive outro scene, call to action feeling, success theme related to {topic}, vertical 9:16, no text",
        ]
        while len(image_prompts) < 5:
            image_prompts.append(default_prompts[len(image_prompts)])

        image_prompts = image_prompts[:5]

        # TTS 스크립트 정리 (이모지/마크다운/줄바꿈 제거)
        script = self._clean_script_for_tts(script)

        # 훅 추출 (첫 문장)
        hook_match = re.match(r'^(.+?[?!])', script)
        hook = hook_match.group(1) if hook_match else script[:50]

        # 설명 + 해시태그 합치기
        if description:
            description = description.rstrip() + "\n\n" + " ".join(hashtags)

        # 제목 길이 제한
        if len(title) > 95:
            title = title[:92] + "..."

        if not script:
            print("⚠️ TTS 대본이 비어있습니다")
            return None

        result = {
            'title': title,
            'hashtags': hashtags,
            'description': description,
            'pinned_comment': pinned_comment,
            'image_prompts': image_prompts,
            'tags': tags,
            'script': script,
            'hook': hook,
            'topic': topic,
            'generated_at': datetime.now().isoformat(),
        }

        print(f"   제목: {title}")
        print(f"   해시태그: {len(hashtags)}개")
        print(f"   설명: {len(description)}자")
        print(f"   이미지 프롬프트: {len(image_prompts)}개")
        print(f"   대본: {len(script)}자")
        print(f"   고정댓글: {len(pinned_comment)}자")

        return result

    # ──────────────────────────────────────────────────
    # 유틸리티
    # ──────────────────────────────────────────────────
    @staticmethod
    def _clean_markdown(text):
        """마크다운 서식 완전 제거"""
        if not text:
            return text
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', text)
        text = re.sub(r'^[-=]{3,}$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @staticmethod
    def _clean_script_for_tts(text):
        """TTS 대본 정리 — 이모지/마크다운/줄바꿈 모두 제거, 한 줄 텍스트로"""
        if not text:
            return text
        # 마크다운 제거
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', text)
        text = re.sub(r'^[-=]{3,}$', '', text, flags=re.MULTILINE)
        # 이모지 제거 (유니코드 이모지 범위)
        text = re.sub(
            r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F'
            r'\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U0000FE0F\U0000200D]+',
            '', text
        )
        # 줄바꿈 → 공백 (한 줄로)
        text = re.sub(r'\s*\n\s*', ' ', text)
        # 다중 공백 정리
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    def save_script(self, script_data, filename=None):
        """생성된 스크립트를 파일로 저장합니다."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/script_{timestamp}.json"

        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 스크립트 저장 완료: {filename}")
        return filename


if __name__ == "__main__":
    generator = ScriptGenerator()

    print("📝 쇼츠 데이터 생성 중...")
    script = generator.generate_script()

    if script:
        print("\n=== 생성된 쇼츠 데이터 ===")
        print(f"제목: {script['title']}")
        print(f"주제: {script['topic']}")
        print(f"해시태그: {' '.join(script['hashtags'])}")
        print(f"\n설명:\n{script['description']}")
        print(f"\n고정댓글:\n{script['pinned_comment']}")
        print(f"\n이미지 프롬프트:")
        for i, p in enumerate(script['image_prompts'], 1):
            print(f"  {i}. {p[:80]}...")
        print(f"\nTTS 대본:\n{script['script']}")

        generator.save_script(script)
