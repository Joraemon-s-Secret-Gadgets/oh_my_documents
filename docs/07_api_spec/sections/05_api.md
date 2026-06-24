# 5. 지도·목적지 API

| Method | Path | Auth | 담당 Lambda | 설명 |
| --- | --- | --- | --- | --- |
| GET | `/destinations` | Public | `Map-Function` | 소도시 목록 조회 |
| GET | `/destinations/{destinationId}` | Public | `Map-Function` | 소도시 상세 조회 |
| GET | `/destinations/map-markers` | Public | `Map-Function` | 지도 마커 조회 |

## 5.1 `GET /destinations/map-markers`

**Query**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| country | string | No | `KR`, `JP` |
| month | number | No | 1~12 |
| theme | string | No | 테마 코드 |

**Response 200**

```json
{
  "items": [
    {
      "destinationId": "uuid",
      "name": "가나자와",
      "country": "JP",
      "latitude": 36.5613,
      "longitude": 136.6562,
      "themes": ["art_sense", "history_tradition"],
      "recommendedMonths": [4, 5, 10, 11]
    }
  ]
}
```

## 5.2 `GET /destinations/{destinationId}`

마커 클릭 시 해당 소도시의 상세 콘텐츠를 조회한다. API path의 `destinationId`는 DB 구현에서 `city_id`와 매핑될 수 있다.

**Response 200**

```json
{
  "destinationId": "uuid",
  "name": "가나자와",
  "country": "JP",
  "latitude": 36.5613,
  "longitude": 136.6562,
  "summary": "전통 거리와 현대 미술관을 함께 즐길 수 있는 일본 소도시입니다.",
  "themes": ["art_sense", "history_tradition"],
  "contents": [
    {
      "contentId": "uuid",
      "title": "히가시차야 거리",
      "contentType": "attraction",
      "sourceUrl": "https://example.official.jp"
    }
  ]
}
```
