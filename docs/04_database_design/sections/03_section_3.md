# 3. 논리 설계

## 3.1 MySQL 논리 ERD

MySQL은 서비스 화면과 API가 신뢰해야 하는 최종 상태를 저장한다.
사용자가 조회·수정·삭제할 수 있어야 하는 데이터는 MySQL에 원장으로 둔다.

| 영역 | 테이블 | 책임 |
| --- | --- | --- |
| 사용자 | `users` | 서비스 사용자 프로필의 기준 원장 |
| 소셜 계정 | `social_accounts` | 소셜 로그인 제공자 계정과 서비스 사용자 연결 |
| 사용자 취향 | `user_preferences` | 온보딩·마이페이지 취향 원장 |
| 저장 일정 | `itineraries` | 사용자가 저장한 최종 여행 일정과 요청·선호 스냅샷 |
| 일정 항목 | `itinerary_items` | 일정에 포함된 세부 장소와 방문 순서 |
| 일정 반응 | `plan_reactions` | 일정에 대한 사용자 반응 |
| 관리자 조직·운영 | `admin_organizations`, `admin_notices`, `admin_recommendation_policies` | 관리자 콘솔의 기관, 공지, 추천 정책 운영 원장 |
| 관리자 역할 | `user_role_assignments` | 사용자별 활성 역할과 유효기간, 부여자 원장 |
| 관리자 지역 | `user_region_assignments` | 사용자별 담당 지역과 유효기간, 부여자 원장 |
| 관리자 데이터 검수 | `admin_data_proposals`, `admin_data_proposal_history`, `monthly_curated_destinations`, `admin_publish_jobs`, `destination_metrics_daily` | 지역 큐레이터 제안, 변경 이력, 월간 큐레이션, 게시 작업, 목적지 지표 원장 |
| 관리자 감사 | `admin_audit_logs` | 관리자 작업의 행위자·권한 스냅샷·결과 원장 |
| 고위험 변경 | `admin_high_risk_change_requests` | 역할·지역·대량 게시의 요청, 독립 결정, 실행 결과 원장 |
| 관리자 MFA | `admin_mfa_credentials`, `admin_mfa_sessions` | 암호화 자격과 로그인 세션별 Step-up 인증 원장 |

![MySQL 논리 ERD](../../assets/images/mermaid/04-database-design-04-database-design-01.png)

## 3.2 RDB 사용자 설계

사용자 RDB 설계는 첨부 ERD 기준의 계정 기반 저장을 담당한다.
PoC에서는 로컬 스토리지로 대체할 수 있으나, Production에서는 `infra/data-stack/rds/schema.sql`의 6개 product table을 기준으로 마이페이지의 계정·취향·저장 일정·반응 API를 구현한다.

### 3.2.1 `users`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | char(36) | PK | 사용자 ID |
| `email` | varchar(255) | nullable | 소셜 제공자가 전달한 이메일 |
| `display_name` | varchar(80) | not null | 서비스에 표시할 닉네임 |
| `avatar_url` | varchar(500) | nullable | 프로필 이미지 URL |
| `created_at` | datetime | not null | 생성 시각 |

### 3.2.2 `social_accounts`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | char(36) | PK | 소셜 계정 연결 ID |
| `user_id` | char(36) | FK | `users.id` |
| `provider` | varchar(30) | not null | 로그인 제공자. 예: `google`, `kakao` |
| `provider_user_id` | varchar(255) | not null | 소셜 제공자 사용자 ID |
| `created_at` | datetime | not null | 연결 시각 |

Unique: (`provider`, `provider_user_id`)

### 3.2.3 `user_preferences`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | char(36) | PK | 취향 레코드 ID |
| `user_id` | char(36) | FK, unique | `users.id` |
| `country_track` | varchar(30) | not null | `KR`, `JP`, `BOTH` |
| `mapped_themes` | json | nullable | 온보딩/마이페이지에서 정규화한 테마 |
| `preferred_regions` | json | nullable | 선호 지역 목록 |
| `pace` | varchar(30) | nullable | 여행 속도 |
| `trip_days` | int | nullable | 선호 여행 일수 |
| `companion_style` | varchar(50) | nullable | 동행 스타일 |
| `travel_styles` | json | nullable | 여행 스타일 배열 |
| `onboarding_completed` | boolean | not null | 온보딩 완료 여부 |
| `created_at`, `updated_at` | datetime | not null | 생성·수정 시각 |

Unique: (`user_id`)

### 3.2.4 `itineraries`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | char(36) | PK | 일정 ID |
| `user_id` | char(36) | FK | `users.id` |
| `title` | varchar(160) | not null | 일정 제목 |
| `summary` | text | nullable | 일정 요약 |
| `duration_label` | varchar(40) | not null | 여행 기간. 예: `1박 2일`, `2박 3일` |
| `festival_choice` | varchar(80) | nullable | 축제 포함 여부 또는 축제 선호 |
| `intensity_label` | varchar(40) | nullable | 일정 강도. 예: `여유`, `보통`, `빡빡` |
| `preference_snapshot` | json | nullable | 저장 당시 취향·조건 스냅샷 |
| `request_summary` | text | nullable | 채팅에서 정리된 최종 요청 요약 |
| `saved_at` | datetime | not null | 사용자가 저장한 시각 |
| `created_at` | datetime | not null | 레코드 생성 시각 |

Index: (`user_id`, `saved_at` desc)

### 3.2.5 `itinerary_items`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | char(36) | PK | 세부 일정 ID |
| `itinerary_id` | char(36) | FK | `itineraries.id` |
| `sort_order` | int | not null | 일정 내 표시 순서 |
| `time_slot` | varchar(40) | nullable | 시간대. 예: `오전`, `오후`, `저녁` |
| `place_name` | varchar(160) | not null | 장소명 |
| `move_hint` | varchar(255) | nullable | 이동 힌트 |
| `recommendation_reason` | text | nullable | 추천 이유 |

Unique: (`itinerary_id`, `sort_order`)

### 3.2.6 `plan_reactions`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | char(36) | PK | 반응 ID |
| `user_id` | char(36) | FK | `users.id` |
| `itinerary_id` | char(36) | FK | `itineraries.id` |
| `reaction_type` | varchar(30) | not null | `like`, `dislike` 등 일정 반응 |
| `created_at` | datetime | not null | 생성 시각 |

Index: (`user_id`, `created_at`), (`itinerary_id`, `created_at`)

## 3.3 DynamoDB NoSQL 사용자 설계

DynamoDB는 사용자 원장을 대체하지 않는다.
사용자 상태, 저장 일정, 일정 항목, 일정 반응의 최종값은 MySQL에 두고, DynamoDB에는 실행 추적과 TTL 이벤트를 둔다.
또한 데이터 수집 계획의 S3 Raw Bucket -> Lambda 전처리 결과는 City, Attraction, Festival, VisitorStatistics 단위의 정규화 문서로 DynamoDB에 적재한다. 이 정규화 문서는 검색·추천 후보 생성의 빠른 조회용이며, 사용자가 저장한 일정은 MySQL의 `itineraries.preference_snapshot`과 `itinerary_items`에 스냅샷으로 남긴다.

### NoSQL 사용자 이벤트 저장 원칙

| 원칙 | 내용 |
| --- | --- |
| 원장 금지 | 사용자 프로필, 저장 일정, 일정 항목, 일정 반응의 최종값은 MySQL을 기준으로 한다. |
| 해시 저장 | `user_id`, IP, user agent는 원문 대신 해시 또는 마스킹 값으로 저장한다. |
| 대화 전문 금지 | 사용자의 자연어 대화 전문, 민감 자유 입력, 비공개 운영 메모는 저장하지 않는다. |
| TTL 필수 | 이벤트와 trace에는 `expires_at`을 두고 보존 기간 이후 자동 삭제한다. |
| 추적 연결 | `recommendation_request_id`, `agent_run_id`, `request_id`로 MySQL 원장과 장애 분석 로그를 연결한다. |
| 검증 캐시 | 축제 검증 캐시는 `festival_id + travelYear` 단위로 저장하고 `confirmed` 30일, `tentative` 7일, `unknown/outdated` 1일 TTL을 권장한다. |
| 수집 정규화 | S3 Raw 원본은 Object Storage에 보존하고, Lambda 전처리 결과만 DynamoDB 정규화 문서에 저장한다. |

아래 테이블은 DynamoDB에 둘 항목을 운영 추적, 검증 캐시, 비동기 작업, API 로그, 수집 정규화 문서로 나눈 것이다. TTL이 필요한 로그성 테이블은 보존 기간 이후 자동 삭제를 전제로 하고, 수집 정규화 테이블은 S3 Raw 원본을 기준으로 재생성 가능한 조회 모델로 관리한다.

| 테이블 | Partition Key | Sort Key | 주요 속성 | TTL |
| --- | --- | --- | --- | --- |
| `lovv_user_event_logs` | `pk` = `USER#{user_id_hash}` 또는 `ANON#{anonymous_session_id}` | `sk` = `EVENT#{created_at}#{event_id}` | `event_type`, `request_id`, `session_id`, `screen`, `action`, `target_id`, `metadata_summary`, `ip_hash` | `expires_at` |
| `lovv_agent_runs` | `pk` = `RUN#{agent_run_id}` | `sk` = `STATE#{created_at}` | `user_id_hash`, `session_id`, `recommendation_request_id`, `status`, `node_name`, `tool_name`, `validation_retry_count`, `error_code`, `payload_summary` | `expires_at` |
| `lovv_festival_verify_cache` | `pk` = `FESTIVAL#{festival_id}` | `sk` = `YEAR#{travel_year}` | `date_status`, `start_date`, `end_date`, `source_url`, `source_type`, `verified_at`, `confidence`, `target_region`, `travel_month` | `expires_at` |
| `lovv_async_jobs` | `pk` = `JOB#{job_id}` | `sk` = `STATUS#{updated_at}` | `job_type`, `status`, `requested_by_user_hash`, `progress`, `result_ref`, `error_code` | `expires_at` |
| `lovv_api_logs` | `pk` = `API#{yyyyMMdd}#{endpoint_group}` | `sk` = `created_at#{request_id}` | `method`, `path`, `status`, `latency_ms`, `user_id_hash`, `error_code` | `expires_at` |
| `lovv_content_documents` | `pk` = `CONTENT#{country}#{entity_type}` | `sk` = `ENTITY#{entity_id}` | `city_id`, `source_type`, `source_url`, `normalized_payload`, `quality_status`, `raw_s3_uri`, `updated_at` | 없음 |
| `lovv_visitor_statistics` | `pk` = `CITY#{city_id}` | `sk` = `STAT#{period}#{source_type}` | `country`, `period`, `visitor_type`, `value`, `unit`, `source_url`, `collected_at`, `quality_status` | 없음 |
| `lovv_anonymous_travel_segment_stats` | `pk` = 세그먼트 식별자 | `sk` = 기간/집계 기준 | 익명 연령·성별·여행 선호 segment별 통계. 개인정보 원장이 아니라 추천 fallback용 집계 조회 모델 | 없음 |

현재 live 구조에서는 backend 운영 테이블과 수집 파이프라인 테이블이 별도 경계로 운영된다.

| 용도 | Live 물리 테이블 | Key/GSI | TTL/PITR | 확인 결과 |
| --- | --- | --- | --- | --- |
| 사용자 이벤트 로그 | `lovv_dev_user_event_logs` | `pk`/`sk`, `GSI1RequestLookup`, `GSI3EventTypeDaily`, `GSI4RecommendationLookup` | TTL `expires_at` enabled | ACTIVE, PAY_PER_REQUEST |
| Agent 실행 trace | `lovv_dev_agent_runs` | `pk`/`sk`, `GSI1RequestLookup`, `GSI2AgentRunLookup`, `GSI4RecommendationLookup` | TTL `expires_at` enabled | ACTIVE, PAY_PER_REQUEST |
| 축제 검증 캐시 | `lovv_dev_festival_verify_cache` | `pk`/`sk` | TTL `expires_at` enabled | ACTIVE, PAY_PER_REQUEST |
| 비동기 작업 | `lovv_dev_async_jobs` | `pk`/`sk` | TTL `expires_at` enabled | ACTIVE, PAY_PER_REQUEST |
| API 로그 | `lovv_dev_api_logs` | `pk`/`sk`, `GSI1RequestLookup` | TTL `expires_at` enabled | ACTIVE, PAY_PER_REQUEST |
| Auth refresh session | `lovv_dev_auth_sessions` | `sessionId`, `GSI1RefreshTokenHashLookup` | TTL `expiresAt` enabled | ACTIVE, PAY_PER_REQUEST |
| 콘텐츠 문서 보조 | `lovv_dev_content_documents` | `pk`/`sk` | TTL 없음 | ACTIVE, 현재 dev 항목 없음 |
| 방문 통계 보조 | `lovv_dev_visitor_statistics` | `pk`/`sk` | TTL 없음 | ACTIVE, 현재 dev 항목 없음 |
| 익명 세그먼트 통계 | `lovv_dev_anonymous_travel_segment_stats` | `pk`/`sk` | TTL 없음 | ACTIVE, 현재 dev 항목 없음 |
| KR 수집 V1 | `TourKoreaDomainData` | `PK`/`SK`, `GSI1`, `GSI2`, `GSI3`, `FestivalMonthIndex` | PITR enabled | ACTIVE, live 항목 약 8천 건 |
| KR 수집 V2 | `TourKoreaDomainDataV2` | `PK`/`SK`, `CityDomainIndex`, `ProvinceDomainIndex`, `EntityTypeDomainIndex`, `FestivalMonthIndex` | PITR enabled | ACTIVE, live 항목 약 1만 건 |

## 3.4 S3 vector index 논리 모델

S3 vector index는 수집 원천과 일정 저장 스냅샷을 검색용으로 복제한 인덱스다.
S3 vector index의 데이터는 원본이 아니며, 장애 복구나 재색인은 MySQL 일정 스냅샷, DynamoDB 정규화 문서, S3 Raw 원본을 기준으로 수행한다.
별도 벡터 DB 제품 도입은 현재 설계의 기본 범위가 아니며, 그래프DB 직접 도입 대신 관계 탐색은 Lambda 기반 보조 기능으로 구현한다.

| 인덱스 대상 | 원본 | S3 vector metadata |
| --- | --- | --- |
| 목적지 | DynamoDB 정규화 문서, S3 Raw 원본 | `destination_id`, `country`, `region`, `themes`, `recommended_months` |
| 축제 | DynamoDB 정규화 문서, S3 Raw 원본 | `festival_id`, `destination_id`, `start_date`, `end_date`, `season_tags` |
| 방문·관광 통계 | DynamoDB `visitor_statistics`, S3 Raw 원본 | 직접 vector 대상이 아니며, 도시·월별 feature와 랭킹 보조 조회로 사용 |
| 관광지·체험 | DynamoDB 정규화 문서, S3 Raw 원본 | `content_id`, `destination_id`, `content_type`, `theme_tags` |
| 출처 문서 | object storage | `source_id`, `source_url`, `collected_at`, `license_type` |

Agent 추천 검색은 S3 vector metadata에 `city_id`, `country`, `latitude`, `longitude`, `theme_tags`, `content_type`, `recommended_months`를 포함해야 한다.
현재 `kr-tour-domain-v2` 재색인 기준에서는 `visitor_statistics`를 S3 Vector에 넣지 않고 DynamoDB에서 별도 조회한다.
`active_required_themes`, 거리 기반 1차 필터, 콘텐츠 타입 균형, 임베딩 유사도 재랭킹은 이 metadata와 MySQL 일정 스냅샷 필드를 함께 사용한다.

## 3.5 Lambda 관계 탐색 논리 모델

Lambda 관계 탐색은 S3 vector index의 의미 검색 결과를 도시·축제·테마·장소 관계로 확장·검증하는 보조 기능이다.
관계 데이터는 원본이 아니며, DynamoDB 정규화 문서, S3 Raw 원본, 운영 검증 결과를 기준으로 재생성할 수 있어야 한다.

> 비용 주의: Neptune은 상시 가동 비용이 높아 PoC/Production 1차에서는 직접 도입하지 않는다.
> 동일 그래프 용도는 DynamoDB 인접 리스트, 사전계산 후보 테이블, Lambda 인메모리 그래프로 구현한다.
> Neptune은 3-hop 이상 임의 경로 탐색, 대규모 실시간 그래프 쓰기, 복잡한 그래프 알고리즘이 실제 병목이 될 때의 고도화 승격 옵션이다.

| 그래프 요소 | 라벨/관계 | 주요 속성 | 용도 |
| --- | --- | --- | --- |
| 목적지 노드 | `City` | `city_id`, `country`, `region`, `latitude`, `longitude` | 추천 후보의 중심 노드 |
| 축제 노드 | `Festival` | `festival_id`, `travel_year`, `date_status`, `start_date`, `end_date` | 축제 포함 추천과 날짜 검증 연결 |
| 테마 노드 | `Theme` | `theme_id`, `theme_name`, `theme_group` | 필수·선호 테마 충족 여부 탐색 |
| 장소 노드 | `Place` | `content_id`, `content_type`, `source_type` | 일정 항목 후보 확장 |
| 관계 | `HAS_THEME`, `HOSTS_FESTIVAL`, `NEAR_CITY`, `HAS_PLACE`, `SEASONAL_FIT` | `weight`, `confidence`, `source_id`, `updated_at` | 다단계 후보 확장과 그래프 기반 재랭킹 |

Lambda 관계 탐색 입력에는 사용자 ID 원문, 대화 전문, 비공개 운영 메모를 포함하지 않는다.
사용자 일정 저장 결과는 MySQL에 남기고, 관계 탐색에는 추천 후보 생성을 위한 공용 콘텐츠 관계만 사용한다.

## 3.6 API 식별자 매핑

API 명세의 camelCase 식별자는 DB 내부에서는 snake_case 컬럼, DynamoDB 속성, Lambda 관계 탐색 노드 ID로 매핑한다.

| API 필드 | MySQL 기준 | DynamoDB/S3 vector/Lambda 관계 탐색 기준 | 비고 |
| --- | --- | --- | --- |
| `userId` | `users.id` | 해시 처리된 `user_id_hash` | 사용자 원장과 이벤트 로그 연결 |
| `itineraryId` | `itineraries.id`, `itinerary_items.itinerary_id`, `plan_reactions.itinerary_id` | 이벤트 로그의 `target_id` | 저장 일정 조회·삭제 기준 |
| `reactionType` | `plan_reactions.reaction_type` | 클릭 이벤트의 `action` 또는 `reaction_type` | 일정 반응 원장은 MySQL 기준 |
| `destinationId` | 없음 | `city_id`, `destination_id` metadata, Lambda 관계 탐색 `City.city_id` | 추천 후보와 지도 마커는 검색·수집 보조 저장소 기준 |
| `festivalId` | 없음 | `lovv_festival_verify_cache.pk`, S3 vector metadata, Lambda 관계 탐색 `Festival.festival_id` | 축제 날짜 검증 캐시와 추천 응답 연결 |

## 3.7 관리자 권한·고위험 변경 논리 모델

관리자 권한은 `user_role_assignments`와 `user_region_assignments`의 활성·유효 할당을 Source of Truth로 사용한다. `R-SUPER-ADMIN`은 기관에 종속되지 않는 전역 역할이며, 마지막 활성 최고 권한 관리자 회수는 애플리케이션 트랜잭션에서 거부한다.

`admin_high_risk_change_requests`는 다음 상태 전이만 허용한다.

```text
pending ── approve + execute ──> executed
pending ── reject ─────────────> rejected
```

- 작업 유형은 `role_grant`, `role_revoke`, `region_grant`, `region_revoke`, `bulk_publish`로 제한한다.
- `requested_by`와 `decided_by`는 달라야 하며 결정자는 활성 `R-SUPER-ADMIN`이어야 한다.
- 승인은 별도 승인 완료 상태를 남기지 않고 대상 변경을 같은 트랜잭션에서 실행한 후 `executed`로 전환한다.
- 역할·지역 변경, 요청 상태 전이, `admin_audit_logs` 기록 중 하나라도 실패하면 전체 트랜잭션을 롤백한다.
- `payload_json`에는 작업별 입력만 저장하고 토큰, TOTP secret·코드, 복구 코드와 민감 원문은 저장하지 않는다.
