# 5. 후속 작성 항목

| 우선순위 | 항목 | 기준 문서 |
| --- | --- | --- |
| P1 | Planner 일정 생성 테스트 계획 | `../05_agent_spec/supplemental/planner_agent.md`, `../05_agent_spec/supplemental/itinerary_flow.md` |
| P1 | API 추천·저장 E2E 테스트 계획 | `../07_api_spec/07_api_spec.md` |
| P2 | Festival Verifier 날짜·출처 검증 테스트 | `../05_agent_spec/supplemental/festival_verifier_agent.md` |
| P2 | UI 주요 여정 수용 테스트 | `../09_ui_ux_guide/09_ui_ux_guide.md` |
| P3 | 배포·운영 smoke 및 rollback 테스트 | `../11_deployment_ops/11_deployment_ops.md` |
| P1 | admin_web `권한 승인` 탭 수용 테스트 | pending eager loading, `50+` badge, `R-ADMIN` 승인 버튼 비노출, `R-SUPER-ADMIN` decision-time MFA 모달 |
| P1 | 관리자 DB migration smoke | `infra/data-stack/rds/schema.sql` 후 admin migration 002→003→004 적용, 001 삭제 유지, 004의 MFA·고위험 테이블 단일 정의 확인 |
