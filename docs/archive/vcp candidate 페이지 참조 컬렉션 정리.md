Viewed VcpPageClient.tsx:50-144
Viewed api.ts:1-160

현재 첨부해주신 **VCP CANDIDATES** 페이지(프론트엔드 [VcpPageClient.tsx]
(cci:7://file:///e:/Downloads/Antigravity%20Project/ClosingSHIN/frontend/src/app/vcp/VcpPageClient.tsx:0:0-0:0) 화면)를 
렌더링하기 위해 백엔드(PocketBase)에서 참조하고 있는 컬렉션은 총 **5가지**입니다.

각 컬렉션이 화면의 어느 부분에 쓰이고 있는지 정리해 드립니다.

1. **`vcp_reports` 컬렉션**
   - **역할:** 화면 좌측의 **종목 리스트(포함될 후보군 자체)**와 36 FOUND 카운트, 
   우측 하단의 **VCP Metrics** (Contractions 진행 상황, Volume Dry Up 달성 여부, 
   Pivot Distance 등)에 쓰이는 VCP 알고리즘 평가 결과를 가져오는 핵심 컬렉션입니다. 

2. **`stock_infos` 컬렉션**
   - **역할:** 화면 좌측 리스트에 보이는 최신 **주가(예: 118,500) 및 등락률(예: +4.6%)**, 그리고 화면에는 다 안 보이지만 종목을 눌렀을 때 우측 하단 탭에 그려질 **Fundamentals, Supply/Demand(수급)** 등의 최신 시장 기본 데이터를 가져오는 데 사용됩니다. (최근에 0원 오류를 고치기 위해 VCP 리포트 가격 대신 여기서 최신 종가를 가져오도록 연결해두었습니다.)

3. **`vcp_charts` 컬렉션**
   - **역할:** 리스트에서 특정 종목을 클릭했을 때 우측 상단 메인 영역에 표시될 **차트 이미지**의 URL을 가져오는 컬렉션입니다.

4. **`news_analysis` 컬렉션**
   - **역할:** 종목 선택 후 하단의 'SENTIMENT' 탭 등을 눌렀을 때, 최근 뉴스들을 바탕으로 AI가 요약한 **종합 분석 의견(요약, 긍정/부정 스코어 등)**을 화면에 뿌려주는 데 사용됩니다.

5. **`news_reports` 컬렉션**
   - **역할:** 특정 종목에 할당된 **개별 뉴스 기사들의 실제 링크와 제목, 시간 데이터**를 리스트업 해주는 컬렉션입니다.

결과적으로 이 한 페이지를 띄우기 위해 프론트엔드는 위 5개의 API를 호출하여 데이터 조각들을 모은 뒤, 하나의 완벽한 대시보드로 조립하여 보여주고 있습니다!