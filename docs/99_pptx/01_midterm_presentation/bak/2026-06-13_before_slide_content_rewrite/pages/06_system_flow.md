# 슬라이드 B1 — 본론 진입: Lovv 시스템 흐름 (Explainable RAG)

> 원본 위치: `
../01_midterm_presentation.md
`
> 상태: Draft
> 역할: 대표 문서에서 분리한 슬라이드별 작업 문서

**핵심 메시지 (화면 카피)**
Explainable RAG — 입력부터 근거 있는 추천·일정까지, 한 흐름으로

**화면 구성**
- 좌→우 5계층 파이프라인 1개: 사용자 입력(국가·시기·테마) → Backend API → Recommendation Agent → Data Store ↔ External APIs → 근거 포함 추천 + 일정
- 5계층 역할:

| 계층 | 한 줄 역할 |
| --- | --- |
| Client Web | 온보딩·지도·챗봇·결과·마이페이지 |
| Backend API | 인증·검증·외부 프록시·추천 실행 |
| Recommendation Agent | 조건 분류 → 검색 → 선정 → 일정·이유 생성 |
| Data Store | 목적지·축제·월별 기상 경향·저장·검토 이력 |
| External APIs | Google/Kakao Maps, WeatherAPI, Yahoo Japan 딥링크 |

- 도식 위 UX 주석 3개: ① 이유·출처·검증 뱃지 ② "덜 걷게/카페 추가" 실시간 수정 ③ 지도·숙소 딥링크

**발표자 노트**
- "입력 → 검색 → 선정 → 일정, 한 흐름"만 빠르게 설명한다.
- 핵심 차별점은 **근거가 보이는 추천 = Explainable RAG**.
- 세부 에이전트 동작은 B3에서 확대한다.
- PoC는 정적 시드/JSON 기반과 최소 추천 API로 핵심 흐름을 검증한다. 추천은 실시간 예보가 아니라 월별 기상 경향 기반이고, WeatherAPI 현재 날씨는 표시용이다.

---
