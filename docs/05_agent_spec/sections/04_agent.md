# 4. Agent 출력

| 출력 | 설명 |
| --- | --- |
| `selectedDestination` | 선정된 소도시 1곳 |
| `itinerary` | 일정 유형에 맞춘 일별 세부 일정 |
| `recommendationReasons` | 사용자 조건, 계절, 테마, 접근성, 콘텐츠 균형 기반 추천 이유 |
| `itineraryFlowReason` | 일정 순서와 동선 흐름 이유 |
| `alternativeItinerary` | 기상 악화 또는 결측 상황의 대체 일정 |
| `festivalDateVerifications` | 축제별 해당 연도 날짜 검증 결과와 신뢰도 |
| `externalLinks` | 지도, 숙소 검색, 현지 탐색 링크 |
| `confidence` | 추천 신뢰도와 결측 정도 |
| `user_notice` | 반영 불가 조건, 검증 한계, 검색 링크 안내 |

API 응답에서는 `externalLinks`를 `links` 객체로 직렬화한다.
Agent 내부 상태와 문서 본문은 링크 생성 책임을 명확히 하기 위해 `externalLinks`라는 논리명을 사용하되, `/recommendations` 응답 계약은 API 명세의 `links.map`, `links.staySearch`를 따른다.
`recommendationReasons`, `itineraryFlowReason`, `confidence`, `user_notice`, `festivalDateVerifications`는 API 명세의 `explainability`와 최상위 검증 필드로 매핑한다.
