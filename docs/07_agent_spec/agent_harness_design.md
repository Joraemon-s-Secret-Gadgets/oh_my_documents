# 로브 (Lovv) Agent 하네스 설계

> 문서 버전: v1.0
> 문서 상태: 검토 중 (Review)
> 기준 문서: `langgraph_flow.md`(그래프 정본), `agent_update.md`(설계 결정), `../01_requirements/lovv_agent_multiturn_context_spec.md`(멀티턴 정책)

# 1. 문서 개요

본 문서는 Lovv 에이전트의 두 가지 하네스를 설계한다.

1. **실행/런타임 하네스** — LangGraph 그래프를 조립하고 `UnifiedAgentState`를 관리하며 AWS Bedrock AgentCore에 연결해 에이전트를 실제 구동하는 스캐폴드.
2. **테스트 하네스** — 멀티턴 시나리오의 정상/폴백/실패 케이스, 입력→기대출력, `fulfilled_matrix` 전이를 검증하는 품질 검증 체계.

두 하네스는 동일한 그래프 정의와 상태 스키마를 공유한다. 실행 하네스가 "프로덕션 구동", 테스트 하네스가 "동일 그래프에 대한 검증"이다.

# 2. 실행 / 런타임 하네스

## 2.1 목적과 책임 경계

실행 하네스는 비즈니스 로직(노드 내부 추론)을 포함하지 않는다. **그래프 배선, 상태 영속화, 외부 연결, 루프·재시도 제어, 관측성**만 담당한다.

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

## 2.6 에러·재시도·폴백

| 상황 | 처리 |
| --- | --- |
| Skill/Tool 호출 실패 | 1회 재시도 후 해당 매트릭스 항목 `△`(폴백) 표시 |
| Web Search 실패 | 축제 `date_status=unknown`, 일정 직접 배치 금지 |
| 검증 실패 | `validation_retry_count++`, 상한 2 도달 시 폴백 응답 확정 |
| 데이터 결측 | `confidence` 하향 + 결측 안내 메시지 포함 |

## 2.7 관측성

- LangSmith: redacted 메타데이터만(노드명, matrix 상태, next_node, dropped_context_categories, latency). 원문/PII 금지(멀티턴 명세 §10).
- AgentCore Observability(CloudWatch): 노드 지연, 토큰 사용, 재시도 횟수, 폴백 비율 대시보드.

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
| TC-E01 | 실패 | 의미 검증 2회 실패 | 폴백 응답 확정 종료 | `retry_count`=2에서 폴백, 무한루프 없음 |
| TC-E02 | 실패 | 국가 혼합 시도(KR+JP) | 차단/재요청 | 단일 국가만 결과, Policy 위반 차단 |
| TC-E03 | 실패 | 필수 조건 누락 | 추가 질문 생성 | NEED_MORE 아니오 경로 |

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

각 케이스에서 매트릭스 스냅샷을 단계별로 단언한다. 예시(TC-N01):

```text
초기:      {retrieval:X, festival:X, ranking:X, itinerary:X, explanation:X, validation:X}
Retriever 후: {retrieval:O, festival:O, ranking:X, ...}
Ranker 후:    {ranking:O, ...}
순차 완료:    전부 O → Backend_Serving 전이
```

전이 불변식: `X`만 라우팅 / Worker 완료 시 `O|△` / `N/A`는 스케줄링 제외 / 재시도 시 해당 항목만 `X` 복귀.

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

- `fulfilled_matrix` 표준 키 확정(`langgraph_flow.md` 8장과 동기화).
- Skill 입출력 계약 문서(Scoring/Matrix/Validation/Link/Weather/Packaging) 작성 → L2 테스트의 골든 값 정의.
- `langgraph_flow.md`가 최상위 기준이므로, 구현 시 본 하네스의 그래프 배선이 정본과 1:1 대응하는지 회귀 검증.
- 롤링 요약 임계값(턴 수/토큰) 실측 후 확정.

# 6. 변경 이력

| 버전 | 날짜 | 변경 내용 |
| --- | --- | --- |
| v1.1 | 2026-06-07 | AgentCore Evaluations 기반 CI/CD 게이트 및 정량 평가 치수(4장) 추가 |
| v1.0 | 2026-06-07 | 실행 하네스(그래프 배선·상태·AgentCore 연결·루프/재시도)와 테스트 하네스(시나리오·멀티턴·matrix 전이·mock·메트릭) 초안 작성 |
