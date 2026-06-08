---
작성자: 조동휘
상태: 진행후
---

# Agent Spec / DB Trace 계약 동기화 계획

## 목적

현재 `04_database_design.md`의 DynamoDB `lovv_agent_runs` 속성 축소와 `05_agent_spec.md`의 Agent trace 저장소 계약이 서로 어긋난다. 본 작업은 DB 설계 문서를 최신 기준으로 두고, Agent 명세·LangGraph 정본·하네스·생성 HTML을 DB 계약에 맞게 동기화하는 것을 목표로 한다.

## 현재 불일치

| 항목 | DB 설계 현재 상태 | Agent Spec 현재 상태 | 판단 |
| --- | --- | --- | --- |
| 기준 문서 메타데이터 | DB `v0.5`, API `v0.1`, 기술 `v0.4` 표기 | DB `v0.2`, 기술 `v0.2`, API `v0.1` 표기 | Agent Spec 상단 기준 문서 업데이트 필요 |
| `lovv_agent_runs.next_node` | 없음 | 저장한다고 명시 | Agent Spec에서 저장 필드로 쓰지 않도록 수정 |
| `fulfilled_matrix_summary` | 없음 | 저장한다고 명시 | Agent Spec에서 저장 필드로 쓰지 않도록 수정 |
| `target_region` | 없음 | 저장한다고 명시 | 런타임/Memory 상태로 유지하되 DB trace 저장 필드에서는 제외 |
| `token_usage` | 없음 | 저장한다고 명시 | AgentCore Observability/CloudWatch 메트릭으로 분리하고 DB trace 저장 필드에서는 제외 |

## 결정 방향

- DB 문서는 이번 작업에서 수정하지 않는다.
- `lovv_agent_runs` 저장 필드는 DB 문서 기준인 `agent_run_id`, `node_name`, `tool_name`, `validation_retry_count`, `error_code`, `payload_summary` 중심으로 맞춘다.
- `next_node`, `fulfilled_matrix_summary`, `target_region`은 LangGraph/Memory/평가용 런타임 상태로 유지하되 DynamoDB trace 저장 필드로 명시하지 않는다.
- `token_usage`는 AgentCore Observability/CloudWatch 메트릭으로 분리하고 DynamoDB trace 저장 필드로 명시하지 않는다.
- `payload_summary`는 원문 payload가 아니라 후보 수, 실패 카테고리, 결측 상태 같은 요약값만 허용한다.

## 작업 체크리스트

- [x] `docs/04_database_design/04_database_design.md`는 수정하지 않고 최신 기준 문서로 둔다.
- [x] `docs/05_agent_spec/05_agent_spec.md` 상단 기준 문서를 현재 문서 버전에 맞게 업데이트한다.
- [x] `docs/05_agent_spec/05_agent_spec.md` 9.1 저장소 연결 원칙을 DB 문서의 `lovv_agent_runs` 필드명·저장 제한으로 정리한다.
- [x] `docs/05_agent_spec/langgraph_flow.md`의 Observability/trace 설명에서 DB 저장 필드와 런타임 상태를 구분한다.
- [x] `docs/05_agent_spec/agent_harness_design.md`의 관측성 항목에서 token/route/matrix는 Observability 메트릭 또는 evaluation trace로 분리한다.
- [x] `python scripts\generate_pages.py`로 `pages/05_agent_spec.html`, `index.html`을 재생성한다.
- [x] `python scripts\verify_pages_structure.py`로 HTML 구조를 검증한다.
- [x] `rg -n "next_node|fulfilled_matrix_summary|target_region|token_usage|lovv_agent_runs" docs/05_agent_spec pages/05_agent_spec.html`로 Agent 문서의 저장소 계약이 DB 기준과 충돌하지 않는지 확인한다.
- [x] `git diff --cached --name-status`와 `git diff --cached -- docs/05_agent_spec pages/05_agent_spec.html`로 staged 범위와 의미를 확인한다.

## 예상 변경 파일

- `docs/05_agent_spec/05_agent_spec.md`
- `docs/05_agent_spec/langgraph_flow.md` (필요 시)
- `docs/05_agent_spec/agent_harness_design.md` (필요 시)
- `pages/05_agent_spec.html`
- `index.html`
- `plans/before/agent-spec-db-trace-sync-plan.md`

## 검증 방법

- `python scripts\generate_pages.py`
- `python scripts\verify_pages_structure.py`
- `rg -n "next_node|fulfilled_matrix_summary|target_region|token_usage|lovv_agent_runs" docs/05_agent_spec pages/05_agent_spec.html`
- `git diff --cached --name-status`

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| trace 필드가 개인정보나 원문 저장으로 오해됨 | NFR-013 위반으로 해석될 수 있음 | DB 저장 필드는 `payload_summary` 중심의 요약값으로 제한 |
| DB 문서와 Agent Spec 기준 버전이 계속 어긋남 | 문서 간 신뢰도 저하 | 상단 기준 문서와 변경 이력까지 함께 갱신 |
| staged 변경이 이미 많음 | 커밋 범위 오염 | 적용 후 staged diff를 파일군별로 확인하고 필요하면 커밋을 분리 |
