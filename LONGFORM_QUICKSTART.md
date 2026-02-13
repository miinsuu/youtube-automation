# 🚀 롱폼 비디오 빠른 시작

## 1️⃣ 즉시 테스트 (로컬)

```bash
# 롱폼 비디오 1개 생성 (업로드 제외)
python main.py --type longform --no-upload

# 진행 상황 보기
tail -f logs/log_*.json
```

예상 시간: **10-15분**
결과: `output/longform_videos/` 폴더에 MP4 생성

---

## 2️⃣ 특정 주제로 생성

```bash
# 예: "성공한 사람들의 일상 습관" 주제로 생성
python main.py --type longform --topic "성공한 사람들의 일상 습관"
```

---

## 3️⃣ 자동 업로드 (실제 YouTube에 올리기)

```bash
# YouTube에 자동 업로드
python main.py --type longform
```

**주의**: 처음 실행 시 YouTube 인증 필요

---

## 4️⃣ 매일 자동 생성 & 업로드

### GitHub Actions로 자동화

저장소에 푸시하기만 하면 자동으로:
- ✅ 매일 12:00, 15:00, 22:00 KST에 롱폼 비디오 생성
- ✅ 자동으로 YouTube에 업로드
- ✅ 제목, 설명, 해시태그, 고정 댓글 자동 추가

---

## 📊 영상 길이별 성과

| 길이 | 조회수 | 구독 | 수익 | 추천 |
|------|--------|------|------|------|
| 5분 이하 | ⭐⭐ | ⭐ | ❌ | 낮음 |
| 10-15분 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 높음 |
| 20분 이상 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 중간 |

**결론**: 10-15분 롱폼이 가장 효율적!

---

## ⏰ 스케줄 한눈에

**롱폼 비디오 자동 업로드 시간:**

- 🌅 **12:00 KST** (정오)
- 🌤️ **15:00 KST** (오후 3시)
- 🌙 **22:00 KST** (오후 10시)

모든 변경사항은 GitHub에 푸시되면 자동 적용됩니다.

---

## 🎯 다음 단계

1. `python main.py --type longform --no-upload` 테스트
2. 결과 확인 (`output/longform_videos/`)
3. 문제 없으면 `python main.py --type longform` 으로 업로드
4. GitHub에 자동 스케줄링 준비 완료

---

**💡 팁**: 더 많은 옵션은 `LONGFORM_VIDEO_GUIDE.md` 참고
