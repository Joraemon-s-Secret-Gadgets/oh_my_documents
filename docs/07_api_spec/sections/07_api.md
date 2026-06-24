# 7. 저장·피드백 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/me/itineraries` | User | 저장 일정 목록 |
| POST | `/me/itineraries` | User | 추천 일정 저장 |
| DELETE | `/me/itineraries/{itineraryId}` | User | 저장 일정 삭제 |
| POST | `/me/feedback` | User | 좋아요/싫어요 저장 |

## 7.1 `POST /me/feedback`

**Request**

```json
{
  "recommendationId": "uuid",
  "destinationId": "uuid",
  "feedbackType": "like",
  "themeTags": ["art_sense", "history_tradition"]
}
```

**Response 201**

```json
{
  "feedbackId": "uuid",
  "createdAt": "2026-05-29T09:00:00Z"
}
```
