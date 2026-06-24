# 12. 관련 요구사항 및 API 영향

| 영역 | 관련 요구사항 | 관련 API |
| --- | --- | --- |
| 인증/세션 | 역할 모델, Production 회원가입 기반 저장 | `/auth/login`, `/auth/logout`, `/auth/me` |
| 온보딩/선호 | `FR-ONBOARD-001`, `FR-STORE-001` | `/me/preferences`, `/themes/onboarding-options` |
| 목적지 탐색 | `FR-COM-001`, `FR-REC-001`, `FR-REC-002` | `/destinations`, `/destinations/map-markers` |
| 추천 생성 | `FR-COM-005`, `FR-REC-003`, `FR-REC-004` | `/recommendations`, `/recommendations/{recommendationId}` |
| 대체 일정 | 월별 기상 경향, 대체 일정 데이터 | `/recommendations/{recommendationId}/alternatives/weather` |
| 저장/피드백 | `FR-STORE-001`, `FR-STORE-002`, `FR-STORE-003` | `/me/itineraries`, `/me/feedback` |
| 외부 연동 | 지도·숙소·현지 플랫폼 딥링크 | `/external/weather/current`, `/external/stay-links`, `/external/search-links` |
| 운영 검토 | 역할 기반 운영, 데이터 품질·출처 추적성 | `/admin/data-submissions`, `/admin/audit-logs` |
