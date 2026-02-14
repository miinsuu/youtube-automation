"""
롱폼 비디오(10-15분) 스크립트 생성 모듈
깊이 있는 스토리텔링으로 감정과 영감을 전달하는 콘텐츠를 생성합니다.
"""

import json
import random
import sys
import re
import time
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class LongformScriptGenerator:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Gemini API 설정
        api_key = self.config.get('gemini_api_key')
        if api_key and genai:
            # Warning 내났제
            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            warnings.filterwarnings('ignore', category=FutureWarning)
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
        
        self.topics = self.config.get('content', {}).get('longform', {}).get('topics', [])
        self.target_length = "10-15분"
    
    def generate_script(self, topic=None):
        """롱폼 스크립트 생성"""
        if not topic:
            topic = random.choice(self.topics)
        
        print(f"\n📚 롱폼 스크립트 생성 중: {topic}")
        
        # 프롬프트 작성
        prompt = self._create_prompt(topic)
        
        try:
            if not self.model:
                print("❌ Gemini 모델이 초기화되지 않았습니다. API 키를 확인해주세요.")
                return None
            
            # Gemini API 호출 (재시도 포함)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    script_text = response.text
                    break
                except Exception as e:
                    err_msg = str(e)
                    if attempt < max_retries - 1 and ('500' in err_msg or 'internal' in err_msg.lower() or 'unavailable' in err_msg.lower()):
                        wait = (attempt + 1) * 5
                        print(f"⚠️ Gemini API 오류 (시도 {attempt+1}/{max_retries}): {err_msg[:100]}")
                        print(f"🔄 {wait}초 후 재시도...")
                        time.sleep(wait)
                    else:
                        raise
            
            # 스크립트 파싱
            title, detailed_script = self._parse_script(script_text, topic)
            
            script_data = {
                "type": "longform",
                "topic": topic,
                "title": title,
                "script": detailed_script,
                "estimated_duration": "10-15분",
                "content_type": "storytelling",
                "generated_at": datetime.now().isoformat()
            }
            
            print(f"✅ 제목: {title}")
            print(f"✅ 스토리 줄 수: {len(detailed_script.split(chr(10)))}")
            
            return script_data
        
        except Exception as e:
            print(f"❌ 스크립트 생성 실패: {str(e)}")
            return None
    
    def _create_prompt(self, topic):
        """롱폼 스크립트 생성 프롬프트"""
        return f"""당신은 감정적인 스토리텔링 전문가입니다. 
YouTube 롱폼 비디오(10-15분, 약 2000-2500단어)를 위한 깊이 있는 스크립트를 만들어주세요.

주제: {topic}

요구사항:
1. 제목: 시청자의 감정을 건드리는 임팩트 있는 제목 (20자 이내)
2. 구조:
   - 오프닝: 시청자의 관심을 끌고 메인 메시지를 소개 (200단어)
   - 본론1: 구체적인 사례나 경험 공유 (400-500단어)
   - 본론2: 다른 관점의 깊이 있는 이야기 (400-500단어)
   - 본론3: 변화와 교훈 (400-500단어)
   - 클로징: 시청자에게 남길 메시지와 행동 촉구 (200단어)

3. 톤: 
   - 따뜻하고 공감적
   - 진솔하고 진정성 있음
   - 영감을 주고 희망적
   - 과장 없이 자연스러움

4. 콘텐츠:
   - 실제 있을 법한 이야기나 통계 포함
   - 감정적 변곡점 포함
   - 시청자가 자신의 이야기로 느낄 수 있도록
   - 실용적인 조언이나 교훈 포함

5. 형식:
   - 각 문단을 명확히 구분
   - 자연스러운 음성 전달용 문체 (TTS로 읽힐 문장)
   - 쉬어가는 부분(음... 또는 생각해보니...) 포함
   - 감정 표현(마음이 아팠어요, 정말 감사합니다 등) 자연스럽게 포함

6. 주의사항 (매우 중요):
   - 절대 마크다운 서식을 사용하지 마세요 (**, *, #, ## 등 금지)
   - 절대 섹션 헤더나 구분자를 본문에 넣지 마세요 ([오프닝], [스토리 1], [클로징] 등 금지)
   - 이 스크립트는 TTS 음성으로 직접 읽혀집니다. 구조 표시용 태그가 들어가면 그대로 발화됩니다.
   - 각 파트의 전환은 자연스러운 문장으로 연결하세요 (예: "자, 이제 또 다른 이야기를 해볼게요.")
   - 순수하게 사람이 말하는 것처럼 자연스러운 문장만 작성하세요

출력 형식:
[제목]
제목을 여기에 작성하세요

[스크립트]
본문 내용을 여기에 작성하세요. 각 문단은 개행으로 구분하세요.

자세하고 감정적인 스크립트를 작성해주세요."""
    
    def _parse_script(self, response_text, topic):
        """생성된 응답에서 제목과 스크립트 추출"""
        lines = response_text.strip().split('\n')
        
        title = topic
        script_start = 0
        
        # 제목 찾기
        for i, line in enumerate(lines):
            if '[제목]' in line:
                # 다음 줄이 제목
                if i + 1 < len(lines):
                    title = lines[i + 1].strip()
                    if len(title) > 100:  # 너무 긴 제목 정리
                        title = title[:80]
            elif '[스크립트]' in line:
                script_start = i + 1
                break
        
        # 스크립트 추출
        if script_start > 0:
            script = '\n'.join(lines[script_start:]).strip()
        else:
            script = response_text.strip()
        
        # ── 마크다운 서식 및 섹션 헤더 제거 (TTS용 정리) ──
        import re
        
        # **텍스트** → 텍스트 (볼드 제거)
        script = re.sub(r'\*\*(.+?)\*\*', r'\1', script)
        # *텍스트* → 텍스트 (이탤릭 제거)
        script = re.sub(r'\*(.+?)\*', r'\1', script)
        # ## 헤더 → 제거
        script = re.sub(r'^#{1,6}\s+', '', script, flags=re.MULTILINE)
        
        # [오프닝], [스토리 1], [클로징] 등 섹션 태그가 포함된 줄 제거
        # 패턴: 줄 전체가 [태그] 또는 [태그] 제목텍스트 형태
        script = re.sub(
            r'^\[(?:오프닝|스토리\s*\d*|본론\s*\d*|클로징|엔딩|인트로|아웃트로|마무리|전환|섹션\s*\d*)\].*$',
            '', script, flags=re.MULTILINE | re.IGNORECASE
        )
        
        # 영어 섹션 태그도 제거
        script = re.sub(
            r'^\[(?:Opening|Story\s*\d*|Section\s*\d*|Closing|Intro|Outro)\].*$',
            '', script, flags=re.MULTILINE | re.IGNORECASE
        )
        
        # --- 또는 === 등 구분선 제거
        script = re.sub(r'^[-=]{3,}$', '', script, flags=re.MULTILINE)
        
        # 빈 줄 정리 (연속 빈 줄 → 단일 빈 줄)
        script = '\n'.join([line.strip() for line in script.split('\n') if line.strip()])
        
        return title, script
    
    def save_script(self, script_data, output_path):
        """스크립트 저장"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 스크립트 저장됨: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 스크립트 저장 실패: {str(e)}")
            return False
    
    def get_random_topic(self):
        """랜덤 토픽 반환"""
        return random.choice(self.topics) if self.topics else "성공한 사람들의 일상 습관"

    # ──────────────────────────────────────────────────
    # YouTube 메타데이터 생성 (제목 / 설명 / 해시태그 / 고정댓글)
    # ──────────────────────────────────────────────────
    def generate_metadata(self, script_data):
        """Gemini로 YouTube 업로드용 메타데이터 생성
        Returns: dict with title, description, hashtags, tags, pinned_comment
        """
        if not self.model:
            print("⚠️ Gemini 모델 없음 — 기본 메타데이터 사용")
            return self._fallback_metadata(script_data)

        raw_title = script_data.get('title', '')
        topic = script_data.get('topic', '')
        script_preview = script_data.get('script', '')[:600]

        prompt = f"""당신은 YouTube SEO 전문가입니다.
아래 롱폼 영상의 제목, 설명글, 해시태그, 고정댓글을 생성해주세요.

원본 제목: {raw_title}
주제: {topic}
스크립트 일부: {script_preview}

## 규칙 (반드시 지켜주세요)
1. **마크다운 서식 절대 금지**: **, *, #, ##, [], --- 등 마크다운 문법을 사용하지 마세요.
2. **이모지 적극 활용**: 각 항목에 어울리는 이모지를 넣어 시선을 끌게 만드세요.
3. **조회수/구독 유도**: 시청자가 클릭하고 싶은 호기심 자극 문구를 사용하세요.

## 출력 형식 (정확히 이 형식으로 출력)

[TITLE]
이모지 포함 매력적인 제목 (40자 이내, 클릭 유도)

[DESCRIPTION]
3-5줄의 영상 설명 (이모지 포함, 핵심 내용 요약)
빈 줄 후 시청 유도 문구 (좋아요/구독/알림 등)
빈 줄 후 채널 소개 한 줄

[HASHTAGS]
#태그1 #태그2 #태그3 ... (10-15개, 공백 구분)

[TAGS]
태그1,태그2,태그3,... (쉼표 구분, 15-20개, YouTube 검색 키워드)

[PINNED_COMMENT]
고정댓글 내용 (이모지 포함, 공감 유도 + 댓글 참여 유도 질문)

주의: 마크다운 문법(**, *, ##, [] 등)을 절대 사용하지 마세요. 순수 텍스트 + 이모지만 사용하세요."""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return self._parse_metadata(response.text, script_data)
            except Exception as e:
                err_msg = str(e)
                if attempt < max_retries - 1 and ('500' in err_msg or 'internal' in err_msg.lower() or 'unavailable' in err_msg.lower()):
                    wait = (attempt + 1) * 5
                    print(f"⚠️ Gemini API 오류 (시도 {attempt+1}/{max_retries}): {err_msg[:100]}")
                    print(f"🔄 {wait}초 후 재시도...")
                    time.sleep(wait)
                else:
                    print(f"⚠️ 메타데이터 생성 실패: {e} — 기본값 사용")
                    return self._fallback_metadata(script_data)
        return self._fallback_metadata(script_data)

    def _parse_metadata(self, text, script_data):
        """Gemini 응답에서 메타데이터 파싱 + 마크다운 필터링"""

        def extract_section(label):
            pattern = rf'\[{label}\]\s*\n(.*?)(?=\n\[|$)'
            m = re.search(pattern, text, re.DOTALL)
            return m.group(1).strip() if m else ''

        title = extract_section('TITLE') or script_data.get('title', '')
        description = extract_section('DESCRIPTION')
        hashtags_raw = extract_section('HASHTAGS')
        tags_raw = extract_section('TAGS')
        pinned_comment = extract_section('PINNED_COMMENT')

        # 마크다운 필터링
        title = self._clean_markdown(title)
        description = self._clean_markdown(description)
        hashtags_raw = self._clean_markdown(hashtags_raw)
        pinned_comment = self._clean_markdown(pinned_comment)

        # 해시태그 파싱
        hashtags = re.findall(r'#\S+', hashtags_raw)
        if not hashtags:
            hashtags = ['#스토리', '#감동', '#영감', '#일상', '#자기계발']

        # 태그 배열 파싱
        if tags_raw:
            tags = [t.strip() for t in tags_raw.replace('#', '').split(',') if t.strip()]
        else:
            tags = ['스토리', '감동', '일상', '성공', '영감', '이야기']

        # 설명 + 해시태그 합치기
        if description:
            description = description.rstrip() + "\n\n" + " ".join(hashtags)
        else:
            description = self._fallback_metadata(script_data)['description']

        # 제목 길이 제한 (YouTube 100자)
        if len(title) > 95:
            title = title[:92] + "..."

        result = {
            'title': title,
            'description': description,
            'hashtags': hashtags,
            'tags': tags,
            'pinned_comment': pinned_comment or self._fallback_pinned_comment(script_data),
        }

        print(f"✅ 메타데이터 생성 완료")
        print(f"   제목: {title}")
        print(f"   설명: {len(description)}자")
        print(f"   해시태그: {len(hashtags)}개")
        print(f"   태그: {len(tags)}개")
        print(f"   고정댓글: {len(pinned_comment)}자")

        return result

    def _clean_markdown(self, text):
        """마크다운 서식 완전 제거"""
        if not text:
            return text
        # **볼드** → 텍스트
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        # *이탤릭* → 텍스트
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        # ## 헤더 → 제거
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # [텍스트](링크) → 텍스트
        text = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', text)
        # --- 구분선 → 제거
        text = re.sub(r'^[-=]{3,}$', '', text, flags=re.MULTILINE)
        # [섹션 태그] → 제거
        text = re.sub(
            r'^\[(?:오프닝|스토리\s*\d*|본론\s*\d*|클로징|엔딩|인트로|아웃트로|마무리)\].*$',
            '', text, flags=re.MULTILINE | re.IGNORECASE
        )
        # 연속 빈 줄 정리
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _fallback_metadata(self, script_data):
        """Gemini 실패 시 기본 메타데이터"""
        title = self._clean_markdown(script_data.get('title', '새로운 이야기'))
        topic = script_data.get('topic', '')

        description = (
            f"🎬 {title}\n\n"
            f"📌 오늘의 주제: {topic}\n\n"
            f"따뜻한 이야기와 깊은 감동을 전합니다.\n"
            f"이 영상이 여러분의 하루에 작은 위로가 되길 바랍니다.\n\n"
            f"❤️ 공감이 되셨다면 좋아요를 눌러주세요\n"
            f"🔔 매일 새로운 이야기가 올라옵니다 — 구독과 알림 설정!\n"
            f"💬 여러분의 이야기도 댓글로 들려주세요\n\n"
            f"#스토리 #감동 #영감 #일상 #자기계발"
        )

        return {
            'title': f"🎯 {title}",
            'description': description,
            'hashtags': ['#스토리', '#감동', '#영감', '#일상', '#자기계발'],
            'tags': ['스토리', '감동', '일상', '성공', '영감', '이야기', '자기계발', '동기부여'],
            'pinned_comment': self._fallback_pinned_comment(script_data),
        }

    def _fallback_pinned_comment(self, script_data):
        """기본 고정댓글"""
        title = self._clean_markdown(script_data.get('title', ''))
        return (
            f"🙏 끝까지 시청해주셔서 정말 감사합니다!\n\n"
            f"💬 여러분은 이 이야기를 듣고 어떤 생각이 드셨나요?\n"
            f"댓글로 여러분의 경험이나 생각을 나눠주세요 😊\n\n"
            f"❤️ 이 영상이 도움이 되셨다면 좋아요 한 번 부탁드려요!\n"
            f"🔔 구독과 알림 설정하시면 매일 새로운 이야기를 받아보실 수 있어요"
        )


if __name__ == "__main__":
    generator = LongformScriptGenerator()
    
    # 테스트
    script = generator.generate_script()
    if script:
        print("\n" + "="*60)
        print(f"제목: {script['title']}")
        print(f"주제: {script['topic']}")
        print("="*60)
        print(f"스크립트 (처음 500자):\n{script['script'][:500]}...")
        
        # 저장
        generator.save_script(script, "output/test_longform_script.json")
