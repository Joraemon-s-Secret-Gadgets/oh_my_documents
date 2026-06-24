# 4. 온보딩·선호 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/me/preferences` | User | 선호 프로필 조회 |
| PUT | `/me/preferences` | User | 온보딩 응답 저장 또는 재설정 |
| GET | `/themes/onboarding-options` | Public | 대도시 스타일 선택지 조회 |

## 4.1 `PUT /me/preferences`

**Request**

```json
{
  "countryTrack": "KR",
  "selectedCityStyle": "GYEONGJU",
  "mappedThemes": ["history_tradition"]
}
```

**Response 200**

```json
{
  "preferenceId": "uuid",
  "mappedThemes": ["history_tradition"],
  "updatedAt": "2026-05-29T09:00:00Z"
}
```
