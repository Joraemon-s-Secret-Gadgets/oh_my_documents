# 10. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.8 | 2026-07-02 | Codex | 관리자 MFA 범위를 고위험 승인·거절 시점으로 정정하고 pending 목록 조회, TOTP 별도 검증, 복구 코드 승인 불가, limit 50 clamp 계약 반영 |
| v0.7 | 2026-06-30 | Codex | `R-SUPER-ADMIN` 역할 enum, 고위험 변경 생성·조회·승인·거절 API, 최근 TOTP·자기 결정 금지·오류 코드와 C4 감사 로그 조회 계약 추가 |
| v0.6 | 2026-06-30 | Codex | 관리자 Step-up MFA 상태·등록·확인·인증·복구 API와 오류 코드 추가 |
| v0.5 | 2026-06-30 | Codex | 관리자 운영 API 인가 규칙, 자기검토 금지 오류 코드, `/admin/*` 오류 코드 교차참조 반영 |
| v0.4 | 2026-06-22 | 로브 기획팀 | 대화형 빌더 API placeholder 반영: 반경 후보 조회, 후보 선택·일정 추가, 서브 윈도우 플래그, 빌더 상태 재개 계약 후보 기록 |
| v0.3 | 2026-06-12 | 로브 기획팀 | Cognito bridge 인증 흐름 추가, Google/Kakao 직접 검증 API legacy 처리, role enum과 logout 책임 경계 반영 |
| v0.2 | 2026-06-08 | 로브 기획팀 | AWS SAM 기반 Auth, Map, AgentCore Lambda별 API 라우팅과 Google/Kakao 인증, 세션, 지도 상세, 저장 없는 Agent 답변 API 추가 |
| v0.1 | 2026-05-29 | 로브 기획팀 | API 명세서 초안 작성 |
