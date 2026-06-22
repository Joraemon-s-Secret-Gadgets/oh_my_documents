# 로브 (Lovv) 대화형 일정 빌더 PRD (범위 한정)

> 문서 버전: v0.1
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-22
> 작성자: 조동휘
> 범위 한정: **대화형 일정 빌더(HITL) + 메모리/상태 아키텍처 전환**. 제품 전체 PRD 아님
> 입력 문서: `05_agent_spec/`(에이전트 설계), `04_database_design/`(저장소·보관), `02_service_flow/`,
>   `94_kick/`, `95_aha_moment/`, `98_prd/db_build_prd.md`
> 구현 정본(별도 repo): `Lovv-agent/docs/specs/` —
>   `LOVV_INTERACTIVE_ITINERARY_BUILDER_DESIGN_V1.md`,
>   `LOVV_AGENTCORE_MEMORY_CHECKPOINTER_SPEC.md`,
>   `LOVV_AGENTCORE_OBSERVABILITY_SPEC.md`
> 기반: LangGraph on **AWS Bedrock AgentCore Runtime** (팀 'Bedrock Agents+Lambda' 가이드는 패턴만 차용)

# 1. 개요

## 1.1 목적

본 PRD는 로브 추천 흐름의 **일정 생성 단계**를, Planner가 후보를 임의 배치하는 **자동 생성**에서
사용자가 장소를 하나씩 고르며 쌓는 **대화형 HITL 빌더**로 전환하기 위한 제품 요구사항을 정의한다.
함께, 이를 지탱하는 **메모리/상태 아키텍처**(단기 AgentCore Memory / 장기 DynamoDB TTL→S3)를 확정한다.
제품 전체 PRD가 아니며, 소도시 선정 이후의 일정 구성·상태·관측 범위에 한정한다.

## 1.2 배경

기존 구조는 Planner가 도시 근거 관광지 후보를 임의 배치해 전체 일정을 자동 생성한다. 문제는
"사용자가 그 임의 동선을 그대로 받아들이는가"이다. 소도시 선정(Intent → Candidate Evidence)까지는
유지하되, 일정 구성은 **가장 적합한 장소 1곳을 시작으로 반경 N km 내 후보를 제시하고 사용자가 고르는
대로 쌓는 루프**로 바꾼다(강사 피드백). 이 구조는 부수적으로 "일정 최소 개수 미충족" 문제도 근본
해결한다(DB 부족 시 지도 API로 즉시 보충).

## 1.3 범위 / 제외

| 구분 | 내용 |
| --- | --- |
| 포함 | 대화형 빌더 루프(HITL), Candidate Evidence 3층 분해, 2티어 후보·sufficiency, Intent/Profile 분리·Lock, Planner Geo-Filter, 메모리(단기/장기) 및 TTL 라인, 관측·CI/CD 요구 |
| 제외 | 소도시 선정 알고리즘 자체 변경, 데이터 수집/ELT(→ `data_pipeline_prd.md`), 결제·예약, 공개 일정 복제 UX 상세(→ `94_kick`) |

# 2. 핵심 결정 요약 (TL;DR)

| # | 결정 | 비고 |
| --- | --- | --- |
| 1 | 일정 구성 = **사용자 주도 HITL 반경 루프** | 동선 = 선택 순서 (임의 배치 폐기) |
| 2 | Candidate Evidence **3층 분해** | 공유 코어 + 도시선정(1회) + 반경 Provider(루프) |
| 3 | 코어 **게이트 추상화** `city ｜ radius` | 후보 좌표·거리 페널티 기존 보유 → 가능 |
| 4 | 후보 **2티어** | DB 큐레이션(통찰○) + 지도 API(식당·카페·gap, 통찰✕) |
| 5 | 최소 개수 = **표시 선택지 soft floor** | 폴백 사다리(반경확장→API→솔직안내), 하드 실패 없음 |
| 6 | **Intent/Profile 분리 + Profile Lock** | 루프 중 Profile 잠금, 근본 변경 시만 재트리거 |
| 7 | Planner = **Geo-Filter (pure code, Haversine)** | LLM 미사용, 구간 동선만 |
| 8 | 단기 = **AgentCore Memory** | checkpoint + 세션, event_expiry 자동정리 |
| 9 | 장기 = **커스텀 DynamoDB TTL → S3 콜드** | 보관기간·삭제권 직접 통제 (ADR 원안) |
| 10 | **매핑·PII 분리** | 어느 저장소에도 미노출, KMS·IAM, actorId=가명 |
| 11 | Supervisor = **결정론 코드(유지)** · 스텝 **병렬 fan-out** | 토큰·지연 최적화 |
| 12 | Output Agent 분리 / sLLM 릴레이 / 다중 반경 교집합 | **보류·옵션** |

# 3. 기능 요구사항 (FR)

## FR-1. 대화형 빌더 루프 (HITL)

매 턴 반복: **Anchor → 반경 Provider → 후보 제시(interrupt) → 사용자 픽 → next anchor**. "DONE"이면
종료 → 출력. interrupt/resume은 활성 checkpointer(§4)를 전제로 한다.

- FR-1.1 최고 점수 장소를 시작 anchor로 잡는다(도시 선정 결과 재사용).
- FR-1.2 후보 제시 시점에 `interrupt()`로 멈추고 사용자 선택을 동일 thread로 resume한다.
- FR-1.3 픽한 장소를 일정에 추가하고 그 장소를 next anchor로 갱신한다.
- FR-1.4 후보 선택은 메인 타임라인과 **격리된 서브 윈도우(사이드바)** 로 표시한다(컨텍스트 오염 방지).

## FR-2. Candidate Evidence 3층 분해

- FR-2.1 **공유 검색·스코어 코어(stateless)**: 입력 `(query_vector, 게이트, 필터)` → 점수순 후보.
  게이트 `city ｜ radius` 추상화. scoring 가중치 context별(도시=테마 커버리지, 반경=거리 중심).
- FR-2.2 **도시 선정 오케스트레이터(1회)**: 코어를 city 게이트로 돌려 소도시 확정.
- FR-2.3 **반경 Provider(루프)**: 코어를 radius 게이트 + 스텝 필터로 anchor 주변 후보 제시.
- FR-2.4 산출물은 **루프 시드** `{도시, query_vector, anchor, budget}` — 체크포인트 초기값.
  query_vector는 캐시·재사용(매 턴 재임베딩 금지).

## FR-3. 후보 2티어 + sufficiency

- FR-3.1 관광지는 **DB 큐레이션**(벡터+scoring, 통찰형 이유), 식당·카페는 **지도 API**로 반경 표시.
- FR-3.2 두 티어를 **사용자에게 명시 구분**한다. API 보충 장소엔 통찰 이유를 억지 생성하지 않는다.
- FR-3.3 후보 제시·축제 추출을 **병렬 fan-out**으로 동시 구동한다.
- FR-3.4 최소 개수는 **표시 선택지 soft floor**로만 둔다(큐레이션은 1곳까지 허용).
- FR-3.5 floor 미달 시 **폴백 사다리**: ① 반경 확장(N→2N) ② API 보충 ③ 솔직한 안내.
  **하드 실패로 되돌리지 않는다.**

## FR-4. Intent / Profile 분리 + Profile Lock

- FR-4.1 **Intent Agent**(매 턴)는 발화를 **action 어휘**로 파싱: `PICK`, `REPLACE_PLACE`,
  `EXCLUDE`, `FILTER`(=follow-up 간판 5종), `DONE`.
- FR-4.2 **Profile Agent**는 가명 영속 프로필(§4)에서 장기 성향을 읽어 **초기 시드에만** 기여한다.
- FR-4.3 루프 중 Profile은 **Lock**(재실행 안 함). **재트리거 조건**: 동행자·테마 등 근본 변경 시.
- FR-4.4 분기는 **결정론 코드 Supervisor**(LLM 아님, 기존 구현 유지)가 action 기준으로 수행한다.

## FR-5. Planner = Geo-Filter

- FR-5.1 Planner는 LLM이 아니라 **pure-code geo**(Haversine/Shapely)로 반경/거리만 검증한다.
- FR-5.2 방문 순서를 임의 결정하지 않는다 — **동선 = 사용자 선택 순서**.
- FR-5.3 구간 이동시간은 직전 장소→새 장소만 교통 API로 계산하고, 값 없으면 표시 생략(0분 금지).
- FR-5.4 (옵션) 다거점(숙소 2곳 등) **다중 반경 교집합** 필터는 확장 항목으로 둔다.

# 4. 메모리 · 상태 설계 (단기 AgentCore / 장기 커스텀 TTL→S3)

원칙: **ephemeral은 통합(AgentCore Memory), persistent는 분리(커스텀)**. AgentCore 장기 메모리는
무한 보존·수동 삭제라 보관기간 통제가 거칠어, 장기 컴플라이언스 데이터는 커스텀 TTL 라인으로 통제한다.

## 4.1 계층

- **단기 (AgentCore Memory)**: `itinerary_builder = { anchor, items[ ], next_anchor, radius_km,
  active_filters, budget }` + 세션 컨텍스트 + checkpoint(interrupt↔resume). `event_expiry` 자동 정리.
- **장기 ① 파생 개인화 프로필 (DynamoDB 핫, TTL 없음)**: 가명 ID PK, 자주 읽는 선호 요약.
  Profile Agent 읽기 소스. 지우지 않음.
- **장기 ② raw 이벤트 로그 (DynamoDB TTL → S3 콜드)**: §4.2.

## 4.2 TTL 라인 (raw 이벤트 → S3 콜드)

1. DynamoDB 이벤트 아이템 `ttl`(epoch 초) = `now + N일`. TTL은 **best-effort**(SLA 없음) →
   "N일 후 반드시"가 요건이면 `expires_at` 필드 + **읽기 시 앱레벨 필터**로 보강.
2. **DynamoDB Streams**(NEW_AND_OLD_IMAGES) 활성화.
3. **Lambda**가 TTL 삭제만 필터: `eventName=="REMOVE"` AND
   `userIdentity.principalId=="dynamodb.amazonaws.com"`.
4. OLD_IMAGE(가명)를 **S3 콜드**에 적재(날짜/actor-해시 파티션).
5. 용도: 프로필 재계산·분석·학습, 복귀 사용자 재하이드레이션.
6. 고볼륨 시 `DynamoDB → Kinesis → Firehose → S3`로 확장(부트캠프 규모엔 Streams+Lambda).

## 4.3 가명화·컴플라이언스 (hard line)

- 매핑 테이블(가명ID↔실제신원)·raw PII는 **어느 저장소에도 넣지 않는다**(별도 KMS·최소권한 IAM).
- 전 계층 **actorId = 가명 ID** 격리. LangGraph `thread_id`→AgentCore `session_id`, `actor_id`→가명.
- **삭제권(right-to-erasure)**: DynamoDB + S3 양쪽 삭제 플로우를 명시 구현한다.
- 개인화 법적 근거는 **동의**, 가명처리는 **안전조치**(특례 트랙 미사용).

# 5. 비기능 요구사항 (NFR)

- **NFR-1 관측성**: OTel + AWS X-Ray + CloudWatch Structured JSON Logs. 노드별 레이턴시·토큰·
  컨텍스트 윈도우·I/O 트레이싱. 빌더 전용 메트릭(루프 길이, 반경 검색 지연, 체크포인트 rw 지연,
  폴백 사다리 카운트, 2티어 비율, 정합성 게이트 실패, Profile 잠금/재트리거). 메트릭에 PII·가명 외
  미포함. (정본: `Lovv-agent/docs/specs/LOVV_AGENTCORE_OBSERVABILITY_SPEC.md`)
- **NFR-2 토큰/비용**: 결정론 Supervisor·Profile Lock·서브 윈도우 격리·sLLM 활용으로 절감.
  *(가이드의 "턴당 70% 절감"은 추정치 — 우리 환경 실측 필요, 신뢰도 낮음.)*
- **NFR-3 지연**: 스텝별 병렬 fan-out으로 단축. *("2.5초" 추정치 — 실측 필요.)*
- **NFR-4 안정성**: 의도·성향·일정의 책임 분리(decoupling)로 프롬프트 복잡도·할루시네이션 저감.
- **NFR-5 정합성 게이트**: 장소명·날짜·좌표가 State와 일치하는지 **코드로 1차 검수**, 불일치 시에만
  LLM 개입(환각 금지·근거 의무).

# 6. 보류 · 옵션

| 항목 | 상태 | 사유 |
| --- | --- | --- |
| Output(Presenter) Agent 분리 | 보류 | 현 ResponsePackager 유지. 후속 재검토 |
| sLLM 생성 + 대형 LLM 릴레이 검수 | 보류 | 지연·복잡도. 우선 코드 정합성 게이트로 대체 |
| 다중 반경 교집합(다거점) | 옵션 확장 | 코어는 단일 anchor 순차 루프 |

# 7. 기반 · 전제

- 오케스트레이션 기반은 **LangGraph on AgentCore Runtime**을 유지한다. 팀 가이드의 "Bedrock
  Agents + Lambda"는 **패턴만 차용**(결정론 라우터·병렬·상태 격리·Profile Lock).
- 가이드의 단일 DynamoDB State는 우리 **단기 AgentCore / 장기 커스텀** 분리로 흡수한다.
- checkpointer는 `compile(checkpointer=...)` 1지점에서 켜며, 무상태 기본 동작을 깨지 않는다(opt-in).

# 8. 수용 기준 (Acceptance)

1. 사용자가 후보를 순차 선택해 일정을 구성하고, 동일 thread로 중단·재개된다(HITL interrupt/resume).
2. 동일 코어가 city·radius 게이트로 도시선정·반경 스텝 양쪽에서 재사용된다.
3. 반경 후보가 부족해도 폴백 사다리로 채워지며 **하드 실패하지 않는다**(큐레이션 1곳 케이스 포함).
4. 단기는 AgentCore Memory, 장기 raw 이벤트는 DynamoDB TTL→S3로 적재되고 TTL 삭제만 아카이브된다.
5. 매핑·PII가 어떤 저장소·메트릭에도 노출되지 않고 actorId=가명으로 격리된다.
6. 노드별 토큰·레이턴시·I/O가 CloudWatch에서 조회된다.
7. 동선이 **선택 순서**로 구성되고 임의 배치가 발생하지 않는다.

# 9. 미해결 / 확인 필요

- [ ] 반경 N km 기본값, soft floor(표시 최소 개수) 수치.
- [ ] 교통 API 선택(Kakao/Google/현지), 구간 이동시간 소스.
- [ ] Profile Lock 재트리거 "근본 변경" 정의.
- [ ] TTL N일 값, `expires_at` 앱레벨 필터 적용 범위.
- [ ] AgentCore Memory(`AgentCoreMemorySaver`) 생성자 시그니처·버전 pin (preview/alpha).
- [ ] state serde 복원기(`unified_state_from_dict`) 중첩 schemas round-trip.
- [ ] 토큰·지연 절감 실측(가이드 추정치 검증).
- [ ] (보류) Output Agent·sLLM 릴레이 재검토 트리거 / (옵션) 다중 반경 교집합 설계.

# 10. 관련 문서

- 에이전트 설계: `../05_agent_spec/05_agent_spec.md`, `candidate_evidence_agent.md`,
  `candidate_evidence_runtime_retrieval.md`(restaurant 제외 §9 갱신 필요), `planner_agent.md`,
  `intent_agent.md`
- 저장소·보관: `../04_database_design/04_database_design.md`,
  `database_design_retention_neptune_update.md`
- 서비스 흐름·UX: `../02_service_flow/`, `../94_kick/`, `../95_aha_moment/`
- 구현 정본(별도 repo): `Lovv-agent/docs/specs/LOVV_INTERACTIVE_ITINERARY_BUILDER_DESIGN_V1.md`,
  `LOVV_AGENTCORE_MEMORY_CHECKPOINTER_SPEC.md`, `LOVV_AGENTCORE_OBSERVABILITY_SPEC.md`

# 11. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-22 | 조동휘 | 대화형 빌더 + 메모리(단기 AgentCore/장기 DynamoDB TTL→S3) 결정사항 PRD 초안 작성 |
