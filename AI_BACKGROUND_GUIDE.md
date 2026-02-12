# AI 배경 이미지 생성 가이드

## 개요
이 프로젝트는 이제 **Pollinations.ai**를 사용하여 **완전 무료**로 AI 배경 이미지를 생성합니다.

## 주요 기능

### 1. AI 이미지 자동 생성
- **5개의 배경 이미지** 자동 생성
  - 인트로 (오프닝)
  - 섹션 1, 2, 3 (메인 콘텐츠)
  - 아웃트로 (클로징)

### 2. 대본 기반 맞춤형 생성
- 각 섹션별 **자동 프롬프트 생성**
- 대본의 핵심 키워드 추출
- 비디오 주제와 어울리는 이미지

### 3. 사용 기술
- **Pollinations.ai** (무료 AI 이미지 생성)
  - 인증 불필요 (API 키 없음)
  - 높은 품질 (FLUX-PRO 모델)
  - 빠른 생성 속도
  - 한국어 프롬프트 지원

## 사용 방법

### 자동 실행
```bash
# AI 배경 이미지 활성화 (기본값)
python main.py

# 기존 Pexels 이미지만 사용 (config.json에서 use_ai_background: false로 변경 후)
python main.py
```

### 설정

`config/config.json`에서:
```json
{
  "video": {
    "use_ai_background": true,        // AI 배경 활성화
    "ai_model": "pollinations"         // 사용할 AI 모델
  }
}
```

## 출력 구조

생성된 이미지는 `output/images/` 폴더에 저장됩니다:
```
output/images/
├── ai_bg_intro_[timestamp].png
├── ai_bg_section1_[timestamp].png
├── ai_bg_section2_[timestamp].png
├── ai_bg_section3_[timestamp].png
└── ai_bg_outro_[timestamp].png
```

## 프롬프트 생성 예시

### 대본
```
"투자의 첫 걸음... 주식 입문... 차근차근 배우기..."
```

### 생성된 프롬프트
1. **인트로**: `Professional cinematic intro image for '주식 투자 시작하기', dynamic lighting, 4K quality...`
2. **섹션1**: `Professional educational visual for '투자의 첫 걸음', informative graphic...`
3. **섹션2**: `Professional educational visual for '주식 입문', modern design...`
4. **섹션3**: `Professional educational visual for '차근차근 배우기', cinematic lighting...`
5. **아웃트로**: `Professional outro image, success and achievement theme...`

## 주의사항

### 속도
- 5개 이미지 생성에 약 **30-60초** 소요
- API 속도 제한 방지를 위해 각 이미지 생성 후 1초 대기

### 품질
- 생성된 이미지가 마음에 안 들면 `output/images/` 폴더에서 수동으로 변경 가능
- 기존 Pexels 이미지와 혼합 사용 가능

### 폴백
- AI 이미지 생성 실패 시 자동으로 **기존 Pexels 방식** 사용
- 부분 생성 시 생성된 이미지 + Pexels 이미지 혼합

## GitHub Actions에서 사용

`.github/workflows/youtube-automation.yml`에 이미 통합되어 있습니다.

```yaml
- name: Create video
  run: python main.py
  # AI 배경 이미지 자동 생성됨
```

## 개선 사항

향후 추가 예정:
- [ ] 이미지 캐싱 (중복 생성 방지)
- [ ] 커스텀 스타일 옵션
- [ ] 여러 AI 모델 지원
- [ ] 로컬 이미지 생성 (Stable Diffusion)

## 비용

**완전 무료** ✅
- Pollinations.ai: 무료 (인증 불필요)
- 대역폭 제한: 없음
- 월간 요청 제한: 없음

## 문제 해결

### 이미지 생성 실패
```
⚠️ API 응답 오류: 429, 재시도 1/3
```
→ API 속도 제한. 시간을 두고 재시도하세요.

### 이미지 형식 오류
```
⚠️ 이미지 형식 오류, 재시도 1/3
```
→ 자동 재시도되며, 실패 시 기존 Pexels 방식 사용

### 프롬프트 관련 문제
프롬프트를 수정하려면 `video_generator.py`의 `generate_ai_prompts()` 메서드 수정:

```python
def generate_ai_prompts(self, script_data):
    # 프롬프트 커스터마이징 가능
    intro_prompt = "원하는 프롬프트"
```

## 추가 정보

- [Pollinations.ai 공식 사이트](https://pollinations.ai/)
- [FLUX 모델 문서](https://flux.ai/)
