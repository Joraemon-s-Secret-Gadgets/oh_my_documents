# 5. 보존 정책 및 권한

| 데이터 | 보존 정책 | 사용자 통제 |
| --- | --- | --- |
| 사용자 계정 | 탈퇴 시 soft delete 후 보존 기간 종료 시 익명화 | 탈퇴 가능 |
| 저장 조건 스냅샷 | 일정 저장 시 `preference_snapshot`에 보존 | 일정 삭제 시 함께 삭제 |
| 저장 일정 | 사용자가 삭제하면 관련 `itinerary_items`, `plan_reactions`와 함께 삭제 | 조회·삭제 가능 |
| 일정 반응 | 개인화에 활용하되 삭제 요청 시 제외 | 조회·삭제 가능 |
| 대화 전문 | 장기 저장하지 않음 | 저장 대상 아님 |
| Agent trace | DynamoDB TTL 기반 단기 보존 | 원문 개인정보 저장 금지 |
| API/이벤트 로그 | DynamoDB TTL 기반 단기 보존 | 해시·마스킹 저장 |
| S3 vector record | 원본 재색인 가능성을 기준으로 운영 보존 | 사용자 개인정보와 대화 전문 저장 금지 |
| Lambda 관계 탐색 캐시 | 원본 재생성 가능성을 기준으로 운영 보존 | 공용 콘텐츠 관계만 저장 |

## 5.1 보존 기간 및 TTL (권고·잠정)

아래 기간은 운영 관행 기준 **권고·잠정값(신뢰도 중)**이며, 법무·보안·개인정보 검토로 확정한다.
`expires_at`은 레코드 생성 시각 + 보존 기간으로 계산해 저장한다. 세부 근거는
`supplemental/database_design_retention_neptune_update.md`를 따른다.

| 대상 | 권고·잠정 보존 기간(TTL) | 비고 |
| --- | --- | --- |
| `lovv_user_event_logs` | 90일 | 분석·퍼널 집계 기준 |
| `lovv_agent_runs` | 30일 | 장애 분석용 단기 trace |
| `lovv_async_jobs` | 14일 | 완료/실패 확인 후 단기 |
| `lovv_api_logs` | 30일 (장기 필요 시 S3 아카이브) | 운영/보안 추적 |
| `lovv_festival_verify_cache` | 상태별 TTL: `confirmed` 30일, `tentative` 7일, `unknown·outdated` 1일 | 기존 확정값 |
| `lovv_content_documents`, `lovv_visitor_statistics` | TTL 없음 | S3 Raw 기준 재생성 |
| 사용자 계정 | 탈퇴 후 30일 유예 → 익명화 | 분쟁/오삭제 대비, 법무 확인 필요 |
| S3 Raw 수집 원본 | 운영 보존(기본 365일 후 재검토) | 재색인·재생성 기준 |
| S3 vector / 관계 탐색 캐시 | TTL 없음 | 원본 재생성 기준 운영 보존 |
