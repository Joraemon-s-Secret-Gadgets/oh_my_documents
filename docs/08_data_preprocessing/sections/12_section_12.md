# 12. 산출물

| 산출물 | 설명 |
| --- | --- |
| `city_normalized` | 국가별 도시 표준 엔티티 |
| `attraction_normalized` | City와 연결된 관광지 표준 엔티티 |
| `festival_normalized` | City와 연결된 축제 표준 엔티티 |
| `visitor_statistics_normalized` | City와 연결된 방문·관광 통계 보조 지표 |
| `data_quality_report` | 누락, 충돌, 최신성, 저작권 위험 리포트 |
| `review_queue` | 수동 검수 대상 목록 |
| `rag_documents` | 추천 Agent와 검색용 내부 요약 문서 |
| `feature_dataset` | 테마, 계절성, 혼잡도, 일정 적합도 파생 필드 |
| `s3_raw_manifest` | DynamoDB Item과 연결되는 S3 Raw 객체 목록 |
| `lambda_processing_log` | Lambda 실행 결과, 실패 사유, 재처리 대상 기록 |
| `s3_vector_index_manifest` | S3 vector index 버전, chunk 수, vector 수, 원천 DynamoDB/S3 Raw 참조 |
