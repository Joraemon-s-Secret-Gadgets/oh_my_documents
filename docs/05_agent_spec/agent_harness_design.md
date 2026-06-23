# 로브 (Lovv) Agent 하네스 설계

> 문서 버전: v1.5
> 문서 상태: 검토 중 (Review)
> 기준 문서: `langgraph_flow.md`(그래프 정본), `agent_spec_revision_plan.md`(설계 결정), `../01_requirements/lovv_agent_multiturn_context_spec.md`(멀티턴 정책)
>
> **[PRD 반영 v0.1 — 대화형 빌더]** 하네스에 **checkpointer 주입 지점**(`compile(checkpointer=AgentCore Memory)`)과 **노드 계측 래퍼**(OTel span + CloudWatch JSON, `trace_node`)를 추가한다. 무상태 기본 동작은 opt-in으로 보존. 상세: `../98_prd/interactive_builder_prd.md`, 관측 정본: `Lovv-agent/docs/specs/LOVV_AGENTCORE_OBSERVABILITY_SPEC.md`.

# 1. 문서 개요

본 문서는 Lovv 에이전트의 두 가지 하네스를 설계한다.

1. **실행/런타임 하네스** — LangGraph 그래프를 조립하고 `UnifiedAgentState`를 관리하며 AWS Bedrock AgentCore에 연결해 에이전트를 실제 구동하는 스캐폴드.
2. **테스트 하네스** — 멀티턴 시나리오의 정상/폴백/실패 케이스, 입력→기대출력, `fulfilled_matrix` 전이를 검증하는 품질 검증 체계.

두 하네스는 동일한 그래프 정의와 상태 스키마를 공유한다. 실행 하네스가 "프로덕션 구동", 테스트 하네스가 "동일 그래프에 대한 검증"이다.

# 2. 실행 / 런타임 하네스

## 2.1 목적과 책임 경계

실행 하네스는 비즈니스 로직(노드 내부 추론)을 포함하지 않는다. **그래프 배선, 상태 영속화, 외부 연결, 루프·재시도 제어, 관측성**만 담당한다.

**구현 환경**: 언어 **Python 3.12**, 프레임워크 LangGraph(Python)로 그래프를 구성해 AgentCore Runtime에 배포한다. 리전은 **us-east-1**, 모델 호출은 Bedrock Converse API. `UnifiedAgentState` 등 타입 힌트는 Python 3.12 기준으로 작성한다.

## 2.2 구성요소

| 구성요소 | 책임 | AgentCore 매핑 |
| --- | --- | --- |
| Graph Builder | 노드 등록, 조건 엣지 배선, entry/finish 지정 | Runtime |
| State Manager | `UnifiedAgentState` 생성·검증·턴 간 persist | Memory |
| Memory Adapter | `messages`/`conversation_summary`/`fulfilled_matrix`/검증 캐시 read·write | Memory |
| Skill/Tool Gateway Adapter | 결정적 Skill(Lambda) 호출 래퍼, 입출력 스키마 검증 | Gateway |
| Browser Adapter | Festival_Verifier 웹 검색 호출 | Browser |
| Loop Controller | 매트릭스 순환·순차 구간 전이·재시도 카운터 가드 | Runtime |
| Identity Binder | 에이전트별 ID·권한, Memory/도구 접근 범위 | Identity |
| Policy Guard | 금지사항(국가 혼합, 미검증 축제 등) 런타임 강제 | Policy |
| Observability Hook | 노드별 trace(redacted), 지연·토큰 메트릭 | Observability |

### 2.2.1 AgentCore 책임 이관 기준

도메인 그래프와 AgentCore 하네스는 책임을 분리한다. Agent 노드, 라우팅 규칙,
프롬프트, 도메인 상태 전이는 Lovv 추천 workflow의 source of truth로 남기고,
반복 실행·운영·보안·입출력 정규화에 가까운 책임은 AgentCore 하네스로 이관한다.

| 항목 | AgentCore 하네스 책임 | 도메인 workflow에 남길 책임 |
| --- | --- | --- |
| 요청 정규화 | `payload.request`, JSON string `prompt`, plain text `prompt`를 Lovv request로 변환 | 정규화된 request를 `UnifiedAgentState`로 변환 |
| Graph lifecycle | 프로세스당 graph compile/cache, 요청당 initial state 생성 | node, edge, routing business rule |
| Model adapter | Bedrock Converse client, model id/tier runtime config, region, credential provider 처리 | prompt, schema, fallback behavior |
| Identity/permission | AgentCore Identity, tool 접근 권한, credential boundary | agent별 필요한 tool 이름과 최소 scope 선언 |
| Runtime guard | timeout, live/fallback flag, request id 주입, exception 구조화 | `status=no_candidate/insufficient/error` 같은 도메인 상태 |
| Redacted logging | `agent_run_id`, `session_id`, node trace, latency, token metric 기록 | 원문 대화, raw RAG/web payload를 log에 넘기지 않음 |
| Entrypoint contract test | AgentCore payload shape, local/dev/invoke 입출력 검증 | agent node 단위 regression test |

초기 구현에서는 Memory, Gateway, Policy를 한 번에 모두 관리형 구성요소로 옮기지
않는다. 먼저 in-process state와 fixture 기반 regression을 AgentCore Runtime에서
동일하게 실행하고, 이후 Memory adapter와 Gateway adapter를 얇게 추가한다.
본 하네스 정본은 특정 모델 ID나 Agent별 모델 tier 배정을 고정하지 않는다.
모델 선택은 배포 환경 설정과 Evaluations 결과를 기준으로 별도 결정한다.

## 2.3 초기화 시퀀스

1. `UnifiedAgentState` 초기화 (`turn_index=0`, `fulfilled_matrix` 미설정, `target_region=None`, `validation_retry_count=0`).
2. Memory에서 세션 컨텍스트(온보딩, 피드백, 직전 턴 상태) 로드.
3. Graph Builder가 노드/엣지 등록 후 컴파일.
4. Identity 바인딩 및 Policy 로드.
5. entry(`Intent_Agent`)부터 실행.

## 2.4 그래프 배선 규칙

- entry = `Intent_Agent`, finish = `Backend_Serving`.
- 조건 엣지: `NEED_MORE`, `target_region == None?`, `결정적 검증 통과?`, `의미 검증 통과?`, `retry_count < 2?` (정의는 `langgraph_flow.md` 6장).
- Supervisor는 `Matrix Transition Skill` 결과로 `next_node`를 설정하며, 자체 LLM 추론으로 raw를 해석하지 않는다.

## 2.5 상태 영속화 (멀티턴)

- 매 턴 종료 시 `messages`, `conversation_summary`, `fulfilled_matrix`, `target_region`, `selected_destination`을 Memory에 저장.
- 다음 턴 진입 시 동일 키로 복원 → `Intent_Agent`가 누적 맥락으로 재증류.
- `messages` 임계 초과 시 롤링 요약 압축(7.5 정책)을 State Manager가 트리거.

### 2.5.1 Memory 저장 경계

Memory는 다음 turn의 의도 해석과 재추천에 필요한 요약 상태만 저장한다. 원본
대화·검색 결과·웹 문서는 장기 보관하지 않고, 필요한 경우 redacted summary와
식별자 중심으로 축약한다.

| 항목 | Memory 역할 | 저장 정책 |
| --- | --- | --- |
| `messages` recent window | 다음 턴 Intent 입력용 단기 context | 원문 장기 저장 금지, 세션 TTL 적용 |
| `conversation_summary` | 긴 대화 압축 summary | redacted summary만 유지 |
| `fulfilled_matrix` | 턴 간 routing 상태 | `X/O/△/N/A` 값만 저장 |
| `execution_mode`, `fixed_city_id`, `city_anchor` | `anchored_place_search` 모드의 도시 고정 상태와 `festival_seeded_city_discovery` 실행 이력 | raw 축제/장소 payload 대신 id와 reason code 중심 |
| `selected_destination` | 다음 턴 재추천·수정 기준 | city id/name 수준으로 축약 |
| `unsupported_conditions`, `user_notice` 후보 | Planner 안내 문구와 후속 질문에 재사용 | 민감한 원문 표현은 요약 |
| `validation_retry_count` | loop guard 유지 | 요청 단위 또는 턴 단위 초기화 기준 명시 |
| `festival_verifications` summary | 같은 턴·세션 내 축제 검증 재사용 | 장기 캐시는 DynamoDB `lovv_festival_verify_cache`가 물리 소유 |
| `PlanDraft` summary | 저장 전 임시 일정 상태 | TTL 필요, 사용자가 저장하면 MySQL 저장 API로 원장화 |

Memory에 저장하지 않는 항목:

- raw RAG result 전문
- raw web search/page content
- `candidate_evidence_package` 전체 원문
- embeddings cache
- API key, credential, user PII 원문

`candidate_evidence_package`는 단일 실행 내부 payload로 유지한다. 멀티턴 수정이나
재추천을 위해 필요하면 전체 패키지 대신 `selected_city`,
`recommended_place_ids`, `reserve_place_ids`, `fallback_audit` 요약만 Memory에 둔다.

## 2.6 에러·재시도·폴백

| 상황 | 처리 |
| --- | --- |
| Skill/Tool 호출 실패 | 1회 재시도 후 해당 매트릭스 항목 `△`(폴백) 표시 |
| Web Search 실패 | 축제 `date_status=unknown`, 일정 직접 배치 금지 |
| 검증 실패 | `validation_retry_count++`, 상한 2 도달 시 폴백 응답 확정 |
| 데이터 결측 | `confidence` 하향 + 결측 안내 메시지 포함 |

## 2.7 관측성

- LangSmith: redacted 메타데이터만(노드명, matrix 상태, next_node, dropped_context_categories, latency). 원문/PII 금지(멀티턴 명세 §10).
- DynamoDB `lovv_agent_runs`: DB 설계 명세서 v0.5 기준으로 `node_name`, `tool_name`, `validation_retry_count`, `error_code`, `payload_summary` 수준의 실행 요약만 저장한다.
- AgentCore Observability(CloudWatch): 노드 지연, 토큰 사용, 재시도 횟수, 폴백 비율, 라우팅 경로, matrix 전이 대시보드.

### 2.7.1 Gateway / Policy / Observability 분리

결정적 계산과 외부 접근은 Agent 노드 안에 직접 섞지 않고, Gateway 또는 Lambda
adapter로 분리한다. 정책 위반과 운영 지표는 별도 구성요소에서 관측·차단한다.

| 항목 | 권장 AgentCore 구성요소 |
| --- | --- |
| Scoring, Matrix Transition, Validation, Link Builder, Weather Trends | Gateway 또는 Lambda |
| Festival official page 탐색 | Browser 또는 Web Search |
| 국가 혼합 금지, 미검증 축제 배치 금지, 원문 trace 금지 | Policy + Validation Skill |
| node latency, retry, fallback, token usage | Observability |
| trajectory, 조건 충족, 근거성 평가 | Evaluations |

# 3. 테스트 하네스

## 3.1 테스트 레이어

| 레이어 | 대상 | 검증 내용 |
| --- | --- | --- |
| L1 노드 단위 | 개별 Sub-Agent | 입력→출력 스키마, 필수 필드 생성 |
| L2 Skill 계약 | 결정적 Skill | 입력→출력 결정성, 경계값 |
| L3 그래프 통합 | 전체 그래프 | 라우팅 경로, 매트릭스 수렴, 종료 조건 |
| L4 멀티턴 시나리오 | 턴 시퀀스 | 턴 간 상태 유지, 컨텍스트 정리, 재활성 |
| L5 품질 평가(Eval) | 추천 결과 | 근거성·환각·조건 충족(수용 기준) |

## 3.2 시나리오 매트릭스 (정상 / 폴백 / 실패)

| ID | 분류 | 입력 시나리오 | 기대 결과 | 핵심 assertion |
| --- | --- | --- | --- | --- |
| TC-N01 | 정상 | 챗봇 "10월 한국 1박2일 단풍" | 소도시 1곳 + 일정 + 이유 | matrix 전부 `O`, 단일 목적지, 이유 2개+ |
| TC-N02 | 정상 | 지도 마커 진입(`destinationId`) | 앵커 생략, 해당 지역 일정 | `target_region` 즉시 고정, 모드2 진입 |
| TC-N03 | 정상 | 축제 포함 + `confirmed` 축제 | 일정에 축제 배치 | 배치 축제는 `date_status=confirmed` |
| TC-F01 | 폴백 | Web Search 실패 | 축제 안내만, 직접 배치 안 함 | `date_status=unknown`, 일정 미배치 |
| TC-F02 | 폴백 | 기상 악화(장마) 지역 | 실내 중심 대체 일정 | `alternativeItinerary` 존재, matrix `△` |
| TC-F03 | 폴백 | 후보 데이터 결측 | 결측 안내 + confidence 하향 | `confidence` 하향, 안내 메시지 포함 |
| TC-F04 | 폴백 | 필수 테마 충족 후보 0건 | 조건 완화 안내 또는 검색 링크 폴백 | `no_candidate`, `retry_count` 미증가 |
| TC-E01 | 실패 | 의미 검증 2회 실패 | 폴백 응답 확정 종료 | `retry_count`=2에서 폴백, 무한루프 없음 |
| TC-E02 | 실패 | 국가 혼합 시도(KR+JP) | 차단/재요청 | 단일 국가만 결과, Policy 위반 차단 |
| TC-E03 | 실패 | 필수 조건 누락 | 추가 질문 생성 | NEED_MORE 아니오 경로 |
| TC-E04 | 실패 | Validator `grounding_missing` | 동일 선정지 기준 생성 재호출 | Retriever 미호출, `Itinerary_Writer_Agent` 재호출 |
| TC-E05 | 실패 | Validator `hallucination` | 재탐색 또는 항목 제거 | raw 생성물 확정 노출 금지 |
| TC-R01 | 추천 로직 | 자연어+온보딩 테마가 3개 초과 | 자연어 우선, 잔여 온보딩은 backup 처리 | `active_required_themes` 최대 3개, `backup_themes` 존재 |
| TC-R02 | 추천 로직 | 사용자가 숙소 가격/전망을 요구 | RAG 조건 제외, 안내 문구 제공 | `unsupported_conditions`, `user_notice` 존재 |
| TC-R03 | 추천 로직 | `user_location`이 있는 당일치기 요청 | 거리 기반 후보 필터 적용 | 후보 도시가 `tripType` 반경 내 |
| TC-R04 | 추천 로직 | 희소 테마 포함 요청 | 희소 테마 완화 기준과 가중 적용 | 희소 테마 1개+ 충족, 가중치 반영 |
| TC-R05 | 추천 로직 | 축제 포함 후보 다수 | 구조화 1차 Top-K만 축제 검증 | Web Search 호출 후보 수 `<= K` |

## 3.3 멀티턴 시퀀스 케이스 (L4)

각 케이스는 `[턴 입력] → [기대 matrix/상태] → [기대 응답]` 시퀀스로 기술한다.

| ID | 패턴 | 턴 시퀀스 | 검증 포인트 |
| --- | --- | --- | --- |
| MT-01 | 명료화 | T1 "조용한 곳 추천" → (추가 질문) → T2 "11월 일본 당일치기" | T2에서 조건 충족, T1 맥락 누적 반영 |
| MT-02 | 수정/재추천 | T1 추천 완료 → T2 "여기 말고 다른 곳" | 해당 항목 `X` 재설정, 재라우팅, 이전 선정지 제외 |
| MT-03 | 선호 추가 | T1 추천 → T2 "바다도 보고 싶어" | `user_preferences` 추가, 관련 테마 `X` |
| MT-04 | 선호 번복 | T1 "축제 빼줘"(festival `N/A`) → T3 "역시 축제 넣어줘" | **N/A→X 재활성**, `excluded_themes`에서 제거 |
| MT-05 | 불확실 번복 | T2 "축제도... 글쎄" | 전이 안 함 + 추가 질문(불확실성 처리) |
| MT-06 | 장기 대화 | 12턴 초과 | 롤링 요약 발동, Intent 입력 bound, 라우팅 비용 평탄 |
| MT-07 | 컨텍스트 정리 | 잡담/감탄 포함 발화 | Supervisor payload에서 잡담 제거(§7 규칙) |

## 3.4 fulfilled_matrix 전이 검증

표준 키는 `retrieval`, `festival`, `ranking`, `generation`, `validation`으로 고정한다.
라우팅 우선순위는 `retrieval → ranking → festival → generation → validation`이다.
각 케이스에서 매트릭스 스냅샷을 단계별로 단언한다. 예시(TC-N01):

```text
초기:      {retrieval:X, festival:X, ranking:X, generation:X, validation:X}
Retriever 후: {retrieval:O, ranking:X, festival:X, ...}
Ranker 1차 후: {ranking:X, festival:X, top_k_candidates:[...]}
Festival 후:  {festival:O, ranking:X, ...}
Ranker 최종 후:{ranking:O, ...}
순차 완료:    전부 O → Backend_Serving 전이
```

전이 불변식: `X`만 라우팅 / Worker 완료 시 `O|△` / `N/A`는 스케줄링 제외 / 재시도 시 해당 항목만 `X` 복귀.
`includeFestivals=false` 케이스는 `festival=N/A`를 기대값으로 둔다.
`no_candidate` 케이스는 `validation_retry_count` 증가 없이 `ranking=△`와 폴백 종료를 기대값으로 둔다.

## 3.5 Mock / Fixture

| 외부 의존 | Mock 전략 |
| --- | --- |
| RAG / Destination Search | 고정 후보 세트 픽스처(국가별 KR/JP) |
| Festival Catalog / Web Search | `confirmed`/`tentative`/`unknown`/실패 4종 응답 픽스처 |
| Weather Trends | 정상/장마/태풍 경향 픽스처 |
| Scoring Skill | 결정적 입력→출력 골든 값 |
| LLM 노드 | 시드 고정 또는 응답 스텁(스키마 검증 위주) |

## 3.6 품질 평가 메트릭 (L5)

| 메트릭 | 정의 | 기준 |
| --- | --- | --- |
| 조건 충족률 | 국가·월·일정 유형 반영 | 100% |
| 근거성 | 추천 이유가 DB 근거와 연결 | 환각 0건 |
| 축제 날짜 정확성 | 배치 축제 `confirmed` 비율 | 100% |
| 단일 목적지 | 소도시 1곳 중심 | 100% |
| 폴백 안전성 | 결측/실패 시 안내 적용 | 100% |
| 루프 안전성 | 재시도 상한 준수 | 무한루프 0건 |

## 3.7 CI 연계

- L1·L2·L4는 PR 게이트(빠른 결정적 테스트).
- L3·L5는 nightly 또는 릴리즈 게이트(LLM 호출 비용 고려).
- 수용 기준(멀티턴 명세 §13) 체크리스트를 릴리즈 전 자동 점검.
- 구체적 게이트·평가자·임계값은 4장(AgentCore Evaluations) 참조.

# 4. AgentCore Evaluations 기반 CI/CD 및 정량 평가

> 본 장은 AWS re:Invent 2025 발표 후 2026-03 GA된 **Amazon Bedrock AgentCore Evaluations**를 기준으로 한다. *(사실 신뢰도: 높음 — AWS 공식 문서·블로그 근거. 단, 13종 평가자 구성과 임계값은 모델/리전에 따라 변동 가능하므로 구현 시 재확인 필요)*

## 4.1 AgentCore Evaluations 개요

AgentCore Evaluations는 에이전트 trace를 평가자(evaluator)로 채점하는 관리형 기능이며, 두 가지 모드를 제공한다.

| 모드 | 용도 | 본 프로젝트 적용 |
| --- | --- | --- |
| On-demand Evaluation | 개발·CI/CD용 실시간 평가 API. ground truth 대비 회귀 테스트, 배포 게이트 | PR/릴리즈 파이프라인 게이트 |
| Online Evaluation | 프로덕션 trace를 일정 비율 샘플링해 지속 채점 | 운영 중 품질 모니터링 |

평가자 종류:

- **내장 평가자 13종** — session/trace/tool 3개 레벨. 예: Correctness(사실 정확성), Faithfulness(근거 충실성), Helpfulness, Harmfulness, Stereotyping, Tool selection accuracy. LLM-as-Judge 방식.
- **커스텀 평가자** — ① LLM-as-Judge 커스텀(도메인 프롬프트), ② **코드 기반(code-based) 평가자**(결정적 규칙). session/trace/span 레벨에서 동작.
- **Ground truth** — assertions / expected response / **expected trajectory**를 session·trace·tool 레벨로 제공. 입력 데이터셋은 trajectory(질문 1개 이상) 형태이며, **버전 관리되는 데이터셋 ID**로 dev·CI/CD·스케줄 회귀에서 동일하게 참조한다.

핵심 이점: **CI/CD에서 쓰는 평가자와 프로덕션 Online 모니터링 평가자가 동일**하므로 개발↔운영 품질 기준이 일관된다.

## 4.2 CI/CD 파이프라인 설계

```text
PR 생성
  → 빌드/단위(L1·L2)
  → On-demand Evaluation 호출 (버전 고정된 ground truth 데이터셋)
       ├─ 결정적 코드 평가자: 조건충족/단일목적지/축제confirmed/국가분리/루프상한
       ├─ 내장 LLM 평가자: Correctness / Faithfulness / Helpfulness / Harmfulness
       └─ Trajectory 평가자: matrix 전이 경로 · 도구 호출 순서
  → 임계 미달 평가자 1개라도 있으면 build FAIL (deployment gate)
  → 통과 시 머지/배포
배포 후
  → Online Evaluation이 프로덕션 trace 샘플링 채점 → 회귀 알림
```

- 본 문서 3.2 시나리오(TC-*)와 3.3 멀티턴 시퀀스(MT-*)를 **trajectory 데이터셋**으로 등록한다. 멀티턴은 "질문 여러 개로 구성된 trajectory"로 표현되어 AgentCore의 trajectory 평가와 자연스럽게 매핑된다.
- 배포 게이트는 published 데이터셋 버전에 고정(pin)하고, 평가자별 임계값을 하회하면 빌드를 실패시킨다.
- L1·L2(결정적)는 매 PR, L4·L5(LLM 평가 포함)는 비용을 고려해 PR 핵심 케이스 + nightly 전체로 분리한다.

## 4.3 정량 평가 치수 도입 검토 (결론: 도입 가능)

정량화는 **가능**하며, 평가자 성격에 따라 세 부류로 나눠 도입한다.

| Lovv 품질 기준 | 평가자 유형 | 레벨 | 정량 지표 | 제안 임계값 |
| --- | --- | --- | --- | --- |
| 조건 충족(국가·월·일정유형) | 코드 기반(결정적) | trace | 충족 비율 | 100% (P0 게이트) |
| 단일 목적지 | 코드 기반 | session | 단일성 통과율 | 100% |
| 축제 날짜 정확성 | 코드 기반 | tool/trace | 배치 축제 `confirmed` 비율 | 100% |
| 국가 분리(KR/JP 비혼합) | 코드 기반 | session | 위반 건수 | 0 |
| 루프 안전성 | 코드 기반 | trace | `retry_count ≤ 2` 준수율 | 100% |
| 근거성/환각 | Faithfulness(내장) | trace | 0–1 스코어 | ≥ 0.90 |
| 사실 정확성 | Correctness(내장, ground truth) | trace | 0–1 스코어 | ≥ 0.85 |
| 추천 유용성 | Helpfulness(내장) | session | 0–1 스코어 | ≥ 0.80 |
| 도구 선택 정확성 | Tool selection(내장) | tool | 정확 선택률 | ≥ 0.90 |
| 매트릭스/동선 경로 | expected trajectory | trace | 경로 일치율 | ≥ 0.95 |
| 안전성·편향 | Harmfulness / Stereotyping(내장) | session | 위반 스코어 | 0 |
| 멀티턴 일관성 | 커스텀 LLM-judge | session | 0–1 스코어 | ≥ 0.85 |

도입 시 유의점:

1. **결정적 지표 vs LLM-judge 지표 분리.** 조건충족·단일목적지·축제confirmed·국가분리·루프상한은 코드 기반 평가자로 **변동 없는 100% 게이트**로 두는 것이 안전하다. LLM-judge 지표(Correctness/Faithfulness 등)는 채점 자체에 **분산**이 있으므로 단일 실행 점수로 게이트하지 말고, 데이터셋 평균 + 마진으로 판단한다. *(신뢰도: 높음 — LLM-judge 변동성은 일반적 특성)*
2. **임계값은 제안치다.** 위 수치는 초기 기준이며, 베이스라인 측정 후 캘리브레이션이 필요하다. *(신뢰도: 중간 — 실측 전 추정)*
3. **Ground truth 데이터셋 구축이 선행**되어야 한다. 최소 expected destination·expected trajectory·assertions를 TC/MT 케이스별로 준비한다. (5장 후속 작업)
4. **비용 관리.** LLM-judge 평가는 호출 비용이 있으므로 PR 단계는 코드 평가자 + 핵심 케이스만, 전체 LLM 평가는 nightly/릴리즈로 제한한다.

# 5. 미해결·후속 작업

- Validator 실패 카테고리별 expected trajectory를 `grounding_missing`, `hallucination`, `condition_unmet`, `explanation_weak`, `fallback_unsafe`로 추가한다.
- Skill 입출력 계약 문서(Scoring/Matrix/Validation/Link/Weather/Packaging) 작성 → L2 테스트의 골든 값 정의.
- 추천 점수 회귀 fixture에 접근성, active theme 충족, 희소 테마 가중, 콘텐츠 타입 균형, soft/raw query 유사도, `unsupported_conditions` 안내 케이스를 추가한다.
- 축제 포함 요청의 Top-K 검증 fixture를 만들고 Web Search 호출 수가 K를 넘지 않는지 단언한다.
- `Itinerary_Writer_Agent`의 구조화 출력 fixture를 만들고 `itinerary`, `alternativeItinerary`, `recommendationReasons`, `itineraryFlowReason`, `externalLinks`, `confidence`, `user_notice`가 같은 후보 근거를 참조하는지 검증한다.
- `langgraph_flow.md`가 최상위 기준이므로, 구현 시 본 하네스의 그래프 배선이 정본과 1:1 대응하는지 회귀 검증.
- 롤링 요약 임계값(턴 수/토큰) 실측 후 확정.

# 6. 변경 이력

| 버전 | 날짜 | 변경 내용 |
| --- | --- | --- |
| v1.4 | 2026-06-13 | 고정 도시 mode명을 `anchored_place_search`로 통일하고 별도 축제 선택 mode 잔여 표현을 제거 |
| v1.3 | 2026-06-12 | 정본에서 특정 LLM 모델 고정 문구를 제거하고 모델 선택을 runtime config/Evaluations 결정으로 분리 |
| v1.2 | 2026-06-12 | AgentCore 하네스 책임 이관 기준, Memory 저장 경계, Gateway/Policy/Observability 분리 원칙 추가 |
| v1.1 | 2026-06-08 | DB v0.5 기준으로 DynamoDB 실행 요약과 Observability 메트릭 경계를 분리 |
| v1.1 | 2026-06-08 | Itinerary Planner와 Explanation Writer를 `Itinerary_Writer_Agent` 단일 생성 노드로 통합 |
| v1.1 | 2026-06-08 | fulfilled_matrix 표준 키 확정, Top-K 축제 검증, no_candidate 폴백, Validator 실패 카테고리 테스트 케이스 추가 |
| v1.1 | 2026-06-07 | AgentCore Evaluations 기반 CI/CD 게이트 및 정량 평가 치수(4장) 추가 |
| v1.0 | 2026-06-07 | 실행 하네스(그래프 배선·상태·AgentCore 연결·루프/재시도)와 테스트 하네스(시나리오·멀티턴·matrix 전이·mock·메트릭) 초안 작성 |
