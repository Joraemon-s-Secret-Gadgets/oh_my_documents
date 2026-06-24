# 3. Agent 입력

| 입력 | 출처 | 설명 | 필수 여부 |
| --- | --- | --- | --- |
| `session_id` | 시스템 | 세션 구분 식별자 | 필수 |
| `onboardingProfile` | 저장 데이터 | 장기 선호 테마와 여행 성향 | 필수 |
| `feedbackHistory` | 저장 데이터 | 좋아요/싫어요, 저장, 재추천 이력 | 선택 |
| `naturalLanguageQuery` | 챗봇/UI | 현재 턴 자연어 요청 | 선택 |
| `entryType` | UI | `chatbot`, `map_marker` 등 진입 방식 | 필수 |
| `country` | UI/챗봇 | `KR` 또는 `JP` | 필수 |
| `travelMonth` | UI/챗봇 | 여행 월, 1~12 | 필수 |
| `travelYear` | UI/시스템 | 축제 개최일 검증 기준 연도 | 선택 |
| `destinationId` | 지도 | 지도 마커 진입 시 고정 목적지 | 선택 |
| `themes` | UI/챗봇 | 현재 요청에서 명시 선택한 테마 코드 배열 | 선택 |
| `tripType` | UI/챗봇 | `daytrip`, `2d1n`, `3d2n` 등 일정 유형 | 필수 |
| `includeFestivals` | UI/챗봇 | 축제·행사 포함 여부 | 필수 |
| `userLocation` | UI 권한 | API 입력 기준 거리 기반 1차 필터의 기준 좌표. Intent adapter에서 내부 `user_location`으로 정규화할 수 있음 | 선택 |
