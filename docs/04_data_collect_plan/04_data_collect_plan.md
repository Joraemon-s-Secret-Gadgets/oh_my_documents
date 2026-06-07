# 로브 (Lovv) 데이터 수집 계획서

> 문서 버전: v0.5
> 문서 상태: 검토 중 (Review)
> 기준 문서: `docs/01_requirements/01_requirements.md` v1.7
> 상세 초안: `docs/04_data_collect_plan/korea_data_acquisition_plan.md`, `docs/04_data_collect_plan/japan_data_acquisition_plan.md`

# 1. 문서 개요

## 1.1 목적

본 문서는 지역 여행 추천 서비스인 로브(Lovv)의 추천 품질과 신뢰성을 확보하기 위해 필요한 한국 및 일본의 도시·관광지·축제 데이터를 한 번에 취득하기 위한 범위, 데이터 소스, 검증 방식, 저장 구조를 정의한다.

세부 국가별 취득 기준은 다음 문서에 분리하여 관리한다.

| 국가 | 상세 문서 | 역할 |
| --- | --- | --- |
| 한국 | `korea_data_acquisition_plan.md` | 강원·경북 40개 City와 TourAPI 4.0 기반 Attraction·Festival·DataLab 통계 취득 필드, 검수 기준 정의 |
| 일본 | `japan_data_acquisition_plan.md` | 일본 도도부현·산하 City·Attraction·Festival 취득 필드, Wikipedia·JNTO·JTA 중심 출처, 검수 기준 정의 |

## 1.2 수집 원칙

- **전체 취득**: City, Attraction, Festival의 정의된 필드는 최초 수집 대상에 모두 포함한다.
- **우선 취득 범위**: 한국은 강원과 경북의 40개 도시를 우선적으로 취득한 뒤 일본의 관동 지역 지자체를 수집한다.
- **한국 실제 검증 범위**: 한국은 `data/KR/cities.json`, `data/KR/attractions.json`, `data/KR/festivals.json`, `data/KR/visitor_statistics.json` 형태의 로컬 검증 산출물을 기준으로 S3 Raw 적재 전 품질을 확인한다.
- **공식 출처 우선**: 관광지 및 축제 정보는 양국 공식 관광 데이터, 공공데이터, 지자체 공식 사이트, 공식 관광 포털을 우선한다.
- **최신성 관리**: 운영시간, 운영기간, 입장료, 축제 기간처럼 변경 가능성이 높은 데이터는 확인일과 출처를 함께 저장한다.
- **일관성 유지**: 서로 다른 출처의 데이터를 통합할 때 명칭, 행정구역 코드, 좌표, 날짜 포맷의 매핑 기준을 통일한다.
- **출처 추적**: 모든 자동 수집 데이터는 `source_name`, `source_url`, `collected_at`, `data_confidence`를 기록한다.

# 2. 데이터 수집 계획 명세

## 2.1 프로젝트 주제

로브(Lovv)는 대도시 편중 현상(오버투어리즘)을 완화하고 여행자에게 덜 알려진 한국(시/군/구 단위) 및 일본(시/정/촌/구 단위)의 매력적인 지역과 그에 최적화된 여행 일정 및 문화 콘텐츠를 추천하는 서비스이다.

본 계획서는 한국과 일본의 지역 기반 추천을 위해 도시, 관광지, 축제 데이터를 공통 구조로 취득하고 국가별 출처 차이를 매핑하는 방안을 다룬다.

## 2.2 데이터 모델

추천 DB는 다음 관계를 기준으로 구축한다.

```text
City
 ├── Attraction
 └── Festival
```

| 관계 | 설명 |
| --- | --- |
| `City 1:N Attraction` | 하나의 도시는 여러 관광지를 가진다. |
| `City 1:N Festival` | 하나의 도시는 여러 축제·행사를 가진다. |

## 2.3 City 수집 항목

City는 추천의 기준 지역이다. 한국은 도의 간략 정보와 산하 시·군·구 목록을 먼저 취득하고, 일본은 도도부현의 간략 정보와 산하 시·정·촌·구 목록을 먼저 취득한다. 실제 도시 상세 정보 크롤링은 이 산하 도시 목록에 포함된 City만 대상으로 한다.

한국 실제 수집 기준에서는 강원과 경북의 40개 도시를 `KR-{도_코드}-{CITY_EN}` 형식의 `city_id`로 관리한다. 예시는 `KR-42-GANGNEUNG`, `KR-47-ANDONG`이며, 광역 단위는 `prefecture_id`로 연결한다. Wikipedia 기후 표는 `climate_table`로 보존하고 자동 취득 실패 시 `needs_review`로 관리한다.

| 필드 | 한국 주요 출처 | 일본 주요 출처 | 수집 상태 |
| --- | --- | --- | --- |
| `city_id` | 내부 생성 | 내부 생성 | 전부 수집 |
| `city_name_ko` | 도 산하 도시 목록, Wikipedia 크롤링, 행정구역 데이터 | 도도부현 산하 도시 목록, Wikipedia 크롤링, 수동 정규화 | 전부 수집 |
| `city_name_local` | 한국어 명칭 | 일본어 원문 명칭 | 전부 수집 |
| `province_or_prefecture` | 도 간략 정보, 행정구역 데이터 | 도도부현 간략 정보, e-Stat, Statistical LOD | 전부 수집 |
| `location` | 산하 도시 Wikipedia 크롤링, TourAPI, 행정구역 데이터 | 산하 도시 Wikipedia 크롤링, Wikidata | 전부 수집 |
| `latitude` | 산하 도시 Wikipedia 크롤링, TourAPI, Wikidata | 산하 도시 Wikipedia 크롤링, Wikidata | 전부 수집 |
| `longitude` | 산하 도시 Wikipedia 크롤링, TourAPI, Wikidata | 산하 도시 Wikipedia 크롤링, Wikidata | 전부 수집 |
| `description` | 산하 도시 Wikipedia 크롤링 기반 요약, 대한민국구석구석 기반 요약 | 산하 도시 Wikipedia 크롤링 기반 요약 | 전부 수집 |
| `climate` | Wikipedia 취득 후 기상청 API허브·기후통계와 비교 | Wikipedia 취득 후 일본기상청(JMA) 자료와 비교 | 전부 수집 |
| `site_url` | 지자체 문화관광 홈페이지, 대한민국구석구석 | Wikipedia 외부 링크, 공식 관광 사이트 | 전부 수집 |

## 2.4 Attraction 수집 항목

Attraction은 일정 카드와 추천 결과 상세 화면의 핵심 소재로 사용한다. 한국은 TourAPI 4.0(KorService2) 기준 강원·경북 관광지 3,709건을 실제 수집 및 명세 확인 범위로 둔다.

| 필드 | 한국 주요 출처 | 일본 주요 출처 | 수집 상태 |
| --- | --- | --- | --- |
| `attraction_id` | 내부 생성 | 내부 생성 | 전부 수집 |
| `city_id` | City 매핑 | City 매핑 | 전부 수집 |
| `source_content_id` | 한국관광공사 TourAPI `contentid` | JNTO/JTA 원본 ID 또는 URL | 전부 수집 |
| `name` | TourAPI, 대한민국구석구석 | JNTO, JTA | 전부 수집 |
| `address` | TourAPI, 공식 사이트 | JNTO, JTA, 공식 사이트 | 전부 수집 |
| `description` | TourAPI 공통정보·소개정보 기반 요약 | JNTO/JTA 기반 요약 | 전부 수집 |
| `site_url` | TourAPI, 공식 사이트 | JNTO, JTA, 공식 사이트 | 전부 수집 |
| `opening_hours` | TourAPI 소개정보, 공식 사이트, 검수 | 공식 사이트, 검수 | 전부 수집 |
| `opening_period` | TourAPI 소개정보, 공식 사이트, 검수 | 공식 사이트, 검수 | 전부 수집 |
| `latitude` | TourAPI 위치정보 | JNTO, Wikidata, 지도 보조 | 전부 수집 |
| `longitude` | TourAPI 위치정보 | JNTO, Wikidata, 지도 보조 | 전부 수집 |
| `admission_fee` | TourAPI 소개정보, 공식 사이트, 검수 | 공식 사이트, 검수 | 전부 수집 |
| `photo_url` | TourAPI 이미지정보, 공식 사이트, 검수 | JNTO, 공식 사이트, 검수 | 전부 수집 |

## 2.5 Festival 수집 항목

Festival은 월별 추천과 계절성 추천의 주요 근거로 사용한다. 한국은 TourAPI 4.0(KorService2) 기준 강원·경북 축제 106건을 실제 수집 및 명세 확인 범위로 둔다.

| 필드 | 한국 주요 출처 | 일본 주요 출처 | 수집 상태 |
| --- | --- | --- | --- |
| `festival_id` | 내부 생성 | 내부 생성 | 전부 수집 |
| `city_id` | City 매핑 | City 매핑 | 전부 수집 |
| `source_content_id` | TourAPI 행사 콘텐츠 ID | JNTO/JTA 원본 ID 또는 URL | 전부 수집 |
| `name` | TourAPI 행사정보, 대한민국구석구석 | JNTO, JTA | 전부 수집 |
| `address` | TourAPI, 공식 사이트 | JNTO, JTA, 공식 사이트 | 전부 수집 |
| `period` | TourAPI 행사 시작일·종료일, 공식 사이트 | JNTO, JTA, 공식 사이트 | 전부 수집 |
| `description` | TourAPI 공통정보·소개정보 기반 요약 | JNTO/JTA 기반 요약 | 전부 수집 |
| `site_url` | TourAPI, 공식 사이트 | JNTO, JTA, 공식 사이트 | 전부 수집 |
| `photo_url` | TourAPI 이미지정보, 공식 사이트, 검수 | JNTO, 공식 사이트, 검수 | 전부 수집 |

## 2.6 데이터 출처

### 2.6.1 한국 데이터 출처

| 출처 | 취득 데이터 | 적용 방식 |
| --- | --- | --- |
| 한국관광공사 TourAPI 4.0(KorService2) | 관광지, 축제, 이미지, 위치, 소개정보, 행사정보 | Attraction·Festival 자동 수집의 1차 소스 |
| 대한민국구석구석 | 관광지·축제 상세 링크, 공식 설명, 지역 관광 정보 | TourAPI 보강 및 공식 링크 확인 |
| 지자체 문화관광 홈페이지 | 운영시간, 입장료, 최신 축제 일정, 공식 공지 | 누락·최신성 확인 |
| Wikipedia API | 도 간략 정보, 도 산하 도시 목록, 원문 링크 | 한국 City 크롤링 대상 목록 확보 |
| Wikipedia 크롤링 / Wikidata | 도 산하 도시의 설명, 위치, 좌표, 외부 링크 | 산하 City 상세 정보 취득 및 보강 |
| 기상청 API허브 / 기후통계 | 월별 기후, 평균 기온, 강수량, 계절 메모 | Wikipedia에서 취득한 한국 City `climate` 비교 검증 및 월별 추천 근거 |
| 한국관광공사 관광 빅데이터 API(DataLabService) | 월별 현지인·외지인·외국인 방문객 통계 | City 보조 지표와 월별 추천 근거 |
| 행정구역 데이터 | 시·군·구 코드와 행정구역 정규화 | City ID와 지역 매핑 |

### 2.6.2 일본 데이터 출처

| 출처 | 취득 데이터 | 적용 방식 |
| --- | --- | --- |
| Wikipedia API / Wikipedia 크롤링 / Wikidata | 도도부현 간략 정보, 도도부현 산하 도시 목록, 산하 도시 설명·위치·좌표 | 일본 City 크롤링 대상 목록 확보 및 상세 정보 취득 |
| JNTO 관광 데이터 | 관광지, 축제, 설명, 주소, 링크 | Attraction·Festival 자동 수집의 1차 소스 |
| JTA 관광 DB | 관광지 상세 설명, 문화 정보, 지역 특산품, 축제 설명 | JNTO 데이터 설명 보강 |
| e-Stat / Statistical LOD | 행정구역 코드, 지역 통계, 시정촌 메타데이터 | City 정규화와 통계 보강 |
| 국토교통성 국토수치정보 | 좌표, 행정구역, 철도역·교통 데이터 | 위치·접근성 데이터 취득 |
| 일본기상청(JMA) | 월별 기후·관측 데이터 | Wikipedia에서 취득한 일본 City `climate` 비교 검증 및 월별 추천 근거 |
| JNTO Statistics / RESAS | 방문객 수, 관광 통계, 지역별 지표 | City 보조 지표 |
| 도도부현·시정촌 공식 관광 사이트 | 운영시간, 입장료, 최신 축제 일정 | 누락·최신성 확인 |

# 3. 데이터 취득 파이프라인

## 3.1 처리 흐름

```text
자동 수집
↓
로컬 검증 산출물 생성
↓
JSON 직렬화
↓
S3 Raw Bucket 적재
↓
Raw 보관 기간 경과
↓
Lambda 배치 전처리
↓
취득 상태 분류
↓
공식 사이트 확인 / Web Search Worker
↓
수동 검수
↓
정규화 DB 적재
```

정의된 모든 필드가 JSON 원본으로 저장되도록 시도한다. 한국은 실제 수집 검증 단계에서 `data/KR/*.json` 로컬 산출물로 City, Attraction, Festival, 방문객 통계의 구조와 수량을 먼저 확인한다. 이후 수집 결과는 엔티티 유형과 출처별 JSON 문서로 직렬화한 뒤 S3 Raw Bucket에 적재한다. Raw 데이터는 재사용과 재처리를 위해 일정 기간 누적 보관하고, 보관 기간 또는 배치 기준이 충족되면 Lambda가 해당 Prefix의 JSON 원본을 읽어 전처리한 뒤 DynamoDB에 적재한다. 운영시간, 운영기간, 입장료, 사진, 축제 기간처럼 출처별 표현 차이가 큰 값도 최초 수집 대상에 포함하며, 자동 수집 실패 시 같은 파이프라인 안에서 공식 확인 또는 수동 검수로 채운다.

## 3.2 취득 상태 관리

| 취득 상태 | 기준 | 처리 방식 |
| --- | --- | --- |
| `collected` | 자동 수집 값이 있고 출처가 명확함 | JSON 저장 후 S3 Raw Bucket 적재 |
| `needs_review` | 값은 있으나 표현이 모호하거나 최신성 확인이 필요함 | 공식 사이트 확인 또는 수동 검수 |
| `missing` | 자동 수집에서 값을 찾지 못함 | Web Search Worker 또는 수동 입력 대상 |
| `blocked` | 약관·저작권·접근 제한으로 수집 불가 | 딥링크 또는 빈 값으로 대체하고 사유 기록 |

## 3.3 원본 및 정규화 저장

| 구분 | 저장 내용 |
| --- | --- |
| Raw 데이터 | API 응답, Wikipedia HTML 수집 원본, 공식 사이트 확인 결과, 이미지 메타데이터를 JSON 문서로 저장한 S3 객체 |
| 로컬 검증 산출물 | 한국 `data/KR/*.json`처럼 S3 Raw 적재 전 수집 구조와 수량을 검증하는 JSON 파일 |
| S3 Raw 객체 | `raw/{country}/{source}/{entity_type}/{yyyy}/{mm}/{dd}/` Prefix에 저장되는 원본 JSON |
| Raw 보관 및 배치 처리 | 일정 기간 Raw Prefix에 누적한 뒤 Lambda 배치 전처리 대상으로 사용 |
| 정규화 데이터 | City, Attraction, Festival, 기후, 통계, 검색 링크 |
| 검수 메타데이터 | `verified_at`, `verified_source_url`, `verification_note`, `data_confidence` |
| 출처 메타데이터 | `source_name`, `source_url`, `collected_at`, `license_type` |

# 4. 데이터 품질 정합성 관리 방법

수집된 데이터의 품질 및 매핑 신뢰성을 보장하기 위해 다음 검증 기준을 적용한다.

| 검증 항목 | 기준 |
| --- | --- |
| City 매핑 | 모든 Attraction과 Festival은 하나의 City에 연결되어야 한다. |
| 행정구역 정합성 | 한국 시·군·구 코드와 일본 시·정·촌·구 코드가 내부 City ID와 일치해야 한다. |
| 한국 실제 수집 수량 | 한국 강원·경북 기준 City 40개, Attraction 3,709건, Festival 106건, 방문객 통계 12개월 범위를 확인한다. |
| 출처 기록 | 모든 자동 수집 데이터는 출처명, 출처 URL, 수집 시각을 가진다. |
| 전체 필드 상태 | 정의된 모든 필드는 `collected`, `needs_review`, `missing`, `blocked` 중 하나의 상태를 가진다. |
| 최신성 | 운영시간, 운영기간, 입장료, 축제 기간은 확인일을 기록한다. |
| 기후 정합성 | City `climate`는 Wikipedia 취득값을 기준으로 하되 한국은 기상청, 일본은 일본기상청(JMA) 자료와 비교해 불일치 여부를 기록한다. |
| 링크 유효성 | 공식 URL과 딥링크는 HTTP 상태와 리다이렉션을 주기적으로 점검한다. |
| 저작권 | 사진과 설명문은 사용 가능 조건을 확인한다. 설명문은 내부 요약문으로 저장한다. |
| 다국어 매핑 | 일본 지역명·축제명은 일본어 원문과 한국어 표기가 같은 대상을 가리키는지 대조한다. |

# 5. 법적 요소 검토

공공데이터 및 오픈 백과사전을 활용하는 만큼 기본 라이선스 기준에 근거하여 법적 의무 사항을 준수한다.

- **위키피디아 라이선스 준수**: 위키피디아 한국어/일본어 버전의 텍스트 콘텐츠는 CC BY-SA 라이선스 조건에 따라 출처와 원문 링크를 기록한다.
- **한국 공공데이터 활용 조건 준수**: 한국관광공사 TourAPI, 대한민국구석구석, 공공데이터포털, 지자체 데이터는 공공누리 유형과 API 이용 조건을 확인한다.
- **일본 공식·상업 플랫폼 제약 준수**: JNTO, JTA, 지자체 관광 사이트, Yahoo Japan, じゃらん, 楽天トラベル, 食べログ 등은 이용약관과 크롤링 허용 범위를 확인한다.
- **사진 사용 조건 확인**: 사진은 저작권 위험이 크므로 자동 수집 값이 있더라도 사용 가능 조건을 확인하고, 불명확하면 `needs_review` 또는 `blocked`로 관리한다.
- **변동 정보 표시**: 운영시간, 입장료, 축제 기간은 변경 가능성이 높으므로 서비스 화면에 "확인일 기준" 문구를 표시한다.

# 6. 수집 정책 및 제외 범위

- **수집 주기**: City 기본 정보는 연 1회 이상, 운영시간·입장료·축제 기간은 최신성 상태에 따라 재확인한다.
- **Raw 재사용**: 수집 JSON은 S3 Raw Bucket에 일정 기간 보관하여 재처리, 검수 기준 변경, DynamoDB 재적재에 재사용한다.
- **전처리 실행**: Raw 데이터가 일정 기간 또는 처리 기준만큼 누적되면 Lambda 배치 전처리를 실행하고 DynamoDB에 정규화 결과를 적재한다.
- **실시간 응답 보강**: DB 값이 없거나 오래된 경우 Web Search Worker가 공식 사이트 또는 공공 관광 페이지를 확인한다.
- **상업 플랫폼 데이터**: 숙박·맛집 플랫폼 데이터는 직접 저장보다 검색 딥링크 제공을 우선한다.
- **본문 원문 저장 제한**: 외부 설명문은 원문 전체 복제가 아니라 내부 요약문으로 저장한다.

# 7. 본 문서 반영 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-02 | LLM 파트 | 데이터 수집 계획서 초안 및 일관된 템플릿 구조 작성 |
| v0.2 | 2026-06-02 | LLM 파트 | 한일 수집 범위, 3종 데이터 모델, 전처리 인프라, 품질·법적 검토 기준 반영 |
| v0.3 | 2026-06-02 | LLM 파트 | 한국·일본 데이터 취득 초안을 main 문서에 반영하고 전체 필드 일괄 취득 전략으로 재정리 |
| v0.4 | 2026-06-06 | LLM 파트 | 도·도도부현 간략 정보와 산하 도시 목록 기반 City 크롤링, JSON 원본의 S3 저장, 기후 데이터 비교 검증 방식 구체화 |
| v0.5 | 2026-06-06 | LLM 파트 | 한국 강원·경북 40개 도시 실제 수집 결과, TourAPI 4.0, DataLabService, `data/KR/*.json` 로컬 검증 산출물과 S3 Raw 적재 관계 반영 |

v0.4에서는 City 취득 범위와 원본 저장 방식을 정리했다. 한국은 도의 간략 정보와 산하 도시 목록, 일본은 도도부현의 간략 정보와 산하 도시 목록을 먼저 확보하고, 실제 Wikipedia 크롤링은 해당 산하 도시 목록에 포함된 City만 대상으로 수행한다. 취득 결과는 JSON 문서로 저장한 뒤 S3 Raw Bucket에 일정 기간 누적 보관하고, Lambda 배치 전처리 후 DynamoDB에 정규화 결과를 적재한다. 기후 정보는 양국 모두 Wikipedia 취득값을 기준으로 하되 한국은 기상청, 일본은 일본기상청(JMA) 자료와 비교해 정합성을 확인한다.

v0.5에서는 한국 실제 수집 결과를 반영했다. 강원과 경북의 40개 City는 `KR-{도_코드}-{CITY_EN}` 형식으로 관리하며, 관광지는 TourAPI 4.0 기준 3,709건, 축제는 106건을 실제 수집 및 명세 확인 범위로 둔다. DataLabService 기반 월별 방문객 통계는 City 보조 지표와 월별 추천 근거로 활용한다. `data/KR/*.json`은 최종 DB가 아니라 S3 Raw Bucket 적재 전 로컬 검증 산출물로 정의한다.
