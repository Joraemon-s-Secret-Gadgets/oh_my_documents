# 2. 시스템 개요

| 계층 | 책임 |
| --- | --- |
| Client Web | 온보딩, 지도, 챗봇 UI, 추천 결과, 마이페이지, 로컬 스토리지 |
| Backend API | 인증·인가, 데이터 조회, 추천 요청, 저장/피드백, 운영 데이터 검토 |
| Recommendation Agent | 조건 분류, 후보 검색, 후보 선정, 일정 구성, 추천 이유 생성 |
| Data Store | 목적지, 축제, 월별 기상 경향, 사용자 저장 데이터, 운영 검토 이력 |
| External APIs | Google Maps, Kakao Maps, Yahoo Japan 딥링크, WeatherAPI 표시용 데이터 |
