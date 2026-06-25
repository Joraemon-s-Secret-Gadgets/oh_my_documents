# Lovv 데이터·운영 범위 보조 문서

> 문서 성격: 보조 Markdown
> 대표 문서: `../00_project_plan.md`
> 기준 문서: `../../03_data_collect_plan/03_data_collect_plan.md`, `../../04_database_design/04_database_design.md`, `../../11_deployment_ops/supplemental/troubleshooting.md`

## PoC 데이터 범위

PoC는 한국 강원·경북과 일본 관동을 우선 수집 범위로 삼는다. 현재 범위는 전국 선제 구축이 아니라 검증 후보 도시를 깊게 구성하기 위한 출발점이다.

최종 목표는 한국·일본 전체 도시 확장이다. 확장 시에도 AdministrativeArea, City, Attraction, Festival, VisitorStatistics를 중심으로 한 공통 데이터 모델을 유지한다.

## 데이터 출처와 역할

| 출처 | 역할 |
| --- | --- |
| TourAPI / DataLab | 한국 관광지·축제·방문 통계 |
| JNTO / 일본 관광청(JTA) / e-Stat | 일본 방문 통계와 지역 검증 |
| Wikipedia 월별 날씨 경향 데이터 | 목적지 상세 화면의 월별 날씨 경향 |
| Wikipedia 월별 날씨 경향 데이터 / 일본기상 정보(JMA) | 월별 날씨 경향, ComfortScore, recommended_months |
| Google Maps Platform / Kakao Maps / Yahoo Japan | 지도, 장소, 외부 탐색 딥링크 |
| 클룩·라쿠텐 트래블·KKday | 예약 가능한 상품·숙박·액티비티 연결 |

## 날씨 역할 구분

Wikipedia 월별 날씨 경향 데이터는 상세 화면에서 월별 날씨 경향를 보여주는 역할이다. 월별 날씨 경향, 추천 적기, 기후 정합성 검증은 Wikipedia 월별 날씨 경향 데이터와 일본기상 정보(JMA)을 기준으로 한다. 두 데이터는 역할이 다르므로 함께 사용한다.

## 데이터 파이프라인

1. 자동 수집
2. 로컬 검증 산출물 생성
3. S3 Raw Bucket 원본 보존
4. Lambda 배치 전처리
5. DynamoDB 정규화 적재
6. 추천·검색 계층에서 RAG와 운영 조회에 활용

## 운영 리스크

- 입국자 수는 고유 사용자 수가 아니므로 여행 횟수 흐름 지표로 해석한다.
- 관문도시 방문을 소도시 성과로 보지 않는다.
- 축제·날씨·교통 데이터는 갱신 시각과 출처를 함께 표시한다.
- 외부 API 제약이 생기면 딥링크, 캐시, 백엔드 프록시를 조합한다.
- 지방 항공 노선 중단 가능성을 고려해 철도 대체 가능 소도시를 우선한다.

## 대표 문서 반영 위치

- `00_project_plan.md` 6.1: PoC 수집 범위와 전국 확장 방향
- `00_project_plan.md` 8장: 필요 데이터와 외부 연동
- `00_project_plan.md` 9.3: 데이터 파이프라인
- `00_project_plan.md` 12장: 데이터·외부 연동 리스크
