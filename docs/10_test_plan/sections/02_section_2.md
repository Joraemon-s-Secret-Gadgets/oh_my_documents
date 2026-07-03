# 2. 테스트 범위

| 구분 | 현재 문서화 상태 | 대표 문서 반영 기준 |
| --- | --- | --- |
| Candidate Evidence 검색 | 계획·결과 문서화 완료 | 현재 문서의 3장에 요약 |
| Planner 일정 생성 | 후속 작성 필요 | `05_agent_spec.md`, `planner_agent.md`, `itinerary_flow.md` 기준으로 테스트 계획 작성 |
| Festival Verifier | 후속 작성 필요 | `festival_verifier_agent.md` 기준으로 날짜·출처 검증 테스트 작성 |
| API E2E | 후속 작성 필요 | `07_api_spec.md` 기준으로 인증, 추천, 저장, 피드백, 운영 API 시나리오 작성 |
| UI/UX 수용 테스트 | 후속 작성 필요 | `09_ui_ux_guide.md` 기준으로 주요 사용자 여정 검증 |
| 배포·운영 검증 | 후속 작성 필요 | `11_deployment_ops.md` 기준으로 배포, 롤백, 모니터링, 장애 대응 검증 |
| 관리자 MFA·고위험 승인 | 명령·범위 문서화 완료, 실행 결과는 별도 기록 필요 | `01_requirements.md`, `07_api_spec.md`, `11_deployment_ops.md` 기준으로 role-only admin read, decision-time TOTP, recovery code 승인 불가, 2인 승인 검증 |
