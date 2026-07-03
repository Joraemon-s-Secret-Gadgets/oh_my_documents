# DynamoDB TTL 보완 실행 스펙

- 문서 버전: 1.1
- 작성일: 2026-06-30
- 기준 보고서: `reports/dynamodb_ttl_status_review_20260630_ko.md`
- 관련 기존 스펙: `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md`

## Objective

Data Stack의 DynamoDB TTL 설정과 애플리케이션 쓰기 경로 사이의 갭을 단계적으로 줄인다.

현재 6개 Data Stack TTL 테이블 중 `lovv_auth_sessions`는 애플리케이션 writer가 `expiresAt`를 기록한다. 나머지 5개 테이블(`lovv_user_event_logs`, `lovv_agent_runs`, `lovv_festival_verify_cache`, `lovv_async_jobs`, `lovv_api_logs`)은 최초 분석 당시 `TimeToLiveSpecification`만 있고 실제 `expires_at` writer가 없었다. 이번 실행 범위에서는 5개 테이블의 라이브러리 수준 writer와 단위 테스트까지 추가됐지만, 제품 Lambda caller, SAM 환경변수, IAM 배선은 아직 연결하지 않는다.

이번 실행 목표는 즉시 안전한 회귀 방지와 라이브러리 수준 writer 구현까지 완료하는 것이다. 실제 제품 호출자가 아직 없는 상태이므로 SAM 환경변수/IAM 배선과 Lambda 호출 연결은 추가하지 않는다.

## Tech Stack

- Runtime: Python 3.11
- Test framework: `pytest`, existing `unittest.TestCase` style tests
- Infra: AWS SAM root `template.yaml`, Data Stack CloudFormation `infra/data-stack/template.yaml`
- Data store: DynamoDB TTL with epoch seconds Number attributes

## Commands

```powershell
python -m pytest tests/test_session_repository.py
python -m pytest tests
$env:AWS_CLI_FILE_ENCODING='UTF-8'; aws cloudformation validate-template --template-body file://infra/data-stack/template.yaml
```

## Project Structure

- `docs/specs/`: durable implementation specs
- `reports/`: analysis and review reports
- `src/auth/session_repository.py`: auth session DynamoDB writer
- `src/shared/dynamodb_ttl.py`: TTL 계산/보존기간/테이블 resolve helper
- `src/shared/operational_events.py`: `user_event_logs`, `api_logs` writer
- `src/shared/async_jobs.py`: `async_jobs` writer
- `src/agentcore/run_repository.py`: `agent_runs` writer
- `src/agentcore/festival_cache_repository.py`: `festival_verify_cache` writer
- `tests/test_session_repository.py`: auth session repository regression tests
- `tests/test_dynamodb_ttl.py`: non-auth TTL helper/writer regression tests
- `infra/data-stack/template.yaml`: Data Stack DynamoDB tables and TTL configuration
- `template.yaml`: SAM app Lambda environment/IAM wiring

## Code Style

Keep the existing repository style for the touched files. For this first remediation step, do not refactor `src/auth/session_repository.py`; only add a focused characterization test.

Expected auth session TTL write contract:

```python
item = {
    "sessionId": session_id,
    "userId": user_id,
    "provider": provider,
    "refreshTokenHash": refresh_token_hash,
    "createdAt": int(now_epoch),
    "expiresAt": int(expires_at_epoch),
}
table.put_item(
    Item=item,
    ConditionExpression="attribute_not_exists(sessionId)",
)
```

Do not rename `expiresAt` to `expires_at` for `lovv_auth_sessions`. The other five Data Stack TTL tables use `expires_at`.

## Testing Strategy

### M1: Auth session TTL regression

Add a test that captures `DynamoDbSessionRepository.create_session()`'s DynamoDB `put_item` call and verifies:

- `Item["expiresAt"]` exists.
- `Item["expiresAt"] == int(expires_at_epoch)`.
- `Item["expiresAt"]` is an `int`.
- `Item` does not include `expires_at`.
- `ConditionExpression` remains `attribute_not_exists(sessionId)`.

### Future writer tests

The five non-auth TTL writer modules must include tests verifying:

- TTL attribute name is exactly `expires_at`.
- TTL value is an `int` epoch seconds value.
- The value equals `created_epoch + retention_seconds`.
- The table writer owns the attribute name explicitly and does not share it through a helper that could mix `expires_at` and `expiresAt`.

### Future SAM wiring tests

When a real Lambda caller starts using one of these writers, add template tests verifying:

- The function receives only the table name environment variable it needs.
- IAM grants only the required DynamoDB actions for that table/GSI.
- No broad DynamoDB wildcard table resource is introduced.

## Boundaries

- Always:
  - Preserve `expiresAt` for `lovv_auth_sessions`.
  - Preserve `expires_at` for the five non-auth Data Stack TTL tables.
  - Add tests before or with any future TTL writer.
  - Keep DynamoDB IAM permissions limited to the Lambda function that actually reads/writes the table.
- Ask first:
  - Adding product behavior that writes event logs, agent runs, async jobs, API logs, or festival cache items.
  - Adding CloudWatch alarms/SNS topics for TTL monitoring.
  - Changing retention windows.
  - Adding S3 archive paths before TTL deletion.
- Never:
  - Do not connect unused writers to Lambda functions with no caller.
  - Do not grant broad DynamoDB table wildcards.
  - Do not normalize all TTL attribute names to one spelling.
  - Do not treat TTL deletion timing as authorization or business-state correctness; TTL deletion is asynchronous.

## Success Criteria

### This execution

1. This spec is saved under `docs/specs/`.
2. `tests/test_session_repository.py` verifies `create_session()` writes integer `expiresAt` and not `expires_at`.
3. `src/shared/dynamodb_ttl.py` defines shared TTL retention constants and `ttl_epoch()`.
4. The five non-auth TTL tables have writer modules that record integer `expires_at`.
5. `tests/test_dynamodb_ttl.py` verifies key format, TTL attribute spelling, TTL value, and `put_item` payloads.
6. `python -m pytest tests/test_session_repository.py tests/test_dynamodb_ttl.py` passes.
7. No SAM environment variable or IAM wiring is added until a real product caller is connected.

### Future completion of the full TTL remediation

1. Each of the five non-auth TTL writers is called from the product flow that owns the write.
2. SAM environment variables and IAM are added only to functions that actually use each table.
3. Data Stack validation passes after any infra change.
4. Runtime smoke tests confirm the product flow calls the writer and sends `expires_at` to DynamoDB.

## Task Plan

- [x] Task: Review current TTL status and define execution boundary
  - Acceptance: The report distinguishes infra TTL setup from app writer completion.
  - Verify: `reports/dynamodb_ttl_status_review_20260630_ko.md`
  - Files: `reports/dynamodb_ttl_status_review_20260630_ko.md`

- [x] Task: Add auth session TTL payload regression test
  - Acceptance: Test captures `put_item` and asserts `expiresAt` int, no `expires_at`, and existing condition expression.
  - Verify: `python -m pytest tests/test_session_repository.py`
  - Files: `tests/test_session_repository.py`

- [x] Task: Defer five non-auth runtime wiring until callers exist
  - Acceptance: Library-level writers exist, but no SAM env/IAM wiring is introduced without a real Lambda caller.
  - Verify: `rg -n "USER_EVENT_LOGS_TABLE_NAME|AGENT_RUNS_TABLE_NAME|FESTIVAL_VERIFY_CACHE_TABLE_NAME|ASYNC_JOBS_TABLE_NAME|API_LOGS_TABLE_NAME" template.yaml`
  - Files: none for runtime wiring in this execution

- [x] Task: Add shared TTL helper and retention constants
  - Acceptance: `ttl_epoch()` returns integer epoch seconds and retention constants match the spec.
  - Verify: `python -m pytest tests/test_dynamodb_ttl.py`
  - Files: `src/shared/dynamodb_ttl.py`, `tests/test_dynamodb_ttl.py`

- [x] Task: Add five non-auth TTL writer modules
  - Acceptance: Writers for `user_event_logs`, `agent_runs`, `festival_verify_cache`, `async_jobs`, and `api_logs` write item payloads with integer `expires_at`.
  - Verify: `python -m pytest tests/test_dynamodb_ttl.py`
  - Files: `src/shared/operational_events.py`, `src/shared/async_jobs.py`, `src/agentcore/run_repository.py`, `src/agentcore/festival_cache_repository.py`

## Open Questions

No blocking question for library-level writer implementation.

Future SAM wiring and runtime integration still need product-scope decisions for which Lambda/function owns writes to:

- `lovv_user_event_logs`
- `lovv_agent_runs`
- `lovv_festival_verify_cache`
- `lovv_async_jobs`
- `lovv_api_logs`
