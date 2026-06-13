# 로브 (Lovv) 일정 생성 흐름 정본 초안

> 문서 버전: v0.4
> 문서 상태: 초안 (Draft)
> 기준 문서: `planner_agent.md`, `candidate_evidence_agent.md`, `festival_verifier_agent.md`, `05_agent_spec.md`, `langgraph_flow.md`, `../01_requirements/01_requirements.md`, `../02_service_flow/02_service_flow.md`, `../04_database_design/04_database_design.md`, `../06_technical_spec/06_technical_spec.md`, `../07_api_spec/07_api_spec.md`

> 정본 우선순위: Planner Agent 구현 기준은 `planner_agent.md`를 우선한다. 일정 밀도, 슬롯 템플릿, 미식·노포 처리, 출력 스키마, 검증·재시도 규칙의 단일 정본은 `planner_agent.md`다. 본 문서는 PlanDraft, 일정 수정 흐름, 대체 일정 아이디어, 일반 수정 API 후보를 보존하는 보조 초안이며, 정본과 충돌할 경우 `planner_agent.md`를 따른다.

> 용어 정합성: 본 문서가 사용하던 일부 초안 용어는 Candidate Evidence / Planner 정본 용어로 정리했다. 매핑은 4.3절을 참고한다.

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

Lovv 전체 추천 흐름에서 일정 생성은 다음 위치에 있다. 정본 그래프 노드 기준(`langgraph_flow.md`, `planner_agent.md` §3)은 다음과 같다.

```text
Intent_Agent
→ Supervisor_Router
→ Candidate_Evidence_Agent   (검색·랭킹·후보 패키지 구성, selected_city 확정)
→ Festival_Verifier_Agent 또는 skip   (축제 날짜 검증)
→ Planner_Agent              (일정 생성 + 추천/흐름 설명 + 출력 검증 통합)
→ Backend_Serving            (API 응답 패키징, 저장/피드백/외부 링크)
```

즉 본 문서의 관심 구간인 "일정 생성·설명·검증"은 모두 `Planner_Agent` 한 노드 안에서 수행된다.
초안 작성 당시에는 `Itinerary_Planner_Agent` 이후 `Explanation_Writer_Agent`, `Validation Skill`, `Output_Validator_Agent`가 순차로 이어지는 흐름으로 표현했으나, 현재 정본에서는 이 책임을 `Planner_Agent`가 통합 수행한다. 본 문서에 남은 구형 노드명은 모두 `Planner_Agent`의 내부 단계로 읽는다.

# 4. 입력 조건

일정 생성의 1차 입력은 Candidate Evidence Agent가 만든 **Candidate Evidence Package**다. Planner는 이 패키지의 `status`/`mode`를 먼저 게이트로 확인한 뒤 일정을 생성한다(상세: `planner_agent.md` §4, §6, §7). 본 절은 그중 일정 편성에 직접 쓰이는 입력만 추린다.

## 4.1 필수 입력

| 입력 | 설명 |
| --- | --- |
| `candidate_evidence_package.status` | `ok`, `insufficient_candidates`, `no_candidate`, `error`. 일정 생성 진입 게이트 |
| `candidate_evidence_package.mode` | `city_discovery`, `anchor_fixed` (`festival_selection` 모드는 폐지 — 축제 포함은 `includeFestivals`로만 제어, 8장 참고) |
| `selected_city` | Ranker가 선정했거나 anchor/지도 마커로 고정된 소도시 1곳 (`candidate_evidence_package.selected_city`) |
| `country` | `KR` 또는 `JP`. 한 응답 안에서 국가를 섞지 않는다. |
| `travelMonth` | 여행 월. 월별 기상 경향과 계절 적합도 판단에 사용 |
| `travelYear` | 축제 날짜 검증 기준 연도. 없으면 여행 시작일 또는 현재 연도 기준 |
| `tripType` | `daytrip`, `2d1n`, `3d2n`, `4d3n`, `5d4n` |
| `includeFestivals` | 축제·행사 포함 여부 |
| `active_required_themes` | 일정에 반드시 반영해야 하는 사용자 선택/자연어 병합 테마 |
| `recommended_places` | 선정 소도시 내부 후보 중 Planner가 우선 사용하는 primary 후보 |
| `reserve_places` | primary 배치 실패 시 사용하는 reserve 후보. 무조건 노출 목록이 아님 |
| `festival_verifications` | 축제별 날짜 검증 결과(API 응답에서는 `festivalDateVerifications`로 패키징) |

## 4.2 선택 입력

| 입력 | 설명 |
| --- | --- |
| `soft_query` / `soft_preference_query` | 조용함, 전망, 산책, 로컬 감성처럼 필터보다는 가중치로 반영하는 분위기·동행·취향 조건 |
| `unsupported_conditions` | 검색·검증으로 반영하지 못한 조건. `user_notice` 안내에 사용 |
| `user_location` | 당일치기 또는 이동 부담 판단을 위한 기준 위치 |
| `weather_trends` | 월별 기상 경향. 대체 일정 분기 기준 (실시간 WeatherAPI는 표시용으로 분리) |
| `feedback_signals` | 좋아요/싫어요, 저장, 재추천 등 선호/비선호 신호 |
| `revisionRequest` | 기존 일정 수정 요청. 예: 카페 추가, 덜 걷기, 축제 제외 (본 문서 10장 전용) |

## 4.3 초안 용어 ↔ 정본 용어 매핑

본 문서 v0.2까지 쓰던 초안 용어를 Candidate Evidence / Planner 정본 용어로 정리한다.

| 초안 용어 (v0.2) | 정본 용어 | 비고 |
| --- | --- | --- |
| `selectedDestination` | `selected_city` | Candidate Evidence Package 필드 |
| `candidatePlaces` | `recommended_places` + `reserve_places` | primary/reserve 분리 개념 도입 |
| `festivalDateVerifications` (입력) | `festival_verifications` | API 응답 필드명만 `festivalDateVerifications` |
| `soft_preferences` | `soft_query` / `soft_preference_query` | |
| `cleaned_raw_query` | `soft_query`에 포함 | Candidate Evidence 단계에서 정제 |
| `feedbackHistory` | `feedback_signals` | |

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

아래 단계는 `Planner_Agent`의 내부 처리 순서이며, `planner_agent.md` §8의 12단계를 일정 편성 관점에서 요약한 것이다. 검증은 별도 노드가 아니라 Planner 내부에서 수행한다.

| 단계 | 처리 | 산출물 |
| --- | --- | --- |
| 0 | status/mode 게이트 | `no_candidate`·`error`는 일정 생성 금지, 안전 폴백으로 분기 (`planner_agent.md` §6) |
| 1 | 소도시 고정 | `selected_city`, `country` 일관성 확인. anchor 모드는 도시 변경 금지 |
| 2 | 일정 조건 확인 | `tripType`, `includeFestivals`, 이동 성향, 필수 테마 |
| 3 | 후보 inventory 정리 | `recommended_places`/`reserve_places`를 `attraction`/`restaurant`/`festival`/placeholder 슬롯으로 분리 |
| 4 | 슬롯 템플릿 + 필수 테마 계획 | `tripType` 슬롯 템플릿 선택, `active_required_themes`별 최소 1회 배치 계획 |
| 5 | 축제 overlay (Pass 2) | `includeFestivals=true`이고 `confirmed`인 축제 1개를 Day 1 오후 메인 슬롯에 배치 (6.3·8장) |
| 6 | 일자/시간대 배치 | 관광 슬롯 테마 round-robin, 식사 슬롯 restaurant 배치 (오전/오후/저녁) |
| 7 | reserve fallback + 이동 부담 조정 | primary 부족 시 같은 도시·국가 reserve 보충(`fromReserve=true`), 가까운 장소 묶기 |
| 8 | placeholder 처리 | 후보가 부족하면 장소명을 만들지 않고 `source=placeholder`, `placeId=null` 자유시간/식사 선택 블록 |
| 9 | 대체 일정 생성 | 월별 기상 경향상 필요 시 실내 중심 일정 생성 |
| 10 | 링크 요청 생성 | 지도, 숙소 검색, 외부 탐색 링크 생성 요청(Link Builder payload) |
| 11 | 설명 생성 | 추천 이유, 일정 흐름 이유, `user_notice` 작성 |
| 12 | 검증(결정적+의미) | Planner 내부 검증. 실패 시 재작성 또는 안전 폴백 (`planner_agent.md` §16) |

## 6.2 장소 선정 기준

장소 선정은 다음 기준을 따른다.

- 사용자가 선택한 테마와 일치하는 장소를 우선한다.
- 선택한 모든 `active_required_themes`가 일정 전체에 포함되도록 구성한다.
- 관광/체험, 음식, 문화/휴식 장소가 한쪽으로 치우치지 않게 조정한다.
- 장소 간 이동거리가 지나치게 멀지 않도록 동선을 고려한다.
- 운영시간이 확인되는 장소는 일정 배치 우선순위를 높인다.
- 운영정보가 부족한 장소는 확정 블록보다 보조 후보(reserve) 또는 안내 포함 블록으로 처리한다.
- `recommended_places`(primary)를 우선 사용하고, 부족하면 같은 도시·국가의 `reserve_places`로 보충한다. 그래도 부족하면 장소명을 만들지 않고 placeholder 블록으로 표시한다.
- 자연어 입력이 있는 경우 `soft_query`/`soft_preference_query`에 잘 맞는 장소를 우선 배치한다.
- 일정 생성 후 해당 소도시 기준 숙박 검색 링크를 제공한다(숙소 직접 추천 금지).

## 6.3 관광지 우선 2-pass 배치

후보 장소 배치는 관광지로 완결된 일정을 먼저 만들고 축제를 그 위에 얹는 2단계로 수행한다. 축제는 Festival Verifier가 별도로 날짜를 검증하고 그 결과가 늦거나 `confirmed`가 아닐 수 있으므로, 관광 일정이 항상 단독으로 성립하는 기준선이 되어야 한다.

### Pass 1 — 관광지 baseline (항상 실행)

1. `tripType` → 슬롯 템플릿 선택.
2. 후보를 `attraction`(테마별 bucket)과 `restaurant`(미식·노포, 식사 슬롯용)로 분리한다.
3. 관광 슬롯은 `active_required_themes`(미식 제외) round-robin으로 채운다. 같은 테마 3연속 금지, 중복 장소 금지.
4. 식사 슬롯은 restaurant 후보를 점수·입력순으로 배치한다.
5. 부족하면 reserve 보충(`fromReserve=true`) → 그래도 부족하면 placeholder.
6. 좌표가 있으면 같은 일차 안에서 가까운 장소끼리 묶는다.

상세 배정 알고리즘(Greedy + Round-Robin)은 `planner_agent.md` §9.1·§9.2가 정본이다.

### Pass 2 — 축제 overlay (조건부)

`includeFestivals=true`이고 선택 도시에 해당 여행 월의 `confirmed` 축제가 있을 때만 실행한다. 축제는 선택 도시 + 여행 월 기준이라 **0개 또는 1개**뿐이다.

1. 적격성은 **월 단위**로 판정한다. 축제 데이터에는 정확한 날짜가 있지만 사용자는 여행 월까지만 입력하고 일정도 상대 day(Day 1 / Day 2)로 구성되어 달력에 묶이지 않으므로, day 단위 겹침은 계산하지 않는다.
2. 축제를 **Day 1의 오후 메인 관광 슬롯**에 배치한다.
3. 축제 데이터에 시간 정보가 없으므로 `timeOfDay`를 단정하지 않고 중립 표시("축제 · 시간 현장 확인")로 둔다.
4. 밀려난 Day 1 오후 관광지는 같은 일차 빈 슬롯으로 이동한다. 자리가 없고 그 관광지가 필수 테마(`active_required_themes`)를 유일하게 충족하는 블록이면 다른 일차·슬롯의 비핵심 관광지와 스왑해 일정 안에 보존한다. 스왑도 불가능하면 **축제 배치를 우선**하고(해당 관광지 제거), `user_notice`에 그 테마가 충분히 반영되지 못했음을 안내한다.
5. 축제의 실제 개최일은 `user_notice`로 알려, "여행 날짜를 축제일에 맞추면 일정대로 즐길 수 있고, 다른 날짜로 가면 축제는 못 볼 수 있다"는 가이드와 시간 미상 고지를 포함한다.
6. 해당 월에 `confirmed` 축제가 없거나 `confirmed`가 아니면 축제를 배치하지 않고 안내만 남긴다(Pass 1 유지).
7. 축제 삽입 후 단일 목적지·국가 분리·밀도·테마 coverage를 재검증한다.

추가 규칙: 축제가 여러 날 열려도 일정에는 Day 1 한 블록만 배치하고 전체 개최 기간은 `user_notice`에 적는다. `daytrip`이나 미식 단독처럼 Day 1 오후가 placeholder인 경우에는 축제가 그 자리를 차지하므로 밀려나는 관광지가 없다.

> 설계 근거: 축제 데이터는 날짜만 있고 시간이 없으며, 사용자 입력은 월까지만 받고 일정은 상대 day로 구성된다. 그래서 축제는 시간대 블록이 아니라 "그 날의 day-level 앵커"로 다루고, 매칭은 월 적격성으로, 실제 날짜는 사용자에게 가이드로 제공한다. `festival_selection` 진입 모드는 사용하지 않으며 축제 포함은 `includeFestivals`로만 제어한다. 동일 모델이 `planner_agent.md` §11에 정본으로 반영되어 있다.

# 7. 일정 유형별 구성 기준

아래는 개념 요약이다. 일차별 권장 블록 수, 슬롯 배열, Greedy + Round-Robin 배정 알고리즘의 단일 정본은 `planner_agent.md` §9(일정 밀도 기준)와 §9.1·§9.2다. 구현 시 수치는 그쪽을 따른다.

| 일정 유형 | 구성 기준 | 정본 권장 블록(§9) |
| --- | --- | ---: |
| `daytrip` | 핵심 명소 2~3개, 식사 1회, 이동 부담 최소화 | 3-4 |
| `2d1n` | 일자별 3~4개 블록, 대표 명소·식사·휴식 포함, 숙소 검색 링크 제공 | 6-8 |
| `3d2n` | 일자별 테마 분리, 첫날·마지막 날 이동 부담 완화 | 9-12 |
| `4d3n` | 핵심 테마와 보조 테마를 나누어 배치, 반복되는 장소 유형 방지 | 12-16 |
| `5d4n` | 장기 체류형 일정. 휴식 블록과 선택형 후보를 충분히 포함 | 15-20 |

시간대는 기본적으로 `morning`, `afternoon`, `evening`을 사용한다.
Planner 내부에서는 `flex`, `meal`, `rest` 보조 구분을 사용하되, API 응답은 현재 `timeOfDay`만 요구하므로 Backend Serving이 UI 계약에 맞게 표시명을 조정한다(`planner_agent.md` §9). `night` 등 추가 구분은 API/DB 확장 후보로 둔다.

## 7.1 미식·노포 테마 처리 (요약)

`미식·노포`(`gourmet_retro`) 후보는 현재 데이터에서 대부분 `restaurant`다. 따라서 미식 테마는 일반 관광 슬롯에서 경쟁시키지 않고 **식사 슬롯에서 충족되는 테마**로 다룬다. 관광 슬롯 round-robin은 미식을 제외한 테마로 수행하고, 미식은 lunch/dinner 슬롯에서 반영한다. 미식 후보가 부족하면 식당명을 만들지 않고 `source=placeholder`인 "현지 식당 자유 선택" 블록과 `user_notice`로 처리한다. 상세 규칙·검증 기준은 `planner_agent.md` §9.3이 정본이다.

# 8. 축제 반영 규칙

축제는 기본 테마 추천에 자동 혼합하지 않고, 사용자가 `includeFestivals=true`로 포함을 선택한 경우에만 일정 요소로 반영한다. 축제 포함 여부는 `includeFestivals`(true/false)로만 제어하며, 별도의 `festival_selection` 진입 모드는 사용하지 않는다. 축제는 도시 선택에 관여하지 않는다 — 도시는 Candidate Evidence가 테마·후보로 정하고, 그 선택 도시에 `confirmed` 축제가 마침 있으면 Pass 2 overlay로 얹는다(6.3 참고).

선택 도시 + 여행 월 기준이므로 일정에 반영할 수 있는 축제는 **0개 또는 1개**뿐이다.

## 8.1 검증 상태별 배치

| 상태 | 일정 반영 |
| --- | --- |
| `confirmed` | Day 1 오후 메인 슬롯에 배치 가능 (6.3 Pass 2) |
| `tentative` | 확정 일정 배치 금지. 후보 정보 또는 안내 문구로만 표시 |
| `unknown` | 확정 일정 배치 금지. 검증 한계 안내 |
| `outdated` | 재검증 전까지 확정 배치 금지 |

## 8.2 날짜·시간 처리

- 적격성은 월 단위로 판정한다(6.3 Pass 2). 축제는 정확한 날짜를 갖지만 사용자는 여행 월까지만 입력하고 일정은 상대 day로 구성되어, day 단위 겹침은 계산하지 않는다.
- 축제 데이터에 시간 정보가 없으므로 시간대를 단정하지 않는다. `timeOfDay`는 중립 표시로 두고, "정확한 시작 시간·운영은 공식/현장 확인 필요"를 `user_notice`로 분리한다.
- 축제의 실제 개최일은 사용자가 여행 날짜를 정하는 가이드로 `user_notice`에 안내한다.

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
- 사용자가 포함한 축제는 대체 일정에서도 **유지한다**. 단 야외 축제인 경우 우천·기상 리스크를 `fallbackReason` 또는 `user_notice`에 고지한다.
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
| 축제 추가 | Pass 2 실행. Day 1 오후 메인 슬롯에 `confirmed` 축제 배치, 해당 관광지 이동/제거 (6.3) |
| 축제 제외 | Pass 2 overlay 제거 → Pass 1 baseline 복원. 밀려났던 Day 1 오후 관광지를 되돌린다 |
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

출력 스키마의 단일 정본은 `planner_agent.md` §13(출력 계약)과 §13의 Planner 내부 필드 ↔ API 응답 필드 매핑 표다. 아래 예시는 그 스키마에 맞춰 정리한 일정 관점 발췌이며, item provenance 필드(`sourcePlaceId`, `themeCode`, `fromReserve`, `source`, `qualityStatus`)와 응답 수준 필드(`recommendationReasons`, `confidence`, `user_notice`, `validation_result`)를 포함한다.

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
            "placeId": "P_001",
            "sourcePlaceId": "129123",
            "themeCode": "art_sense",
            "durationMinutes": 90,
            "moveHint": "도보 이동이 쉬운 구간입니다.",
            "reason": "예술·감성 선호와 도보 이동 조건에 맞습니다.",
            "source": "primary",
            "sourceBadges": ["tour_api", "dynamodb"],
            "verificationStatus": "evidence_backed",
            "isFestival": false,
            "fromReserve": false
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
  "recommendationReasons": [
    "선택한 필수 테마가 후보 장소 근거에서 확인됩니다.",
    "선택 도시는 일정에 필요한 primary 후보를 충분히 제공합니다."
  ],
  "itineraryFlowReason": "오전에는 대표 거리 산책, 오후에는 실내 문화 콘텐츠를 배치해 이동 부담을 낮췄습니다.",
  "externalLinks": {
    "map": "https://maps.google.com/...",
    "staySearch": "https://..."
  },
  "confidence": 0.86,
  "user_notice": null,
  "validation_result": {
    "passed": true,
    "failure_categories": []
  }
}
```

> 주의: `source`는 `primary`/`reserve`/`festival`/`placeholder` 중 하나이며, `placeholder` item은 `placeId=null`이고 장소명·운영정보를 만들지 않는다. `sourceBadges`·`verificationStatus`의 표준 코드(`tour_api`, `official`, `dynamodb`, `web_verified`, `evidence_backed` 등)는 `planner_agent.md` §21 Open Decisions에서 확정 예정이다.

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

검증은 별도 노드가 아니라 `Planner_Agent` 내부에서 수행한다. 아래는 일정 관점 체크리스트이며, 결정적·의미 검증의 실패 카테고리(`destination_mixed`, `country_mixed`, `grounding_missing`, `placeholder_unsafe`, `festival_unconfirmed`, `theme_unmet`, `lodging_policy_violation`, `unsafe_fallback`, `explanation_mismatch`, `hallucination` 등)와 재시도 규칙의 정본은 `planner_agent.md` §16이다.

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

1. `05_agent_spec.md`의 `Planner_Agent` 절에 본 문서와 `planner_agent.md` 링크를 유지한다.
2. `07_api_spec.md`에 일반 일정 수정 API 후보를 반영할지 결정한다.
3. `04_database_design.md`에 `itinerary_days`, `itinerary_items` 상세 컬럼과 API 매핑 표를 반영한다.
4. `agent_harness_design.md`에 일정 생성 전용 테스트 케이스를 추가한다.
5. `02_service_flow.md`의 `PlanDraft` 설명을 최신 API/DB 원칙에 맞게 보완한다.
6. `docs/02_service_flow/Update.md`의 구형 `/v1/chat/*`, `/v1/plans/*`, Transcript 저장 표현은 최신 정본과 충돌하므로 참고 문서로만 유지하거나 정리한다.

# 17. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.4 | 2026-06-13 | llm | **무엇을:** 후보 장소 배치를 관광지 우선 2-pass(Pass 1 관광 baseline → Pass 2 축제 overlay)로 구체화. §4.1 mode에서 `festival_selection` 제거, §6.1 단계 5 수정, §6.3 신설, §8 재작성(8.1 상태별·8.2 날짜시간), §10 수정 행에 "축제 추가" 신설 및 "축제 제외"를 overlay 제거·baseline 복원으로 정비. 축제는 `includeFestivals`만으로 제어, 선택 도시·여행 월 기준 0/1개, 월 적격성 판정, Day 1 오후 메인 슬롯 배치, time_slot 중립화, 실제 개최일 가이드 안내. 축제 상호작용 규칙으로 ①밀린 관광지가 필수 테마 유일 블록이면 스왑 보존하되 불가하면 축제 우선 배정 후 테마 부족 안내, ②기상 대체 일정에서 축제 유지 + 야외 리스크 고지, ③다일 축제는 Day 1 단일 블록 + 개최 기간 notice, ④daytrip·미식 단독은 placeholder 자리라 충돌 없음을 추가. **왜:** 축제 데이터는 날짜만 있고 시간이 없으며, 사용자는 여행 월까지만 입력하고 일정은 상대 day로 구성되어 day 단위 겹침·시간대 단정이 불가능하고, `festival_selection` 진입 모드는 실제로 존재하지 않기 때문. `planner_agent.md`(v1.3)와 동반 수정 |
| v0.3 | 2026-06-13 | llm | Candidate Evidence/Planner 정본과 용어 정합화. 입력 계약을 `candidate_evidence_package`(status/mode/recommended_places/reserve_places) 기준으로 정리하고 초안↔정본 용어 매핑(4.3) 추가. 그래프 노드 체인 반영, 생성 단계에 status gate·reserve fallback·placeholder 보강, 출력 스키마를 `planner_agent.md` §13 기준으로 정합화, 미식·노포 처리(7.1)·밀도·검증 교차참조 추가 |
| v0.2 | 2026-06-12 | llm | Planner Agent 상세 정본 `planner_agent.md` 우선순위 메모 추가 및 구형 Itinerary/Explanation 분리 표현 정리 |
| v0.1 | 2026-06-08 | llm | 일정 생성 흐름 정본 초안 작성. PlanDraft, 일정 생성 규칙, 수정 흐름, API/DB/테스트 영향 정리 |
