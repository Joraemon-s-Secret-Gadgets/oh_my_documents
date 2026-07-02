# DynamoDB TTL 작업 상태 분석 보고서

- 작성일: 2026-06-30
- 대상 저장소: `03_lovv_BE`
- 분석 범위: `infra/data-stack/template.yaml`, 루트 `template.yaml`, `src/**`, `tests/**`, `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md`, 기존 TTL 분석 보고서

## 결론

`infra/data-stack/template.yaml`의 DynamoDB `TimeToLiveSpecification` 설정은 6개 테이블 모두 완료되어 있다.

다만 DynamoDB TTL은 테이블 설정만으로는 삭제가 발생하지 않는다. 애플리케이션이 각 item에 TTL 속성값을 Number 타입의 epoch seconds로 기록해야 한다. 2026-06-30 추가 작업 이후 현재 코드 기준으로는 `lovv_auth_sessions` writer와 5개 비인증 테이블의 라이브러리 수준 writer가 존재한다.

남은 갭은 SAM 환경변수/IAM 배선과 실제 제품 호출 연결이다. 즉 현재 상태는 "TTL 인프라 준비 완료, writer 모듈/단위 테스트 완료, Lambda runtime 연결 미완료"로 판단한다.

## 검토 Findings

### [P1] 5개 `expires_at` 테이블 writer는 생겼지만 Lambda caller 배선은 없다

- 영향 테이블: `lovv_user_event_logs`, `lovv_agent_runs`, `lovv_festival_verify_cache`, `lovv_async_jobs`, `lovv_api_logs`
- 스펙 요구사항: `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md:23-27`, `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md:231-235`
- 현재 근거:
  - Data Stack TTL 설정은 존재한다: `infra/data-stack/template.yaml:510-513`, `infra/data-stack/template.yaml:571-574`, `infra/data-stack/template.yaml:624-626`, `infra/data-stack/template.yaml:651-653`, `infra/data-stack/template.yaml:682-684`
  - writer 모듈은 추가됐다: `src/shared/operational_events.py`, `src/shared/async_jobs.py`, `src/agentcore/run_repository.py`, `src/agentcore/festival_cache_repository.py`
  - TTL 계산/보존기간 helper는 `src/shared/dynamodb_ttl.py`에 있다.
  - writer 단위 테스트는 `tests/test_dynamodb_ttl.py`에서 `expires_at` 속성명, 정수 epoch 값, key format, `put_item` payload를 검증한다.
  - 루트 `template.yaml`의 DynamoDB 환경변수/IAM은 여전히 `AUTH_SESSIONS_TABLE_NAME`과 별도 `AUTH_AUTHZ_CACHE_TABLE_NAME`만 배선한다: `template.yaml:420-472`
- 판정: 부분 완료. 라이브러리 writer는 완료됐지만, 실제 Lambda runtime에서 호출되지 않으므로 운영 데이터에 `expires_at`가 기록된다고 볼 수는 없다.

### [P2] `auth_sessions` TTL writer는 있으나 회귀 테스트가 약하다

- 영향 테이블: `lovv_auth_sessions`
- 스펙 요구사항: `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md:184-191`, `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md:231`
- 현재 근거:
  - `src/auth/app.py`가 refresh TTL epoch를 계산해 `create_session()`에 넘긴다: `src/auth/app.py:227-239`, `src/auth/app.py:303-315`
  - `src/auth/session_repository.py`가 `"expiresAt": int(expires_at_epoch)`를 `put_item()` item에 포함한다: `src/auth/session_repository.py:25-44`
  - `tests/test_session_repository.py`는 현재 GSI 조회명만 확인하고, `create_session()`의 `put_item` payload를 캡처하지 않는다: `tests/test_session_repository.py:10-49`
- 판정: 구현 및 회귀 테스트 보강 완료. `tests/test_session_repository.py`가 `expiresAt` camelCase 유지와 `expires_at` 혼입 방지를 검증한다.

### [정보] `AdminAuthzCacheTable`은 이번 6개 테이블 검토 범위 밖이다

- 현재 근거:
  - 루트 `template.yaml`의 `AdminAuthzCacheTable`은 `expiresAt` TTL을 가진 별도 캐시 테이블이다: `template.yaml:403-418`
  - `src/auth/authz_cache_repository.py`는 해당 별도 테이블에 `"expiresAt": int(now) + int(ttl_seconds)`를 쓴다: `src/auth/authz_cache_repository.py:52-61`, `src/auth/authz_cache_repository.py:109-119`
- 판정: 이 테이블의 TTL writer는 존재하지만, 사용자가 제시한 Data Stack 6개 테이블 중 하나가 아니므로 `lovv_user_event_logs` 등 5개 미구현 판정을 뒤집지 않는다.

## 테이블별 상태

| 테이블 | TTL 속성 | 인프라 TTL 설정 | 앱 쓰기 경로 | 상태 판단 |
| --- | --- | --- | --- | --- |
| `lovv_user_event_logs` | `expires_at` | 완료 | writer 있음, caller 배선 없음 | 부분 완료 |
| `lovv_agent_runs` | `expires_at` | 완료 | writer 있음, caller 배선 없음 | 부분 완료 |
| `lovv_festival_verify_cache` | `expires_at` | 완료 | writer 있음, caller 배선 없음 | 부분 완료 |
| `lovv_async_jobs` | `expires_at` | 완료 | writer 있음, caller 배선 없음 | 부분 완료 |
| `lovv_api_logs` | `expires_at` | 완료 | writer 있음, caller 배선 없음 | 부분 완료 |
| `lovv_auth_sessions` | `expiresAt` | 완료 | 있음 | 구현 및 테스트 완료 |

## 인프라 확인

`infra/data-stack/template.yaml`에는 6개 테이블 모두 `TimeToLiveSpecification`이 있다.

| 리소스 | 물리 테이블명 | 근거 |
| --- | --- | --- |
| `UserEventLogsTable` | `lovv_${EnvName}_user_event_logs` | `infra/data-stack/template.yaml:485-513` |
| `AgentRunsTable` | `lovv_${EnvName}_agent_runs` | `infra/data-stack/template.yaml:546-574` |
| `FestivalVerifyCacheTable` | `lovv_${EnvName}_festival_verify_cache` | `infra/data-stack/template.yaml:607-626` |
| `AsyncJobsTable` | `lovv_${EnvName}_async_jobs` | `infra/data-stack/template.yaml:634-653` |
| `ApiLogsTable` | `lovv_${EnvName}_api_logs` | `infra/data-stack/template.yaml:661-684` |
| `AuthSessionsTable` | `lovv_${EnvName}_auth_sessions` | `infra/data-stack/template.yaml:749-767` |

Data Stack은 6개 테이블명을 SSM Parameter로도 게시한다.

- `/lovv/${EnvName}/ddb/user_event_logs`: `infra/data-stack/template.yaml:970-975`
- `/lovv/${EnvName}/ddb/agent_runs`: `infra/data-stack/template.yaml:977-982`
- `/lovv/${EnvName}/ddb/festival_verify_cache`: `infra/data-stack/template.yaml:984-989`
- `/lovv/${EnvName}/ddb/async_jobs`: `infra/data-stack/template.yaml:991-996`
- `/lovv/${EnvName}/ddb/api_logs`: `infra/data-stack/template.yaml:998-1003`
- `/lovv/${EnvName}/ddb/auth_sessions`: `infra/data-stack/template.yaml:1019-1024`

## 애플리케이션 쓰기 경로 확인

### `lovv_auth_sessions`

구현되어 있다.

- 루트 `template.yaml`은 `AuthFunction`에 `AUTH_SESSIONS_TABLE_NAME`을 주입한다: `template.yaml:420-438`
- `AuthFunction`은 `auth_sessions` 테이블과 refresh-token GSI에 대해 `dynamodb:PutItem`, `dynamodb:Query`, `dynamodb:UpdateItem` 권한을 가진다: `template.yaml:457-465`
- `src/auth/app.py`는 소셜 로그인과 Cognito 세션 생성에서 `expires_at_epoch = _now_epoch() + _refresh_ttl_seconds()`를 계산한다: `src/auth/app.py:227-239`, `src/auth/app.py:303-315`
- `src/auth/session_repository.py`는 `create_session()`에서 DynamoDB item에 `"expiresAt": int(expires_at_epoch)`를 포함하고 `put_item()`으로 저장한다: `src/auth/session_repository.py:25-44`
- `_is_active()`는 TTL 삭제가 비동기라는 전제하에 `expiresAt`를 다시 확인한다: `src/auth/session_repository.py:100-106`

주의점: `tests/test_session_repository.py`는 현재 GSI 조회명만 검증한다. `create_session()`이 `expiresAt`를 정수로 쓰고 `expires_at`를 쓰지 않는다는 회귀 테스트는 아직 없다.

### 나머지 5개 `expires_at` 테이블

라이브러리 수준 writer는 구현됐지만, 아직 제품 Lambda 호출 경로에는 연결되지 않았다.

검색 기준:

- `put_item`, `update_item`, `batch_writer`, DynamoDB `Table(...)` 사용처
- `USER_EVENT`, `AGENT_RUN`, `FESTIVAL_VERIFY`, `ASYNC_JOB`, `API_LOGS` 계열 환경변수/상수
- Data Stack SSM parameter 경로(`/lovv/${EnvName}/ddb/...`)

현재 `src/`에서 확인된 DynamoDB writer는 다음이다.

- `src/auth/session_repository.py`: `lovv_auth_sessions`용, `expiresAt`
- `src/auth/authz_cache_repository.py`: 루트 SAM 템플릿의 별도 `AdminAuthzCacheTable`용, `expiresAt`
- `src/shared/operational_events.py`: `lovv_user_event_logs`, `lovv_api_logs`용, `expires_at`
- `src/shared/async_jobs.py`: `lovv_async_jobs`용, `expires_at`
- `src/agentcore/run_repository.py`: `lovv_agent_runs`용, `expires_at`
- `src/agentcore/festival_cache_repository.py`: `lovv_festival_verify_cache`용, `expires_at`

`AdminAuthzCacheTable`은 루트 `template.yaml:403-418`에서 정의되는 별도 캐시 테이블이다. `src/auth/authz_cache_repository.py:52-61`, `src/auth/authz_cache_repository.py:109-119`에 실제 `expiresAt` writer가 있다. 그러나 이 테이블은 사용자가 제시한 6개 Data Stack 테이블에 포함되지 않는다.

추가 구현 이후 `USER_EVENT_LOGS_TABLE_NAME`, `AGENT_RUNS_TABLE_NAME`, `FESTIVAL_VERIFY_CACHE_TABLE_NAME`, `ASYNC_JOBS_TABLE_NAME`, `API_LOGS_TABLE_NAME`은 writer 모듈에서 사용된다. 단, 루트 `template.yaml`에는 아직 해당 환경변수/IAM 배선이 없다. 이는 writer는 준비됐지만 Lambda runtime 연결은 남았다는 판단을 뒷받침한다.

## 문서/스펙 상태

`docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md`는 이미 현재 상태를 정확히 전제로 잡고 있다.

- `auth_sessions`는 `expiresAt` 정수 epoch writer가 있어 TTL이 끝까지 동작한다고 명시한다: `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md:12-17`
- 나머지 5개는 TTL 설정은 있으나 애플리케이션 writer가 없다고 명시한다: `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md:14-15`
- 신규 writer가 사용할 `expires_at` 계약과 테이블별 키 포맷을 정의한다: `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md:36-60`
- 실제 제품 기능이 범위에 들어올 때만 테이블별 라이터/IAM을 추가하라고 정리되어 있다: `docs/specs/DYNAMODB_TTL_WRITE_PATHS_SPEC.md:176-179`

즉, 스펙의 M1/M2/M3 라이브러리 구현은 반영됐고, M4 인프라 배선과 실제 제품 호출 연결이 남아 있다.

## 권장 다음 작업

1. 실제 제품 쓰기 흐름에 writer를 연결한다.
   - `user_event_logs`, `api_logs`: 공통 요청 처리/운영 이벤트 기록 위치를 확정한다.
   - `agent_runs`, `festival_verify_cache`: `AgentCoreFunction` 내부 어느 단계에서 기록할지 확정한다.
   - `async_jobs`: 비동기 작업 생성/상태 변경 owner를 확정한다.

2. 라이터를 추가한 Lambda 함수에만 환경변수와 IAM을 최소 권한으로 배선한다.
   - Data Stack SSM parameter를 사용해 테이블명을 주입한다.
   - `PutItem`, `UpdateItem`, `GetItem`, `Query`는 실제 필요한 작업에만 부여한다.

3. 검증 기준을 명확히 둔다.
   - 인프라: CloudFormation template validation.
   - 앱: writer 단위 테스트에서 TTL 속성명, 타입, epoch seconds 계산값 확인.
   - 운영: 쓰기 발생 후 `TimeToLiveDeletedItemCount`는 보조 지표로만 본다. TTL 속성 누락 item은 삭제가 발생하지 않으므로 앱 측 테스트/메트릭이 더 중요하다.
