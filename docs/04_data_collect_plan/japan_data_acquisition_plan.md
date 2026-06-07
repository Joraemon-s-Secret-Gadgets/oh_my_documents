# 일본 데이터 취득 계획서

> 문서 버전: v0.5
> 문서 상태: 관동 우선 수집 및 S3 Raw 계약 보완
> 작성일: 2026-06-02
> 동기화 대상 문서: `docs/04_data_collect_plan/04_data_collect_plan.md`
> 공유 산출물: `pages/04_data_collect_plan.html`, `pdf/japan_data_acquisition_plan.pdf`

# 1. 목적

본 문서는 여행 추천 Multi-Agent 서비스에서 일본 소도시 추천에 필요한 도시·관광지·축제·방문객 통계 데이터를 한 번에 취득하기 위한 범위, 데이터 소스, 검증 방식, 저장 구조를 정의한다.

이번 문서의 핵심은 다음과 같다.

- City, Attraction, Festival, VisitorStatistics의 정의된 항목을 모두 수집 대상으로 둔다.
- 일본은 관동 지역 지자체를 우선 수집 범위로 둔다.
- 도도부현의 간략 정보와 산하 도시 목록을 먼저 취득하고, 산하 도시 목록에 포함된 City만 Wikipedia 문서 크롤링 대상으로 둔다.
- 취득 결과는 JSON 문서로 저장한 뒤 S3 Raw Bucket에 적재한다.
- 로컬 검증 산출물은 `data/JP/*.json` 형태로 관리한다.
- 운영시간, 운영기간, 입장료, 사진처럼 출처별 표현 차이가 큰 항목도 최초 취득 범위에 포함한다.
- 자동 수집, 공식 사이트 확인, Web Search Worker, 수동 검수를 하나의 취득 파이프라인으로 묶어 처리한다.
- 추천 DB는 `City 1:N Attraction`, `City 1:N Festival`, `City 1:N VisitorStatistics` 관계를 기준으로 설계한다.

# 2. 목표 데이터 모델

## 2.1 관계 구조

```text
City
 ├── Attraction
 ├── Festival
 └── VisitorStatistics
```

| 관계 | 설명 |
| --- | --- |
| `City 1:N Attraction` | 하나의 일본 도시는 여러 관광지를 가진다. |
| `City 1:N Festival` | 하나의 일본 도시는 여러 축제·행사를 가진다. |
| `City 1:N VisitorStatistics` | 하나의 일본 도시는 지역별 또는 월별 관광 통계 보조 지표를 가진다. |

## 2.2 City 데이터

City는 추천의 기준 지역이다. 일본 목적지는 시·정·촌·구 단위의 소도시를 기본 단위로 관리한다. 도도부현 문서에서는 간략 정보와 산하 도시 목록만 취득하고, 상세 정보 크롤링은 이 산하 도시 목록에 포함된 City만 대상으로 한다.

최초 운영 범위는 대표 문서의 수집 우선순위에 맞춰 관동 지역 지자체를 우선 대상으로 둔다.

| 필드 | 수집 방식 | 수집 상태 | 설명 |
| --- | --- | --- | --- |
| `city_id` | 내부 생성 | 전부 수집 | 시스템 내부 지역 식별자 |
| `city_name_ko` | 도도부현 산하 도시 목록 / Wikipedia 크롤링 / 수동 정규화 | 전부 수집 | 한국어 도시명 |
| `city_name_ja` | 도도부현 산하 도시 목록 / Wikipedia 크롤링 / Wikidata | 전부 수집 | 일본어 원문 도시명 |
| `prefecture` | 도도부현 간략 정보 / 행정구역 데이터 | 전부 수집 | 도도부현 |
| `location` | 산하 도시 Wikipedia 크롤링 / Wikidata | 전부 수집 | 위치 정보, 좌표 또는 행정 위치 |
| `latitude` | 산하 도시 Wikipedia 크롤링 / Wikidata | 전부 수집 | 대표 위도 |
| `longitude` | 산하 도시 Wikipedia 크롤링 / Wikidata | 전부 수집 | 대표 경도 |
| `description` | 산하 도시 Wikipedia 크롤링 기반 요약 | 전부 수집 | 도시 역사·문화·특징 설명 |
| `climate` | Wikipedia 취득 후 일본기상청(JMA) 자료와 비교 | 전부 수집 | 기후 개요 또는 월별 기후 메모 |
| `site_url` | Wikipedia 외부 링크 / 공식 관광 사이트 | 전부 수집 | 도시 또는 관광 공식 사이트 |

## 2.3 Attraction 데이터

Attraction은 도시와 1:N 관계를 가지며, 일정 카드와 추천 결과 상세 화면의 핵심 소재로 사용한다.

| 필드 | 수집 방식 | 수집 상태 | 설명 |
| --- | --- | --- | --- |
| `attraction_id` | 내부 생성 | 전부 수집 | 관광지 식별자 |
| `city_id` | City 매핑 | 전부 수집 | 소속 도시 |
| `name` | JNTO / JTA | 전부 수집 | 관광지명 |
| `address` | JNTO / JTA / 공식 사이트 | 전부 수집 | 주소 |
| `description` | JNTO / JTA 기반 요약 | 전부 수집 | 관광지 설명 |
| `site_url` | JNTO / JTA / 공식 사이트 | 전부 수집 | 공식 또는 안내 페이지 |
| `opening_hours` | 공식 사이트 / 검수 | 전부 수집 | 운영시간 |
| `opening_period` | 공식 사이트 / 검수 | 전부 수집 | 계절 운영기간 |
| `latitude` | JNTO / Wikidata / 지도 보조 | 전부 수집 | 위도 |
| `longitude` | JNTO / Wikidata / 지도 보조 | 전부 수집 | 경도 |
| `admission_fee` | 공식 사이트 / 검수 | 전부 수집 | 입장료 |
| `photo_url` | JNTO / 공식 사이트 / 검수 | 전부 수집 | 대표 사진 URL |

## 2.4 Festival 데이터

Festival은 도시와 1:N 관계를 가지며, 월별 추천과 계절성 추천의 주요 근거로 사용한다.

| 필드 | 수집 방식 | 수집 상태 | 설명 |
| --- | --- | --- | --- |
| `festival_id` | 내부 생성 | 전부 수집 | 축제 식별자 |
| `city_id` | City 매핑 | 전부 수집 | 개최 도시 |
| `name` | JNTO / JTA | 전부 수집 | 축제명 |
| `address` | JNTO / JTA / 공식 사이트 | 전부 수집 | 개최 장소 주소 |
| `period` | JNTO / JTA / 공식 사이트 | 전부 수집 | 개최 기간 또는 개최 월 |
| `description` | JNTO / JTA 기반 요약 | 전부 수집 | 축제 설명 |
| `site_url` | JNTO / JTA / 공식 사이트 | 전부 수집 | 공식 또는 안내 페이지 |
| `photo_url` | JNTO / 공식 사이트 / 검수 | 전부 수집 | 대표 사진 URL |

## 2.5 VisitorStatistics 데이터

VisitorStatistics는 도시별 추천 보조 지표와 월별·지역별 수요 판단에 사용한다.

일본 통계는 한국 DataLabService처럼 확정 수량을 전제로 하지 않고, JNTO Statistics, e-Stat, RESAS에서 제공 가능한 집계 단위를 우선 수집한 뒤 City와 연결한다.

| 필드 | 수집 방식 | 수집 상태 | 설명 |
| --- | --- | --- | --- |
| `statistics_id` | 내부 생성 | 전부 수집 | 통계 식별자 |
| `city_id` | City 매핑 | 전부 수집 | 연결 City |
| `period` | JNTO Statistics / e-Stat / RESAS | 전부 수집 | 월별 또는 연도별 집계 기간 |
| `metric_name` | 원본 통계 항목 | 전부 수집 | 방문객 수, 관광 지표, 지역 지표명 |
| `metric_value` | 원본 통계 수치 | 전부 수집 | 지표 값 |
| `metric_unit` | 원본 통계 단위 | 전부 수집 | 명, 건, 비율 등 |
| `source_name` | JNTO Statistics / e-Stat / RESAS | 전부 수집 | 통계 출처 |
| `source_url` | 원본 API 또는 통계 페이지 | 전부 수집 | 원본 링크 |

# 3. 데이터 소스 전략

## 3.1 Wikipedia

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 도도부현 간략 정보, 산하 도시 목록, 산하 도시 위치 정보와 역사·문화 개요 |
| 취득 대상 | 도도부현 이름, 도도부현 간략 설명, 산하 도시 목록, 산하 도시명, 위치, 설명, 기후, 사이트 링크 |
| 장점 | 도도부현 단위에서 크롤링 대상 City 목록을 먼저 확정하고, 산하 도시 단위 설명과 위치 정보를 체계적으로 취득할 수 있다. |
| 한계 | 관광지·축제 상세 정보는 불완전할 수 있고, 설명문 사용 시 라이선스 표기가 필요하다. |
| 적용 방식 | Wikipedia API 또는 도도부현 문서에서 간략 정보와 산하 도시 목록을 우선 확보하고, 산하 도시 목록에 포함된 City 문서만 Wikipedia 크롤링 대상으로 삼아 설명·위치·외부 링크·기후를 추출한다. |

## 3.2 JNTO 관광 데이터

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 관광지 정보, 축제 정보 |
| 취득 대상 | 관광지명, 주소, 설명, 사이트 링크, 축제명, 기간, 축제 설명 |
| 장점 | 일본 공식 관광 데이터로 신뢰도가 높고, 관광지·축제 정보 품질이 좋다. |
| 한계 | 운영시간, 입장료, 사진은 항목별 누락 가능성이 있다. |
| 적용 방식 | Attraction과 Festival 자동 수집의 1차 소스로 사용한다. |

## 3.3 JTA 관광 DB

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 관광지 상세 설명, 축제 상세 설명 |
| 취득 대상 | 관광지 설명, 문화 정보, 지역 특산품, 축제 설명 |
| 장점 | 설명 데이터 품질이 높고 전국 단위 보강에 적합하다. |
| 한계 | 실제 제공 데이터 구조와 이용 조건 확인이 필요하다. |
| 적용 방식 | JNTO 데이터의 설명 보강 소스로 사용한다. |

## 3.4 일본 정부 통계 및 JNTO Statistics

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 통계 데이터 |
| 취득 대상 | 방문객 수, 관광 통계, 지역별 통계 |
| 장점 | 추천 품질 향상과 혼잡도·수요 분석에 활용할 수 있다. |
| 한계 | 추천 점수에 바로 반영하려면 지표 해석 기준을 추가로 정의해야 한다. |
| 적용 방식 | 지역별 방문객 수와 관광 통계를 함께 수집하고 City 기준 보조 지표로 연결한다. |

## 3.5 보조 공식·공공 출처

| 출처 | 사용 목적 | 적용 방식 |
| --- | --- | --- |
| e-Stat / Statistical LOD | 행정구역 코드, 지역 통계, 시정촌 메타데이터 | City 정규화와 통계 보강 |
| 국토교통성 국토수치정보 | 좌표, 행정구역, 철도역·교통 데이터 | 위치·접근성 데이터 취득 |
| 일본기상청(JMA) | 월별 기후·관측 데이터 | Wikipedia에서 취득한 City `climate` 비교 검증 |
| 도도부현·시정촌 공식 관광 사이트 | 운영시간, 입장료, 최신 축제 일정 확인 | 누락·최신성 확인 |

# 4. 전체 취득 범위

## 4.1 전체 수집 대상

아래 항목은 모두 최초 취득 대상으로 둔다. 자동 수집에서 누락되거나 신뢰도가 낮은 값은 제외하지 않고 공식 사이트 확인, Web Search Worker, 수동 검수로 이어서 채운다.

| 구분 | 수집 항목 | 주요 출처 | 누락 시 처리 |
| --- | --- | --- | --- |
| 도시 | 도도부현 간략 정보, 산하 도시 목록, 도시명, 위치, 설명, 기후, 사이트 링크, 위도, 경도 | Wikipedia API, Wikipedia 크롤링, Wikidata, JMA 비교 자료 | `needs_review` 또는 산하 도시 목록 재확인 |
| 관광지 | 관광지명, 운영시간, 운영기간, 주소, 위도, 경도, 설명, 입장료, 사이트 링크, 사진 | JNTO, JTA, 공식 사이트, Wikidata | 공식 사이트 확인 또는 Web Search Worker |
| 축제 | 축제명, 주소, 기간, 설명, 사진, 사이트 링크 | JNTO, JTA, 공식 사이트 | 공식 사이트 확인 또는 수동 검수 |
| 통계 | 방문객 수, 관광 통계, 지역별 지표 | JNTO Statistics, e-Stat, RESAS | 집계 단위 확인 후 `needs_review` |

## 4.2 취득 상태 관리

| 취득 상태 | 기준 | 처리 방식 |
| --- | --- | --- |
| `collected` | 자동 수집 값이 있고 출처가 명확함 | JSON 저장 후 S3 Raw Bucket 적재 |
| `needs_review` | 값은 있으나 표현이 모호하거나 최신성 확인이 필요함 | 수동 검수 |
| `missing` | 자동 수집에서 값을 찾지 못함 | Web Search 또는 수동 입력 대상 |
| `blocked` | 약관·저작권·접근 제한으로 수집 불가 | 딥링크 또는 빈 값으로 대체하고 사유 기록 |

## 4.3 공식 확인 우선순위

| 항목 | 확인 우선순위 | 사유 |
| --- | --- |
| 운영시간 | 높음 | 사용자 질문 빈도가 높고 일정 구성에 직접 영향을 준다. |
| 운영기간 | 높음 | 계절 운영, 휴관일, 임시 중단 등 예외가 많다. |
| 입장료 | 중간 | 무료·유료·계절 요금·패키지 요금이 혼재한다. |
| 사진 | 중간 | 저작권과 외부 핫링크 문제가 있어 검증이 필요하다. |
| 위도·경도 | 높음 | 지도 표시와 동선 계산에 필요하다. |

공식 사이트 또는 수동 검수로 확인한 값에는 `verified_at`, `verified_source_url`, `verification_note`를 함께 기록한다.

# 5. 수집 전략

## 5.1 자동 수집 전략

| 대상 | 자동 수집 소스 | 처리 방식 |
| --- | --- | --- |
| 도시 | Wikipedia API, Wikipedia 크롤링, Wikidata, JMA | 관동 지역 도도부현과 산하 지자체를 우선 대상으로 삼는다. 도도부현 간략 정보와 산하 도시 목록을 먼저 추출하고, 산하 도시 목록에 포함된 City 문서만 크롤링해 설명·위치·외부 링크·기후를 추출한다. 기후는 일본기상청(JMA) 자료와 비교한 뒤 City 테이블로 정규화한다. |
| 관광지 | JNTO, JTA, 공식 사이트, Wikidata | 관광지명, 운영시간, 운영기간, 주소, 위도, 경도, 설명, 입장료, 사이트 링크, 사진을 추출하고 City와 매핑한다. |
| 축제 | JNTO, JTA, 공식 사이트 | 축제명, 주소, 기간, 설명, 사진, 사이트 링크를 추출하고 City와 매핑한다. |
| 통계 | JNTO Statistics, e-Stat, RESAS | 방문객 수, 관광 통계, 지역별 지표를 수집하고 City 기준 보조 지표로 연결한다. |

## 5.2 공식 확인 및 검수 전략

공식 확인과 검수는 자동 수집에서 실패했거나 검수 필요 상태로 분류된 항목에 적용한다. 이 과정은 별도 단계가 아니라 같은 취득 파이프라인의 후속 처리로 본다.

| 확인 항목 | 입력 기준 |
| --- | --- |
| 운영시간 | 공식 사이트에 명시된 최신 운영시간만 입력 |
| 운영기간 | 계절 운영 또는 축제 기간이 명확한 경우 입력 |
| 입장료 | 공식 사이트 또는 공공 관광 페이지에 있는 금액만 입력 |
| 사진 | 사용 가능 조건이 명확한 공식 이미지 또는 내부 제작 이미지 사용 |

## 5.3 데이터 정규화 규칙

- 도시명은 `city_name_ja`, `city_name_ko`, `city_name_en`을 분리 저장한다.
- 도도부현 간략 정보와 산하 도시 목록의 Wikipedia API 응답 또는 HTML 원본, 산하 도시 Wikipedia HTML 크롤링 원본을 Raw 데이터로 보존한다.
- 관광지와 축제는 반드시 `city_id`를 가진다.
- 기간 정보는 원문 문자열(`period_text`)과 정규화 값(`start_date`, `end_date`, `month`)을 함께 저장한다.
- 운영시간과 입장료는 최신성이 낮을 수 있으므로 `data_confidence`를 별도 기록한다.
- 외부 설명문은 원문 복제가 아니라 내부 요약문으로 재작성한다.

# 6. 단일 취득 파이프라인

## 6.1 처리 흐름

```text
자동 수집
↓
취득 상태 분류
↓
공식 사이트 확인 / Web Search Worker
↓
수동 검수
↓
JSON 직렬화
↓
data/JP/*.json 검증 산출물 생성
↓
S3 Raw Bucket 적재 대상 확정
```

정의된 모든 필드가 JSON 원본으로 저장되도록 시도하는 것이 목표다. 수집 결과는 엔티티 유형과 출처별 JSON 문서로 직렬화하고 `data/JP/*.json` 로컬 검증 산출물로 구조를 확인한 뒤 S3 Raw Bucket 적재 대상으로 확정한다. Raw 원본을 일정 기간 누적 보관한 뒤 Lambda가 전처리하고 DynamoDB에 적재하는 과정은 전처리 계획서에서 관리한다. 운영시간·입장료·사진도 최초 수집 대상에 포함하며, 자동 수집 실패 시 `missing` 또는 `needs_review` 상태로 남기고 같은 취득 파이프라인 안에서 공식 확인 또는 수동 검수로 채운다.

예시:

```text
사용자 질문: 도쿄타워 운영시간 알려줘

1. DB에서 도쿄타워 Attraction 조회
2. opening_hours가 없거나 오래된 값이면 Web Search Worker 실행
3. 공식 사이트 또는 공식 관광 페이지 확인
4. 운영시간과 확인 출처를 함께 반환
```

## 6.2 Web Search Worker 적용 조건

| 조건 | 처리 |
| --- | --- |
| DB에 정보 없음 | 공식 사이트 검색 |
| 운영시간·입장료 값이 오래됨 | 공식 사이트 재확인 |
| 축제 기간이 연도별로 바뀜 | 해당 연도 공식 페이지 확인 |
| 공식 출처가 아닌 블로그·SNS만 존재 | 답변 근거로 사용하지 않거나 낮은 신뢰도로 표시 |

# 7. 저장 구조

## 7.1 로컬 검증 산출물과 S3 Raw 계약

```text
City
Attraction
Festival
VisitorStatistics
S3 Raw Bucket
```

수집 원본은 DB에 바로 쓰지 않고 JSON 파일로 저장한 뒤 S3 Raw Bucket에 적재한다. S3 객체는 국가, 출처, 엔티티 유형, 수집일 기준 Prefix로 구분한다. 일정 기간 누적된 Raw Prefix는 Lambda 배치 전처리의 입력으로 재사용하며, 전처리 결과만 DynamoDB에 정규화 Item으로 적재한다.

| 로컬 파일 | 내용 | S3 Raw 적재 기준 |
| --- | --- | --- |
| `data/JP/prefectures.json` | 관동 지역 도도부현 간략 정보 | `raw/JP/wikipedia/prefecture/{yyyy}/{mm}/{dd}/` |
| `data/JP/cities.json` | 관동 지역 산하 지자체 City 목록과 상세 정보 | `raw/JP/wikipedia/city/{yyyy}/{mm}/{dd}/` |
| `data/JP/attractions.json` | JNTO/JTA/공식 사이트 기반 관광지 | `raw/JP/jnto/attraction/{yyyy}/{mm}/{dd}/` |
| `data/JP/festivals.json` | JNTO/JTA/공식 사이트 기반 축제 | `raw/JP/jnto/festival/{yyyy}/{mm}/{dd}/` |
| `data/JP/visitor_statistics.json` | JNTO Statistics, e-Stat, RESAS 기반 관광 통계 | `raw/JP/statistics/visitor_statistics/{yyyy}/{mm}/{dd}/` |

## 7.2 City 예시

| 필드 | 예시 |
| --- | --- |
| `city_id` | `JP-TOKYO-TAITO` |
| `city_name_ko` | 다이토구 |
| `city_name_ja` | 台東区 |
| `prefecture` | 東京都 |
| `description` | 아사쿠사와 우에노를 중심으로 전통 문화와 도시 관광 자원이 밀집한 도쿄의 지자체 |
| `climate` | 여름은 고온다습하고 겨울은 비교적 건조하다. 봄·가을 관광 적합도가 높다. |
| `site_url` | 공식 관광 사이트 URL |

## 7.3 Attraction 예시

| 필드 | 예시 |
| --- | --- |
| `name` | 東京スカイツリー |
| `city_id` | `JP-TOKYO-SUMIDA` |
| `address` | 東京都墨田区押上 |
| `description` | 전망대와 상업시설을 함께 갖춘 도쿄 동부의 대표 관광지 |
| `opening_hours` | 공식 사이트 확인값 |
| `admission_fee` | 공식 사이트 확인값 |
| `site_url` | 공식 사이트 URL |

## 7.4 Festival 예시

| 필드 | 예시 |
| --- | --- |
| `name` | 三社祭 |
| `city_id` | `JP-TOKYO-TAITO` |
| `address` | 東京都台東区浅草 |
| `period` | 매년 5월 |
| `description` | 아사쿠사 신사를 중심으로 열리는 도쿄의 대표 전통 축제 |
| `photo_url` | 공식 또는 사용 가능 조건이 확인된 이미지 URL |

## 7.5 VisitorStatistics 예시

| 필드 | 예시 |
| --- | --- |
| `statistics_id` | `JP-TOKYO-STAT-202501` |
| `city_id` | `JP-TOKYO-TAITO` |
| `period` | `2025-01` |
| `metric_name` | 방문객 수 |
| `metric_value` | 원본 통계 수치 |
| `metric_unit` | 명 |
| `source_name` | JNTO Statistics |
| `source_url` | 원본 통계 페이지 URL |

# 8. 품질 검증 기준

| 검증 항목 | 기준 |
| --- | --- |
| City 매핑 | 모든 Attraction, Festival, VisitorStatistics는 하나의 City에 연결되어야 한다. |
| 출처 기록 | 모든 자동 수집 데이터는 `source_name`, `source_url`, `collected_at`을 가진다. |
| 전체 필드 상태 | 정의된 모든 필드는 `collected`, `needs_review`, `missing`, `blocked` 중 하나의 상태를 가진다. |
| 최신성 | 운영시간, 운영기간, 입장료는 확인일을 기록한다. |
| 기후 정합성 | Wikipedia에서 취득한 City `climate`를 일본기상청(JMA) 자료와 비교하고 불일치 여부를 검수 메타데이터로 남긴다. |
| 통계 정합성 | VisitorStatistics는 집계 기간, 지표명, 단위, 출처 URL을 가져야 하며 City 매핑이 불명확하면 `needs_review`로 둔다. |
| 저작권 | 사진과 설명문은 사용 가능 조건을 확인한다. 설명문은 내부 요약문으로 저장한다. |
| 공식성 | 자동 수집과 Web Search Worker는 공식 사이트 또는 공공 관광 페이지를 우선한다. |

# 9. 법적·운영 제약

- Wikipedia 기반 설명은 라이선스 조건에 따라 출처와 원문 링크를 기록한다.
- JNTO, JTA, 지자체 관광 페이지는 이용약관과 크롤링 허용 범위를 확인한다.
- 사진은 저작권 위험이 크므로 자동 수집 값이 있더라도 사용 가능 조건을 확인하고, 불명확하면 `needs_review` 또는 `blocked`로 관리한다.
- 상업 플랫폼의 숙박·맛집 데이터는 직접 저장보다 딥링크 제공을 우선한다.
- 운영시간과 입장료는 변경 가능성이 높으므로 "확인일 기준" 문구를 서비스에 표시한다.

# 10. 운영 반영 방향

본 문서의 핵심 내용은 일본 데이터 취득 계획의 실제 운영 기준으로 정리한다.
문서 확정 후에는 대표 데이터 취득 계획, 전처리 계획, 공유용 HTML, PDF 산출물이 같은 기준을 바라보도록 순차적으로 동기화한다.

1. 일본 우선 수집 범위는 관동 지역 지자체를 기준으로 시작하고, 이후 동일한 구조로 다른 지역을 확장한다.
2. City는 도도부현 간략 정보와 산하 도시 목록을 먼저 확보한 뒤 산하 City 문서만 크롤링한다.
3. Attraction과 Festival은 JNTO, JTA, 공식 관광 사이트를 우선하고 누락 항목은 Web Search Worker 또는 수동 검수로 채운다.
4. VisitorStatistics는 JNTO Statistics, e-Stat, RESAS의 제공 가능한 집계 단위를 City 보조 지표로 연결한다.
5. 수집 결과는 `data/JP/*.json` 로컬 검증 산출물로 확인한 뒤 S3 Raw Prefix 적재 대상으로 확정한다.
6. 공유용 HTML과 PDF 산출물은 확정된 데이터 취득 계획을 사용자가 바로 확인할 수 있는 형태로 갱신한다.

# 11. 참고 출처

- Wikipedia: https://www.wikipedia.org/
- JNTO: https://www.jnto.go.jp/
- Japan Tourism Statistics: https://statistics.jnto.go.jp/en/
- e-Stat API: https://www.e-stat.go.jp/api/
- Statistical LOD Area Data: https://data.e-stat.go.jp/lodw/index.php/en/provdata/lodRegion
- 국토교통성 국토수치정보: https://nlftp.mlit.go.jp/ksj/
- 일본기상청 기후 데이터: https://www.data.jma.go.jp/stats/data/en/index.html

# 12. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-02 | LLM 파트 | 일본 데이터 취득 계획서 초안 작성 |
| v0.2 | 2026-06-02 | LLM 파트 | 데이터 모델, 자동 수집·검수 범위, Web Search Worker 확인 전략 구체화 |
| v0.3 | 2026-06-02 | LLM 파트 | 정의 필드를 모두 수집하고 누락 항목은 취득 상태로 관리하는 방향 반영 |
| v0.4 | 2026-06-02 | LLM 파트 | 단계 경계를 제거하고 도도부현 간략 정보와 산하 도시 목록 기반 City 크롤링, JSON 원본의 S3 저장, 기후 데이터 비교 검증 방식으로 재정리 |
| v0.5 | 2026-06-07 | LLM 파트 | 관동 우선 수집 범위, VisitorStatistics 보조 데이터, `data/JP/*.json` 검증 산출물, S3 Raw Prefix 기준 보완 |
