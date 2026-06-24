# 7. 보안 및 개인정보

| 항목 | 정책 |
| --- | --- |
| 대화 로그 | 전문 저장 금지 |
| 일정·선호·피드백 | PoC 로컬, Production 계정 기반 저장 |
| API Key | 서버 환경 변수 또는 프록시에서 관리 |
| 운영 기능 | 역할 기반 인증·인가 필수 |
| 외부 응답 | 스키마 검증 후 사용 |
| Agent 권한 | AgentCore Identity 또는 동등한 권한 경계로 Memory, Gateway Skill, Browser, Knowledge Base 접근 범위를 분리 |
| Agent 정책 | 국가 혼합 금지, 미검증 축제 일정 배치 금지, 대화 원문 trace 금지를 Policy/Validation Skill로 강제 |
