# 7. 구현 체크리스트

- [ ] MySQL에 `users`, `social_accounts`, `itineraries`, `itinerary_items`, `plan_reactions` 테이블을 생성했는가?
- [ ] 마이페이지 저장 일정 조회·삭제 API가 MySQL 원장 테이블 기준으로 동작하는가?
- [ ] 일정 반응 저장·집계 로직이 `plan_reactions`와 API 응답 필드에 연결되어 있는가?
- [ ] DynamoDB 이벤트·trace 테이블에 `expires_at` TTL과 해시 저장 로직을 적용했는가?
- [ ] 사용자 대화 전문, 민감 자유 입력, 비공개 운영 메모가 장기 저장소에 남지 않도록 차단했는가?
- [ ] S3 vector index 재색인 배치가 DynamoDB 정규화 문서와 S3 Raw 원본 기준으로 재생성되는가?
- [ ] Lambda 관계 탐색 보조 기능이 공용 콘텐츠 관계만 읽고 사용자 개인정보를 캐시하지 않는가?
- [ ] PoC 로컬 스토리지 대체 코드와 Production DB 연동 코드의 전환 지점을 분리했는가?
