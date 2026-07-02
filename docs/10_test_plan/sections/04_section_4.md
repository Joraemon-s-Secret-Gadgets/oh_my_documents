# 4. 공통 검증 원칙

- 테스트 범위는 요구사항 ID, Agent 입출력, API 계약, 데이터 모델과 연결한다.
- 부분 평가 문서는 전체 시스템 합격으로 해석하지 않는다.
- 실행 결과는 통과·실패 수치뿐 아니라 범위, 제외 항목, 해석 한계를 함께 기록한다.
- LLM judge나 합성 fixture를 사용하는 경우 실제 사용자 검증을 대체하지 않는다고 명시한다.
- 성능, 비용, observability 항목은 기술 명세서와 배포·운영 문서의 기준을 따른다.
- 관리자 보안 테스트는 role 인증, MFA 세션, 고위험 승인 트랜잭션, 감사 로그를 분리해 기록한다. 일반 admin 읽기·목록 경로는 MFA 없이 role 인증만 요구하는지 별도 확인한다.
- opt-in 실DB 통합 테스트는 일반 unittest와 구분한다. `RUN_ADMIN_DB_INTEGRATION=1` 또는 `RUN_RDS_DATA_API_INTEGRATION=1`을 켜지 않았다면 실행 완료로 기록하지 않는다.

## 4.1 관리자 MFA·고위험 승인 검증 명령

BE 일반 테스트:

```powershell
$env:PYTHONPATH='src'
python -m unittest
```

BE 고위험/MFA 핵심 테스트:

```powershell
python -m unittest tests.test_admin_high_risk_app
python -m unittest tests.test_admin_mfa_app.AdminMfaAppTest.test_admin_read_routes_need_role_only_and_mfa_status_is_accessible
```

admin_web 검증:

```powershell
npm.cmd run lint
npm.cmd test
npm.cmd run build
```

opt-in 실DB 통합 테스트:

```powershell
$env:RUN_ADMIN_DB_INTEGRATION='1'
$env:RUN_RDS_DATA_API_INTEGRATION='1'
python -m unittest
```

위 opt-in 테스트는 실제 DB 연결·자격 증명·격리된 테스트 데이터가 준비된 경우에만 실행한다. 문서 작업 또는 일반 unittest 실행만으로는 완료 처리하지 않는다.
