# 로브 (Lovv) Agent V2 명세서 (Draft 집대성)

> 문서 버전: v2-draft.0.1
> 문서 상태: 초안 (Draft · 협의 확정 반영 · 구현 전)
> 위상: 본 문서는 **V2 설계 스냅샷의 집대성**이다. 현 대표 문서 `05_agent_spec.md`는 V1 정본으로 유지하며, 본 draft는 V2 승격 전 단계의 통합 초안이다.
> 정본 위치: `Lovv-agent/docs/reports/v2/` + `Lovv-agent/docs/specs/v2/` — 충돌 시 Lovv-agent repo 우선.
> 상세 정본(보조): `supplemental/v2/architecture_final.md`, `supplemental/v2/scenario_coverage.md`, `supplemental/v2/intent_parsing_spec.md`, `supplemental/v2/verification_plan.md`, `supplemental/v2/decisions_log.md`, `supplemental/v2/memory_checkpointer_spec.md`, `supplemental/v2/cognito_pseudonymization_memory_lifecycle.md`
> 표기: ✅ 확정 · ◐ 부분 확정 · ⚠ 경계 확인 필요(임의 미결정)

---

# 1. 문서 개요

## 1.1 목적

V2는 V1의 **단방향 1-shot 추천**을 **"일정 생성 + 자연어 수정(resume 루프)"**로 확장한다. 본 문서는 그 V2 에이전트의 통합 초안 정본이다. 범위:

- 초회 생성: 자연어·온보딩·지도 진입을 구조화해 소도시 1곳 + 일정을 생성한다.
- 자연어 수정: 생성된 일정을 interrupt/resume로 이어받아 **비-seed 슬롯 교체**(단일·다건)로 고친다.
- 품질 개선: 테마 **soft 게이트**, **capacity 결합 제거**, **seed 앵커 배치**로 멀티테마 소도시 발견력을 높인다.
- 상태·계약: checkpointer(AgentCore Memory) 기반 resume, 가명화 Identity, 출력 스키마 확장을 정의한다.

## 1.2 V1 대비 핵심 변경 (요약)

| 영역 | V1 | V2 |
|---|---|---|
| 흐름 | 단방향 추천(1-shot) | 생성 + **자연어 수정 resume 루프** |
| 라우팅 | `fulfilled_matrix` 매트릭스 전이 | Supervisor **허브 라우터**(매 노드 후 개입) + 초회/resume 분기 |
| 후보 구성 | Candidate_Evidence_Agent(retrieval+ranker 통합) | **city_select subgraph(2-node)** = retrieval_node + scoring_and_selection_node |
| 테마 게이트 | AND(전 테마 보유 도시만) | **soft**(부분 충족 허용, 미충족 강감점) |
| 후보 충분성 | candidate_sufficiency 결합 | **제거**(항상 rank 0, 부족은 Planner Pass2) |
| 후보 풀 | recommended + reserve | **seed-only**(reserve 폐기) + PlacePool ~30–50 |
| 배치 | FIFO, move=null | **seed 라운드로빈 + geo_penalty**, move=front |
| 날씨 대안 | — | **on-demand Plan B**(weatherNotice 후 동의 시 생성) |
| 개인화 | 없음/약함 | **저장 확정 일정 기반** theme_weights |
| 상태 보존 | 무상태 | **checkpointer**(resume/interrupt) + 세션 avoid |

## 1.3 설계 원칙

| 원칙 | 설명 |
|---|---|
| Supervisor 허브 | 매 노드 후 Supervisor가 개입해 초회/resume·수정 의도를 라우팅. raw 보유 안 함. |
| 노드 책임 분리 | Intent=파싱·검증, city_select=검색·스코어·도시선택, Planner=배치·설명, Packager=포장. |
| soft 우선 | 테마는 soft 게이트(완전 0매칭일 때만 no_candidate). 신호(무드·혼잡도·이동수단)는 가중. |
| seed 앵커 | 도시 선택 이유가 된 대표 장소 = day anchor. 수정·배치가 seed를 축으로 돈다. |
| 최소 노출·on-demand | Plan B는 미리 만들지 않고 동의 시 생성. 출력 스키마는 최소 확장. |
| 저장 기반 학습 | profile은 저장 확정 일정에서만 write(변덕 방지). |
| 계측 우선 | 측정 못 하는 것은 검증 못 한다 — 점수 분해 로깅·사유 enum이 선결. |

---

# 2. Agent 목표

| 목표 | 설명 |
|---|---|
| 조건 구조화 | 자연어·UI 조건을 파싱·검증해 검색/배치 신호로 변환(생성/수정 분리) |
| 멀티테마 발견 | soft 게이트로 다테마에서도 소도시 생존(V1 최대 약점 해소) |
| seed 기반 일정 | 도시 선택 이유(seed)를 day anchor로 둔 geo 동선 배치 |
| 자연어 수정 | resume 루프로 비-seed 슬롯 교체(단일·다건), seed·배치수(≤3) 불변 |
| 날씨 대응 | 기상 임계 초과 시 weatherNotice, 동의 시 실내 대안(on-demand) |
| 개인화 | 저장 확정 일정 기반 theme_weights 주입, 모호 입력 fallback |
| 안전·폴백 | 모순→되묻기, 범위 밖→안내, no_candidate/거부→상태값 |

---

# 3. Agent 입력

## 3.1 초회 생성 입력
| 입력 | 출처 | 설명 | 필수 |
|---|---|---|---|
| `session_id` | 시스템 | 세션 식별자(= thread_id) | 필수 |
| `actorId` | Identity | **가명 ID**(Cognito sub의 HMAC) | 필수 |
| `country` | UI | KR 고정(V2 강원·경북) | 필수 |
| `travelMonth` | UI | 1–12 | 필수 |
| `tripType` | UI | daytrip·2d1n·3d2n (4d3n+ 한계 고지) | 필수 |
| `themes` | UI | 5종 enum(sea_coast·nature_mountain·history_tradition·art_sense·healing_rest) | 선택 |
| `destinationId` | 지도 | 지정 도시(anchored) | 선택 |
| `includeFestivals` | UI | 축제 포함 | 필수 |
| `userLocation` | 권한 | 거리 필터·즉흥용 좌표 | 선택 |
| `NL` | 챗봇 | 자연어 요청(soft 신호·긴서사) | 선택 |

## 3.2 수정 입력 (resume)
| 입력 | 설명 |
|---|---|
| `NL`(수정 발화) | "2일차 오후 바다로", 다건("2일차 카페, 3일차 바다"), 전면 불만, 날씨 동의 |
| `thread_id` | 기존 checkpoint 재개 키 |

상세 파싱 기준: `supplemental/v2/intent_parsing_spec.md`.

---

# 4. Agent 출력

| 출력 | 설명 | V2 변경 |
|---|---|---|
| `selectedDestination` | 소도시 1곳 | 유지 |
| `itinerary` | 일별 일정(seed anchor) | move는 **front 담당**(에이전트 미채움) |
| `recommendationReasons` | 추천 이유 | profile 반영 시 "이전 선호 기반" 명시 |
| `alternativeItinerary` | 실내 위주 대안 | **신규(nullable)** · on-demand, 평시 null |
| `weatherNotice` | 기상 임계 안내·사유 | **신규(nullable)** |
| `festivalDateVerifications` | 축제 날짜 검증 | confirmed만 배치 |
| `response_status` | 응답 상태 | `completed`/`END_WAIT_USER` + **`modification_pending`** |
| `confidence` / `user_notice` | 신뢰도·안내 | 유지 |

> 출력 스키마는 front 협의 계약. `move`는 front가 이동시간 제공으로 채움(중복 회피).

---

# 5. 파이프라인

## 5.1 Agent 구성도
![Lovv Agent V2 구성도](../../assets/images/V2_ARCHITECTURE_STRUCTURE_final.png)

> 초회 생성(상단 Main Graph) + 자연어 수정 루프(resume) + Memory(checkpoint·세션 avoid). 상세: `supplemental/v2/architecture_final.md`.

## 5.2 파이프라인 단계
| 단계 | 노드 | 역할 | 출력 |
|---|---|---|---|
| 1 | `Intent` | 파싱·검증·플래그(생성/수정 분리) | IntentResult / ModifyResult |
| 2 | `Supervisor` | 초회/resume 분기, 수정 의도 분해, 응답상태 | 라우팅 결정 |
| 3 | `city_select`(retrieval_node → scoring_and_selection_node) | S3 검색·merge·prune → soft 스코어·도시 확정·**seed 추출** | CitySelectionResult, PlacePool |
| 4 | `Festival Verifier`(optional) | 축제 날짜 검증·테마 정합 | confirmed 축제 |
| 5 | `Planner` | 2-pass 배치 + 수정 모드 + on-demand Plan B | itinerary, alternativeItinerary, reasons |
| 6 | `Response Packager` | 포장 + interrupt → checkpoint | 응답 + 수정 대기 |
| — | `Profile Agent` | read theme_weights / write(저장 시) | 개인화 |
| — | `Memory` | checkpoint/resume·TTL·세션 avoid | 상태 보존 |

---

# 6. UnifiedAgentState (V2 변경)

V1 `UnifiedAgentState`(`supplemental/langgraph_flow.md`) 위에 V2 필드를 더한다. 핵심 변경만 표기.

| 필드 | 변경 | 설명 |
|---|---|---|
| `theme_weights` | 신규 | 테마별 가중(soft 게이트·profile 주입) |
| `seed` | 신규 | 도시 선택 이유 = day anchor 장소 |
| `transport_pref` | 신규 | walk/car/unknown(거친 soft) |
| `congestion_pref` | 신규 | 한적/북적 선호 |
| `edit_ops` | 신규 | 수정 분해 결과 `[{target, op:REPLACE, condition}]` |
| `response_status` | 확장 | + `modification_pending` |
| `alternativeItinerary`/`weatherNotice` | 신규 | nullable, on-demand |
| `session_avoid` | 신규 | 전면 불만 도시/테마(TTL까지) |
| `candidate_sufficiency` | **제거** | capacity 결합 폐기 |
| `reserve_places` | **제거** | seed-only |

데이터 계약: `CitySelectionResult`(candidate_sufficiency 제거·theme_weights·seed), `PlacePool`(seed-only·세부타입·indoor/outdoor 태그), `PlannerInput`(transport_pref), `LovvUserProfile`(`saved_trip_count`·집계 theme_weights). 상태 직렬화 round-trip은 checkpointer 활성화 선행 게이트(`supplemental/v2/memory_checkpointer_spec.md` R4).

---

# 7. 단계별 명세

## 7.1 `Intent`
| 항목 | 내용 |
|---|---|
| 책임 | "원시 입력 → 타입된 파싱·검증 객체"까지. 검색·스코어·배치·fallback 결정은 안 함 |
| 생성 산출 | 구조 필드 정규화, `execution_mode` 도출, NL soft 신호(raw/soft_query·congestion·transport·theme_hint), 긴서사 압축 |
| 수정 산출 | 수정 의도 분류, `edit_ops` 분해(다건), seed 보호, 특수 신호(reset·confirm_plan_b·change_city) |
| 플래그 | 모순→되묻기 · 모호→underspecified · 범위밖→안내 · 이상값/누락→거부 |

`execution_mode`: destinationId → `anchored_place_search` / includeFestivals → `festival_seeded_city_discovery` / else → `city_discovery`.
긴서사: 분리→보수적 매핑(**감정으로 테마 단정 금지**)→정합. 상세 `supplemental/v2/intent_parsing_spec.md`.

## 7.2 `Supervisor`
| 항목 | 내용 |
|---|---|
| 책임 | 초회/resume 분기(thread_id+checkpoint), 수정 의도 분류, 응답상태 결정, 세션 avoid 주입 |
| 수정 분류 | 슬롯 교체(1차) / 도시 변경(경로만, V2.1) / 백로그(길이·날짜·전체무드·맥락→userNotice) |
| 다건 | edit_ops 리스트로 분해 라우팅. 모순 → 되묻기 |

## 7.3 `city_select` subgraph (2-node)
**retrieval_node**: S3 Vector 검색·merge·prune. 수정 시 슬롯 단위 재인출 진입점.
**scoring_and_selection_node**:
| 항목 | 내용 |
|---|---|
| score_city | semantic_evidence + theme_coverage + theme_balance − scale_correction − distance/congestion penalty (**candidate_sufficiency 제거**) |
| 테마 게이트 | **soft**(부분 충족 허용·미충족 강감점). 다테마 → seed에 모든 테마 soft 보장 |
| seed 추출 | 도시 선택 이유 대표 장소 = day anchor. reserve 폐기 |
| transport | walk→거리 페널티↑ / car→완화 |

## 7.4 `Festival Verifier` (optional)
`festival_seeded_city_discovery`일 때 활성. confirmed 축제만 **실제 날짜 분산 배치**(V1은 day-1 고정). 시즌 불일치 → 축제 제외 + userNotice. 테마 정합 필터(축제 테마 태깅 데이터 적재 시).

## 7.5 `Planner` (2-pass + 수정 모드)
| 모드 | 내용 |
|---|---|
| 초회 | Pass1(도시·테마 게이트) → Pass2(도시 고정·테마 off·PlacePool ~30–50) → **seed 라운드로빈 + geo_penalty(haversine)** |
| 후보 부족 | Pass2 재인출(theme off·top_k 확대)로 먼저 채움 → 축소 빈도↓ |
| 수정 | 비-seed 슬롯 교체(슬롯 조건=무드·타입·위치 추가 query), seed 고정·≤3 불변. 다건=일괄 적용→단일 재배치(순차 금지), 부분 실패=부분 적용+안내 |
| Plan B | weatherNotice 동의 시 실내 대안 생성 → alternativeItinerary(on-demand) |
| 동선 | 출력 move=front. 배치=haversine 1차(실이동 API ⚠검토) |

## 7.6 `Response Packager`
출력 스키마 포장(alternativeItinerary·weatherNotice·response_status) → **interrupt 발행 → checkpoint 저장 → resume 대기**. 평시 alt/notice=null.

## 7.7 `Profile Agent`
read: theme_weights 주입(초회). write: **저장 확정 일정에서만** 집계(수정 발화 누적 안 함). fallback "충분"=`saved_trip_count ≥ n`(추천 이유에 "이전 선호 기반"), 부족하면 되묻기. 신규 의존: front "일정 저장" 이벤트.

## 7.8 `Memory` (AgentCore)
checkpoint/interrupt/resume, thread_id + TTL. 세션 avoid = checkpoint 보관, TTL까지 유지(영구 profile 아님). 활성화는 env-gated·기본 off, serde round-trip 게이트 선행. 상세 `supplemental/v2/memory_checkpointer_spec.md`.

---

# 8. 도구 · 인프라

| 도구/인프라 | 책임 | 상세 |
|---|---|---|
| S3 Vector index | 의미 검색(raw/soft query, 슬롯 재인출) | retrieval_node |
| Scoring | score_city/score_place(soft·seed·geo·transport) | scoring_and_selection |
| Weather Trends | 월별 기상 경향(임계 판정) | Planner(weatherNotice) |
| AgentCore Memory Saver | checkpoint+세션(공유 expiry) | `memory_checkpointer_spec.md` |
| Cognito + HMAC 가명화 | actorId 생성·PII 경계·삭제권 | `cognito_pseudonymization_memory_lifecycle.md` |
| Bedrock Converse | LLM 추론(Intent·Planner) | 모델 비종속 |
| Titan/Cohere Embed | 쿼리·장소 임베딩 | ⚠ 임베딩 생성 위치(Intent vs retrieval) |

데이터 적재(4종): 세부타입 · indoor/outdoor · 도시·월 기상 · visitor stats.

---

# 9. Bedrock 및 AgentCore 매핑

| V2 요소 | 매핑 |
|---|---|
| Supervisor·노드 그래프 | AgentCore Runtime |
| checkpoint·세션·세션 avoid | AgentCore Memory(Saver) |
| Scoring·Weather·Link Skill | Gateway / Lambda |
| 축제 웹 검증 | Browser / Web Search |
| actorId 가명·권한 | AgentCore Identity (+ Cognito) |
| 모순·범위밖·국가 분리 | AgentCore Policy |
| 점수 분해·trace·retry | AgentCore Observability(계측) |
| 골든셋·trajectory·judge | AgentCore Evaluations |

LLM 호출은 Bedrock Converse adapter로 추상화(모델 ID 비고정). 영속 가명 프로필·raw 이벤트는 **커스텀 DynamoDB(TTL)→S3 콜드**로 분리(AgentCore Memory 장기 이관 안 함).

---

# 10. 품질 검증 기준

> 전제: **계측 선결**(점수 분해 로깅·seed id·userNotice 사유 enum·LLM 비결정 통제). 상세 `supplemental/v2/verification_plan.md`.

| 검증 항목 | 기준 |
|---|---|
| execution_mode 도출 | 단위 100%(0 허용) |
| soft 게이트 효과 | **AND 기준선 대비 멀티테마 소도시 생존율↑** 입증 |
| seed 결정성 | 동일 입력 → 동일 seed |
| 배치 동선 | 총 haversine < FIFO 기준선 |
| 다건 재배치 | **op 순서 독립**(순열 불변) |
| 모순 감지 | recall ≥ 0.95(false negative=엉뚱 생성) |
| 범위밖 인식 | recall ≥ 0.95 |
| 출력 스키마 | 평시 alt/notice=null, modification_pending 1개 |
| 결정 준수 | D-A 자동생성 0 · D-K 저장 시에만 write · 되묻기 절충 0 |
| 무상태 회귀 | Memory off에서 V1 동작 불변 |

검증 난이도: 결정론(쉬움·0허용) → 분포(중·기준선 대비) → 정성(judge+스팟). E2E는 SC-* 핵심 8~9개 골든 트레이스.

---

# 11. 범위 · 금지 사항

**V2 범위 밖**(인식 후 안내만, 구현 X): 숙소·식당 직접 추천 · 예약·결제 · 실시간 혼잡 · 내비 연동 · 사진·음성 입력 · 다국어 출력 · 저예산/무료. **front 담당**: 조회(이전 일정·통계·축제 달) · 지도 동선 시각화 · 장소 간 이동시간(move). **별도 트랙**: 안전 정책(프롬프트 주입·차별).

**금지**: 미검증 축제 확정 배치 · 출처 없는 장소 확정 · 모순 입력 창의적 절충(→되묻기) · 수정 중 발화의 장기 profile 누적 · raw sub/PII를 Memory·log·DynamoDB·S3 저장 · Plan B 자동 사전 생성.

---

# 12. 결정 요약 · 우선순위 · 미해결

## 12.1 확정 결정 (상세 `supplemental/v2/decisions_log.md`)
D-A on-demand Plan B · D-B 슬롯 교체 1차/도시변경 경로만/나머지 백로그 · D-K 저장 기반 write·fallback n · D-C move=front·haversine 1차 · D-E transport walk/car/unknown · D-J 기온 KMA(33/-12)+강수 일평균·상대(수치 추후) · 4d3n 짧은 일정 먼저 · 응답상태 +modification_pending · 되묻기 모순 무조건 · 기피 세션 avoid · 배치 편집 다건 분해+부분 적용.

## 12.2 우선순위 / 로드맵
| 등급 | 항목 |
|---|---|
| **P0(기반)** | F1 데이터 4종 적재 · F2 출력 스키마 · F3 수정 루프 인프라(resume/interrupt) |
| **P1(코어)** | C1 capacity 제거 · C2 soft 게이트 · C3 seed 배치 · C4 슬롯 교체(단일·다건) · W1 weatherNotice 룰 |
| **P2(부가)** | T1 transport · K1 profile write · W2 Plan B 생성 · A1 세션 avoid · M1 되묻기 · V1 축제 정합 |

**★ V2.0 thin slice** = F1+F2+F3+C1+C2+C3+C4+W1 (품질 개선된 초회 + 슬롯 교체 수정 + 날씨 안내). 나머지 V2.1.

## 12.3 미해결 (구체화 단계)
⚠ 쿼리 임베딩 생성 위치 · ⚠ tripType 결측 기본값 · ⚠ transport 수정 적용 · D-J 임계 수치 · D-C 실이동 API · profile fallback n · 4d3n 확장 시점 · 수정 응답 diff 반환(front) · 축제 테마 태깅 데이터.

## 12.4 변경 이력
| 버전 | 날짜 | 변경 내용 |
|---|---|---|
| v2-draft.0.1 | 2026-06-28 | V2 설계 협의(Step 1~5)·결정 10건·시나리오 커버리지·Intent 파싱·검증 계획·인프라 스펙(checkpointer·Cognito)을 단일 draft로 집대성 |
