# 9. Bedrock 및 AgentCore 매핑

| 본 설계 요소 | 매핑 |
| --- | --- |
| Sub-Agent, Supervisor 그래프 | AgentCore Runtime |
| 온보딩, 피드백, 세션, 요약, `fulfilled_matrix`, 축제 검증 캐시 | AgentCore Memory |
| Scoring, Matrix, Validation, Link, Weather, Packaging Skill | AgentCore Gateway 또는 Lambda |
| Festival 웹 검색 | AgentCore Browser 또는 Web Search |
| Agent별 권한 | AgentCore Identity |
| 국가 혼합 금지, 미검증 축제 차단 | AgentCore Policy |
| trace, latency, token, retry, fallback 비율 | AgentCore Observability |
| 회귀 평가, trajectory 평가, LLM-as-Judge | AgentCore Evaluations |

AgentCore 하네스는 도메인 추론을 대체하지 않는다. 요청 정규화, graph compile/cache,
model adapter, identity, runtime guard, redacted logging, entrypoint contract test는
하네스 책임으로 두고, Agent node·routing rule·prompt·schema·fallback behavior는
도메인 workflow의 정본으로 유지한다. 상세 책임 경계는 `supplemental/agent_harness_design.md`
2.2.1을 따른다.

Memory에는 다음 턴의 의도 해석과 재추천에 필요한 요약 상태만 저장한다.
`messages` recent window, `conversation_summary`, `fulfilled_matrix`, `city_anchor`,
`festival_verifications` summary, `PlanDraft` summary는 저장 후보지만, raw RAG result,
raw web content, full `candidate_evidence_package`, embedding cache, secret, PII는
Memory와 log에 저장하지 않는다. 전체 `candidate_evidence_package`는 단일 실행 내부
payload로만 사용하고, 멀티턴 재추천에는 city/place id와 audit 요약만 남긴다.

LLM 호출은 Bedrock Converse API로 추상화한다.
본 정본은 특정 모델 ID나 Agent별 모델 tier 배정을 고정하지 않는다.
실제 모델 ID와 tier 배정은 Bedrock Converse adapter, 배포 환경 설정, 비용·지연·품질
평가 결과에 따라 결정한다.
임베딩은 Amazon Titan Text Embeddings V2 또는 Cohere Embed 계열을 후보로 두고, S3 vector 기능 기반 RAG 인덱스와 연동한다.

## 9.1 저장소 연결 원칙

| 데이터 | 저장소 | Agent 책임 |
| --- | --- | --- |
| 추천 요청/결과 원장 | MySQL `recommendation_requests`, `recommendation_results` | `recommendation_request_id` 기준으로 요청과 결과를 연결한다. |
| 생성 일정 | MySQL `itineraries`, `itinerary_items` | 최종 검증을 통과한 일정만 저장 대상으로 전달한다. |
| Agent 실행 trace | DynamoDB `lovv_agent_runs` | DB 설계 명세서 v0.5 기준으로 `agent_run_id`, `node_name`, `tool_name`, `validation_retry_count`, `error_code`, `payload_summary` 중심의 원문 없는 실행 요약만 남긴다. `next_node`, `fulfilled_matrix`, `target_region`은 런타임/Memory 상태로 관리하고, `token_usage`는 AgentCore Observability 메트릭으로 분리한다. |
| 비동기 작업 상태 | DynamoDB `lovv_async_jobs` | 장시간 실행 또는 재시도 작업의 `job_type`, `status`, `progress`, `result_ref`, `error_code`를 갱신한다. |
| 축제 검증 캐시 | DynamoDB `lovv_festival_verify_cache` | `festival_id + travelYear` 단위로 `date_status`, 날짜, 공식 출처, 신뢰도를 재사용한다. |
| RAG 검색 인덱스 | S3 vector index | 목적지·축제·관광지 chunk와 metadata filter를 조회하되 원본 확정 근거로 단독 사용하지 않는다. |
| 관계 탐색 보조 | Lambda + DynamoDB 인접 리스트 | 도시·축제·테마·장소 관계를 탐색해 후보를 확장하되 원본 확정 근거로 단독 사용하지 않는다. |

Agent는 저장소별 책임을 넘지 않는다.
MySQL 원장은 사용자에게 조회·저장·피드백으로 노출되는 최종 상태를 담당하고, DynamoDB는 TTL 기반 실행 상태와 로그성 데이터를 담당한다.
S3 vector index는 검색 성능과 의미 재랭킹을 위한 파생 인덱스이며, 재색인과 복구는 MySQL, DynamoDB 정규화 문서, S3 Raw 원본을 기준으로 수행한다.
Lambda 관계 탐색 보조 기능은 관계 탐색과 그래프 기반 후보 확장을 위한 파생 기능이며, 재적재와 복구는 DynamoDB 정규화 문서와 S3 Raw 원본을 기준으로 수행한다. Neptune은 3-hop 이상 임의 경로 탐색이나 대규모 실시간 그래프 쓰기가 필요해질 때의 고도화 승격 옵션으로 둔다.
