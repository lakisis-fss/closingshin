---
name: News Investigator
description: Collects news for target stocks, filters duplicates, scores by source authority, and performs AI sentiment analysis.
---

# News Investigator Skill

Target stocks list(CSV)를 입력받아 관련 뉴스를 수집하고, AI로 심층 분석하여 투자 판단을 돕는 리포트를 생성합니다.

## 기능
1.  **뉴스 수집**: Naver Search API를 통해 최신 뉴스 수집.
2.  **중복 제거**: `difflib`를 사용하여 유사한 제목의 기사 필터링.
3.  **가중치 평가**: 주요 언론사(한국경제, 매일경제 등)에 가중치를 부여하여 우선순위 산정.
4.  **Top 3 선정**: 종목별 점수 상위 3개 기사 선별.
5.  **AI 분석**: Google Gemini API를 사용하여 Sentiment, Impact, Signal 등 핵심 지표 분석.

## 요구 사항
*   **Environment Variables**: `.env` 파일에 다음 키가 설정되어 있어야 합니다.
    *   `NAVER_CLIENT_ID`
    *   `NAVER_CLIENT_SECRET`
    *   `GOOGLE_API_KEY` (Gemini API)

## 사용법

```bash
python skills/news_investigator/run_investigation.py --input <path_to_vcp_report.csv> --output <path_to_output_report.csv>
```

### 예시
```bash
python skills/news_investigator/run_investigation.py --input Scripts/results/vcp_report_20260205.csv --output Scripts/results/final_investigation_result.csv
```

## 입력 파일 형식 (CSV)
*   `ticker`, `name` 컬럼 필수.

## 출력 파일 형식 (CSV)
*   기존 뉴스 정보 + AI 분석 결과 (`sentiment_score`, `trading_signal` 등)
