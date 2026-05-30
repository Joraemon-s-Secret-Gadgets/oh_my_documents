# 로브 (Lovv) API 명세서

> 문서 버전: v0.1
> 문서 상태: 기획 단계 (Planning)
> 기준 문서: `docs/01_requirements/01_requirements.md` v1.5

# 1. 문서 개요

## 1.1 목적

본 문서는 로브 서비스의 프론트엔드, 백엔드, 추천 Agent, 운영 화면이 사용하는 API 계약을 정의한다.
엔드포인트는 Production 기준의 목표 계약이며, PoC에서는 일부를 정적 데이터 또는 로컬 스토리지로 대체할 수 있다.

## 1.2 공통 규칙

| 항목 | 규칙 |
| --- | --- |
| Base URL | `/api/v1` |
| Content-Type | `application/json; charset=utf-8` |
| 인증 | 공개 추천 조회는 선택, 운영·저장·마이페이지는 로그인 필요 |
| 날짜 형식 | ISO 8601 |
| ID 형식 | UUID 권장 |

# 2. 공통 오류 응답

| HTTP Status | Code | 의미 |
| --- | --- | --- |
| 400 | BAD_REQUEST | 요청 형식 오류 |
| 401 | UNAUTHENTICATED | 인증 필요 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | NOT_FOUND | 리소스 없음 |
| 409 | CONFLICT | 중복 또는 상태 충돌 |
| 422 | VALIDATION_ERROR | 의미상 유효하지 않은 요청 |
| 500 | INTERNAL_ERROR | 서버 오류 |

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "여행 월은 1부터 12 사이여야 합니다.",
    "details": {
      "field": "travelMonth"
    }
  }
}
```

# 3. 인증 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| POST | `/auth/login` | Public | 이메일/소셜 로그인 |
| POST | `/auth/logout` | User | 로그아웃 |
| GET | `/auth/me` | User | 현재 사용자와 역할 조회 |

## 3.1 `GET /auth/me`

**Response 200**

```json
{
  "userId": "uuid",
  "displayName": "홍길동",
  "roles": ["R-USER"]
}
```

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

# 5. 지도·목적지 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/destinations` | Public | 소도시 목록 조회 |
| GET | `/destinations/{destinationId}` | Public | 소도시 상세 조회 |
| GET | `/destinations/map-markers` | Public | 지도 마커 조회 |

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

# 6. 추천 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| POST | `/recommendations` | Optional | 추천 생성 |
| GET | `/recommendations/{recommendationId}` | Optional | 추천 결과 조회 |
| POST | `/recommendations/{recommendationId}/alternatives/weather` | Optional | 기상 악화 대체 일정 조회 |

## 6.1 `POST /recommendations`

**Request**

```json
{
  "entryType": "map_marker",
  "country": "JP",
  "travelMonth": 10,
  "destinationId": "uuid",
  "themes": ["art_sense"],
  "tripType": "2d1n",
  "includeFestivals": true,
  "naturalLanguageQuery": "가을에 감성적인 일본 소도시 추천해줘"
}
```

**Response 201**

```json
{
  "recommendationId": "uuid",
  "destination": {
    "destinationId": "uuid",
    "name": "가나자와",
    "country": "JP"
  },
  "itinerary": {
    "tripType": "2d1n",
    "days": [
      {
        "day": 1,
        "items": [
          {
            "timeOfDay": "morning",
            "title": "히가시차야 거리 산책",
            "reason": "도보 이동이 쉽고 예술·감성 선호와 맞습니다."
          }
        ]
      }
    ]
  },
  "explainability": {
    "matchedConditions": ["art_sense", "travelMonth:10"],
    "summary": "가을 계절 적합도와 예술·감성 선호가 높아 추천합니다."
  },
  "links": {
    "map": "https://maps.google.com/...",
    "staySearch": "https://..."
  }
}
```

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

# 8. 외부 정보 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/external/weather/current` | Public | 목적지 현재 날씨 표시 |
| GET | `/external/stay-links` | Public | 숙소 검색 링크 생성 |
| GET | `/external/search-links` | Public | Kakao/Yahoo/Google 탐색 링크 생성 |

WeatherAPI 응답은 추천 스코어링에 사용하지 않고 목적지 상세 표시용으로만 사용한다.

# 9. 운영·검토 API

| Method | Path | Auth | 설명 |
| --- | --- | --- | --- |
| GET | `/admin/data-submissions` | Admin/Operator | 데이터 제안 목록 |
| POST | `/admin/data-submissions` | Operator/DataProvider | 데이터 제안 등록 |
| PATCH | `/admin/data-submissions/{submissionId}/review` | Admin | 승인, 반려, 수정 요청 |
| GET | `/admin/audit-logs` | Admin | 검토·승인 이력 조회 |

# 10. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-05-29 | 로브 기획팀 | API 명세서 초안 작성 |

