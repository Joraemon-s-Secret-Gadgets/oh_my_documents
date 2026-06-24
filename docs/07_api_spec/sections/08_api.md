# 8. 외부 정보 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/external/weather/current` | Public | 목적지 현재 날씨 표시 |
| GET | `/external/stay-links` | Public | 숙소 검색 링크 생성 |
| GET | `/external/search-links` | Public | Kakao/Yahoo/Google 탐색 링크 생성 |

WeatherAPI 응답은 추천 스코어링에 사용하지 않고 목적지 상세 표시용으로만 사용한다.
