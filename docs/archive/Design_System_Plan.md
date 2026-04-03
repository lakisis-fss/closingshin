# ClosingSHIN 디자인 시스템 (Design System) v2.0
> **컨셉:** "The Geometric Vanguard" (바우하우스 x 모던 뎁스)
> **키워드:** 구축적(Constructive), 본질(Essential), 깊이감(Depth)

## 1. 디자인 철학 (Design Philosophy)
**"형태는 기능을 따른다 (Form follows function)"**는 바우하우스의 철학을 현대적인 디지털 인터페이스로 재해석합니다.
평범한 "표"와 "카드" 대신, **강렬한 도형과 원색의 대비**를 통해 데이터를 예술적으로 시각화합니다.

*   **Radical Geometry:** 모든 UI 요소는 완벽한 기하학적 형태(원, 삼각형, 사각형)를 가집니다.
*   **Primary Colors:** 정보의 위계는 바우하우스의 삼원색(Red, Blue, Yellow)으로만 표현합니다.
*   **Modern Material:** 단순한 평면이 아닌, **반투명한 유리는(Glassmorphism)**나 **깊이감 있는 그림자**를 사용하여 공간감을 줍니다.

---

## 2. 컬러 팔레트 (Color Palette)

바우하우스 포스터에서 볼 법한 강렬하고 근본적인 색채를 사용합니다.

### 🎨 Bauhaus Primary (삼원색)
*   **Bauhaus Red (#E03C31)**: 상승, 매수, 공격적 신호. (가장 강렬한 에너지)
*   **Bauhaus Blue (#005698)**: 하락, 매도, 냉철한 데이터. (차분하고 이성적)
*   **Bauhaus Yellow (#F2A900)**: 강조, 주목, AI의 인사이트. (경쾌한 포인트)

### 🌑 Neutral & Background
*   **Off-White (#F0F0F0)**: 캔버스 같은 밝은 회색 배경.
*   **Ink Black (#121212)**: 텍스트와 라인은 완전한 검정으로 강한 대비를 줍니다.

---

## 3. 타이포그래피 (Typography)

장식이 없는, 기하학적인 산세리프(Sans-serif) 서체를 크게 사용합니다.

*   **서체:** Futura (기하학적 산세리프의 정석) 또는 Pretendard (Bold Weight)
*   **스타일:**
    *   **Big & Bold:** 헤드라인은 아주 크고 굵게 배치하여 포스터 같은 느낌을 줍니다.
    *   **All Caps:** 섹션 제목은 대문자로 처리하여 건축적인 느낌을 줍니다.

---

## 4. 레이아웃 & 컴포넌트 (UI Elements)

"디자인 자체가 데이터 분석 도구"가 되도록 합니다.

### 📐 그리드 & 구조 (The Grid)
*   **비대칭 균형 (Asymmetrical Balance):** 모든 박스를 똑같이 맞추지 않고, 중요한 정보는 2배, 4배 크기로 과감하게 배치합니다.
*   **플로팅 패널 (Floating Panels):** 배경 위에 종이나 유리 판이 떠 있는 듯한 레이어링(Layering)을 통해 깊이감을 줍니다.

### 🔶 데이터 시각화 (Geometric Data)
*   **원(Circle) & 반원(Arc):** 달성률이나 비중은 파이 차트가 아닌, 대담한 '원' 그 자체로 표현합니다.
*   **선(Line):** 구분선은 얇게 숨기지 않고, 굵은 검은색 선(3px solid black)으로 명확하게 구획을 나눕니다 (몬드리안 스타일).

---

## 5. 적용 가이드 (Tailwind CSS)

```javascript
// tailwind.config.js 예시
module.exports = {
  theme: {
    extend: {
      colors: {
        'bauhaus-red': '#E03C31',
        'bauhaus-blue': '#005698',
        'bauhaus-yellow': '#F2A900',
        'canvas': '#F0F0F0',
      },
      boxShadow: {
        'hard': '4px 4px 0px 0px rgba(0,0,0,1)', // 딱딱한 그림자
      }
    }
  }
}
```
