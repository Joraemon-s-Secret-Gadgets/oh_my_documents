# 11. 금지 사항

- 대화 로그 전문을 장기 저장하지 않는다.
- Supervisor에 전체 대화 로그, 웹 검색 원문, RAG 원문을 전달하지 않는다.
- Memory와 log에 raw RAG result, raw web content, full `candidate_evidence_package`, embedding cache, secret, PII를 저장하지 않는다.
- WeatherAPI 실시간 예보를 추천 후보 스코어링 기준으로 사용하지 않는다.
- 출처 없는 장소 정보를 확정 사실처럼 제시하지 않는다.
- 검증되지 않은 축제 날짜를 확정 일정처럼 제시하지 않는다.
- 한국 요청에 일본 목적지를 섞거나, 일본 요청에 한국 목적지를 섞지 않는다.
- 숙소를 직접 추천하지 않고 검색 링크만 제공한다.
- 검증 실패 결과를 최종 추천으로 반환하지 않는다.
