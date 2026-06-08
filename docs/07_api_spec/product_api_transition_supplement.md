# 로브 (Lovv) Product API 전환 보강 명세서

> 문서 버전: v0.1
> 문서 상태: 기획 단계 (Planning)
> 기준 문서: API 명세서 v0.2, 기술 명세서 v0.3, 프론트엔드 PoC 구현 흐름
> 대표 문서: [07_api_spec.md](./07_api_spec.md)

# 1. 문서 개요

## 1.1 목적

본 문서는 현재 PoC 프론트엔드 흐름을 Product API 계약으로 전환할 때 필요한 API 명세 요약과 보강점을 정리한다.
대표 API 계약 문서인 `07_api_spec.md`를 대체하지 않고, Product 전환 전에 대표 문서에 반영할 보강 후보와 적용 순서를 정의한다.

## 1.2 문서 성격

| 항목 | 내용 |
| --- | --- |
| 문서 유형 | API 명세 보조 문서 |
| 적용 범위 | 온보딩, 지도, 추천 Agent, 저장 일정, 마이페이지 API 보강 후보 |
| 비적용 범위 | 실제 백엔드 구현 코드, DB 마이그레이션, 외부 API 과금 정책 |
| 반영 기준 | 사용자 흐름과 PoC 프론트엔드 상태를 Product API 계약으로 전환할 때 필요한 필드와 endpoint 정합성 |

# 2. 전제

현재 PoC 프론트엔드는 API 호출 없이 정적 데이터와 localStorage 중심으로 구현한다. Product 단계에서는 백엔드 API 명세가 Source of Truth가 되어야 하며, 프론트엔드는 백엔드 enum, response field, error format에 맞춘 adapter layer로 이동한다.

즉, Product 전환 시 프론트의 임시 테마 코드, 소도시 더미 데이터, 추천 결과 더미 구조를 유지하지 않는다. 백엔드가 제공하는 `themeId`, `destinationId`, `contentId`, `itineraryId`, 추천 응답 구조를 기준으로 프론트 상태를 재매핑한다.

# 3. 기존 API 명세 요약

## 3.1 공통 규칙

- Base URL은 `/api/v1`.
- Content-Type은 `application/json; charset=utf-8`.
- 공개 추천 조회는 선택 인증, 운영·저장·마이페이지는 로그인 필요.
- 날짜는 ISO 8601, ID는 UUID 권장.
- 공통 오류 응답은 `error.code`, `error.message`, `error.details` 구조를 사용한다.

## 3.2 Lambda 라우팅

- `Auth-Function`: `/auth/*`, 로그인, JWT 발급·검증, 세션 요약 조회.
- `Map-Function`: `/destinations/*`, 지도 마커, 소도시 상세, DB/S3 기반 읽기 API.
- `AgentCore-Function`: `/recommendations`, `/agent/answer`, LLM 호출과 추천 설명 생성.

## 3.3 인증 API

- `POST /auth/google`
- `POST /auth/kakao`
- `POST /auth/logout`
- `GET /auth/me`
- `GET /auth/session`

`GET /auth/session`은 로그인 직후 사용자 정보, 저장 테마, 저장 일정 요약을 한 번에 반환한다.

## 3.4 온보딩·선호 API

- `GET /me/preferences`
- `PUT /me/preferences`
- `GET /themes/onboarding-options`

현재 `PUT /me/preferences`는 `countryTrack`, `selectedCityStyle`, `mappedThemes` 저장을 기준으로 한다.

## 3.5 지도·목적지 API

- `GET /destinations`
- `GET /destinations/{destinationId}`
- `GET /destinations/map-markers`

현재 지도 마커 조회는 `country`, `month`, `theme` query를 지원한다. 목적지 상세는 `destinationId`, `name`, `country`, `latitude`, `longitude`, `summary`, `themes`, `contents` 중심이다.

## 3.6 추천·Agent API

- `POST /recommendations`
- `GET /recommendations/{recommendationId}`
- `POST /recommendations/{recommendationId}/alternatives/weather`
- `POST /agent/answer`

`POST /recommendations`는 `entryType`, `country`, `travelMonth`, `destinationId`, `themes`, `tripType`, `includeFestivals`, `naturalLanguageQuery`, `user_location`을 받아 추천 일정과 추천 근거를 반환한다.

`POST /agent/answer`는 대화 원문 저장 없는 단일 턴 AI 답변 생성 API다.

## 3.7 저장·피드백 API

- `GET /me/itineraries`
- `POST /me/itineraries`
- `DELETE /me/itineraries/{itineraryId}`
- `POST /me/feedback`

현재 저장 API는 일정 목록, 일정 저장, 일정 삭제, 좋아요/싫어요 저장을 커버한다.

## 3.8 외부 정보·운영 API

- `GET /external/weather/current`
- `GET /external/stay-links`
- `GET /external/search-links`
- `GET /admin/data-submissions`
- `POST /admin/data-submissions`
- `PATCH /admin/data-submissions/{submissionId}/review`
- `GET /admin/audit-logs`

WeatherAPI 응답은 추천 스코어링이 아니라 목적지 상세 표시용으로만 사용한다.

# 4. Product 전환 시 유지 가능한 부분

현재 API 명세는 PoC 프론트엔드의 핵심 흐름을 대부분 커버한다.

- 로그인 후 세션 복원과 마이페이지 진입은 `GET /auth/session`, `GET /auth/me`로 연결 가능하다.
- 온보딩 테마 선택과 재설정은 `GET /themes/onboarding-options`, `PUT /me/preferences`로 연결 가능하다.
- 지도 마커와 소도시 상세 패널은 `GET /destinations/map-markers`, `GET /destinations/{destinationId}`로 연결 가능하다.
- 지도에서 소도시를 선택한 뒤 일정 생성은 `POST /recommendations`의 `entryType: "map_marker"`로 연결 가능하다.
- 챗봇 자연어 입력은 `POST /agent/answer` 또는 `POST /recommendations`의 `naturalLanguageQuery`로 연결 가능하다.
- 추천 결과 저장, 좋아요/싫어요는 `POST /me/itineraries`, `POST /me/feedback`로 연결 가능하다.
- 숙소 검색 링크는 추천 응답의 `links.staySearch` 또는 `GET /external/stay-links`로 연결 가능하다.

# 5. API 명세 보강 필요 항목

## 5.1 백엔드 기준 테마 enum 확정

Product 단계에서는 백엔드 테마 enum을 기준으로 프론트 온보딩, 지도 필터, 추천 요청, 피드백 저장을 모두 통일해야 한다.

현재 명세 예시는 `art_sense`, `history_tradition`, `healing` 등이 섞여 있고, PoC 프론트는 별도 임시 코드가 존재한다. Product 전환 전에 `GET /themes/onboarding-options`의 response가 canonical theme source가 되어야 한다.

### 보강 제안: `GET /themes/onboarding-options`

```json
{
  "items": [
    {
      "themeId": "healing_rest",
      "label": "온천·휴양",
      "shortLabel": "온천",
      "description": "숙소 체류, 온천, 스파처럼 회복감이 있는 장면을 먼저 봅니다.",
      "displayOrder": 1,
      "isActive": true,
      "sampleDestinations": [
        {
          "destinationId": "uuid",
          "name": "아산/온양",
          "country": "KR",
          "imageUrl": "https://..."
        }
      ]
    }
  ]
}
```

### 보강 규칙

- `themeId`는 온보딩, 지도, 추천, 피드백, 콘텐츠 태그에서 동일하게 사용한다.
- 선택 가능한 테마 수는 1~3개로 명시한다.
- Product 전환 시 프론트 PoC 코드는 백엔드 `themeId`로 migration mapping을 둔다.
- theme label 변경은 프론트 배포 없이 백엔드 데이터로 반영 가능해야 한다.

## 5.2 소도시 상세 API 필드 확장

현재 `GET /destinations/{destinationId}`는 상세 화면과 추천 전환에 필요한 최소 필드가 부족하다. 현재 UI와 Product 추천 흐름을 고려하면 소도시 상세는 지도 패널, 추천 근거, 일정 생성 seed를 모두 제공해야 한다.

### 보강 제안: `GET /destinations/{destinationId}`

```json
{
  "destinationId": "uuid",
  "name": "경주",
  "country": "KR",
  "region": "경상북도",
  "latitude": 35.8562,
  "longitude": 129.2247,
  "summary": "오래된 골목과 전통 산책 리듬이 잘 맞는 소도시입니다.",
  "description": "불국사, 첨성대, 황리단길을 중심으로 전통과 산책 동선을 구성할 수 있습니다.",
  "themes": ["history_tradition"],
  "recommendedMonths": [3, 4, 5, 9, 10, 11],
  "image": {
    "heroImageUrl": "https://...",
    "thumbnailImageUrl": "https://...",
    "gallery": [
      {
        "imageUrl": "https://...",
        "alt": "경주 야경",
        "sourceUrl": "https://..."
      }
    ]
  },
  "routeSeed": ["불국사", "첨성대", "황리단길"],
  "recommendationReasons": [
    "역사·전통 테마 장소가 충분합니다.",
    "대표 장소 간 이동 동선이 단순합니다."
  ],
  "festival": {
    "festivalAvailable": false,
    "festivalIds": []
  },
  "contents": [
    {
      "contentId": "uuid",
      "title": "불국사",
      "contentType": "attraction",
      "themeTags": ["history_tradition"],
      "latitude": 35.7901,
      "longitude": 129.3321,
      "estimatedDurationMinutes": 90,
      "openingHoursSummary": "09:00-18:00",
      "sourceUrl": "https://...",
      "verificationStatus": "verified"
    }
  ]
}
```

### 보강 규칙

- `contents[].themeTags`는 백엔드 canonical theme enum만 사용한다.
- 지도 마커에는 소도시 이름만 표시하고, 테마·장소·동선은 상세 패널과 일정 생성 단계에서 사용한다.
- `festival.festivalAvailable`이 false면 챗봇은 축제 포함 여부를 묻지 않는다.
- `routeSeed`는 지도에서 소도시 선택 후 자연어 입력 없이 일정 생성할 때 seed로 사용한다.

## 5.3 일정 드래그앤드랍 수정·저장 API 추가

현재 저장 API는 생성된 일정을 저장·조회·삭제하는 수준이다. Product에서 사용자가 아침/점심/저녁 카드 순서를 바꾸고 저장하려면 일정 수정 API가 필요하다.

### 보강 제안: `PATCH /me/itineraries/{itineraryId}`

```json
{
  "version": 3,
  "days": [
    {
      "day": 1,
      "items": [
        {
          "itemId": "uuid",
          "contentId": "uuid",
          "timeOfDay": "morning",
          "sortOrder": 1,
          "title": "불국사 산책",
          "memo": "오전 첫 일정으로 이동",
          "isLocked": false
        },
        {
          "itemId": "uuid",
          "contentId": "uuid",
          "timeOfDay": "lunch",
          "sortOrder": 2,
          "title": "황리단길 점심",
          "memo": "",
          "isLocked": false
        }
      ]
    }
  ],
  "editReason": "drag_and_drop_reorder"
}
```

### Response 200

```json
{
  "itineraryId": "uuid",
  "version": 4,
  "updatedAt": "2026-06-08T09:00:00Z",
  "days": [
    {
      "day": 1,
      "items": [
        {
          "itemId": "uuid",
          "contentId": "uuid",
          "timeOfDay": "morning",
          "sortOrder": 1,
          "title": "불국사 산책"
        }
      ]
    }
  ]
}
```

### 보강 규칙

- `version`으로 낙관적 동시성 제어를 한다.
- 충돌 시 `409 CONFLICT`와 최신 `version`을 반환한다.
- `timeOfDay` enum은 `morning`, `lunch`, `afternoon`, `dinner`, `evening`처럼 확정한다.
- drag-and-drop은 `sortOrder`와 `timeOfDay` 변경으로 저장한다.
- 기존 추천 근거는 유지하되, 사용자가 수정한 항목은 `userEdited: true`를 남길 수 있다.

## 5.4 지도 필터 고도화는 GPS 단계에서 확장

현재 PoC와 초기 Product는 `country`, `month`, `theme`만으로 충분하다. GPS 기반 추천과 지도 범위 검색이 들어갈 때 `GET /destinations/map-markers` query를 확장한다.

### 보강 제안: `GET /destinations/map-markers`

```http
GET /api/v1/destinations/map-markers?country=KR&theme=history_tradition&q=경주&region=GANGWON&bounds=37.1,127.0,38.5,129.4&userLatitude=37.5665&userLongitude=126.9780&radiusKm=250&limit=80&cursor=...
```

### 추가 query 후보

| 이름 | 타입 | 설명 |
| --- | --- | --- |
| `q` | string | 도시명 검색어 |
| `region` | string | 국가별 행정 권역 코드 |
| `bounds` | string | 지도 viewport 기반 SW/NE 좌표 |
| `userLatitude` | number | 사용자 위치 위도 |
| `userLongitude` | number | 사용자 위치 경도 |
| `radiusKm` | number | 사용자 위치 기준 반경 |
| `limit` | number | 반환 개수 |
| `cursor` | string | 다음 페이지 커서 |
| `themeMode` | string | `any` 또는 `all` |

### 보강 규칙

- GPS 권한이 없으면 위치 query는 생략 가능해야 한다.
- 지도 마커는 소도시 이름과 좌표 중심으로 유지한다.
- 장소·테마 상세는 마커가 아니라 상세 API에서 제공한다.

## 5.5 추천 API request/response 세부 정합성 보강

`POST /recommendations`는 현재 PoC의 두 흐름을 모두 커버해야 한다.

1. 지도 마커 선택 후 자연어 입력 없이 일정 생성
2. 챗봇에서 축제 여부, 여행 일수, 자연어 조건을 받은 뒤 일정 생성

### 보강 제안: Request

```json
{
  "entryType": "map_marker",
  "destinationId": "uuid",
  "country": "KR",
  "travelYear": 2026,
  "travelMonth": 10,
  "tripType": "2d1n",
  "themes": ["history_tradition", "food_local"],
  "includeFestivals": false,
  "naturalLanguageQuery": null,
  "userLocation": null
}
```

### 보강 규칙

- `entryType` enum은 `map_marker`, `chat`, `home_recommendation` 등으로 확정한다.
- 지도 마커 선택 흐름에서는 `destinationId`가 필수다.
- 자연어가 없으면 `naturalLanguageQuery`는 `null` 또는 생략 가능하다.
- `includeFestivals`는 선택한 소도시의 `festivalAvailable`이 false면 프론트가 보내지 않거나 false로 보낸다.
- `tripType`은 현재 UI의 일정 기간 선택과 1:1 매핑한다.
- `themes`는 온보딩에서 선택한 1~3개 canonical theme enum이다.

### 보강 제안: Itinerary item

```json
{
  "itemId": "uuid",
  "contentId": "uuid",
  "timeOfDay": "morning",
  "sortOrder": 1,
  "title": "불국사 산책",
  "body": "전통 산책 흐름을 먼저 잡습니다.",
  "reason": "선택 테마와 소도시 상세 seed가 맞습니다.",
  "moveMinutes": 18,
  "latitude": 35.7901,
  "longitude": 129.3321
}
```

### 보강 규칙

- Product에서 일정 지도 경로를 보여주려면 item 단위 좌표가 필요하다.
- 일정 수정 API와 동일한 `itemId`, `timeOfDay`, `sortOrder`를 사용한다.
- 추천 응답의 `links.staySearch`는 일정 생성 후 숙박 검색 CTA에 사용한다.

## 5.6 저장 일정 API 상세화

현재 `POST /me/itineraries`는 존재하지만 request/response schema가 명세에 자세히 나오지 않는다. 추천 결과 저장과 사용자가 수정한 일정 저장을 모두 지원하려면 저장 payload를 명확히 해야 한다.

### 보강 제안: `POST /me/itineraries`

```json
{
  "recommendationId": "uuid",
  "destinationId": "uuid",
  "title": "경주 1박 2일 전통 산책",
  "tripType": "2d1n",
  "themes": ["history_tradition"],
  "days": [
    {
      "day": 1,
      "items": [
        {
          "contentId": "uuid",
          "timeOfDay": "morning",
          "sortOrder": 1,
          "title": "불국사 산책"
        }
      ]
    }
  ]
}
```

### 보강 규칙

- 저장 일정은 추천 결과 snapshot을 보존한다.
- 원 추천 결과가 삭제되거나 만료되어도 저장 일정은 마이페이지에서 열 수 있어야 한다.
- 사용자가 편집한 일정은 `sourceRecommendationId`와 별개로 독립 저장된다.

# 6. 변경 요약

## 6.1 기존 명세에서 충분한 부분

- 인증, 세션, 마이페이지 초기화 구조는 Product 연결에 충분하다.
- 온보딩 선호 저장 구조는 방향성이 맞다.
- 지도 마커, 소도시 상세, 추천 생성, 저장, 피드백의 기본 endpoint 구성이 있다.
- AgentCore와 Map/Auth Lambda 분리 기준이 명확하다.
- 대화 원문을 영구 저장하지 않는 정책이 명확하다.

## 6.2 추가 또는 수정해야 하는 부분

| 구분 | 변경 필요성 | 우선순위 |
| --- | --- | --- |
| 테마 enum 통일 | 프론트 임시 코드 제거, 백엔드 canonical theme 사용 | 높음 |
| `GET /themes/onboarding-options` 상세 schema | 온보딩 UI를 백엔드 데이터로 렌더링 | 높음 |
| `GET /destinations/{destinationId}` 상세 필드 확장 | 지도 상세, 추천 근거, 일정 seed 연결 | 높음 |
| `POST /recommendations` request/response 정합성 | 지도 선택 흐름과 챗봇 흐름 모두 커버 | 높음 |
| 일정 item schema 확정 | 일정 지도 경로, 드래그앤드랍 수정 기반 | 높음 |
| `PATCH /me/itineraries/{itineraryId}` 추가 | 아침/점심/저녁 카드 순서 변경 저장 | 중간 |
| `POST /me/itineraries` schema 상세화 | 추천 결과 snapshot 저장 | 중간 |
| 지도 query 고도화 | GPS, bounds, region, 검색어 필터 | 낮음, GPS 단계 |
| 외부 숙소 링크 schema | 일정 후 숙박 CTA 안정화 | 중간 |

# 7. Product API 적용 순서 제안

1. 백엔드 canonical theme enum 확정
2. `GET /themes/onboarding-options` schema 확정
3. `GET /destinations/map-markers` 초기 query 유지
4. `GET /destinations/{destinationId}` 상세 field 확장
5. `POST /recommendations`를 지도 선택 흐름과 챗봇 흐름에 맞게 확정
6. 추천 응답의 itinerary item schema를 저장·수정 API와 공유
7. `POST /me/itineraries` schema 상세화
8. `PATCH /me/itineraries/{itineraryId}` 추가
9. GPS 단계에서 지도 query 고도화

# 8. 결론

현재 API 명세 v0.2는 PoC 프론트엔드의 Product 전환을 시작하기에 충분한 큰 뼈대를 갖고 있다. 다만 Product 전환 전에 백엔드 중심으로 theme enum과 destination detail schema를 먼저 확정해야 한다. 이후 추천 API의 itinerary item 구조와 저장·수정 API를 같은 형태로 맞추면, 현재 프론트의 온보딩, 지도 선택, 챗봇 일정 생성, 마이페이지 저장 흐름을 무리 없이 백엔드 API로 전환할 수 있다.

# 9. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-08 | 로브 기획팀 | Product API 전환을 위한 기존 API 명세 요약, 보강 필요 항목, 적용 순서 정리 |
