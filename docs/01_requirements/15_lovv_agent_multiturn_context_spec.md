# Lovv 에이전트 명세서 — 멀티턴 컨텍스트 관리 정책

## 0. 문서 상태

- **문서 유형:** 에이전트 명세서
- **시스템 코드명:** `Lovv`
- **메인 기준 파일:** `langgraph_flow.md`
- **메인 파일 규칙:** `langgraph_flow.md`는 수정 금지이며 최상위 기준이다.
- **산출물 형식:** Markdown + HTML
- **작성 목적:** `Intent_Agent`가 `Supervisor`로 넘기기 전에 의도 맥락상 불필요한 컨텍스트를 제거하여 환각과 라우팅 오판을 줄인다.

## 1. 문서 우선순위

1. `langgraph_flow.md` — 수정 금지 메인 아키텍처 명세
2. 같은 임시 폴더의 보조 컨텍스트 정책 문서
3. 본 문서 — 멀티턴 컨텍스트 관리용 에이전트 명세서

본 문서와 `langgraph_flow.md`가 충돌하면 `langgraph_flow.md`를 우선한다.

## 2. 목적

본 명세서는 `Lovv` LangGraph 멀티에이전트 시스템의 멀티턴 컨텍스트 관리 정책을 재정립한다.

핵심 목적은 **환각 및 라우팅 오판 방지**다. 이를 위해 `Intent_Agent`는 사용자와의 멀티턴 대화에서 의도와 선호를 먼저 정리하고, `Supervisor`에는 라우팅에 필요한 최소 컨텍스트만 전달한다.

UI 설계는 본 문서의 범위가 아니다.

## 3. 메인 아키텍처 정렬

`Lovv`는 `langgraph_flow.md`에 정의된 Orchestrator-Worker 구조를 따른다.

```text
User
  ↓
Intent_Agent
  ↓
Supervisor
  ↓
Supervisor Router / Fulfilled Matrix
  ├─ Festival_Worker
  ├─ Media_Worker
  ├─ Theme_Worker
  └─ Backend_Serving / SAM
```

`Supervisor`는 기본적으로 전체 원문 대화 로그를 받지 않는다. `Intent_Agent`가 정리한 **의도 기반 handoff payload**만 받는다.

## 4. 에이전트 역할 명세

### 4.1 Intent_Agent

**주 역할:** 의도 추출, 취향 구체화, 컨텍스트 정리, Fulfilled Matrix 초기화.

책임:

1. 사용자 입력과 초기 제약 조건을 수신한다.
2. 멀티턴 대화로 취향과 명시적 거부 테마를 구체화한다.
3. 정형 제약 조건을 `extracted_inputs`에 기록한다.
4. RAG/검색용 핵심 비정형 선호 문장을 `user_preferences`에 기록한다.
5. 사용자가 명시적으로 제외한 테마를 `N/A`로 표시한다.
6. 활성화 대상 테마를 `X`로 표시한다.
7. `Supervisor` 전달 payload에서 의도 맥락상 불필요한 컨텍스트를 제거한다.
8. 정리된 handoff payload만 `Supervisor`에 전달한다.

### 4.2 Supervisor

**주 역할:** `Fulfilled Matrix` 기반 상태 라우팅.

책임:

1. `Intent_Agent`가 정리한 handoff payload를 받는다.
2. `fulfilled_matrix`를 평가한다.
3. `X` 상태인 테마 중 우선순위가 가장 높은 Sub-Agent를 선택한다.
4. `next_node`를 설정한다.
5. 선택된 Worker로 라우팅한다.
6. 더 이상 `X`가 없으면 `Backend_Serving`으로 전이한다.

### 4.3 Sub-Agent Worker

예시:

- `Festival_Worker`
- `Media_Worker`
- `Theme_Worker`

책임:

1. 자신의 도메인에 필요한 컨텍스트만 받는다.
2. RAG, Neo4j Vector Search, 외부 API 등 SAM 도구를 호출한다.
3. 결과를 `raw_collected_data`에 추가한다.
4. 자신의 matrix 상태를 `O` 또는 `△`로 갱신한다.
5. 처리가 끝나면 제어권을 `Supervisor`로 반환한다.

### 4.4 Route_Critic

선택형 검증 노드다.

책임:

1. 수집 데이터와 사용자 제약 조건을 교차 검증한다.
2. 예산 초과, 날씨 부적합, 모순, 정책 위반을 탐지한다.
3. 재탐색이 필요하면 해당 테마를 다시 `X`로 되돌린다.
4. 검증 통과 또는 폴백 확정 후에만 `Backend_Serving`을 허용한다.

### 4.5 Backend_Serving / SAM

책임:

1. Matrix 수렴 후 최종 데이터 패키지를 받는다.
2. 검증된 백엔드 패키지를 저장하고 UI 서빙에 제공한다.
3. Matrix 상태와 Worker 수행 결과를 보존한다.
4. 저장 전 PII 마스킹을 적용한다.

## 5. UnifiedAgentState 매핑

메인 파일은 다음 상태 모델을 기준으로 한다.

```python
class UnifiedAgentState(TypedDict):
    messages: List[Dict[str, str]]
    next_node: str
    extracted_inputs: Dict[str, Any]
    user_preferences: List[str]
    fulfilled_matrix: Dict[str, str]
    raw_collected_data: List[Dict[str, Any]]
```

정책 해석:

| 필드 | 의미 | 컨텍스트 정책 |
|---|---|---|
| `messages` | 전체 멀티턴 대화 백로그 | 상태에는 유지 가능하지만 Supervisor에 통째로 전달하지 않음 |
| `next_node` | Supervisor가 선택한 다음 라우트 | 제어 필드 |
| `extracted_inputs` | 구조화된 사용자 제약 조건 | pruning 후 Supervisor에 전달 |
| `user_preferences` | RAG/검색용 선호 문장 | 의도 관련성이 명확할 때만 전달 |
| `fulfilled_matrix` | 테마별 완료 상태 | Intent_Agent가 초기화, Supervisor가 제어 |
| `raw_collected_data` | Worker/SAM 결과 | Worker 실행 후 누적 |

## 6. Intent → Supervisor Handoff 정책

### 6.1 Handoff 경계

확정된 경계는 **Supervisor 전달값만 정리**다.

즉:

- `UnifiedAgentState.messages`에는 원본 대화 백로그가 남을 수 있다.
- `Supervisor`는 전체 `messages`를 기본으로 받지 않는다.
- `Intent_Agent`는 `Supervisor`용 pruned handoff payload를 만든다.
- 이 payload에는 라우팅, Matrix 평가, Worker 스케줄링, 검색에 필요한 컨텍스트만 포함한다.

### 6.2 권장 Handoff Payload

```json
{
  "extracted_inputs": {
    "country": "KR|JP|both",
    "season": ["spring", "summer"],
    "budget": "optional",
    "companions": "optional",
    "duration_type": "optional",
    "weather_pref": "optional"
  },
  "user_preferences": [
    "RAG/search-ready preference phrase only"
  ],
  "fulfilled_matrix": {
    "festival": "X|N/A",
    "media": "X|N/A",
    "theme": "X|N/A"
  },
  "excluded_themes": ["media"],
  "handoff_policy": {
    "mode": "intent_pruned",
    "uncertain_context_policy": "drop_if_uncertain",
    "raw_messages_forwarded": false
  }
}
```

## 7. 컨텍스트 제거 규칙

`Intent_Agent`는 `Supervisor` handoff payload에서 다음 항목을 제거한다.

| 항목 | 제거 여부 | 이유 |
|---|---:|---|
| 잡담/감탄 | 제거 | 라우팅 판단 오염 방지 |
| 거부된 테마 세부내용 | 제거 | `N/A` 테마가 스케줄링에 영향 주지 않도록 함 |
| 현재 의도와 충돌하는 과거 선호 | 제거 | 현재 의도를 우선하기 위함 |
| Worker 도메인과 무관한 정보 | 제거 | 관련 없는 Worker 라우팅 방지 |
| 민감정보/PII 원문 | 제거 | 라우팅에 불필요하며 추적/저장 위험 존재 |

## 8. 불확실성 처리 원칙

기본 원칙은 다음과 같다.

> **관련성이 불확실하면 Supervisor handoff payload에서 제거한다.**

근거:

- 이 정책의 1차 목적은 환각 및 오판 방지다.
- `Supervisor`는 높은 확신의 의도 신호만 기반으로 라우팅해야 한다.
- 애매한 컨텍스트는 Matrix 초기화와 Worker 스케줄링을 오염시킬 수 있다.

주의:

- 제거는 `Supervisor` handoff payload 기준이다.
- `UnifiedAgentState.messages`에서 원본을 반드시 삭제한다는 의미는 아니다.
- 나중에 필요하면 과거 애매한 문맥을 재사용하기보다 사용자에게 다시 질문한다.

## 9. Fulfilled Matrix 정책

`Fulfilled Matrix`는 멀티턴 컨텍스트 생명주기와 Worker 라우팅의 핵심 제어판이다.

| 상태 | 의미 | 정책 효과 |
|---|---|---|
| `X` | 실행 대기 | 활성 Worker 대상 |
| `O` | 성공 | Worker 정상 완료 |
| `△` | 폴백/오류 | 예외 또는 대체 경로 사용 |
| `N/A` | 제외 | 스케줄링 금지 |

초기화 규칙:

- 사용자가 명시적으로 거부한 테마 → `N/A`
- 현재 의도와 관련 있는 활성 테마 → `X`
- 지원하지 않거나 현재 의도와 무관한 테마 → `N/A`

`Supervisor`는 `X` 상태만 라우팅한다.

## 10. LangSmith Trace 정책

LangSmith는 관측성 전용이며 redacted metadata만 기록한다.

허용 예시:

```json
{
  "node_name": "Intent_Agent",
  "matrix_status": "X|O|△|N/A",
  "next_node": "festival_worker",
  "handoff_mode": "intent_pruned",
  "dropped_context_categories": ["chitchat", "excluded_theme", "pii_raw"],
  "latency_ms": 1234
}
```

금지:

- 사용자 메시지 원문
- assistant 응답 원문
- PII 원문
- 전체 `user_preferences`
- 전체 `messages`
- 사용자 세부정보가 포함된 여행 요약 원문

## 11. SAM 저장 정책

기존 SAM 정책은 유지하되 다음을 명확히 한다.

- SAM은 Matrix 수렴 후 최종 백엔드 서빙 패키지를 받을 수 있다.
- SAM 저장 전 PII는 마스킹해야 한다.
- `Supervisor` handoff pruning과 SAM 최종 패키지 저장은 별개다.
- 원본 대화가 상태에 남아 있더라도 `Supervisor` handoff는 항상 가볍고 의도 중심이어야 한다.

## 12. 에이전트 요구사항

### 12.1 기능 요구사항

| ID | 요구사항 | 우선순위 |
|---|---|---|
| AG-FR-001 | `Intent_Agent`는 Supervisor 라우팅 전 의도 구체화를 수행해야 한다. | P0 |
| AG-FR-002 | `Intent_Agent`는 `extracted_inputs`, `user_preferences`, 초기 `fulfilled_matrix`를 생성해야 한다. | P0 |
| AG-FR-003 | `Intent_Agent`는 Supervisor handoff payload에서 의도 무관 컨텍스트를 제거해야 한다. | P0 |
| AG-FR-004 | `Intent_Agent`는 전체 `messages`를 기본적으로 Supervisor에 전달하지 않아야 한다. | P0 |
| AG-FR-005 | 관련성이 불확실한 컨텍스트는 Supervisor handoff payload에서 제거해야 한다. | P0 |
| AG-FR-006 | 사용자가 명시적으로 거부한 테마는 `N/A`로 표시해야 한다. | P0 |
| AG-FR-007 | `Supervisor`는 `X` 상태의 matrix 항목만 라우팅해야 한다. | P0 |
| AG-FR-008 | Worker는 실행 후 자신의 matrix 항목을 `O` 또는 `△`로 갱신해야 한다. | P0 |
| AG-FR-009 | `Route_Critic`은 검증 실패 테마를 `X`로 되돌려 폴백 라우팅을 유도할 수 있다. | P1 |
| AG-FR-010 | LangSmith trace는 redacted metadata만 사용해야 한다. | P0 |

### 12.2 비기능 요구사항

| ID | 요구사항 | 우선순위 |
|---|---|---|
| AG-NFR-001 | `langgraph_flow.md`는 수정하지 않는다. | P0 |
| AG-NFR-002 | UI 설계는 범위 밖이다. | P0 |
| AG-NFR-003 | Supervisor payload는 최소화되고 의도 관련성이 명확해야 한다. | P0 |
| AG-NFR-004 | PII는 LangSmith에 전달하지 않는다. | P0 |
| AG-NFR-005 | PII는 SAM 저장 전 마스킹해야 한다. | P0 |

## 13. 수용 기준

- [ ] `langgraph_flow.md`가 변경되지 않는다.
- [ ] 명세서가 `Intent_Agent → Supervisor → Worker` 토폴로지를 따른다.
- [ ] `Intent_Agent`가 Supervisor handoff payload를 pruning한다.
- [ ] 전체 `messages`가 기본적으로 Supervisor에 전달되지 않는다.
- [ ] 잡담/감탄, 제외 테마 세부내용, 모순된 과거 선호, Worker 비관련 정보, 민감/PII 원문이 Supervisor payload에서 제거된다.
- [ ] 관련성이 불확실하면 Supervisor handoff payload에서 제거된다.
- [ ] `Fulfilled Matrix`가 라우팅과 종료 조건을 제어한다.
- [ ] LangSmith에는 redacted metadata만 전달된다.
- [ ] 산출물이 Markdown과 HTML 두 형식으로 존재한다.

## 14. 최종 정책 문장

`Lovv`는 `Intent_Agent`를 `Supervisor` 이전의 컨텍스트 게이트로 사용한다. 원본 대화 백로그는 `UnifiedAgentState.messages`에 남을 수 있지만, `Supervisor`는 `Intent_Agent`가 정리한 의도 중심 handoff payload만 받는다. 의도, Matrix 초기화, Worker 라우팅에 명확히 필요하지 않은 컨텍스트는 handoff payload에서 제거한다. 관련성이 불확실하면 제거한다. 이를 통해 `langgraph_flow.md`의 메인 아키텍처를 유지하면서도 불필요한 컨텍스트가 라우팅 판단을 오염시키는 것을 방지한다.
