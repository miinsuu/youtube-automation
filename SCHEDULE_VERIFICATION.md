# ⏰ 스케줄 설정 가이드 (정확 정리)

**마지막 검토 날짜**: 2026년 2월 13일

---

## 🎯 최종 확정 스케줄

### 📊 요약 테이블

| 시간 | 요일 | 생성 타입 | Cron (UTC) | 한국 시간 |
|------|------|---------|-----------|---------|
| **08:00** | 월-금 | 🎬 쇼츠 | `0 23 * * 0,1-5` | 일 23:00 + 월-금 23:00 |
| **12:00** | **매일** | 🎬 쇼츠 + 📺 롱폼 | `0 3 * * *` | 매일 03:00 |
| **15:00** | **매일** | 🎬 쇼츠 + 📺 롱폼 | `0 6 * * *` | 매일 06:00 |
| **18:00** | 월-금 | 🎬 쇼츠 | `0 9 * * 1-5` | 월-금 09:00 |
| **22:00** | **매일** | 🎬 쇼츠 + 📺 롱폼 | `0 13 * * *` | 매일 13:00 |

---

## 🗓️ 요일별 상세 스케줄

### 평일 (월-금)

```
08:00 KST → 쇼츠만 생성
            (GitHub: 일 23:00 UTC = 월 08:00 KST + 월-금 23:00 UTC = 08:00 KST)

12:00 KST → 쇼츠 + 롱폼 생성
            (GitHub: 매일 03:00 UTC = 12:00 KST)

15:00 KST → 쇼츠 + 롱폼 생성
            (GitHub: 매일 06:00 UTC = 15:00 KST)

18:00 KST → 쇼츠만 생성
            (GitHub: 월-금 09:00 UTC = 18:00 KST)

22:00 KST → 쇼츠 + 롱폼 생성
            (GitHub: 매일 13:00 UTC = 22:00 KST)

총: 5번 (쇼츠 5회, 롱폼 3회)
```

### 주말 (토-일)

```
12:00 KST → 쇼츠 + 롱폼 생성
            (GitHub: 매일 03:00 UTC = 12:00 KST)

15:00 KST → 쇼츠 + 롱폼 생성
            (GitHub: 매일 06:00 UTC = 15:00 KST)

22:00 KST → 쇼츠 + 롱폼 생성
            (GitHub: 매일 13:00 UTC = 22:00 KST)

총: 3번 (쇼츠 3회, 롱폼 3회)
```

---

## 📝 Config.json 설정

```json
{
  "scheduler": {
    "shorts": {
      "weekday_times": ["08:00", "12:00", "15:00", "18:00", "22:00"],
      "weekend_times": ["09:00", "12:00", "15:00", "18:00", "22:00"]
    },
    "longform": {
      "weekday_times": ["12:00", "15:00", "18:00", "22:00"],
      "weekend_times": ["12:00", "15:00", "18:00", "22:00"]
    }
  }
}
```

---

## 🔄 GitHub Actions Cron 설정

### 워크플로우 파일: `.github/workflows/youtube-automation.yml`

```yaml
on:
  schedule:
    # 평일 08:00 KST (쇼츠)
    - cron: '0 23 * * 0'     # 일 23:00 UTC = 월 08:00 KST
    - cron: '0 23 * * 1-5'   # 월-금 23:00 UTC = 08:00 KST
    
    # 매일 12:00 KST (쇼츠 + 롱폼)
    - cron: '0 3 * * *'      # 매일 03:00 UTC = 12:00 KST
    
    # 매일 15:00 KST (쇼츠 + 롱폼)
    - cron: '0 6 * * *'      # 매일 06:00 UTC = 15:00 KST
    
    # 평일 18:00 KST (쇼츠)
    - cron: '0 9 * * 1-5'    # 월-금 09:00 UTC = 18:00 KST
    
    # 매일 22:00 KST (쇼츠 + 롱폼)
    - cron: '0 13 * * *'     # 매일 13:00 UTC = 22:00 KST
```

### Cron 분석

| Cron | 의미 |
|------|------|
| `0 23 * * 0` | 매주 일요일 23:00 UTC (월요일 08:00 KST) |
| `0 23 * * 1-5` | 월-금 매일 23:00 UTC (08:00 KST) |
| `0 3 * * *` | 매일 03:00 UTC (12:00 KST) |
| `0 6 * * *` | 매일 06:00 UTC (15:00 KST) |
| `0 9 * * 1-5` | 월-금 매일 09:00 UTC (18:00 KST) |
| `0 13 * * *` | 매일 13:00 UTC (22:00 KST) |

---

## 🔨 Scheduler.py 설정

### 파일: `scheduler.py`

```python
# setup_schedule() 메서드에서 config.json의 스케줄을 읽음

shorts_config = self.schedule_config.get('shorts', {})
longform_config = self.schedule_config.get('longform', {})

shorts_weekday = shorts_config.get('weekday_times', 
    ['08:00', '12:00', '15:00', '18:00', '22:00'])
longform_weekday = longform_config.get('weekday_times', 
    ['12:00', '15:00', '18:00', '22:00'])
```

### 실행 방법

```bash
# 정기 스케줄 실행
python3 scheduler.py --enable-upload

# 테스트 (한 번만 실행)
python3 scheduler.py --run-once --enable-upload

# 스케줄 확인 (실행 안함)
python3 scheduler.py --dry-run
```

---

## ✅ 검증 체크리스트

### Config.json 검증
- [x] `shorts.weekday_times` = `["08:00", "12:00", "15:00", "18:00", "22:00"]`
- [x] `shorts.weekend_times` = `["09:00", "12:00", "15:00", "18:00", "22:00"]`
- [x] `longform.weekday_times` = `["12:00", "15:00", "18:00", "22:00"]`
- [x] `longform.weekend_times` = `["12:00", "15:00", "18:00", "22:00"]`

### GitHub Actions 검증
- [x] 08:00 KST: `0 23 * * 0,1-5` (쇼츠)
- [x] 12:00 KST: `0 3 * * *` (쇼츠 + 롱폼)
- [x] 15:00 KST: `0 6 * * *` (쇼츠 + 롱폼)
- [x] 18:00 KST: `0 9 * * 1-5` (쇼츠)
- [x] 22:00 KST: `0 13 * * *` (쇼츠 + 롱폼)

### Scheduler.py 검증
- [x] Config에서 shorts 설정 읽음
- [x] Config에서 longform 설정 읽음
- [x] video_type 파라미터 전달
- [x] 쇼츠와 롱폼 분리 실행

---

## 📊 월간 생성 예상량

### 평일 (월-금, 20일 기준)
```
쇼츠: 5회/일 × 20일 = 100개
롱폼: 3회/일 × 20일 = 60개
```

### 주말 (토-일, 8-9일 기준)
```
쇼츠: 3회/일 × 8.5일 = 25개
롱폼: 3회/일 × 8.5일 = 25개
```

### 월간 총합
```
쇼츠: 125개
롱폼: 85개
전체: 210개 영상/월
```

---

## 🕐 시간대 변환 참고표

### KST (한국) ↔ UTC 변환

| KST | UTC | 설명 |
|-----|-----|------|
| 08:00 | 23:00 (전날) | 평일 아침 |
| 12:00 | 03:00 | 정오 |
| 15:00 | 06:00 | 오후 3시 |
| 18:00 | 09:00 | 저녁 6시 |
| 22:00 | 13:00 | 밤 10시 |

### Cron 요일 번호

| 번호 | 요일 |
|------|------|
| 0 | 일요일 |
| 1 | 월요일 |
| 2 | 화요일 |
| 3 | 수요일 |
| 4 | 목요일 |
| 5 | 금요일 |
| 6 | 토요일 |

---

## 🔄 변경 방법

### 시간 변경하기

1. **Config.json 수정**
   ```json
   "shorts": {
     "weekday_times": ["08:00", "새로운_시간", ...]
   }
   ```

2. **GitHub Actions 업데이트**
   ```yaml
   - cron: 'NEW_CRON_VALUE * * *'
   ```

3. **Git 커밋**
   ```bash
   git add config/config.json .github/workflows/youtube-automation.yml
   git commit -m "⏰ 스케줄 시간 변경"
   git push origin main
   ```

### 요일 변경하기

Cron에서 요일 범위 수정:
- `1-5` = 월-금
- `0,6` = 토-일
- `*` = 매일

---

## 🚀 다음 스케줄 확인

### GitHub Actions에서 확인

```
저장소 → Actions → "YouTube Shorts & Longform Auto Upload"
→ 가장 최신 실행 클릭
```

### 로컬 스케줄러에서 확인

```bash
python3 scheduler.py --dry-run

# 출력:
# ✅ 총 25개의 스케줄이 설정되었습니다.
# 📋 스케줄 목록:
# - Every 1 hour at 08:00:00 do create_and_upload() (type=shorts) ...
```

---

## 📞 문제 해결

**Q: 스케줄이 실행되지 않음**

1. GitHub Actions 활성화 확인
2. Cron 문법 검증 (cronhub.io)
3. 시간대 (UTC/KST) 확인

**Q: 중복 실행됨**

1. Config와 GitHub Actions의 시간이 일치하는지 확인
2. 중복 Cron 제거

**Q: 예상과 다른 시간에 실행됨**

1. UTC/KST 변환 재확인 (KST = UTC + 9시간)
2. GitHub의 시간 지연 고려 (보통 5-15분)

---

## ✨ 최종 확인

✅ **Config.json** - 쇼츠/롱폼 분리 설정  
✅ **GitHub Actions** - 단순하고 명확한 Cron  
✅ **Scheduler.py** - Config 기반 동적 스케줄  
✅ **시간 일치** - 모든 설정이 동일 시간 기준  

**모든 준비가 완료되었습니다!** 🎉
