# 8. 도구 및 Skill

## 8.1 사용 도구/Skill

| 도구/Skill | 책임 | 호출 주체 |
| --- | --- | --- |
| `Destination Search Tool` | S3 vector metadata filter, 목적지·장소·테마 DB 조회, 의미 검색 기반 장소 evidence 조회 | Candidate Evidence Agent |
| `Festival Catalog Search` | 축제명, 지역, 대략 시기, 공식 출처 후보 조회 | Festival Verifier |
| `Web Search` | 해당 연도 축제 공식 출처 검색 | Festival Verifier |
| `Weather Trends Skill` | 월별 기상 경향 정형값 조회 | Candidate Evidence Agent, Planner Agent |
| `Scoring Skill` | 도시/장소 후보 점수 계산과 primary/reserve 후보 구성 | Candidate Evidence Agent |
| `Matrix Transition Skill` | `fulfilled_matrix` 전이 | Supervisor |
| `Validation Skill` | 결정적 출력 검증 | Planner Agent |
| `Link Builder Skill` | 지도·숙소 검색 링크 생성 | Planner Agent |
| `Output Packaging Skill` | UI 응답 패키징과 민감정보 마스킹 | Backend Serving |
| `Food Search Link Builder` | 선택 도시 기준 외부 맛집 검색 링크 생성. 식당 DB 조회나 특정 식당 추천이 아님 | Planner / Backend Serving |
| `WeatherAPI Proxy` | 상세 화면 표시용 실시간 날씨 조회 | Backend Serving |

## 8.2 `fulfilled_matrix` 규격

표준 키는 `evidence`, `festival`, `planning`으로 고정한다.
Supervisor는 `X` 항목을 아래 우선순위로 처리한다.
`evidence`는 기존 retrieval/ranking을 통합한 Candidate Evidence Agent 구간이며, 장소 evidence 검색, 도시/장소 scoring, primary/reserve 후보 패키징을 포함한다.
`planning`은 일정 생성, 설명 생성, 결정적/의미 검증을 포함한 Planner Agent 구간이다.

| 우선순위 | 키 | 담당 |
| --- | --- | --- |
| 1 | `evidence` | Candidate Evidence Agent |
| 2 | `festival` | Festival Verifier |
| 3 | `planning` | Planner Agent |

| 기호 | 의미 | 라우팅 |
| --- | --- | --- |
| `X` | Pending / 탐색 또는 처리 필요 | Supervisor 라우팅 대상 |
| `O` | Success / 성공적으로 처리 완료 | 라우팅 제외 |
| `△` | Fallback / 데이터 결측 또는 실패로 제한 처리 완료 | 기본 라우팅 제외. 명시된 retry 규칙이 있을 때만 제한 재시도 |
| `N/A` | Excluded / 조건 미선택 또는 명시 거부 | 라우팅 제외 |

멀티턴에서 사용자가 명시 거부를 번복하면 `Matrix Transition Skill`이 `N/A → X` 전이를 수행한다.
확신이 낮으면 전이하지 않고 추가 질문을 생성한다.

Matrix Transition Skill의 표준 전이는 아래를 따른다.
`needs_clarification=true`는 사용자 응답이 필요한 상태이므로 Supervisor가 Planner를 호출하지 않고 `END_WAIT_USER`로 종료한다.

| 발생 지점 | 조건 | matrix 전이 | 다음 동작 |
| --- | --- | --- | --- |
| Intent Agent | 필수 API/UI 입력 또는 사용자 확인이 부족하고 `needs_clarification=true` | 관련 항목 `X` 유지 | `clarifying_question` 생성 후 `END_WAIT_USER` |
| Candidate Evidence Agent | `status=ok` | `evidence=O` | `includeFestivals=true`이면 `festival` 구간, 아니면 `planning` 구간으로 진행 |
| Candidate Evidence Agent | `status=insufficient_candidates` | `evidence=△` | 제한된 후보 패키지로 `planning` 진행 |
| Candidate Evidence Agent | `status=no_candidate`이고 `needs_clarification=true` | `evidence=△` | 사용자 질문 후 `END_WAIT_USER`. Festival Verifier와 Planner는 호출하지 않음 |
| Candidate Evidence Agent | `status=no_candidate`이고 `needs_clarification=false` | `evidence=△` | 승인된 safe fallback 정책이 있을 때만 `planning` 또는 Backend fallback 진행 |
| Candidate Evidence Agent | `status=error` | retry 가능 시 `evidence=X`, retry 소진 시 `evidence=△` | 1회 제한 재시도 또는 safe fallback |
| Festival Verifier Agent | 검증 축제 1개 이상 `date_status=confirmed` | `festival=O` | `planning` 진행 |
| Festival Verifier Agent | 검증 축제 0개, 부분 실패, 또는 축제 미선택 | `festival=△` 또는 `festival=N/A` | 확정 축제 없이 `planning` 진행 |
| Planner Agent | 출력 구조/결정적 검증 통과 | `planning=O` | Backend Serving으로 전이 |
| Planner Agent | 검증 실패, retry 가능 | `planning=X` | Planner 재호출 |
| Planner Agent | 검증 실패, retry 소진 | `planning=△` | Backend safe fallback 또는 실패 안내 |
