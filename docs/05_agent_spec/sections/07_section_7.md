# 7. 단계별 명세

## 7.1 `Intent_Agent`

| 항목 | 내용 |
| --- | --- |
| 책임 | 멀티턴 대화 정리, 자연어 조건 파싱, 온보딩·현재 의도 병합, 추가 질문 여부 판단 |
| 입력 | `messages`, `conversation_summary`, UI 조건, 온보딩, 피드백 |
| 출력 | `extracted_inputs`, `active_required_themes`, `soft_preferences`, `unsupported_conditions`, `fulfilled_matrix` |
| 통합 책임 | 기존 `Condition_Parser_Agent`의 물리 노드는 제거하고 논리 책임을 내장한다. |
| 분리 트리거 | 파싱 정확도 저하, 프롬프트 비대화, 테스트 하네스에서 파싱 실패율 상승 시 별도 노드로 분리한다. |

온보딩은 장기 선호, 자연어는 현재 여행 의도로 본다.
active theme는 최대 3개를 기본으로 하며, 자연어가 강하게 요구한 테마가 온보딩보다 우선한다.

현재 단계의 Intent Agent 구현 기준은 `supplemental/intent_agent.md`를 따른다. 핵심 산출물은 `supplemental/candidate_evidence_agent.md`의 입력 계약에 맞춘 `candidate_evidence_input`이며, Intent Agent는 도시 검색·점수화·일정 생성을 수행하지 않는다.

## 7.2 `Supervisor_Router`

| 항목 | 내용 |
| --- | --- |
| 책임 | `fulfilled_matrix`를 읽고 다음 노드 호출, 재시도·폴백 제어, 최종 패키징 전 상태 조립 |
| 직접 수행 | 상태 읽기/쓰기, handoff payload 조립, `Matrix Transition Skill` 호출, retry 상한 판단 |
| 수행하지 않음 | 대화 원문 해석, 웹 원문 해석, 점수 계산, 일정·설명 생성 |
| raw 정책 | raw 대화, raw RAG 결과, raw 웹 검색 결과를 보유하지 않는다. |

`fulfilled_matrix` 기호 규격은 8.2를 단일 출처로 사용한다.

## 7.3 `Candidate_Evidence_Agent`

| 항목 | 내용 |
| --- | --- |
| 책임 | 관광지 evidence 검색, 도시/장소 scoring, Planner 입력용 primary/reserve 후보 패키징 |
| 통합 책임 | 기존 `Polymorphic_Retriever_Agent`와 `Ranker_Agent`의 물리 노드를 통합한다. |
| 도구 | `Destination Search Tool`, `Scoring Tool`, `Weather Trends Skill` |
| 출력 | `selected_city`, `city_rankings`, `recommended_places`, `reserve_places`, `coverage_audit`, `retrieval_audit` |
| 하지 않음 | 일정 생성, 추천 설명 생성, 최종 API 응답 생성, restaurant table 조회 또는 식당 후보 직접 추천 |
| city discovery | `destinationId`가 없으면 여러 도시의 장소 evidence를 검색하고 scoring으로 `selected_city`를 고른다. |
| anchored search | `destinationId`가 있으면 해당 도시 내부의 장소 evidence와 예비 후보를 구성한다. |
| 제약 | 한국 요청에는 한국 데이터만, 일본 요청에는 일본 데이터만 검색한다. |

Candidate Evidence Agent의 기본 로직:

1. `Intent_Agent`가 구조화한 `active_required_themes`, `cleaned_raw_query`, `soft_preference_query`, 내부 `user_location`(API `userLocation`에서 정규화), `destinationId`를 입력으로 받는다.
2. `active_required_themes`는 deterministic metadata gate와 theme coverage 계산에 사용한다. 단, 현재 단계에서 `미식·노포`는 restaurant 후보 조회가 아니라 선택 도시 기준 맛집 검색 링크 요구로 Planner에 전달한다.
3. `cleaned_raw_query`와 `soft_preference_query`는 장소 evidence 검색의 별도 query channel로 사용한다.
4. `Scoring Tool`은 도시/장소 점수, 테마 커버리지, 테마 균형, 거리/일수 가능성, 후보 충분성을 계산한다.
5. Planner fallback 지연을 줄이기 위해 최종 일정 필요 수보다 넉넉한 관광지 `recommended_places`와 `reserve_places`를 반환한다.
6. 복수 테마 선택 시 theme quota와 balance audit을 적용해 특정 테마 후보로 쏠리지 않게 한다.
7. `unsupported_conditions`는 검색 조건으로 전달하지 않는다.

검색 인덱스 계약:

| 항목 | 기준 |
| --- | --- |
| 정형 원장 | 목적지, 축제, 관광지, 일정 결과의 확정 기준은 MySQL 원장을 따른다. |
| 실행/이벤트 상태 | Agent trace, API 로그, 사용자 이벤트, async job은 DynamoDB TTL 테이블에 요약 저장한다. |
| 의미 검색 | S3 vector index는 재생성 가능한 검색 인덱스로만 사용하며 원본 저장소로 보지 않는다. |
| 관계 탐색 | 그래프DB 직접 도입 대신 Lambda 관계 탐색 보조 기능으로 도시·축제·테마·장소 관계를 확장한다. |
| 필수 metadata | `country`, `destination_id`, `city_id`, `content_type`, `theme_tags`, `recommended_months`, `source_type` |
| 금지 metadata | 사용자 ID 원문, 대화 전문, 비공개 운영 메모 |

Candidate Evidence Agent는 S3 vector metadata filter로 국가·도시·테마·월·콘텐츠 유형을 1차 제한하고, Lambda 관계 탐색 보조 기능으로 도시·축제·테마·장소 관계를 확장한 뒤 MySQL 원장 또는 DynamoDB 정규화 문서의 확정 필드로 후보를 재검증한다.
S3 vector 결과만으로 장소 존재, 축제 일정, 운영 여부를 확정하지 않는다.

## 7.4 `Festival_Verifier_Agent`

| 항목 | 내용 |
| --- | --- |
| 책임 | 축제 후보의 해당 연도 개최 기간을 공식 웹 출처 기준으로 검증 |
| 입력 | 축제 후보, `target_region`, `travelYear`, `travelMonth`, 공식 출처 후보 |
| 출력 | `festival_id`, `date_status`, `start_date`, `end_date`, `source_url`, `source_type`, `verified_at`, `confidence` |
| 캐시 키 | `festival_id + travelYear` |
| downstream 정책 | 웹 검색 원문은 전달하지 않고 검증 JSON만 반환한다. |

캐시 TTL:

| `date_status` | TTL | 처리 |
| --- | --- | --- |
| `confirmed` | 30일 | TTL 내 웹 검색 생략 |
| `tentative` | 7일 | 짧은 주기로 재검증 |
| `unknown` / `outdated` | 1일 | 다음 요청에서 재검색 유도 |

`confirmed` 축제만 일정에 직접 배치한다.
`tentative`는 안내 문구 또는 후보 정보로만 사용한다.
축제 포함 요청에서는 모든 후보를 웹 검증하지 않고, Candidate Evidence Agent가 구성한 상위 도시/축제 후보 K곳(기본 2~3곳)만 검증한다.
`includeFestivals=false`이면 Festival Verifier를 건너뛰고 `festival` 매트릭스 항목을 `N/A`로 둔다.

## 7.5 `Planner_Agent`

| 항목 | 내용 |
| --- | --- |
| 책임 | 일정 생성, 추천 설명 생성, 최종 출력 검증을 하나의 Planner 책임으로 통합 |
| 입력 | Candidate Evidence Package, `tripType`, `active_required_themes`, 축제 검증, 사용자 안내 대상 조건 |
| 출력 | `itinerary`, `alternativeItinerary`, `recommendationReasons`, `itineraryFlowReason`, `externalLinks`, `confidence`, `user_notice` |
| 통합 이유 | 일정, 설명, 검증이 같은 후보·점수·검증 결과를 보게 해 "이유-일정" 불일치와 후단 재호출을 줄인다. |
| 규칙 | 필수 테마를 일정과 설명에 함께 반영하고, 과도한 이동·검증되지 않은 축제 배치·DB 근거 없는 장소 설명을 금지한다. |

Planner Agent의 상세 정본은 `supplemental/planner_agent.md`를 따른다. `supplemental/itinerary_flow.md`는 PlanDraft, 수정 흐름, 대체 일정 아이디어를 담은 초안 문서로 유지하되 구현 기준은 `supplemental/planner_agent.md`를 우선한다.

추천 이유와 동선 설명은 다음 세 축을 중심으로 작성한다.

| 축 | 포함 내용 |
| --- | --- |
| 조건 충족 | 국가, 월, 일정 유형, 선택 테마, 거리 조건 |
| 도시 특성 | 테마 특화도, 희소 테마, 혼잡·규모 보정 |
| 일정 가능성 | 콘텐츠 타입 균형, soft/raw 적합도, `confirmed` 축제 여부 |

반영하기 어려운 조건은 `user_notice`로 분리한다.
숙박 품질, 가격, 예약 가능 여부, 실시간 혼잡도, 실시간 운영 여부는 확정 추천 근거로 쓰지 않는다.

## 7.6 `Validation Skill`

Planner Agent 내부에서 LLM 의미 검증 전에 결정적으로 검사한다.

| 검증 | 기준 |
| --- | --- |
| 필드 누락 | 필수 출력 필드가 존재하는가 |
| 국가 혼합 | 한 응답에 KR/JP 데이터가 섞이지 않는가 |
| 단일 목적지 | 최종 추천이 소도시 1곳 중심인가 |
| 축제 배치 | 일정 배치 축제는 `confirmed`인가 |
| active theme | `active_required_themes`가 결과에 반영됐는가 |

## 7.7 Planner 의미 검증

| 항목 | 기준 | 실패 카테고리 |
| --- | --- | --- |
| 근거성 | 추천 이유가 DB/검색 근거와 연결되는가 | `grounding_missing` |
| 환각 방지 | 존재하지 않는 장소·축제·운영 정보를 만들지 않았는가 | `hallucination` |
| 조건 충족 | `active_required_themes`가 최종 결과에 반영됐는가 | `condition_unmet` |
| 설명 가능성 | 추천 이유와 일정 흐름 이유가 자연어로 충분한가 | `explanation_weak` |
| 폴백 안전성 | 결측과 실패 상황이 `confidence`, `user_notice`로 안내되는가 | `fallback_unsafe` |

검증 실패 시 `validation_retry_count`를 증가시킨다.
2회 미만이면 Supervisor가 실패 카테고리별 결정 규칙으로 분기한다.
2회에 도달하면 안전 폴백 응답으로 종료한다.

| 실패 카테고리 | Supervisor 분기 |
| --- | --- |
| `grounding_missing` | `Planner_Agent` 재호출. 동일 Candidate Evidence Package를 유지하되 설명·근거 필드를 우선 재작성한다. |
| `hallucination` | `Candidate_Evidence_Agent` 재탐색 또는 해당 항목 제거 |
| `condition_unmet` | `Candidate_Evidence_Agent` 재탐색 또는 Planner 재구성 |
| `explanation_weak` | `Planner_Agent` 재호출. 일정 골격을 유지하고 설명 필드를 보강한다. |
| `fallback_unsafe` | 안전 폴백 템플릿으로 즉시 전환 |
