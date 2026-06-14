# Planner Agent 명세서

> 문서 버전: v1.6
> 문서 상태: Review / Planner Agent 상세 정본
> 작성일: 2026-06-12
> 기준 문서: `05_agent_spec.md`, `langgraph_flow.md`, `candidate_evidence_agent.md`, `candidate_evidence_baseline_comparison.md`, `itinerary_flow.md`, `../07_api_spec/07_api_spec.md`, `../04_database_design/04_database_design.md`

## 1. 문서 목적

본 문서는 Lovv 추천 Agent에서 `Planner_Agent`가 수행해야 하는 일정 생성, 설명 생성, 출력 검증의 상세 정본이다.

`itinerary_flow.md`는 일정 생성 흐름과 PlanDraft 아이디어를 정리한 초안으로 유지한다. 구현 기준은 본 문서를 우선한다.

Planner Agent의 핵심 책임은 Candidate Evidence Package를 사용자용 추천 결과로 변환하는 것이다. Planner는 목적지나 장소를 새로 찾아내는 검색 Agent가 아니며, 존재하지 않는 장소·축제·운영 정보를 만들어내면 안 된다.

## 2. 책임 범위

Planner Agent가 담당하는 범위:

| 범위 | 설명 |
| --- | --- |
| 일정 생성 | 선택된 소도시 1곳과 후보 장소를 바탕으로 `tripType`별 고정 슬롯 템플릿에 맞는 일차별 일정 생성 |
| 후보 소비 | `recommended_places`를 우선 사용하고, 부족하거나 배치가 어려우면 `reserve_places`를 사용 |
| 축제 반영 | `confirmed` 축제만 일정 블록으로 직접 배치 |
| 대체 일정 | MVP에서는 기상 대체 일정을 생성하지 않고 `alternativeItinerary=null` 또는 빈 값으로 둠 |
| 추천 설명 | 조건 충족, 도시 특성, 일정 가능성 근거를 사용자 언어로 설명 |
| 출력 검증 | 결정적 검증과 의미 검증을 수행하고 실패 시 재작성 또는 안전 폴백 |
| 링크 요청 | 지도 링크, 숙소 검색 링크, 선택 도시 맛집 검색 링크 생성을 위한 요청 payload 구성 |

Planner Agent가 담당하지 않는 범위:

| 비범위 | 담당 |
| --- | --- |
| 도시/장소 검색 | `Candidate_Evidence_Agent` |
| 도시 ranking과 후보 scoring | `Candidate_Evidence_Agent` |
| 축제 날짜 후보 조회와 검증 | `Festival_Verifier_Agent` |
| 숙소 품질·가격·예약 가능 여부 판단 | 외부 검색 링크 또는 별도 숙소 서비스 |
| 사용자 저장 일정 원장화 | Backend/MySQL 저장 API |
| 실시간 날씨 기반 추천 scoring | 사용하지 않음. 실시간 WeatherAPI는 표시용 |

## 3. 그래프 내 위치

Planner Agent는 Candidate Evidence와 Festival Verifier 이후의 순차 생성 구간에 위치한다.

```text
Intent_Agent
→ Supervisor_Router
→ Candidate_Evidence_Agent
→ Festival_Verifier_Agent 또는 skip
→ Planner_Agent
→ Backend_Serving
```

`anchored_place_search` 모드에서는 Planner 진입 전에 도시가 이미 고정되어 있어야 한다. Planner는 이 anchor를 바꾸지 않는다. 축제 포함은 `includeFestivals`로만 제어하며, 고정 도시 모드에서도 축제 포함을 선택할 수 있다. Planner는 축제로 도시를 재선택하지 않지만, `selected_city`는 Candidate Evidence 단계에서 축제 seed를 반영해 선택됐거나, anchored mode에서 사용자 anchor로 고정됐을 수 있다(§11 참고).

## 4. 입력 계약

Planner Agent의 필수 입력:

| 입력 | 설명 |
| --- | --- |
| `candidate_evidence_package.status` | `ok`, `no_candidate`, `insufficient_candidates`, `error` |
| `candidate_evidence_package.mode` | `city_discovery`, `anchored_place_search`, `festival_seeded_city_discovery` |
| `candidate_evidence_package.selected_city` | 최종 추천 도시. `no_candidate`와 `error`에서는 `null` 가능 |
| `candidate_evidence_package.city_anchor` | `anchored_place_search` 모드의 anchor 근거. 그 외 모드에서는 `null` 가능 |
| `candidate_evidence_package.recommended_places` | Planner가 우선 사용하는 primary 후보 |
| `candidate_evidence_package.reserve_places` | primary 배치 실패 시 사용하는 reserve 후보 |
| `candidate_evidence_package.selected_festival_candidates` | Candidate Evidence가 최종 선택 도시 안에서 Verifier로 넘긴 축제 후보. Planner는 직접 배치 근거로 쓰지 않고 검증 결과의 provenance 확인에만 사용 |
| `candidate_evidence_package.festival_seed_audit` | `includeFestivals=true`에서 축제 seed 또는 고정 도시 내부 축제 lookup이 어떻게 적용됐는지 설명하는 audit |
| `candidate_evidence_package.coverage_audit` | 테마 충족, shortfall, quota 정보 |
| `candidate_evidence_package.fallback_audit` | 후보 부족 또는 도시 fallback 근거 |
| `candidate_evidence_package.candidate_reason_claims` | Candidate Evidence가 구조화 근거를 LLM으로 압축한 claim 후보. `evidence_refs`, `required_place_ids`와 함께 전달되며 최종 사용자 문장은 아님 |
| `tripType` | `daytrip`, `2d1n`, `3d2n`, `4d3n`, `5d4n` |
| `travelMonth`, `travelYear` | 계절, 축제, 대체 일정 판단 기준 |
| `active_required_themes` | 일정 안에 반영해야 하는 필수 테마 |
| `includeFestivals` | 사용자의 축제 포함 여부. `false`이면 축제 배치 시도 없음 |
| `festival_verifications` | 축제 검증 결과. Planner는 `date_status=confirmed`인 축제만 직접 배치 가능 |
| `unsupported_conditions` | 검색·검증으로 반영하지 못한 조건 |

선택 입력:

| 입력 | 설명 |
| --- | --- |
| `soft_query` 또는 `soft_preference_query` | 분위기·동행·취향 배치 참고 |
| `userLocation` / 내부 `user_location` | API `userLocation`을 Intent adapter가 정규화한 좌표. 이동 부담 설명과 당일치기 밀도 조정 참고 |
| `feedback_signals` | 선호/비선호 장소 유형 참고 |

Candidate Evidence는 구조화 근거를 바탕으로 짧은 claim 후보를 만들 수 있지만, 최종 추천 이유 문장을 확정하지 않는다. Planner는 `candidate_reason_claims`, `recommended_places`/`reserve_places`의 `evidence_reason_code`, `coverage_audit`, `fallback_audit`, raw/soft query, 검증된 축제 결과, 그리고 최종 배치 item의 detail enrichment 결과를 함께 사용해 사용자에게 보일 설명을 생성한다.

## 5. 핵심 불변식

Planner Agent는 아래 규칙을 항상 지켜야 한다.

1. 최종 일정은 소도시 1곳 중심이다.
2. 한 응답 안에 한국과 일본 데이터를 섞지 않는다.
3. Candidate Evidence Package에 없는 장소를 새로 만들지 않는다.
4. `reserve_places`는 Planner fallback용 후보이지 사용자에게 무조건 노출되는 목록이 아니다.
5. `no_candidate`와 `error` 상태에서 억지 일정을 생성하지 않는다.
6. `confirmed`가 아닌 축제를 확정 일정 블록으로 배치하지 않는다.
7. 숙소와 식당을 직접 추천하지 않고 각각 `links.staySearch`, `links.foodSearch` 또는 외부 검색 링크 CTA로 분리한다.
8. 운영시간, 가격, 예약 가능 여부, 실시간 혼잡도는 확정 사실처럼 말하지 않는다.
9. 추천 이유와 일정 블록의 장소·테마·축제 근거는 서로 일치해야 한다.
10. 검증 실패 결과를 Backend Serving으로 넘기지 않는다.
11. MVP Planner는 경로 최적화 문제가 아니라 후보 패키지의 슬롯 배정 문제로 다룬다.
12. 후보가 부족하면 장소명을 만들지 않고 `source=placeholder`인 자유시간·식사 선택 블록으로 표시한다.

## 6. Candidate Evidence Status별 처리

| status | Planner 처리 |
| --- | --- |
| `ok` | 정상 일정 생성. primary 후보를 중심으로 구성하고 필요한 경우 reserve를 일부 사용 |
| `insufficient_candidates` | 가능한 후보만으로 축소 일정 생성. 누락 테마, 부족 장소, 낮아진 confidence를 `user_notice`에 명시 |
| `no_candidate` | 일정 생성 금지. 조건 완화 안내, 검색 링크, 재질문 후보를 포함한 안전 폴백 응답 생성 |
| `error` | 일정 생성 금지. 시스템/검색 실패 안내와 재시도 가능성을 반환 |

`insufficient_candidates`는 실패가 아니라 제한된 결과다. 단, 필수 테마를 하나도 반영하지 못하거나 선택 도시가 없으면 `no_candidate`와 동일하게 안전 폴백으로 처리한다.

## 7. 실행 모드별 처리

| mode | Planner 기준 |
| --- | --- |
| `city_discovery` | Candidate Evidence가 선택한 `selected_city`를 사용 |
| `anchored_place_search` | `city_anchor.locked=true`인 도시를 유지. 후보나 축제가 부족해도 다른 도시로 변경하지 않음. `includeFestivals=true`이면 같은 도시 안에서 검증된 축제만 overlay 가능 |
| `festival_seeded_city_discovery` | Candidate Evidence가 축제 seed를 반영해 선택한 `selected_city`를 사용. Planner는 축제로 도시를 다시 고르지 않음 |

고정 도시 모드에서 후보가 부족하면 Planner는 일정 밀도를 낮추거나 reserve를 사용한다. 그래도 부족하면 `insufficient_candidates` 또는 `no_candidate`를 유지하며 다른 도시 후보를 섞지 않는다.

## 8. 일정 생성 단계

Planner Agent는 다음 순서로 실행한다.

| 단계 | 처리 | 산출물 |
| --- | --- | --- |
| 1 | status gate | 정상/제한/폴백 경로 결정 |
| 2 | 도시 anchor 확인 | `selected_city`, `city_anchor`, 국가 일관성 확인 |
| 3 | 후보 inventory 생성 | primary/reserve 후보를 `attraction`, `festival`, `meal_link`, `placeholder 가능 슬롯`으로 분리 |
| 4 | 슬롯 템플릿 선택 | `tripType` 기준 일차, 시간대, 관광/식사 목표 슬롯 산정 |
| 5 | 테마 coverage 계획 | 필수 테마별 최소 1개 이상 배치 시도 |
| 6 | 축제 overlay 배치 | `includeFestivals=true`이고 `date_status=confirmed`인 축제 1개를 Day 1 오후 메인 슬롯에 배치 (§11) |
| 7 | 장소 슬롯 배정 | 관광 슬롯은 테마 round-robin으로 배치하고, 식사 슬롯은 선택 도시 맛집 검색 링크/placeholder로 처리 |
| 8 | reserve fallback | primary로 부족하면 같은 도시·국가의 reserve 후보 사용 |
| 9 | 대체 일정 처리 | MVP에서는 기상 대체 일정을 생성하지 않고 빈 값으로 둠 |
| 10 | 최종 item detail enrichment | 최종 배치된 attraction item만 `DynamoLookupTool`로 DynamoDB detail을 보강하고 실패 warning 기록 |
| 11 | 설명 생성 | 추천 이유, 일정 흐름 이유, 안내 문구 작성 |
| 12 | 결정적 검증 | 필드, 국가, 도시, 테마, 축제, 근거 검증 |
| 13 | 의미 검증 | 설명-일정 일치, 환각, 폴백 안전성 검증 |

## 9. 일정 밀도 기준

| tripType | 일차 | 권장 블록 | 구성 원칙 |
| --- | ---: | ---: | --- |
| `daytrip` | 1 | 3-4 | 핵심 명소 2개, 식사 1회, 이동 부담 최소화 |
| `2d1n` | 2 | 6-8 | 대표 명소, 식사, 휴식, 숙소 검색 링크 포함 |
| `3d2n` | 3 | 9-12 | 일차별 테마 분리, 첫날·마지막 날 이동 부담 완화 |
| `4d3n` | 4 | 12-16 | 핵심 테마와 보조 테마를 나누고 반복 장소 유형 방지 |
| `5d4n` | 5 | 15-20 | 장기 체류형. 휴식·선택형 후보를 충분히 포함 |

시간대 표준값:

| 값 | 의미 |
| --- | --- |
| `morning` | 오전 핵심 방문 |
| `afternoon` | 오후 방문·체험 |
| `evening` | 저녁 식사·야경·가벼운 산책 |
| `flex` | 일정 밀도 조절용 선택 블록 |
| `meal` | 식사 중심 블록 |
| `rest` | 휴식 또는 이동 완충 |

API 응답은 현재 `timeOfDay`만 요구한다. 내부에서는 `flex`, `meal`, `rest`를 사용하되 Backend Serving에서 UI 계약에 맞게 표시명을 조정한다. 축제 블록은 시간 데이터가 없어 `timeOfDay`를 단정하지 않고 중립 표시("축제 · 시간 현장 확인")로 둔다(§11).

### 9.1 MVP 슬롯 템플릿

초기 Planner는 TSP나 지도 API 기반 route optimization을 수행하지 않는다. Candidate
Evidence Agent가 만든 primary/reserve 후보 순서를 신뢰하고, Planner는 사용자가 바로
이해할 수 있는 시간표에 후보를 배정한다.

| tripType | 기본 템플릿 |
| --- | --- |
| `daytrip` | 오전 관광 → 점심 → 오후 관광 → 저녁/귀가 |
| `2d1n` | Day1 관광 2개 + 식사 2개, Day2 관광 2개 + 식사 1개 |
| `3d2n` | Day1 가볍게, Day2 full day, Day3 짧게 |
| `4d3n+` | 중간 날에 핵심 관광을 배치하고 첫날/마지막날은 여유롭게 |

기본 슬롯 배열:

| tripType | day slots |
| --- | --- |
| `daytrip` | `[attraction, meal_link_lunch, attraction, meal_link_dinner]` |
| `2d1n` | Day1 `[attraction, meal_link_lunch, attraction, meal_link_dinner]`, Day2 `[attraction, meal_link_lunch, attraction]` |
| `3d2n` | Day1 `[attraction, meal_link_lunch, attraction, meal_link_dinner]`, Day2 `[attraction, attraction, meal_link_lunch, attraction, meal_link_dinner]`, Day3 `[attraction, meal_link_lunch, attraction]` |
| `4d3n` | Day1/Day4는 짧게, Day2/Day3은 full day 템플릿 사용 |
| `5d4n` 이상 | `4d3n` 템플릿에 중간 full day를 추가하고 휴식 슬롯을 늘림 |

### 9.2 Greedy + Round-Robin 배정 알고리즘

MVP 배정 절차:

1. `recommended_places`와 `reserve_places`를 입력 순서대로 유지한다.
2. 각 후보를 `entity_type` 기준으로 `attraction`, `festival`로 분리한다. 현재 단계에서 `restaurant` 후보는 입력으로 받지 않는다.
3. 관광 후보는 `theme_code` 또는 `assigned_theme`별 bucket으로 나눈다.
4. 관광 슬롯은 `active_required_themes`에서 `gourmet_retro`/`미식·노포`를 제외한 테마 순서로 round-robin 배정한다.
5. 필수 테마 bucket이 비면 남은 테마 후보를 입력 순서대로 사용한다.
6. 식사 슬롯은 특정 식당명을 배정하지 않고, 선택 도시 기준 맛집 검색 링크 CTA 또는 `placeId=null` placeholder로 둔다.
7. primary가 부족하면 reserve에서 같은 도시·국가 후보를 보충하고 `fromReserve=true`로 표시한다.
8. 그래도 부족하면 장소명을 만들지 않고 자유시간, 현지 식당 탐색, 숙소 체크인 같은 placeholder를 넣는다.

배정 결과 item에는 최소한 다음 provenance를 남긴다.

```json
{
  "slotType": "attraction",
  "title": "송지호해안 서낭바위",
  "themeCode": "sea_coast",
  "reason": "조용한 해안 풍경이라는 요청과 일치",
  "source": "primary",
  "qualityStatus": "passed",
  "fromReserve": false
}
```

placeholder item은 아래처럼 명명 장소가 아닌 시간표 보조 블록으로만 허용한다.

```json
{
  "slotType": "free_time",
  "title": "현지 산책 또는 휴식",
  "placeId": null,
  "source": "placeholder",
  "reason": "후보가 부족해 억지 장소 생성을 피합니다."
}
```

### 9.3 미식·노포 테마 특수 처리

현재 단계에서 `미식·노포`는 `restaurant` table 또는 restaurant 후보 조회로 처리하지 않는다.
Planner는 미식 테마를 일반 관광 테마와 같은 attraction bucket에서 경쟁시키지 않고,
선택 도시 내부 맛집을 탐색할 수 있는 외부 검색 링크와 meal slot CTA로 처리한다.

미식 테마 규칙:

1. 식사 슬롯은 특정 식당명을 생성하거나 DB에서 조회하지 않는다.
2. 미식 테마는 선택 도시 기준 `foodSearch` 링크 또는 meal slot CTA가 제공되면 coverage를 인정한다.
3. `active_required_themes`에 미식과 다른 관광 테마가 함께 있으면, 관광 슬롯 round-robin은 미식을 제외한 테마로 수행하고 미식은 식사 슬롯/링크에서 반영한다.
4. `active_required_themes`가 미식만 있으면, 일정은 "미식 탐색 중심"으로 낮은 밀도를 적용한다. 관광 후보가 부족하면 현지 산책·휴식·시장 둘러보기 placeholder와 맛집 검색 링크를 제공한다.
5. 식당 정보를 attraction slot에 억지로 넣지 않는다. 단, 향후 food market, 양조장, 요리 체험처럼 `entity_type=attraction|experience`로 들어오는 미식 후보는 관광 슬롯 배치가 가능하다.
6. 외부 링크 생성에 실패하면 존재하지 않는 식당명을 만들지 않고 `source=placeholder`, `placeId=null`인 "현지 식당 탐색" 블록과 `user_notice`를 생성한다.

미식 coverage 검증 기준:

| 요청 형태 | 충족 기준 |
| --- | --- |
| 미식 + 관광 테마 | 관광 테마는 attraction slot, 미식은 meal slot CTA 또는 `foodSearch` 링크로 각각 반영 |
| 미식 단독 daytrip | meal slot CTA 또는 `foodSearch` 링크 1개 이상 |
| 미식 단독 숙박형 | 가능한 경우 일차별 meal slot CTA를 제공하고 공통 `foodSearch` 링크를 연결 |
| 외부 링크 생성 실패 | 명명 식당 생성 금지, `theme_unmet` 또는 낮은 confidence와 안내 |

## 10. 장소 선택 정책

Planner는 후보를 다음 우선순위로 사용한다.

1. `recommended_places` 중 필수 테마와 일정 밀도에 맞는 장소
2. primary 후보 중 같은 테마의 대체 장소
3. `reserve_places` 중 같은 도시·국가·테마를 만족하는 장소
4. 후보가 부족하면 일정 밀도 축소 및 `user_notice`

장소 배치 기준:

- 필수 테마는 일정 전체에 최소 1회 이상 드러나야 한다.
- `미식·노포` 필수 테마는 식사 슬롯 CTA와 선택 도시 맛집 검색 링크에서 드러나면 충족으로 본다.
- `assigned_theme`와 `theme_code`가 있는 후보를 우선한다.
- 같은 title 또는 같은 `source_place_id`는 중복 배치하지 않는다.
- 같은 테마가 연속 3회 이상 나오지 않도록 관광 슬롯을 조정한다.
- 식사 슬롯에는 특정 식당 후보를 배치하지 않고, 하루 1-2회 이하의 맛집 탐색 CTA 또는 placeholder를 둔다.
- 야외 장소가 많아도 MVP에서는 별도 기상 대체 일정을 생성하지 않고 `user_notice`에서 현장 날씨 확인을 안내한다.
- 좌표가 있으면 같은 일차 안에서 가까운 장소끼리 묶을 수 있다.
- 좌표가 없으면 동선 이유를 단정하지 않고 “도시 내부 탐방 흐름” 수준으로 설명한다.
- 마지막 날은 관광 슬롯 수를 줄이고 이동·휴식 여지를 둔다.
- 후보 부족은 숨기지 않고 placeholder와 `user_notice`로 표시한다.

## 11. 축제 배치 정책

축제는 사용자가 `includeFestivals=true`를 선택했을 때만 일정에 반영한다. 축제 포함은 `includeFestivals`(true/false)로만 제어한다. Planner는 축제를 이용해 도시를 재선택하지 않는다.

`selected_city`는 두 방식 중 하나로 정해질 수 있다.

| mode | 축제와 도시의 관계 |
| --- | --- |
| `festival_seeded_city_discovery` | Candidate Evidence가 월·테마 조건을 만족하는 축제 seed 도시군 안에서 장소 evidence를 scoring해 `selected_city`를 고른다. |
| `anchored_place_search` | 사용자가 고정한 도시를 그대로 유지하고, 그 도시 내부에서만 월·테마 조건 축제 후보를 조회한다. 축제 후보가 없거나 검증 실패해도 Planner가 다른 도시로 바꾸지 않는다. |

Planner는 이미 확정된 `selected_city` 안에서 관광 baseline을 먼저 배치한 뒤, 해당 여행 월의 `confirmed` 축제를 일정 블록으로 overlay한다.

선택 도시 + 여행 월 기준이므로 배치 대상 축제는 **0개 또는 1개**다.

| `date_status` | 처리 |
| --- | --- |
| `confirmed` | Day 1 오후 메인 슬롯에 직접 배치 |
| `tentative` | 확정 배치 금지. 안내 문구 또는 후보 정보로만 표시 |
| `unknown` | 확정 배치 금지. 검증 한계 안내 |
| `outdated` | 확정 배치 금지. 재검증 필요 안내 |

배치 규칙:

1. 적격성은 **월 단위**로 판정한다. 축제 데이터에는 정확한 날짜가 있으나 사용자는 여행 월까지만 입력하고 일정은 상대 day(Day 1 / Day 2)로 구성되어 달력에 묶이지 않으므로, day 단위 겹침은 계산하지 않는다.
2. `confirmed` 축제는 **Day 1의 오후 메인 관광 슬롯**에 배치한다.
3. 축제 데이터에 시간 정보가 없으므로 `timeOfDay`를 단정하지 않고 중립 표시("축제 · 시간 현장 확인")로 둔다.
4. 밀려난 Day 1 오후 관광지는 같은 일차 빈 슬롯으로 이동한다. 자리가 없고 그 관광지가 필수 테마(`active_required_themes`)를 유일하게 충족하는 블록이면 다른 일차·슬롯의 비핵심 관광지와 스왑해 보존한다. 스왑도 불가능하면 **축제 배치를 우선**하고(해당 관광지 제거), `user_notice`에 그 테마 반영 부족을 안내한다.
5. 축제의 실제 개최일은 `user_notice`로 안내해, 사용자가 여행 날짜를 축제일에 맞추도록 가이드하고 시간 미상을 고지한다. 축제가 여러 날 열려도 일정에는 Day 1 한 블록만 배치하고 전체 개최 기간은 `user_notice`에 적는다.
6. 해당 월에 `confirmed` 축제가 없으면 축제를 배치하지 않고 일반 장소 중심으로 구성한 뒤 `user_notice`에 사유를 남긴다. `daytrip`이나 미식 단독처럼 Day 1 오후가 placeholder인 경우에는 축제가 그 자리를 차지하므로 밀려나는 관광지가 없다.

> 설계 근거: 축제 데이터는 날짜만 있고 시간이 없으며, 사용자 입력은 월까지만 받고 일정은 상대 day로 구성된다. 그래서 축제는 시간대 블록이 아니라 "그 날의 day-level 앵커"로 다루고, 매칭은 월 적격성으로, 실제 날짜는 사용자에게 가이드로 제공한다. 이 정책은 일정 생성을 관광 baseline(Pass 1) → 축제 overlay(Pass 2)의 2단계로 보는 `itinerary_flow.md` §6.3과 동일한 모델이다.

## 12. 대체 일정 정책

`alternativeItinerary`는 일반 일정 수정이 아니라, 같은 목적지 안에서 날씨나 데이터 결측에 대비하는 보조 일정이다. 단, MVP에서는 기상 대체 일정 생성을 우선 고려하지 않는다. Planner는 기본 일정만 생성하고, `alternativeItinerary`는 `null` 또는 빈 배열/객체로 둔다.

후속 고도화에서 검토할 생성 조건:

- 월별 기상 경향상 우천, 폭설, 태풍, 혹서/혹한 리스크가 큼
- 본 일정의 야외 장소 비중이 높음
- 축제 또는 야외 핵심 후보가 `tentative`, `unknown`, `outdated`
- 운영시간·좌표·검증 상태 결측으로 확정 배치가 어려움

후속 고도화 원칙:

- 동일한 `selected_city` 안에서 구성한다.
- 실내 관광지, 문화시설, 공예·체험, 음식점, 카페 후보를 우선한다.
- 필수 테마를 가능한 한 유지한다.
- 사용자가 포함한 축제는 대체 일정에서도 **유지한다**. 단 야외 축제이면 우천·기상 리스크를 `fallbackReason` 또는 `user_notice`에 고지한다.
- 야외 장소를 제외한 이유를 `fallbackReason` 또는 `user_notice`에 남긴다.
- 대체 일정이 불가능하면 빈 배열과 사유를 반환한다.

## 13. 출력 계약

Planner Agent의 내부 출력:

```json
{
  "itinerary": {
    "tripType": "2d1n",
    "days": [
      {
        "day": 1,
        "title": "전통 거리와 바다 산책 중심 일정",
        "summary": "오전에는 대표 산책지를 보고 오후에는 지역 음식 후보를 배치합니다.",
        "items": [
          {
            "sortOrder": 1,
            "timeOfDay": "morning",
            "title": "장사해수욕장",
            "contentType": "attraction",
            "placeId": "P_001",
            "sourcePlaceId": "129123",
            "themeCode": "sea_coast",
            "durationMinutes": 90,
            "moveHint": "같은 도시 안에서 이어지는 가벼운 산책 블록입니다.",
            "reason": "바다·해안 테마와 raw query 근거가 함께 확인된 후보입니다.",
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
    "trigger": null,
    "reason": null,
    "days": []
  },
  "recommendationReasons": [
    "선택한 필수 테마가 후보 장소 근거에서 확인됩니다.",
    "선택 도시는 일정에 필요한 primary 후보를 충분히 제공합니다."
  ],
  "itineraryFlowReason": "오전에는 대표 산책지를 먼저 배치하고, 오후에는 음식·문화 후보를 이어 이동 부담을 낮췄습니다.",
  "externalLinks": {
    "map": "https://maps.google.com/...",
    "staySearch": "https://...",
    "foodSearch": "https://..."
  },
  "confidence": 0.86,
  "user_notice": null,
  "validation_result": {
    "passed": true,
    "failure_categories": []
  }
}
```

Backend Serving은 이 내부 출력을 API 명세의 `/recommendations` 응답으로 패키징한다.

| Planner 내부 필드 | API 응답 필드 |
| --- | --- |
| `selected_city` | `destination` |
| `itinerary` | `itinerary` |
| `recommendationReasons` | `explainability.recommendationReasons` |
| `itineraryFlowReason` | `explainability.itineraryFlowReason` |
| `confidence` | `explainability.confidence` |
| `user_notice` | `explainability.user_notice` |
| `festival_verifications` | `festivalDateVerifications` |
| `externalLinks.map` | `links.map` |
| `externalLinks.staySearch` | `links.staySearch` |
| `externalLinks.foodSearch` | `links.foodSearch` 또는 `links.searchLinks.food` |

## 14. 설명 생성 규칙

`recommendationReasons`는 2-4개를 기본으로 한다.

설명 생성은 Candidate Evidence가 제공한 claim 후보를 최종 일정 기준으로 검증하고 사용자 언어로 확정하는 단계다. Planner는 `candidate_reason_claims`와 `evidence_reason_code`를 방향 신호로 쓰되, 실제 문장에는 최종 일정에 배치된 item, detail enrichment로 확인된 정보, raw/soft query, 검증된 축제 결과만 반영한다.

`candidate_reason_claims` 처리 규칙:

| 규칙 | 설명 |
| --- | --- |
| evidence ref 확인 | `evidence_refs`가 Candidate Evidence Package 내부 필드와 연결되어야 한다 |
| place id 확인 | `required_place_ids`가 있으면 해당 장소가 최종 itinerary에 배치된 경우에만 claim 사용 |
| detail 충돌 확인 | detail enrichment 결과와 claim이 충돌하거나 detail이 부족하면 claim을 수정하거나 폐기 |
| raw/soft query 반영 | claim이 사용자 요청과 연결된다고 말하려면 `cleaned_raw_query` 또는 `soft_preference_query`와 최종 배치 item overview가 함께 뒷받침해야 한다 |
| 복사 금지 | CE claim을 검증 없이 그대로 `recommendationReasons`에 복사하지 않는다 |

포함해야 하는 축:

| 축 | 포함 내용 |
| --- | --- |
| 조건 충족 | 국가, 월, 일정 유형, 필수 테마 |
| 도시 특성 | 선택 도시가 가진 테마 evidence, 후보 충분성, 축제 anchor 여부 |
| 일정 가능성 | 장소 유형 균형, 이동 부담, primary/reserve 후보 사용 여부 |
| 한계 안내 | 미반영 조건, 미검증 축제, 숙박/실시간 정보 한계 |

`itineraryFlowReason`은 장소 나열이 아니라 순서와 밀도에 대한 설명이어야 한다.

금지:

- “가장 저렴한 숙소”, “예약 가능”, “현재 운영 중”처럼 실시간 확인이 필요한 표현
- Candidate Evidence에 없는 장소명
- `tentative/unknown/outdated` 축제를 확정 개최처럼 말하는 표현
- 테마 coverage가 부족한데 모든 조건을 완벽히 만족한다고 말하는 표현

## 15. Confidence와 User Notice

기본 confidence는 Candidate Evidence 상태와 Planner 검증 결과를 함께 반영한다.

| 조건 | confidence 영향 |
| --- | --- |
| `status=ok`이고 검증 통과 | 높음 |
| `insufficient_candidates` | 중간 이하 |
| reserve 후보 다수 사용 | 소폭 하향 |
| 필수 테마 일부 shortfall | 하향 및 `user_notice` 필요 |
| 축제 미검증 또는 미배치 | 하향 또는 안내 |
| 운영시간·좌표 결측 | 하향 또는 안내 |
| `no_candidate/error` | 낮음, 일정 생성 금지 |

`user_notice`에 반드시 포함할 상황:

- 조건 일부를 반영하지 못함
- 필수 테마 후보 부족
- confirmed 축제가 없음
- 숙박 가격·예약 가능 여부는 직접 확인 필요
- 실시간 날씨·운영 여부는 표시 또는 외부 링크에서 확인 필요
- 후보 부족으로 일정 밀도를 낮춤

## 16. 검증 계약

### 16.1 결정적 검증

| 검증 | 기준 | 실패 카테고리 |
| --- | --- | --- |
| 필수 필드 | API 필수 필드가 존재 | `field_missing` |
| 단일 목적지 | 모든 item이 `selected_city.city_id`에 속함 | `destination_mixed` |
| 국가 분리 | 모든 item이 같은 `country` | `country_mixed` |
| 근거 연결 | `source=primary/reserve/festival`인 장소·축제 item이 Candidate Evidence 또는 confirmed festival에 존재 | `grounding_missing` |
| 외부 링크 근거 | `source=food_search` 또는 `source=external_link`인 식사 item은 선택 도시 기준 Link Builder payload와 연결 | `external_link_missing` |
| placeholder 안전성 | `source=placeholder` item은 장소명·운영정보를 만들지 않고 `placeId=null` | `placeholder_unsafe` |
| 축제 상태 | 직접 배치 축제는 `confirmed` | `festival_unconfirmed` |
| 필수 테마 | 관광 테마는 attraction/festival slot, 미식 테마는 meal slot CTA 또는 `foodSearch` 링크/안내에 반영 | `theme_unmet` |
| 숙박·식당 정책 | 숙소·식당 직접 추천 없이 검색 링크 또는 placeholder 제공 | `external_recommendation_policy_violation` |
| 상태별 처리 | `no_candidate/error`에서 일정 미생성 | `unsafe_fallback` |

### 16.2 의미 검증

| 검증 | 기준 | 실패 카테고리 |
| --- | --- | --- |
| 설명-일정 일치 | 이유가 실제 itinerary item과 연결됨 | `explanation_mismatch` |
| 환각 방지 | 없는 장소·축제·운영 정보 없음 | `hallucination` |
| 동선 설명 적정성 | 좌표 결측 시 과도한 이동 단정 없음 | `route_overclaim` |
| 폴백 안전성 | 부족·결측·실패가 사용자에게 설명됨 | `fallback_unsafe` |

### 16.3 재시도 규칙

| 실패 카테고리 | 처리 |
| --- | --- |
| `field_missing` | Planner 재작성 |
| `grounding_missing` | 해당 item 제거 또는 reserve 대체 |
| `external_link_missing` | 식사 item을 placeholder로 전환하고 `user_notice`에 링크 생성 실패 안내 |
| `placeholder_unsafe` | placeholder를 일반 자유시간/식사 선택 문구로 재작성 |
| `festival_unconfirmed` | 축제 item 제거 후 안내 문구로 전환 |
| `theme_unmet` | reserve에서 같은 테마 후보 보충. 불가하면 `user_notice` |
| `explanation_mismatch` | 일정 골격 유지, 설명만 재작성 |
| `hallucination` | Planner 재작성. 2회 반복 시 안전 폴백 |
| `unsafe_fallback` | 안전 폴백 템플릿으로 즉시 전환 |

`validation_retry_count < 2`이면 Planner 내부 재작성 또는 Supervisor 재진입을 허용한다. 2회에 도달하면 안전 폴백 응답으로 종료한다.

## 17. 안전 폴백 응답

안전 폴백은 일정 생성 실패를 숨기지 않는다.

`no_candidate` 예시:

```json
{
  "itinerary": null,
  "recommendationReasons": [],
  "itineraryFlowReason": null,
  "confidence": 0.2,
  "user_notice": "선택한 테마와 월 조건을 동시에 만족하는 후보가 부족해 일정을 만들 수 없습니다. 테마를 줄이거나 다른 월을 선택해 주세요.",
  "externalLinks": {
    "map": null,
    "staySearch": null,
    "foodSearch": null
  }
}
```

`insufficient_candidates` 예시는 일정은 생성하되 다음을 포함한다.

- 축소된 일정 밀도
- 누락된 필수 테마 또는 부족한 장소 유형
- reserve 사용 여부
- 사용자에게 필요한 확인 사항

## 18. PlanDraft와 저장 경계

PlanDraft는 추천 결과를 사용자가 저장하기 전까지의 임시 상태다.

| 단계 | 저장 위치 | 원칙 |
| --- | --- | --- |
| 동기 추천 응답 | AgentCore Memory 또는 응답 cache | 짧은 수명. 원문 대화 저장 금지 |
| 사용자가 저장 | MySQL `itineraries`, `itinerary_items` | 저장 API 호출 시 스냅샷 저장 |
| 축제 검증 cache | DynamoDB `lovv_festival_verify_cache` | `festival_id + travelYear` 기준 TTL |
| trace/metrics | Observability 또는 TTL 로그 | 원문 대신 요약·참조 키 저장 |

현재 API 정본에는 일반 일정 수정 API가 확정되어 있지 않다. Planner MVP는 최초 추천 생성을 우선하며, 일반 일정 수정과 기상 대체 일정은 후속 고도화 후보로 분리 검토한다.

## 19. Link Builder 계약

Planner는 링크 문자열을 직접 조합해도 되지만, 운영 구현에서는 `Link Builder Skill` 또는 Backend helper에 payload를 넘기는 방식을 우선한다.

| 링크 | 기준 |
| --- | --- |
| `map` | 선택 도시와 itinerary item의 장소명을 포함한 지도 검색 링크 |
| `staySearch` | 선택 도시명, 여행 월, 일정 유형 기반 숙소 검색 링크 |
| `foodSearch` | 선택 도시명과 미식·맛집 키워드 기반 외부 검색 링크. 특정 식당 추천이 아니라 탐색 CTA |

숙소·맛집 링크는 검색 진입점일 뿐 추천 결과가 아니다.

## 20. 테스트 기준

| ID | 유형 | 입력 | 기대 결과 |
| --- | --- | --- | --- |
| PL-N01 | 정상 | `status=ok`, `2d1n`, 테마 2개 | 2일 일정, 필수 테마 반영, 설명-일정 일치 |
| PL-N02 | 정상 | `includeFestivals=true`, 그 달 confirmed 축제 1개 | Day 1 오후 메인 슬롯에 축제 배치, 밀린 관광지 이동/제거, 시간 미상 안내 |
| PL-N03 | 정상 | `anchored_place_search`, 후보 충분 | 고정 도시 안에서만 일정 생성 |
| PL-N04 | 정상 | `anchored_place_search`, `includeFestivals=true`, 고정 도시 안 confirmed 축제 1개 | 고정 도시 유지, 관광 baseline 위에 축제 overlay |
| PL-F01 | 부족 | `insufficient_candidates` | 축소 일정, confidence 하향, 부족 안내 |
| PL-F02 | 후보 없음 | `no_candidate` | 일정 생성 금지, 조건 완화 안내 |
| PL-F03 | 오류 | `error` | 일정 생성 금지, 재시도 안내 |
| PL-F04 | 축제 미확정 | `tentative` 축제만 존재 | 축제 직접 배치 금지, 안내 문구 |
| PL-F05 | 국가 혼합 | KR selected city + JP place | Validation 실패 |
| PL-F06 | 근거 없음 | Candidate Evidence에 없는 장소명 생성 | Validation 실패 |
| PL-F07 | 숙박 직접 추천 | 특정 숙소명 추천 | Validation 실패 |
| PL-F08 | 식당 직접 추천 | 특정 식당명 생성 | Validation 실패, `foodSearch` 링크 또는 placeholder로 전환 |
| PL-R01 | reserve 사용 | primary 슬롯 배정 부족, reserve 충분 | reserve 사용, `fromReserve=true`, audit 기록 |
| PL-S01 | 슬롯 배정 | `2d1n`, 관광 4개, 식사 슬롯 3개 | 관광 슬롯은 후보 배치, 식사 슬롯은 맛집 검색 CTA/placeholder 배정 |
| PL-S02 | 테마 균형 | 필수 테마 3개, 후보 충분 | round-robin으로 테마가 고르게 분산되고 같은 테마 3연속 없음 |
| PL-S03 | 링크 생성 실패 | 식당 후보 없음, `foodSearch` 링크 실패 | 명명 식당 생성 없이 `source=placeholder` 식사 슬롯과 `user_notice` 생성 |
| PL-G01 | 미식 혼합 | `미식·노포` + `바다·해안` | 바다는 관광 슬롯, 미식은 식사 슬롯 CTA/`foodSearch` 링크에서 충족 |
| PL-G02 | 미식 단독 | `미식·노포`만 있고 restaurant 후보 조회 없음 | 낮은 밀도의 미식 탐색 중심 일정, 관광 슬롯은 휴식/산책 placeholder 허용 |
| PL-G03 | 미식 링크 실패 | 미식 필수이나 외부 링크 생성 실패 | 명명 식당 생성 금지, `theme_unmet` 또는 부족 안내 |

## 21. Open Decisions

| 항목 | 결정 필요 |
| --- | --- |
| `durationMinutes` 표준값 | 장소 유형별 기본 체류 시간 테이블 필요 |
| 이동거리 계산 | 좌표 기반 단순 거리, 외부 지도 API, 또는 heuristic 중 MVP 기준 결정 |
| UI 표시용 source badge | `tour_api`, `official`, `dynamodb`, `web_verified` 등 표준 코드 |
| 맛집 링크 API 응답 필드 | `links.foodSearch`로 확장할지, 기존 `GET /external/search-links` 결과를 `links` 하위에 포함할지 API 정본 확인 필요 |

## 22. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v1.6 | 2026-06-13 | llm | `restaurant` 후보/테이블 조회를 Planner 입력 전제에서 제거하고, 식사·미식 처리를 선택 도시 기반 외부 맛집 검색 링크와 placeholder 중심으로 전환 |
| v1.5 | 2026-06-13 | llm | `anchored_place_search`에서도 `includeFestivals=true`가 가능함을 명시하고, 고정 도시 내부 축제 lookup 결과만 Planner가 overlay하도록 정리 |
| v1.4 | 2026-06-13 | llm | `anchored_place_search`를 정식 고정 도시 mode로 통일하고, Planner는 축제로 도시를 재선택하지 않지만 `selected_city`는 Candidate Evidence의 축제 seed를 반영했을 수 있음을 명시. 축제 배치 조건을 `date_status=confirmed` 기준으로 정리하고 MVP에서 기상 대체 일정과 일반 일정 수정을 보류. API `userLocation`과 내부 `user_location` 경계를 명시 |
| v1.3 | 2026-06-13 | llm | 축제 배치를 관광 baseline 위 overlay 모델로 구체화. 축제 포함은 `includeFestivals`만으로 제어하고, §8 단계 6·§9 timeOfDay·§11을 재작성해 선택 도시·여행 월 기준 0/1개, 월 적격성 판정, Day 1 오후 메인 슬롯 배치, 시간 데이터 부재로 timeOfDay 중립화, 밀린 관광지 이동/제거, 실제 개최일 가이드 안내를 정의 |
| v1.2 | 2026-06-12 | llm | `미식·노포` 테마를 meal slot coverage로 인정하는 특수 처리와 검증·테스트 기준 추가 |
| v1.1 | 2026-06-12 | llm | Planner MVP를 `tripType`별 슬롯 템플릿, 관광/식당 분리, 테마 round-robin, reserve 보충, placeholder 부족 표시 방식으로 구체화 |
| v1.0 | 2026-06-12 | llm | `itinerary_flow.md` 초안을 보완해 Planner Agent 상세 정본 작성. Candidate Evidence status별 처리, 고정 도시 모드, 축제 배치, 검증·재시도, API/DB 경계 정의 |
