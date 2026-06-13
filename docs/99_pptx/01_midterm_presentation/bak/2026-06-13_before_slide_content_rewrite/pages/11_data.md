# 슬라이드 B5 — 활용 데이터

> 원본 위치: `
../01_midterm_presentation.md
`
> 상태: Draft
> 역할: 대표 문서에서 분리한 슬라이드별 작업 문서

**핵심 메시지 (화면 카피)**
공식·공공 데이터로 후보를 만들고, 출처를 함께 저장한다

**화면 구성 — 카드 3섹션**

| 카드 | 데이터 | 목적 |
| --- | --- | --- |
| 한국 데이터 | TourAPI 4.0 관광지·축제, DataLab 월별 방문객, Wikipedia·기상청 월별 기상 경향 | 후보·일정 소재, 혼잡도·계절성 보정, 대체 일정 |
| 일본 데이터 | JNTO/JTA, 지자체 공식, e-Stat·RESAS·Statistical LOD, JMA | 후보·일정 소재, 지역 방문·기후·계절성 보정 |
| 표시·연동용 | WeatherAPI, Google/Kakao Maps, Yahoo Japan 딥링크 | 현재 날씨 표시, 지도·장소 상세·숙소 검색 이동 |

**발표자 노트**
- 모든 데이터는 `source_url`, `collected_at`, `data_confidence`를 함께 저장한다.
- WeatherAPI 현재 날씨는 추천 점수에 쓰지 않는다. 추천은 월별 기상 경향과 혼잡도 기준을 중심으로 한다.
- 숙소는 직접 추천하지 않고 현지 플랫폼 검색 딥링크로 연결한다.

---
