# Lovv PoC Database Design

> 문서 성격: 보조 Markdown
> 대표 문서: `../04_database_design.md`

작성일: 2026-06-05

## 1. 설계 범위

Lovv PoC 단계의 데이터베이스는 "사용자가 마음에 들어 저장한 최종 여행 일정"을 중심으로 구성한다.

이 단계에서는 AI 채팅 과정 전체를 DB에 저장하지 않는다. 사용자가 채팅을 통해 일정 조건을 조정하더라도, DB에는 최종적으로 저장된 일정과 그 일정의 세부 항목만 남긴다.

### 포함 범위

- 사용자 기본 정보
- 소셜 로그인 계정 연결 정보
- 사용자가 저장한 여행 일정
- 여행 일정의 세부 장소 및 순서
- 일정에 대한 가벼운 반응 정보

### 제외 범위

- 채팅 원문 저장
- 검색 조건 전용 테이블
- 일정 초안 또는 버전 관리 테이블
- 추천 피드백 전용 테이블
- 사용자 취향 전용 테이블. 단, 저장된 일정에 사용된 테마 선호 스냅샷은 JSON에 포함한다.
- 저장 여부만 표현하는 별도 저장 테이블
- 리뷰 및 별점 테이블

## 2. 핵심 설계 방향

PoC에서는 사용자의 의사결정 흐름을 모두 영속화하지 않고, 저장 결과만 데이터로 남긴다.

사용자가 AI 채팅에서 여러 번 피드백을 주더라도 그 과정은 서비스 실행 중의 임시 상태로 처리한다. 사용자가 최종 일정을 저장하는 순간, 해당 일정이 `ITINERARIES`에 생성되고 세부 일정은 `ITINERARY_ITEMS`에 저장된다.

`USER_PREFERENCES`, `SEARCH_CRITERIA`, `PLAN_DRAFTS`를 별도 테이블로 두지 않는 대신, 저장 당시의 취향과 요청 조건은 `ITINERARIES.preference_snapshot`과 `ITINERARIES.request_summary`에 함께 저장한다. 사용자가 선택한 테마 선호는 `preference_snapshot.theme_tags` 배열에 저장한다.

## 3. ERD

![Lovv PoC RDB ERD](../../assets/images/mermaid/04-database-design-lovv-poc-database-design-01.png)

## 4. 테이블 설계

### 4.1 USERS

사용자 계정의 기준 테이블이다. PoC에서는 자체 이메일/비밀번호 로그인을 두지 않고, 소셜 로그인으로 식별된 사용자 프로필만 저장한다.

| 컬럼 | 타입 | 키 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 사용자 고유 ID |
| email | string |  | 소셜 제공자가 전달한 이메일 |
| display_name | string |  | 서비스에 표시할 닉네임 |
| avatar_url | string |  | 프로필 이미지 URL |
| created_at | datetime |  | 가입일 |

### 4.2 SOCIAL_ACCOUNTS

소셜 로그인 제공자와 서비스 사용자를 연결하는 테이블이다. 한 사용자가 여러 소셜 계정을 연결할 수 있으므로 `USERS`와 1:N 관계를 가진다.

| 컬럼 | 타입 | 키 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 소셜 계정 연결 ID |
| user_id | uuid | FK | `USERS.id` 참조 |
| provider | string |  | 로그인 제공자. 예: `google`, `kakao` |
| provider_user_id | string |  | 소셜 제공자 내부 사용자 ID |
| created_at | datetime |  | 연결일 |

권장 제약:

- `UNIQUE(provider, provider_user_id)`
- `INDEX(user_id)`

### 4.3 ITINERARIES

사용자가 최종적으로 저장한 여행 일정 테이블이다. PoC에서는 별도의 `SAVED_PLANS` 테이블을 두지 않고, 이 테이블에 존재하는 일정 자체를 "저장된 일정"으로 본다.

| 컬럼 | 타입 | 키 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 일정 ID |
| user_id | uuid | FK | `USERS.id` 참조 |
| title | string |  | 일정 제목 |
| summary | text |  | 일정 요약 |
| duration_label | string |  | 여행 기간. 예: `1박 2일`, `2박 3일` |
| festival_choice | string |  | 축제 포함 여부 또는 축제 선호 |
| intensity_label | string |  | 일정 강도. 예: `여유`, `보통`, `빡빡` |
| preference_snapshot | json |  | 저장 당시 취향/조건 스냅샷 |
| request_summary | text |  | 채팅에서 정리된 최종 요청 요약 |
| saved_at | datetime |  | 사용자가 저장한 시각 |
| created_at | datetime |  | 일정 레코드 생성 시각 |

`preference_snapshot` 예시:

```json
{
  "city_pair": "전주-군산",
  "themes": ["food", "local", "walkable"],
  "duration": "1박 2일",
  "festival": "optional",
  "intensity": "normal"
}
```

권장 제약:

- `INDEX(user_id, saved_at DESC)`
- `saved_at`은 사용자가 저장을 완료한 시각으로 사용
- `created_at`은 레코드 생성 시각으로 사용

### 4.4 ITINERARY_ITEMS

저장된 일정에 포함된 세부 장소와 방문 순서를 저장한다. 하나의 일정은 여러 개의 세부 일정 항목을 가진다.

| 컬럼 | 타입 | 키 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 세부 일정 ID |
| itinerary_id | uuid | FK | `ITINERARIES.id` 참조 |
| sort_order | int |  | 일정 내 표시 순서 |
| time_slot | string |  | 시간대. 예: `오전`, `오후`, `저녁` |
| place_name | string |  | 장소명 |
| move_hint | string |  | 이동 힌트 |
| recommendation_reason | text |  | 추천 이유 |

권장 제약:

- `INDEX(itinerary_id, sort_order)`
- `UNIQUE(itinerary_id, sort_order)`

### 4.5 PLAN_REACTIONS

사용자가 일정에 대해 남긴 가벼운 반응을 저장한다. PoC에서는 리뷰처럼 긴 텍스트를 받지 않고, 좋아요/싫어요 같은 단순 반응만 다룬다.

| 컬럼 | 타입 | 키 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 반응 ID |
| user_id | uuid | FK | `USERS.id` 참조 |
| itinerary_id | uuid | FK | `ITINERARIES.id` 참조 |
| reaction_type | string |  | 반응 타입. 예: `like`, `dislike` |
| created_at | datetime |  | 반응 생성일 |

권장 제약:

- 한 사용자가 한 일정에 하나의 반응만 가질 경우: `UNIQUE(user_id, itinerary_id)`
- 반응 타입별 중복만 막을 경우: `UNIQUE(user_id, itinerary_id, reaction_type)`
- `INDEX(itinerary_id, reaction_type)`

PoC에서는 일반적으로 `UNIQUE(user_id, itinerary_id)`를 권장한다. 사용자가 좋아요에서 싫어요로 바꾸는 동작은 새 row 추가가 아니라 기존 row의 `reaction_type` 업데이트로 처리하는 편이 단순하다.

## 5. JSON 처리 스키마

PoC에서 DB에 JSON으로 저장하는 대상은 `ITINERARIES.preference_snapshot` 하나로 제한한다. 사용자가 선택한 테마 선호, 도시 조합, 여행 강도 같은 User Preference는 별도 `USER_PREFERENCES` 테이블로 분리하지 않고 이 JSON 스냅샷에 포함한다.

핵심 조회 조건인 `duration_label`, `festival_choice`, `intensity_label`은 `ITINERARIES`의 일반 컬럼에도 저장한다. 이 값들은 목록 필터, 정렬, 통계 조회에 쓰일 수 있기 때문이다. 반면 `preference_snapshot`은 사용자가 일정을 저장하던 시점의 조건을 복원하기 위한 스냅샷이다.

### 5.1 JSON 컬럼 목록

| 테이블 | 컬럼 | 권장 DB 타입 | 용도 |
| --- | --- | --- | --- |
| `ITINERARIES` | `preference_snapshot` | PostgreSQL: `jsonb`, MySQL: `json` | 저장 당시 취향, 도시 조합, 기간, 축제 선호, 강도, 추가 조건 스냅샷 |

### 5.2 `preference_snapshot` 저장 예시

```json
{
  "schema_version": 1,
  "city_pair": {
    "primary_city": "전주",
    "secondary_city": "군산"
  },
  "theme_tags": ["food", "local", "walkable"],
  "duration_label": "1박 2일",
  "festival_choice": "optional",
  "intensity_label": "normal",
  "companion_type": "friends",
  "budget_level": "medium",
  "transport_preference": "public_transport",
  "captured_from": "chat_summary",
  "captured_at": "2026-06-05T13:04:12+09:00"
}
```

### 5.3 `preference_snapshot` JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ItineraryPreferenceSnapshot",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "city_pair",
    "theme_tags",
    "duration_label",
    "festival_choice",
    "intensity_label",
    "captured_from",
    "captured_at"
  ],
  "properties": {
    "schema_version": {
      "type": "integer",
      "minimum": 1,
      "description": "JSON 구조 버전"
    },
    "city_pair": {
      "type": "object",
      "additionalProperties": false,
      "required": ["primary_city"],
      "properties": {
        "primary_city": {
          "type": "string",
          "minLength": 1,
          "description": "주 여행 도시"
        },
        "secondary_city": {
          "type": ["string", "null"],
          "description": "함께 방문할 수 있는 보조 도시"
        }
      }
    },
    "theme_tags": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string"
      },
      "description": "사용자가 선택했거나 채팅에서 도출된 여행 테마"
    },
    "duration_label": {
      "type": "string",
      "description": "여행 기간 라벨"
    },
    "festival_choice": {
      "type": "string",
      "enum": ["include", "exclude", "optional", "none"],
      "description": "축제 포함 선호"
    },
    "intensity_label": {
      "type": "string",
      "enum": ["relaxed", "normal", "tight"],
      "description": "일정 강도"
    },
    "companion_type": {
      "type": ["string", "null"],
      "description": "동행 유형. 예: solo, couple, friends, family"
    },
    "budget_level": {
      "type": ["string", "null"],
      "enum": ["low", "medium", "high", null],
      "description": "대략적인 예산 선호"
    },
    "transport_preference": {
      "type": ["string", "null"],
      "description": "이동 수단 선호. 예: public_transport, car, walk"
    },
    "captured_from": {
      "type": "string",
      "enum": ["chat_summary", "onboarding", "manual"],
      "description": "스냅샷 생성 출처"
    },
    "captured_at": {
      "type": "string",
      "format": "date-time",
      "description": "스냅샷 생성 시각"
    }
  }
}
```

### 5.4 JSON 저장 규칙

- `preference_snapshot`에는 원문 채팅을 넣지 않는다.
- 사용자가 직접 입력한 문장을 그대로 저장하지 않고, 서비스가 정규화한 조건만 저장한다.
- 목록 조회나 자주 쓰는 필터 조건은 JSON 내부 값에 의존하지 않고 일반 컬럼을 우선 사용한다.
- JSON 구조가 바뀔 가능성을 고려해 `schema_version`을 필수로 둔다.
- 민감정보, access token, refresh token, 외부 API 응답 원문은 JSON에 저장하지 않는다.

### 5.5 DB 레벨 검증 예시

PostgreSQL을 사용할 경우 최소한 다음 수준의 검증을 권장한다.

```sql
preference_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb,
CHECK (jsonb_typeof(preference_snapshot) = 'object'),
CHECK ((preference_snapshot ? 'schema_version') = true),
CHECK ((preference_snapshot ? 'city_pair') = true)
```

정교한 JSON Schema 검증은 DB 제약만으로 처리하기보다 백엔드 저장 로직에서 수행하는 편이 유지보수에 유리하다.

## 6. 관계 설계

| 관계 | 카디널리티 | 설명 |
| --- | --- | --- |
| `USERS` -> `SOCIAL_ACCOUNTS` | 1:N | 한 사용자는 여러 소셜 계정을 연결할 수 있다. |
| `USERS` -> `ITINERARIES` | 1:N | 한 사용자는 여러 저장 일정을 가질 수 있다. |
| `ITINERARIES` -> `ITINERARY_ITEMS` | 1:N | 한 일정은 여러 세부 일정 항목을 가진다. |
| `USERS` -> `PLAN_REACTIONS` | 1:N | 한 사용자는 여러 일정에 반응할 수 있다. |
| `ITINERARIES` -> `PLAN_REACTIONS` | 1:N | 한 일정은 여러 사용자 반응을 받을 수 있다. |

## 7. PoC 데이터 흐름

1. 사용자가 Google 또는 Kakao로 로그인한다.
2. `USERS`에 사용자 기본 정보가 생성된다.
3. `SOCIAL_ACCOUNTS`에 소셜 제공자 계정 정보가 연결된다.
4. 사용자가 AI 채팅을 통해 여행 조건을 조정한다.
5. 채팅 원문은 DB에 저장하지 않고, 최종 저장 시점의 요청 요약만 만든다.
6. 사용자가 마음에 든 일정을 저장하면 `ITINERARIES`가 생성된다.
7. 일정의 장소, 순서, 시간대, 추천 이유는 `ITINERARY_ITEMS`에 저장된다.
8. 사용자가 일정에 좋아요/싫어요를 누르면 `PLAN_REACTIONS`가 생성되거나 갱신된다.

## 8. 제외 테이블 판단 근거

| 제외 테이블 | 제외 이유 |
| --- | --- |
| `CHAT_MESSAGES` | PoC에서는 채팅 원문을 저장하지 않는다. |
| `SEARCH_CRITERIA` | 조건은 `request_summary`와 `preference_snapshot`으로 충분하다. |
| `USER_PREFERENCES` | 사용자 취향을 독립적으로 관리하지 않고, 저장된 일정의 스냅샷으로만 보관한다. |
| `PLAN_DRAFTS` | 생성된 일정은 저장 전 임시 상태로만 다루며 DB에 초안으로 남기지 않는다. |
| `RECOMMENDATION_FEEDBACKS` | 채팅 중 피드백은 최종 일정 생성에 반영되고 별도 분석 테이블로 저장하지 않는다. |
| `SAVED_PLANS` | `ITINERARIES` 자체가 저장된 일정이므로 중간 테이블이 필요하지 않다. |
| `PLAN_REVIEWS` | 리뷰 기능은 PoC 범위에서 제외한다. |

## 9. 보안 및 개인정보 고려사항

- 소셜 access token, refresh token은 이 스키마에 저장하지 않는다.
- 채팅 원문을 저장하지 않아 사용자의 자유 입력 개인정보 노출 위험을 줄인다.
- `preference_snapshot`에는 서비스 추천에 필요한 최소 조건만 저장한다.
- `avatar_url`은 외부 이미지 URL일 수 있으므로 클라이언트 렌더링 시 검증된 URL만 사용한다.
- 사용자 삭제 기능을 구현할 때는 일정/반응 데이터를 즉시 hard delete할지, 익명화할지 정책을 먼저 정해야 한다.

## 10. 구현 시 우선순위

PoC 구현 순서는 다음을 권장한다.

1. `USERS`, `SOCIAL_ACCOUNTS`로 로그인 사용자 식별을 먼저 구성한다.
2. 저장 버튼 동작에 맞춰 `ITINERARIES`, `ITINERARY_ITEMS` 생성을 구현한다.
3. 마이페이지 또는 저장 목록 조회를 위해 `ITINERARIES(user_id, saved_at DESC)` 인덱스를 사용한다.
4. 좋아요/싫어요가 필요해지는 시점에 `PLAN_REACTIONS`를 추가한다.
5. 리뷰, 피드백 분석, 추천 품질 개선 로그는 PoC 이후 Product 단계에서 별도 설계한다.

## 11. 설계 검토 체크리스트

- PoC 범위에 필요한 최소 테이블만 포함했다.
- 채팅 원문과 추천 피드백 로그는 저장하지 않는다.
- 사용자가 저장한 최종 일정만 영속화한다.
- 사용자 취향은 별도 테이블이 아니라 일정 스냅샷 JSON으로 보관한다.
- `preference_snapshot` JSON 구조와 저장 규칙을 정의했다.
- 리뷰 테이블은 PoC 범위에서 제외했다.
- 각 1:N 관계가 ERD와 테이블 필드의 FK 기준으로 연결된다.
