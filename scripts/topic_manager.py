"""
주제 이력 관리 모듈
이전에 사용한 주제를 추적하여 중복 생성을 방지합니다.
"""

import json
import os
from datetime import datetime, timedelta


HISTORY_FILE = "logs/topic_history.json"

# 의미없는/저품질 주제 필터링 키워드
BLOCKED_KEYWORDS = [
    "밈", "meme", "트렌드 밈", "짤", "유행어", "챌린지",
    "tiktok", "틱톡", "릴스", "viral", "바이럴",
    "드립", "인터넷 밈", "짤방", "웃긴",
    # 채널 컨셉과 맞지 않는 주제
    "요리", "레시피", "recipe", "cooking", "cook",
    "편의점", "다이소", "daiso", "먹방", "mukbang",
    "음식", "맛집", "식당", "카페", "베이킹", "baking",
]

# YouTube 채널에 이미 올라와 있는 영상 제목 (런타임에 설정)
_youtube_titles = []
_youtube_titles_raw = []  # 원본 제목 (Gemini 프롬프트용)

import re as _re

# ──────────────────────────────────────────────────
# 키워드 기반 중복 체크 강화
# ──────────────────────────────────────────────────

# 키워드 추출 시 제외할 일반 단어 (주제 특정성이 없는 표현)
_STOPWORDS = {
    # 숫자/수량
    "3가지", "5가지", "7가지", "10가지",
    # YouTube 관용 표현
    "방법", "비밀", "비법", "이유", "꿀팁", "공개", "대공개",
    "현실", "시청", "필수", "완전", "미친", "대박", "레전드", "충격",
    "100%",
    # 수식어/부사
    "진짜", "절대", "무조건", "반드시", "확실", "딱", "확", "더", "또",
    # 대명사/지시
    "당신", "당신도", "당신은", "당신의", "당신만",
    "여러분", "사람", "사람들", "사람들의", "사람들은", "사람도", "사람은",
    "이거", "이것", "이것만", "저것", "그것",
    # 일반 동사/형용사 어미
    "하는", "되는", "있는", "없는", "만드는", "바꾸는",
    "높이는", "낮추는", "올리는", "내리는",
    "알면", "하면", "보면", "모르는", "아는",
    # 다양한 맥락에서 사용되는 일반 명사 (주제 특정성 낮음)
    "행동", "기술", "특징", "효과", "변화", "결과",
    # 기타
    "쇼츠", "shorts", "영상", "채널",
}

# 어근 비교 시 무시할 일반적인 2음절 접두사
_GENERIC_ROOTS = {
    # 인칭/지시
    "사람", "당신", "우리", "여러", "모든", "아무",
    # 수식어
    "진짜", "정말", "완전", "아주", "매우", "너무",
    "절대", "무조건", "반드시",
    # 광범위한 명사 접두사 (다양한 맥락에서 사용)
    "한국", "일상", "인간", "세상", "특징",
    "기술", "행동", "효과", "변화", "결과",
    # 일반 동사 어근 (다양한 맥락)
    "살아", "만들", "바꾸", "느낌",
    # 타겟/수준 관련
    "초보",
}


def _extract_keywords(text):
    """텍스트에서 핵심 키워드 추출 (중복 체크용, 2자 이상, 일반 단어 제외)"""
    text = _re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FAFF\U0000FE0F\U0000200D]+', '', text)
    text = _re.sub(r'#\S+', '', text)
    text = _re.sub(r'[?!.,;:()~\[\]{}\-"\'\u201C\u201D\u2018\u2019\u2026\u00B7\u2022\u25B6\u25BA\u2605\u2606\d]+', ' ', text)
    words = text.split()
    return {w.strip() for w in words if len(w.strip()) >= 2 and w.strip() not in _STOPWORDS}


def _share_korean_root(word1, word2, min_prefix=2):
    """두 단어가 동일한 한국어 어근(앞 2음절)을 공유하는지 확인
    예: '가난에서' ↔ '가난하게' → 어근 '가난' 공유 → True"""
    if len(word1) < min_prefix or len(word2) < min_prefix:
        return False
    prefix1 = word1[:min_prefix]
    prefix2 = word2[:min_prefix]
    # 한국어 음절인 경우만
    if not all('\uAC00' <= c <= '\uD7AF' for c in prefix1):
        return False
    if not all('\uAC00' <= c <= '\uD7AF' for c in prefix2):
        return False
    # 일반적인 접두사면 무시
    if prefix1 in _GENERIC_ROOTS:
        return False
    return prefix1 == prefix2


# ──────────────────────────────────────────────────
# 테마 기반 다양성 관리
# ──────────────────────────────────────────────────

# 주제의 대분류 테마 → 감지 키워드 (부분 문자열 매칭)
_THEME_KEYWORDS = {
    "재물금융": ["부자", "가난", "돈", "재테크", "투자", "저축", "월급", "수익",
                "주식", "코인", "암호화폐", "부동산", "연봉", "거지", "빈곤",
                "소비", "절약", "금융", "재산", "자산", "경제", "부유"],
    "습관루틴": ["습관", "루틴"],
    "자존감심리": ["자존감", "자존심", "심리", "멘탈", "우울", "불안"],
    "대인관계": ["대인관계", "인맥", "손절", "에너지 뱀파이어"],
    "대화설득": ["대화법", "말투", "설득", "화법", "거절"],
    "성공실패": ["성공한 사람", "실패하는 사람", "인생 망치", "인생을 바꾸"],
    "건강운동": ["건강", "운동", "다이어트", "헬스", "수면", "체중", "살빼"],
    "뇌과학집중": ["뇌과학", "집중력", "도파민", "뇌가소성", "IQ"],
    "SNS미디어": ["SNS", "유튜브 수익", "알고리즘"],
    "내향외향": ["내향", "외향", "MBTI"],
    "외모인상": ["외모", "첫인상", "관상"],
    "번아웃스트레스": ["번아웃", "스트레스", "감정 기복"],
}

# 테마별 최근 영상 허용 횟수 / 확인 윈도우
_THEME_MAX_RECENT = 3
_THEME_WINDOW = 15

# 테마 → 사람이 읽을 수 있는 이름
_THEME_DISPLAY = {
    "재물금융": "부자/가난/돈/투자/재테크",
    "습관루틴": "습관/루틴",
    "자존감심리": "자존감/심리/멘탈",
    "대인관계": "대인관계/친구/인맥",
    "대화설득": "대화법/말투/설득",
    "성공실패": "성공/실패/인생 역전",
    "건강운동": "건강/운동/다이어트",
    "뇌과학집중": "뇌과학/집중력/도파민",
    "SNS미디어": "SNS/유튜브/알고리즘",
    "내향외향": "내향/외향/MBTI",
    "외모인상": "외모/첫인상/관상",
    "번아웃스트레스": "번아웃/스트레스/감정",
}


def _get_topic_themes(text):
    """텍스트에서 테마 카테고리를 추출 (부분 문자열 매칭)"""
    themes = set()
    if not text:
        return themes
    for theme, keywords in _THEME_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                themes.add(theme)
                break
    return themes


def _get_saturated_themes():
    """최근 생성 영상에서 과포화된 테마 목록 반환 (로컬 이력 기준)

    Returns:
        (saturated: set, theme_counts: dict)
    """
    history = _load_history()
    all_entries = []
    for vtype in history:
        all_entries.extend(history[vtype])
    all_entries.sort(key=lambda e: e.get("date", ""), reverse=True)
    recent = all_entries[:_THEME_WINDOW]

    theme_counts = {}
    for entry in recent:
        combined = entry.get("topic", "") + " " + entry.get("title", "")
        for theme in _get_topic_themes(combined):
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

    saturated = {theme for theme, count in theme_counts.items()
                 if count >= _THEME_MAX_RECENT}
    return saturated, theme_counts


def is_theme_saturated(topic):
    """주제의 테마가 최근 영상에서 과포화되었는지 확인"""
    topic_themes = _get_topic_themes(topic)
    if not topic_themes:
        return False
    saturated, _ = _get_saturated_themes()
    overlap = topic_themes & saturated
    if overlap:
        names = ", ".join(_THEME_DISPLAY.get(t, t) for t in overlap)
        print(f"  🎯 테마 포화 제외: {topic[:30]}… (포화 테마: {names})")
        return True
    return False


def get_saturated_themes_for_prompt():
    """Gemini 프롬프트에 삽입할 과포화 테마 정보 문자열"""
    saturated, theme_counts = _get_saturated_themes()
    if not saturated:
        return ""

    lines = []
    for theme in sorted(saturated):
        name = _THEME_DISPLAY.get(theme, theme)
        count = theme_counts.get(theme, 0)
        lines.append(f"  - {name} (최근 {count}회 사용)")

    return ("\n\n🚫 과포화 테마 — 최근 영상에서 너무 자주 다룬 카테고리:\n"
            + "\n".join(lines)
            + "\n위 카테고리와 관련된 주제는 절대 추천하지 마세요. "
            "완전히 다른 카테고리의 참신한 주제만 추천해주세요.")


def set_youtube_titles(titles):
    """YouTube 채널 기존 영상 제목을 중복 체크 대상에 등록"""
    global _youtube_titles, _youtube_titles_raw
    _youtube_titles_raw = list(titles)
    cleaned = []
    for t in titles:
        # 이모지, 해시태그, 특수문자 제거 → 핵심 키워드만 추출
        c = _re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FAFF]+', '', t)
        c = _re.sub(r'#\S+', '', c)
        c = c.strip()
        if c:
            cleaned.append(c)
    _youtube_titles = cleaned


def _load_history():
    """주제 이력 파일 로드"""
    if not os.path.exists(HISTORY_FILE):
        return {"shorts": [], "longform": []}
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"shorts": [], "longform": []}


def _save_history(history):
    """주제 이력 파일 저장"""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def record_topic(video_type, topic, title=""):
    """사용한 주제를 이력에 기록"""
    history = _load_history()
    if video_type not in history:
        history[video_type] = []

    history[video_type].append({
        "topic": topic,
        "title": title,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    _save_history(history)


def get_used_topics(video_type, days=9999):
    """지금까지 사용된 주제 목록 반환 (로컬 이력 + YouTube 채널 전체 영상 포함)
    
    Args:
        days: 로컬 이력 기준 일수 (기본값 9999 = 사실상 전체)
    """
    history = _load_history()
    # shorts/longform 구분 없이 모든 이력 병합 (어떤 타입이든 중복 방지)
    all_entries = []
    for vtype in history:
        all_entries.extend(history[vtype])

    cutoff = datetime.now() - timedelta(days=days)
    used = []
    for entry in all_entries:
        try:
            dt = datetime.strptime(entry["date"], "%Y-%m-%d %H:%M")
            if dt >= cutoff:
                used.append(entry.get("topic", ""))
                # title도 중복 체크 대상에 포함
                if entry.get("title"):
                    used.append(entry["title"])
        except (ValueError, KeyError):
            used.append(entry.get("topic", ""))
            if entry.get("title"):
                used.append(entry["title"])

    # YouTube 채널 전체 영상 제목도 포함
    used.extend(_youtube_titles)
    return used


def is_topic_blocked(topic):
    """의미없는/저품질 주제인지 확인"""
    topic_lower = topic.lower().strip()
    for kw in BLOCKED_KEYWORDS:
        if kw.lower() in topic_lower:
            return True
    return False


def is_topic_duplicate(topic, used_topics):
    """주제가 이미 사용된 주제와 중복(또는 유사)한지 확인 (강화 버전)

    6단계 중복 체크:
    1. 완전 일치
    2. 부분 문자열 포함
    3. 단어 겹침 비율 (≥40%, 최소 2단어)
    4. 핵심 키워드 교집합
    5. 한국어 어근(접두사) 공유
    6. 테마 키워드 부분 문자열 교차 매칭 (복합어 내 핵심 키워드 감지)
    """
    topic_clean = topic.strip()
    if not topic_clean:
        return False

    topic_kw = _extract_keywords(topic_clean)

    for used in used_topics:
        used_clean = used.strip()
        if not used_clean:
            continue

        # 1. 완전 일치
        if topic_clean == used_clean:
            return True

        # 2. 한쪽이 다른쪽을 포함
        if len(topic_clean) > 5 and len(used_clean) > 5:
            if topic_clean in used_clean or used_clean in topic_clean:
                return True

        # 3. 공통 단어 비율 (임계값 낮춤: 0.6→0.4, 최소 단어수 3→2)
        words_a = set(topic_clean.split())
        words_b = set(used_clean.split())
        if len(words_a) >= 2 and len(words_b) >= 2:
            common = words_a & words_b
            ratio = len(common) / min(len(words_a), len(words_b))
            if ratio >= 0.4:
                return True

        # 4. 핵심 키워드 교집합
        used_kw = _extract_keywords(used_clean)
        common_kw = topic_kw & used_kw
        if common_kw:
            return True

        # 5. 한국어 어근 공유 체크 (형태 변화 대응)
        #    예: '가난에서' ↔ '가난하게' → 어근 '가난' 공유
        for tkw in topic_kw:
            for ukw in used_kw:
                if _share_korean_root(tkw, ukw):
                    return True

        # 6. 테마 키워드 부분 문자열 교차 매칭
        #    복합어 안에 숨은 핵심 키워드를 감지
        #    예: "부자되기위한" 안의 "부자" ↔ "부자들의" 안의 "부자"
        topic_themes = _get_topic_themes(topic_clean)
        used_themes = _get_topic_themes(used_clean)
        if len(topic_themes & used_themes) >= 2:
            return True

    return False


def pick_unique_topic(topics, video_type, days=9999):
    """중복되지 않고 사용 가능한 주제를 선택. 테마 포화도 고려."""
    import random

    used = get_used_topics(video_type, days=days)
    saturated_themes, _ = _get_saturated_themes()

    # 1차: 미사용 + 비차단 + 테마 미포화 주제 중 선택
    available = [t for t in topics
                 if not is_topic_duplicate(t, used)
                 and not is_topic_blocked(t)
                 and not (_get_topic_themes(t) & saturated_themes)]

    if available:
        choice = random.choice(available)
        return choice

    # 1.5차: 미사용 + 비차단 (테마 포화 무시)
    available_no_theme = [t for t in topics
                          if not is_topic_duplicate(t, used) and not is_topic_blocked(t)]
    if available_no_theme:
        choice = random.choice(available_no_theme)
        print(f"  ⚠️ 테마 포화 무시하고 선택: {choice[:30]}")
        return choice

    # 2차: 로컬 이력 무시하고 YouTube 채널 영상에만 없으면 허용
    # (Gemini가 새 주제를 주지 않고 로컬 history에만 있는 경우 대비)
    youtube_only_used = list(_youtube_titles)
    available2 = [t for t in topics
                  if not is_topic_duplicate(t, youtube_only_used) and not is_topic_blocked(t)]

    if available2:
        choice = random.choice(available2)
        return choice

    # 3차: 차단만 제외하고 가장 덜 최근 것
    non_blocked = [t for t in topics if not is_topic_blocked(t)]
    if non_blocked:
        # 사용 이력에서 가장 오래된 순으로 정렬
        history = _load_history()
        all_entries = []
        for vtype in history:
            all_entries.extend(history[vtype])
        topic_last_used = {}
        for entry in all_entries:
            t = entry.get("topic", "")
            topic_last_used[t] = entry.get("date", "2000-01-01 00:00")

        non_blocked.sort(key=lambda t: topic_last_used.get(t, "2000-01-01 00:00"))
        return non_blocked[0]

    # 최종 폴백
    return random.choice(topics)


def filter_trending_topics(trending_list, video_type):
    """트렌딩 주제 목록에서 차단/중복/테마포화 제거"""
    used = get_used_topics(video_type)  # days=9999 (전체)
    saturated_themes, _ = _get_saturated_themes()
    filtered = []
    for t in trending_list:
        if is_topic_blocked(t):
            print(f"  ⛔ 차단 주제 제외: {t}")
            continue
        if is_topic_duplicate(t, used):
            print(f"  🔄 중복 주제 제외: {t}")
            continue
        topic_themes = _get_topic_themes(t)
        if topic_themes & saturated_themes:
            names = ", ".join(_THEME_DISPLAY.get(th, th) for th in (topic_themes & saturated_themes))
            print(f"  🎯 테마 포화 제외: {t} ({names})")
            continue
        filtered.append(t)
    return filtered


def get_existing_titles_for_prompt():
    """Gemini 프롬프트에 삽입할 기존 영상 제목/주제 목록 (중복 회피 안내용)"""
    titles = []
    # YouTube 채널 영상 제목
    for t in _youtube_titles:
        if t and len(t.strip()) > 3:
            titles.append(t.strip())
    # 로컬 이력의 topic도 포함
    history = _load_history()
    for vtype in history:
        for entry in history[vtype]:
            topic = entry.get("topic", "").strip()
            if topic and len(topic) > 3:
                titles.append(topic)
    # 중복 제거 (앞 15자 기준)
    seen = set()
    unique = []
    for t in titles:
        key = t[:15]
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique


# ──────────────────────────────────────────────────
# 인기 영상 카테고리 분석
# ──────────────────────────────────────────────────
_popular_categories_cache = None


def analyze_popular_categories(popular_videos):
    """인기 영상 제목에서 대분류 카테고리 힌트를 추출합니다.
    
    Args:
        popular_videos: list of dict (get_popular_videos() 결과)
            [{'title': str, 'views': int, 'likes': int}, ...]
    
    Returns:
        str: Gemini 프롬프트에 삽입할 인기 카테고리 컨텍스트 문자열
    """
    global _popular_categories_cache
    
    if not popular_videos:
        return ""
    
    # 인기 영상 제목에서 참고 데이터 구성
    lines = []
    for i, v in enumerate(popular_videos[:15], 1):
        # 이모지, 해시태그 제거
        import re
        title = re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FAFF]+', '', v['title'])
        title = re.sub(r'#\S+', '', title).strip()
        if title:
            lines.append(f"  {i}. \"{title}\" (조회수 {v['views']:,}, 좋아요 {v['likes']})")
    
    if not lines:
        return ""
    
    hint = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[참고: 채널 인기 영상 TOP {len(lines)}]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
아래는 이 채널에서 조회수/좋아요가 높았던 영상입니다.
이 영상들의 '대분류 카테고리'(예: 심리학, 자기계발, 인간관계, 재테크 등)를 참고하여
비슷한 카테고리의 새로운 주제를 선정하세요.
단, 아래 영상의 주제를 그대로 반복하지 마세요. 같은 카테고리의 '새로운' 주제여야 합니다.

{chr(10).join(lines)}
"""
    _popular_categories_cache = hint
    return hint


def get_popular_categories_hint():
    """캐시된 인기 카테고리 힌트 반환 (없으면 빈 문자열)"""
    return _popular_categories_cache or ""
