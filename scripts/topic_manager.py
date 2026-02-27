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


def set_youtube_titles(titles):
    """YouTube 채널 기존 영상 제목을 중복 체크 대상에 등록"""
    global _youtube_titles
    import re
    cleaned = []
    for t in titles:
        # 이모지, 해시태그, 특수문자 제거 → 핵심 키워드만 추출
        c = re.sub(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FAFF]+', '', t)
        c = re.sub(r'#\S+', '', c)
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
    """주제가 이미 사용된 주제와 중복(또는 유사)한지 확인"""
    topic_clean = topic.strip()

    for used in used_topics:
        used_clean = used.strip()
        # 완전 일치
        if topic_clean == used_clean:
            return True
        # 한쪽이 다른쪽을 포함
        if len(topic_clean) > 5 and len(used_clean) > 5:
            if topic_clean in used_clean or used_clean in topic_clean:
                return True
        # 공통 핵심 단어 비율로 유사도 체크
        words_a = set(topic_clean.split())
        words_b = set(used_clean.split())
        if len(words_a) >= 3 and len(words_b) >= 3:
            common = words_a & words_b
            ratio = len(common) / min(len(words_a), len(words_b))
            if ratio >= 0.6:
                return True
    return False


def pick_unique_topic(topics, video_type, days=9999):
    """중복되지 않고 사용 가능한 주제를 선택. 없으면 가장 오래된 것 재사용."""
    import random

    used = get_used_topics(video_type, days=days)

    # 1차: 미사용 + 비차단 주제 중 선택
    available = [t for t in topics
                 if not is_topic_duplicate(t, used) and not is_topic_blocked(t)]

    if available:
        choice = random.choice(available)
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
    """트렌딩 주제 목록에서 차단/중복 제거 (전체 이력 + 전체 YouTube 채널 기준)"""
    used = get_used_topics(video_type)  # days=9999 (전체)
    filtered = []
    for t in trending_list:
        if is_topic_blocked(t):
            print(f"  ⛔ 차단 주제 제외: {t}")
            continue
        if is_topic_duplicate(t, used):
            print(f"  🔄 중복 주제 제외: {t}")
            continue
        filtered.append(t)
    return filtered
