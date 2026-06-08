# 로브 (Lovv) 일정 생성 흐름 정본 초안

> 문서 버전: v0.1
> 문서 상태: 초안 (Draft)
> 기준 문서: `05_agent_spec.md`, `langgraph_flow.md`, `../01_requirements/01_requirements.md`, `../02_service_flow/02_service_flow.md`, `../04_database_design/04_database_design.md`, `../06_technical_spec/06_technical_spec.md`, `../07_api_spec/07_api_spec.md`

# 1. 문서 목적

본 문서는 로브 추천 Agent에서 **소도시 1곳이 선정된 이후 일별 여행 일정을 생성, 수정, 대체, 저장하는 흐름**을 별도 정본으로 정리한다.

기존 문서에서 일정 생성은 추천 결과의 일부로 정의되어 있었으나, 구현 기준으로 쓰기에는 `PlanDraft`, 일정 아이템 스키마, 수정 흐름, 대체 일정, 저장 API, DB 매핑이 분산되어 있었다.
따라서 본 문서는 일정 생성 기능을 독립적인 **일정 편성 엔진** 관점으로 정리한다.

# 2. 적용 범위

본 문서의 범위는 다음과 같다.

- 선정된 소도시 1곳을 기준으로 한 일정 생성
- 일정 유형별 방문 밀도와 시간대 구성
- 후보 장소 선정과 일정 블록 배치 기준
- 축제 포함 여부와 검증 상태 반영
- 월별 기상 경향 기반 대체 일정
- 사용자 피드백 기반 일정 수정
- 저장 전 `PlanDraft` 상태와 최종 저장 흐름
- API, DB, 테스트 문서에 반영해야 할 영향

본 문서는 소도시 후보 검색과 최종 목적지 선정 로직은 다루지 않는다.
해당 흐름은 `recommendation_flow.md`, `05_agent_spec.md`, `langgraph_flow.md`를 따른다.

# 3. 일정 생성의 위치

Lovv 전체 추천 흐름에서 일정 생성은 다음 위치에 있다.

```text
조건 파악
→ RAG/정적 DB 검색
→ 후보 소도시 랭킹
→ 소도시 1곳 선정
→ 일정 생성
→ 추천 이유 및 일정 흐름 설명
→ 검증
→ 응답 패키징
→ 저장/피드백/외부 링크
```

LangGraph 기준으로는 `Supervisor_Router`가 소도시 선정 이후 `Itinerary_Planner_Agent`를 순차 호출한다.
`Itinerary_Planner_Agent` 이후에는 `Explanation_Writer_Agent`, `Validation Skill`, `Output_Validator_Agent`가 이어진다.

# 4. 입력 조건

## 4.1 필수 입력

| 입력 | 설명 |
| --- | --- |
| `selectedDestination` | Ranker가 선정했거나 지도 마커로 고정된 소도시 1곳 |
| `country` | `KR` 또는 `JP`. 한 응답 안에서 국가를 섞지 않는다. |
| `travelMonth` | 여행 월. 월별 기상 경향과 계절 적합도 판단에 사용 |
| `travelYear` | 축제 날짜 검증 기준 연도. 없으면 여행 시작일 또는 현재 연도 기준 |
| `tripType` | `daytrip`, `2d1n`, `3d2n`, `4d3n`, `5d4n` |
| `includeFestivals` | 축제·행사 포함 여부 |
| `active_required_themes` | 일정에 반드시 반영해야 하는 사용자 선택/자연어 병합 테마 |
| `candidatePlaces` | 선정 소도시 내부의 관광지, 체험, 음식, 문화/휴식 장소 후보 |
| `festivalDateVerifications` | 축제별 날짜 검증 결과 |

## 4.2 선택 입력

| 입력 | 설명 |
| --- | --- |
| `soft_preferences` | 조용함, 전망, 산책, 로컬 감성처럼 필터보다는 가중치로 반영하는 조건 |
| `cleaned_raw_query` | 반영 가능한 자연어 조건만 남긴 검색·배치 참고 문장 |
| `user_location` | 당일치기 또는 이동 부담 판단을 위한 기준 위치 |
| `feedbackHistory` | 좋아요/싫어요, 저장, 재추천 이력 |
| `revisionRequest` | 기존 일정 수정 요청. 예: 카페 추가, 덜 걷기, 축제 제외 |

# 5. PlanDraft 상태

`PlanDraft`는 사용자가 최종 저장하기 전까지의 임시 일정 상태다.
현재 정본 기준에서는 대화 전문을 장기 저장하지 않으므로, `PlanDraft`도 사용자 원장 DB에 대화 로그와 함께 저장하지 않는다.

## 5.1 저장 위치 원칙

| 단계 | 저장 위치 | 원칙 |
| --- | --- | --- |
| PoC | 브라우저 메모리 또는 로컬 스토리지 | 사용자가 저장을 누르기 전에는 임시 상태 |
| Production 동기 추천 | AgentCore Memory 또는 응답 캐시 | `recommendationId`와 연결되는 짧은 수명 상태 |
| 최종 저장 | MySQL `itineraries`, `itinerary_days`, `itinerary_items`, `saved_itineraries` | 사용자가 명시적으로 저장할 때만 원장화 |
| Agent trace | DynamoDB TTL 로그 | 원문 대신 요약 상태만 저장 |

## 5.2 PlanDraft 최소 구조

```json
{
  "recommendationId": "uuid",
  "destinationId": "uuid",
  "tripType": "2d1n",
  "includeFestivals": true,
  "conditionsSnapshot": {
    "country": "JP",
    "travelMonth": 10,
    "activeRequiredThemes": ["art_sense", "history_tradition"],
    "softPreferences": ["quiet"]
  },
  "itinerary": {
    "days": []
  },
  "alternativeItinerary": {
    "trigger": "weather_trend",
    "days": []
  },
  "validationStatus": {
    "festivalConfirmedOnly": true,
    "singleDestination": true,
    "countrySeparated": true
  }
}
```

# 6. 일정 생성 단계

## 6.1 단계 요약

| 단계 | 처리 | 산출물 |
| --- | --- | --- |
| 1 | 소도시 고정 | `selectedDestination` |
| 2 | 일정 조건 확인 | `tripType`, `includeFestivals`, 이동 성향, 필수 테마 |
| 3 | 후보 장소 정리 | 테마, 장소 유형, 운영시간, 출처, 거리, 검증 상태 기준 후보군 |
| 4 | 필수 테마 반영 계획 | 일정 안에 `active_required_themes` 전체 반영 |
| 5 | 축제 조건 반영 | `includeFestivals=true`이고 `confirmed`인 축제만 고정 배치 |
| 6 | 일자/시간대 배치 | 오전/오후/저녁 또는 일차별 블록 구성 |
| 7 | 이동 부담 조정 | 가까운 장소 묶기, 과도한 이동 방지 |
| 8 | 대체 일정 생성 | 월별 기상 경향상 필요 시 실내 중심 일정 생성 |
| 9 | 링크 요청 생성 | 지도, 숙소 검색, 외부 탐색 링크 생성 요청 |
| 10 | 검증 전달 | Validation Skill 및 Output Validator로 전달 |

## 6.2 장소 선정 기준

장소 선정은 다음 기준을 따른다.

- 사용자가 선택한 테마와 일치하는 장소를 우선한다.
- 선택한 모든 `active_required_themes`가 일정 전체에 포함되도록 구성한다.
- 관광/체험, 음식, 문화/휴식 장소가 한쪽으로 치우치지 않게 조정한다.
- 장소 간 이동거리가 지나치게 멀지 않도록 동선을 고려한다.
- 운영시간이 확인되는 장소는 일정 배치 우선순위를 높인다.
- 운영정보가 부족한 장소는 확정 블록보다 보조 후보 또는 안내 포함 블록으로 처리한다.
- 자연어 입력이 있는 경우 `soft_preferences`와 `cleaned_raw_query`에 잘 맞는 장소를 우선 배치한다.
- 일정 생성 후 해당 소도시 기준 숙박 검색 링크를 제공한다.

# 7. 일정 유형별 구성 기준

| 일정 유형 | 구성 기준 |
| --- | --- |
| `daytrip` | 핵심 명소 2~3개, 식사 1회, 이동 부담 최소화 |
| `2d1n` | 일자별 3~4개 블록, 대표 명소·식사·휴식 포함, 숙소 검색 링크 제공 |
| `3d2n` | 일자별 테마 분리, 첫날·마지막 날 이동 부담 완화 |
| `4d3n` | 핵심 테마와 보조 테마를 나누어 배치, 반복되는 장소 유형 방지 |
| `5d4n` | 장기 체류형 일정. 휴식 블록과 선택형 후보를 충분히 포함 |

시간대는 기본적으로 `morning`, `afternoon`, `evening`을 사용한다.
필요하면 `night`, `flex`, `meal`, `rest` 같은 보조 구분을 API/DB 확장 후보로 둔다.

# 8. 축제 반영 규칙

축제는 기본 테마 추천에 자동 혼합하지 않고, 사용자가 포함을 선택한 경우에만 일정 요소로 반영한다.

| 상태 | 일정 반영 |
| --- | --- |
| `confirmed` | 일정에 직접 배치 가능 |
| `tentative` | 확정 일정 배치 금지. 후보 정보 또는 안내 문구로만 표시 |
| `unknown` | 확정 일정 배치 금지. 검증 한계 안내 |
| `outdated` | 재검증 전까지 확정 배치 금지 |

`includeFestivals=true`인데 해당 월에 반영 가능한 `confirmed` 축제가 없으면, 일정에 축제를 넣지 않고 마지막 안내 문구에 “해당 기간에 확정 검증된 축제가 없어 일반 장소 중심으로 구성했다”는 설명을 포함한다.

# 9. 대체 일정

대체 일정은 일반 일정 수정과 구분한다.

## 9.1 기상 대체 일정

월별 기상 경향상 우천, 폭설, 장마, 태풍 가능성이 높은 목적지는 `alternativeItinerary`를 생성한다.
WeatherAPI 실시간 예보는 목적지 상세 표시용이며, 추천 스코어링과 대체 일정 분기에는 월별 기상 경향 데이터를 사용한다.

기상 대체 일정은 다음 기준을 따른다.

- 동일한 소도시 안에서 구성한다.
- 실내 관광지, 문화시설, 공예·체험, 음식점, 카페 후보를 우선한다.
- 기존 일정의 핵심 테마를 가능한 한 유지한다.
- 야외 장소가 빠진 이유를 `fallbackReason` 또는 `user_notice`에 남긴다.

## 9.2 데이터 결측 대체

운영시간, 위치, 출처, 축제 날짜 같은 핵심 데이터가 부족하면 다음 중 하나로 처리한다.

- 확정 블록에서 제외
- 보조 후보로 표시
- `confidence` 하향
- `user_notice`에 결측 안내

# 10. 일정 수정 흐름

일정 수정은 기존 `PlanDraft`를 기준으로 특정 블록 또는 일정 전체를 재구성하는 흐름이다.
기상 대체 일정 API와 역할을 분리해야 한다.

## 10.1 수정 요청 유형

| 요청 | 처리 기준 |
| --- | --- |
| 덜 걷게 해줘 | 이동거리와 이동 횟수를 줄이고 가까운 장소끼리 재배치 |
| 카페 추가 | 카페 후보를 추가하되 출처와 외부 탐색 링크 포함 |
| 맛집 추가 | 음식점 후보를 추가하고 일정 밀도가 과도하면 다른 블록과 교체 |
| 축제 제외 | 축제 블록 제거 후 같은 시간대 대체 장소 제안 |
| 2일차만 바꿔줘 | 대상 일차만 수정하고 나머지 일차는 유지 |
| 더 조용한 일정 | soft preference를 강화해 혼잡·활동성 높은 블록 교체 |
| 추천 다시 받기 | 현재 조건을 유지하되 직전 목적지 또는 직전 일정 블록을 제외/감점 |
| 일정 유형 변경 | `tripType` 변경 후 전체 일정 밀도와 일차 구조 재생성 |

## 10.2 수정 응답 원칙

수정 응답은 다음을 포함해야 한다.

- 변경된 블록
- 유지된 블록
- 변경 이유
- 새로 추가된 장소의 출처 또는 외부 링크
- 검증 상태
- `confidence`와 `user_notice`

# 11. 출력 스키마 초안

```json
{
  "itinerary": {
    "tripType": "2d1n",
    "days": [
      {
        "day": 1,
        "title": "전통 거리와 미술관 중심 일정",
        "summary": "오전에는 대표 거리, 오후에는 실내 문화 콘텐츠를 배치합니다.",
        "items": [
          {
            "sortOrder": 1,
            "timeOfDay": "morning",
            "title": "히가시차야 거리 산책",
            "contentType": "attraction",
            "placeId": "uuid",
            "durationMinutes": 90,
            "moveHint": "도보 이동이 쉬운 구간입니다.",
            "reason": "예술·감성 선호와 도보 이동 조건에 맞습니다.",
            "sourceBadges": ["official", "local_government"],
            "verificationStatus": "verified",
            "isFestival": false
          }
        ]
      }
    ]
  },
  "alternativeItinerary": {
    "trigger": "weather_trend",
    "reason": "10월 우천 가능성에 대비해 실내 중심 대체 일정을 제공합니다.",
    "days": []
  },
  "itineraryFlowReason": "오전에는 대표 거리 산책, 오후에는 실내 문화 콘텐츠를 배치해 이동 부담을 낮췄습니다.",
  "externalLinks": {
    "map": "https://maps.google.com/...",
    "staySearch": "https://..."
  }
}
```

# 12. API 영향

현재 최신 API 정본에는 `POST /recommendations`와 기상 대체 일정 API가 정의되어 있다.
일반 일정 수정 흐름을 구현하려면 다음 API를 추가 검토해야 한다.

## 12.1 추가 후보 API

```text
POST /recommendations/{recommendationId}/revise
```

요청 후보:

```json
{
  "revisionType": "reduce_walking",
  "targetDay": 2,
  "targetItemId": "uuid",
  "message": "2일차는 덜 걷게 해줘",
  "preserve": ["destination", "tripType", "includeFestivals"],
  "exclude": ["previous_long_walk_block"]
}
```

응답 후보:

```json
{
  "recommendationId": "uuid",
  "itinerary": {},
  "changedItems": [],
  "preservedItems": [],
  "revisionReason": "이동거리가 긴 블록을 가까운 실내 장소로 교체했습니다.",
  "confidence": 0.84,
  "user_notice": null
}
```

## 12.2 기존 API와의 역할 분리

| API | 역할 |
| --- | --- |
| `POST /recommendations` | 최초 소도시 추천 및 일정 생성 |
| `POST /recommendations/{recommendationId}/alternatives/weather` | 기상 악화 대체 일정 조회 |
| `POST /recommendations/{recommendationId}/revise` | 사용자 피드백 기반 일반 일정 수정 후보 |
| `POST /me/itineraries` | 사용자가 확정한 일정 저장 |

# 13. DB 영향

대표 DB 문서에는 일정 영역이 `itineraries`, `itinerary_days`, `itinerary_items`, `saved_itineraries`로 정의되어 있다.
구현 시 API 응답과 DB 컬럼을 다음처럼 매핑하는 표가 필요하다.

| API 필드 | DB 후보 | 설명 |
| --- | --- | --- |
| `recommendationId` | `recommendation_results.id` | 추천 결과 식별자 |
| `itinerary.tripType` | `itineraries.trip_type` | 일정 유형 |
| `days[].day` | `itinerary_days.day_no` | 일차 번호 |
| `days[].title` | `itinerary_days.title` | 일차 제목 |
| `days[].summary` | `itinerary_days.summary` | 일차 요약 |
| `items[].sortOrder` | `itinerary_items.sort_order` | 일정 내 순서 |
| `items[].timeOfDay` | `itinerary_items.time_of_day` | 오전/오후/저녁 |
| `items[].title` | `itinerary_items.title` | 일정 블록 제목 |
| `items[].reason` | `itinerary_items.reason` | 해당 블록 추천 이유 |
| `items[].placeId` | `itinerary_items.attraction_id` 또는 `experience_id` | 장소 참조 |
| `items[].isFestival` | `itinerary_items.festival_id` 존재 여부 | 축제 블록 여부 |
| `items[].sourceBadges` | `itinerary_items.source_badges_json` | 출처/검증 표시 |

# 14. 검증 기준

일정 생성 결과는 다음 기준을 통과해야 한다.

| 검증 | 기준 |
| --- | --- |
| 단일 목적지 | 일정 내 장소가 선정 소도시 1곳 중심인가 |
| 국가 분리 | 한국/일본 데이터가 한 응답에 섞이지 않는가 |
| 일정 유형 반영 | `tripType`에 맞는 일차와 밀도인가 |
| 필수 테마 반영 | `active_required_themes`가 일정 안에 반영됐는가 |
| 축제 배치 | 일정에 직접 배치된 축제가 모두 `confirmed`인가 |
| 이동 부담 | 과도한 이동 또는 불가능한 이동을 만들지 않았는가 |
| 출처성 | 장소와 축제에 출처 또는 검증 상태가 연결되는가 |
| 숙박 정책 | 숙소를 직접 추천하지 않고 검색 링크로 분리했는가 |
| 폴백 안전성 | 결측, 미검증, 실패 상황을 `confidence`와 `user_notice`로 안내하는가 |

# 15. 테스트 케이스 후보

| ID | 유형 | 입력 | 기대 결과 |
| --- | --- | --- | --- |
| IT-N01 | 정상 | 10월 일본 1박2일 예술·감성 | 소도시 1곳 기준 2일 일정, 예술·감성 장소 포함 |
| IT-N02 | 정상 | 축제 포함 + `confirmed` 축제 | 일정에 축제 블록 직접 배치 |
| IT-N03 | 정상 | 자연어 “조용한 산책 위주” | 산책·휴식 장소 우선 배치 |
| IT-F01 | 폴백 | 축제 포함 요청 + `tentative` 축제만 존재 | 축제 직접 배치 금지, 안내 문구 출력 |
| IT-F02 | 폴백 | 우천 경향 높은 월 | `alternativeItinerary` 생성 |
| IT-F03 | 폴백 | 운영시간 결측 장소 | 보조 후보 처리 또는 안내 포함 |
| IT-R01 | 수정 | “덜 걷게 해줘” | 이동거리 긴 블록 교체 또는 재배치 |
| IT-R02 | 수정 | “카페 추가해줘” | 카페 블록 추가, 일정 밀도 조정 |
| IT-R03 | 수정 | “2일차만 바꿔줘” | 2일차만 수정하고 1일차 유지 |
| IT-R04 | 수정 | “축제 빼줘” | 축제 블록 제거, 대체 장소 제안 |
| IT-E01 | 실패 | 검증되지 않은 축제 확정 배치 | Validation 실패 후 재작성 |
| IT-E02 | 실패 | KR/JP 장소 혼합 | 국가 혼합 차단 |

# 16. 후속 반영 작업

1. `05_agent_spec.md`의 `Itinerary_Planner_Agent` 절에 본 문서 링크를 추가한다.
2. `07_api_spec.md`에 일반 일정 수정 API 후보를 반영할지 결정한다.
3. `04_database_design.md`에 `itinerary_days`, `itinerary_items` 상세 컬럼과 API 매핑 표를 반영한다.
4. `agent_harness_design.md`에 일정 생성 전용 테스트 케이스를 추가한다.
5. `02_service_flow.md`의 `PlanDraft` 설명을 최신 API/DB 원칙에 맞게 보완한다.
6. `docs/02_service_flow/Update.md`의 구형 `/v1/chat/*`, `/v1/plans/*`, Transcript 저장 표현은 최신 정본과 충돌하므로 참고 문서로만 유지하거나 정리한다.

# 17. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-08 | Codex | 일정 생성 흐름 정본 초안 작성. PlanDraft, 일정 생성 규칙, 수정 흐름, API/DB/테스트 영향 정리 |
