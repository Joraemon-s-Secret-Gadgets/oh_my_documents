# 8. 후속 작업

1. `infra/data-stack/rds/schema.sql`의 `users`, `social_accounts`, `user_preferences`, `itineraries`, `itinerary_items`, `plan_reactions`와 API 문서의 필드 매핑을 계속 동기화한다.
2. DynamoDB `lovv_user_event_logs`, `lovv_agent_runs`, `lovv_async_jobs`, `lovv_api_logs`의 TTL 기간을 확정한다. (5.1절에 권고·잠정값 반영 완료, 법무·보안 검토로 최종 확정 예정)
3. API 명세의 `/me/itineraries`, `/me/itineraries/{itineraryId}`, `/me/itineraries/{itineraryId}/reactions` 응답 필드와 테이블 컬럼을 1:1로 매핑한다.
4. S3 vector index의 prefix, vector ID, metadata filter, 재색인 배치 기준을 기술 명세와 맞추고, `visitor_statistics`는 vector 제외·DynamoDB 조회 기준을 유지한다.
5. Lambda 관계 탐색 보조 기능의 `City`, `Festival`, `Theme`, `Place` 관계 ID와 인접 리스트 생성 기준을 기술 명세와 맞춘다.
6. 구현 체크리스트를 기준으로 개발 완료 항목을 점검하고 미구현 항목을 백로그에 등록한다.
7. BE 저장소의 `schema/aurora_mysql/002_admin_console_tables.sql`에 고위험 승인·MFA 테이블 중복 정의가 없는지 확인하고, `scripts/apply_admin_migration.py`의 선택 적용 사용법을 운영 문서와 맞춘다.
8. `lovv-pipeline-images-dev-925273580929` public access block live 값이 Terraform 정의와 다른 원인을 확인하고 적용 또는 예외 사유를 남긴다.
