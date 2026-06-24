# 6. PoC 적용 범위와 Production 전환

| 단계 | 적용 범위 |
| --- | --- |
| PoC | 정적 데이터, 로컬 스토리지 기반 사용자 일정·반응, 최소 MySQL 테이블 또는 샘플 DB, S3 vector 기능 기반 검색 실험 |
| Production 1차 | 계정 기반 MySQL 사용자 원장, 소셜 계정, 저장 일정, 일정 항목, 일정 반응 |
| Production 운영 | DynamoDB Agent trace, async job, 사용자 이벤트 로그, API 로그, 운영 검수 로그, TTL 정책(5.1절), CloudWatch 기반 운영 대시보드·AWS Budgets 예산 알람 |
| Production 고도화 | 개인화 랭킹 재학습, A/B 테스트 이벤트, S3 vector 재색인 자동화, 3-hop 이상 관계 탐색 병목 확인 시 Neptune 승격 검토 |
