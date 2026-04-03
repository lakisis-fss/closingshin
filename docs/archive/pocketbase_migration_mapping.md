# PocketBase 마이그레이션 및 리팩토링 대응 표

이 문서는 로컬 파일 시스템(`Scripts/data`, `Scripts/results`)에서 관리되던 주식 분석 데이터를 PocketBase로 통합하기 위한 매핑 정보를 담고 있습니다.

## 데이터 매핑 가이드

| 로컬 파일 경로 (Scripts/..) | 데이터 성격 | PocketBase 컬렉션명 | 관련 소스 코드 |
| :--- | :--- | :--- | :--- |
| `results/vcp_report_*.csv` | VCP 분석 결과 (종목별 점수) | **`vcp_reports`** | `02_scan_vcp.py`, `03_visualize_vcp.py` |
| `results/charts/*.png` | 종목별 VCP 분석 차트 이미지 | **`vcp_reports`** (field: `chart_image`) | `02_scan_vcp.py`, `03_visualize_vcp.py` |
| `results/news_analysis_*.csv` | AI 기반 뉴스 분석 및 감성 지수 | **`news_analysis`** | `05_analyze_news.py`, `generate_news_data.py` |
| `data/portfolio.json` | 현재 투자 종목, 매수가, 상태 | **`portfolio`** | `07_calc_portfolio.py`, `exit_monitor.py` |
| `data/market_status/status_*.json` | 일별 지수 미치 시장 지표 컨디션 | **`market_status`** | `05_collect_market_status.py`, `analysis_market.py` |
| `data/target_list_*.csv` | 특정 날짜의 관심 종목 리스트 | **`target_lists`** | `06_collect_stock_data.py` |
| `data/prices/*.csv` | 전 종목 일봉 데이터 (OHLCV) | **`ohlcv`** | `06_collect_stock_data.py`, `get_price_history.py` |
| `data/config.json` | 텔레그램, 알림 설정 값 | **`settings`** | (여러 스크립트 공통 사용) |

## 리팩토링 원칙
1. **PocketBase 우선**: 데이터를 생성하는 모든 Writer 로직은 이제 PocketBase API를 통해 저장합니다.
2. **하이브리드 지원**: 초기 전환기에는 로컬 CSV 쓰기 기능을 유지(Backup 용도)하되, 메인 데이터 소스는 PB로 전환합니다.
3. **병렬 처리**: OHLCV와 같이 대량의 데이터는 API 부하를 고려하여 병렬 업로드 및 벌크 처리를 수행합니다.
