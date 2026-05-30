# 로브 (Lovv) 데이터베이스 설계 명세서

> 문서 버전: v0.1
> 문서 상태: 기획 단계 (Planning)
> 기준 문서: `docs/01_requirements/01_requirements.md` v1.5

# 1. 문서 개요

## 1.1 목적

본 문서는 로브 서비스의 핵심 데이터 모델, 테이블 후보, 관계, 인덱스, 보존 정책을 정의한다.
PoC에서는 일부 데이터를 정적 파일과 로컬 스토리지로 대체할 수 있으나, Production 전환 시 본 문서를 기준으로 데이터베이스를 설계한다.

## 1.2 데이터베이스 방향

| 항목 | 결정 |
| --- | --- |
| 기본 모델 | 관계형 데이터베이스 우선 |
| 권장 DB | PostgreSQL |
| 이유 | 목적지, 축제, 사용자, 저장 일정, 검토 이력 간 관계가 명확하고 ACID 트랜잭션이 필요함 |
| 보조 저장소 | 벡터 검색 또는 문서 검색 저장소는 RAG 단계에서 별도 검토 |

# 2. 논리 데이터 모델

| 엔티티 | 설명 |
| --- | --- |
| users | 로그인 사용자 |
| roles | 역할 정의 |
| user_roles | 사용자-역할 매핑 |
| user_preferences | 온보딩 선호 프로필 |
| destinations | 소도시 목적지 |
| destination_themes | 목적지-테마 매핑 |
| themes | 기본·확장 테마 |
| weather_monthly_trends | 월별 기상 경향 |
| festivals | 축제·행사 |
| recommendations | 추천 실행 결과 |
| itinerary_days | 추천 일정의 일자 |
| itinerary_items | 일자별 방문 항목 |
| saved_itineraries | 사용자 저장 일정 |
| recommendation_feedback | 좋아요/싫어요 피드백 |
| data_submissions | 관광 운영자·데이터 제공 기관의 데이터 제안 |
| review_histories | 제안 검토·승인·반려 이력 |

# 3. 핵심 테이블 설계

## 3.1 users

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 사용자 ID |
| email | varchar | unique, nullable | 이메일 로그인 사용자 |
| display_name | varchar | not null | 표시 이름 |
| status | varchar | not null | active, blocked, deleted |
| created_at | timestamptz | not null | 생성 시각 |
| updated_at | timestamptz | not null | 수정 시각 |

## 3.2 destinations

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 목적지 ID |
| country | varchar | not null | KR, JP |
| name_ko | varchar | not null | 한국어 이름 |
| name_local | varchar | nullable | 현지어 이름 |
| region | varchar | not null | 도/현/지역 |
| latitude | decimal | not null | 위도 |
| longitude | decimal | not null | 경도 |
| description | text | not null | 대표 설명 |
| crowding_score | numeric | nullable | 혼잡도 점수 |
| verification_status | varchar | not null | draft, verified, deprecated |
| source_url | text | nullable | 출처 |
| created_at | timestamptz | not null | 생성 시각 |
| updated_at | timestamptz | not null | 수정 시각 |

## 3.3 weather_monthly_trends

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 기상 경향 ID |
| destination_id | uuid | FK | 목적지 |
| month | int | 1~12 | 여행 월 |
| sunny_score | numeric | not null | 맑음 적합도 |
| rain_risk | numeric | not null | 우천 경향 |
| snow_risk | numeric | not null | 폭설 경향 |
| typhoon_risk | numeric | not null | 태풍 경향 |
| notes | text | nullable | 설명 |
| source_url | text | nullable | 출처 |
| updated_at | timestamptz | not null | 갱신 시각 |

## 3.4 recommendations

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 추천 ID |
| user_id | uuid | FK, nullable | 비로그인 추천은 null |
| entry_type | varchar | not null | map_marker, chatbot |
| country | varchar | not null | KR, JP |
| travel_month | int | not null | 여행 월 |
| destination_id | uuid | FK | 선정 소도시 |
| trip_type | varchar | not null | daytrip, 2d1n, 3d2n, 4d3n, 5d4n |
| include_festivals | boolean | not null | 축제 포함 여부 |
| explanation | text | not null | 추천 이유 |
| created_at | timestamptz | not null | 생성 시각 |

## 3.5 recommendation_feedback

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 피드백 ID |
| user_id | uuid | FK | 사용자 |
| recommendation_id | uuid | FK | 추천 결과 |
| destination_id | uuid | FK | 대상 소도시 |
| feedback_type | varchar | not null | like, dislike |
| theme_tags | jsonb | nullable | 피드백 시점 테마 태그 |
| created_at | timestamptz | not null | 생성 시각 |

## 3.6 data_submissions

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| id | uuid | PK | 제안 ID |
| submitted_by | uuid | FK | 제안자 |
| target_type | varchar | not null | destination, festival, weather, link |
| target_id | uuid | nullable | 기존 데이터 수정 시 대상 |
| payload | jsonb | not null | 제안 내용 |
| status | varchar | not null | submitted, approved, rejected, change_requested |
| created_at | timestamptz | not null | 생성 시각 |
| updated_at | timestamptz | not null | 수정 시각 |

# 4. 관계 정의

| 관계 | 설명 |
| --- | --- |
| users 1:N user_preferences | 사용자는 선호 프로필을 가질 수 있다 |
| destinations N:M themes | 목적지는 여러 테마를 가질 수 있다 |
| destinations 1:N weather_monthly_trends | 목적지별 12개월 기상 경향 |
| destinations 1:N festivals | 축제·행사는 목적지 또는 지역에 연결 |
| recommendations 1:N itinerary_days | 추천은 여러 일자를 가진다 |
| itinerary_days 1:N itinerary_items | 일자별 방문 항목 |
| users 1:N saved_itineraries | 사용자는 일정을 저장한다 |
| users 1:N recommendation_feedback | 사용자는 추천 피드백을 남긴다 |

# 5. 인덱스 후보

| 테이블 | 인덱스 | 목적 |
| --- | --- | --- |
| destinations | `(country, region)` | 국가·지역 필터 |
| destinations | `(verification_status)` | 검증 상태 필터 |
| destination_themes | `(theme_id, destination_id)` | 테마 기반 후보 검색 |
| weather_monthly_trends | `(destination_id, month)` unique | 목적지 월별 기상 조회 |
| festivals | `(country, region, start_date, end_date)` | 기간·지역 축제 검색 |
| recommendations | `(user_id, created_at desc)` | 사용자 추천 이력 |
| saved_itineraries | `(user_id, created_at desc)` | 마이페이지 저장 일정 |
| recommendation_feedback | `(user_id, destination_id)` | 개인화 가중치 계산 |
| data_submissions | `(status, created_at desc)` | 관리자 검토 목록 |

# 6. 데이터 보존 정책

| 데이터 | PoC | Production |
| --- | --- | --- |
| 대화 로그 | 저장하지 않음 | 저장하지 않음 |
| 온보딩 선호 | 로컬 스토리지 | 사용자 계정 저장 |
| 추천 일정 | 로컬 스토리지 | 사용자가 저장한 일정만 보관 |
| 피드백 | 로컬 스토리지 | 사용자별 개인화 목적으로 보관 |
| 운영 검토 이력 | 제외 가능 | 감사 목적 보관 |

# 7. 트랜잭션 경계

| 작업 | 트랜잭션 범위 |
| --- | --- |
| 추천 일정 저장 | saved_itineraries와 관련 itinerary snapshot 저장을 단일 트랜잭션 처리 |
| 피드백 저장 | feedback 저장과 개인화 집계 갱신을 단일 트랜잭션 처리 |
| 데이터 제안 승인 | 원본 데이터 반영, 제출 상태 변경, review history 기록을 단일 트랜잭션 처리 |

# 8. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-05-29 | 로브 기획팀 | 데이터베이스 설계 명세서 초안 작성 |

