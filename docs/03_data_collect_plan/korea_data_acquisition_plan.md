# 한국 데이터 취득 계획서

> 문서 버전: v0.4.1
> 문서 상태: 실제 수집 데이터 구조 및 API 명세 분석 결과 반영
> 작성일: 2026-06-06
> 기준 문서: `docs/03_data_collect_plan/korea_data_acquisition_plan_updated.md` v0.3
> 동기화 대상 문서: `docs/03_data_collect_plan/03_data_collect_plan.md`
> 공유 산출물: `pages/03_data_collect_plan.html`, `pdf/korea_data_acquisition_plan.pdf`

# 1. 목적

본 문서는 여행 추천 Multi-Agent 서비스에서 한국 소도시 추천에 필요한 도시·관광지·축제·방문객 통계 데이터를 취득하기 위한 범위, 데이터 소스, 검증 방식, 저장 구조를 정의한다.

이번 문서의 기준은 실제 수집과 TourAPI 명세 확인을 거친 강원·경북 40개 도시 데이터다.
로컬 `data/KR/*.json` 파일은 실제 수집 검증 산출물이자 S3 Raw Bucket 적재 전 입력으로 관리한다.
서비스 조회용 정규화 데이터는 S3 Raw 누적 후 Lambda 전처리를 거쳐 DynamoDB에 적재한다.

핵심 방향은 다음과 같다.

- City, Attraction, Festival, 방문객 통계의 정의된 항목을 모두 최초 취득 대상으로 둔다.
- 한국은 강원·경북 40개 도시를 실제 수집 검증 범위로 둔다.
- City는 Wikipedia/Wikidata 기반으로 취득하고, `KR-{도_코드}-{CITY_EN}` 형식의 안정 ID를 사용한다.
- 관광지와 축제는 한국관광공사 TourAPI 4.0(KorService2)을 중심으로 취득한다.
- 방문객 통계는 한국관광공사 관광 빅데이터 API(DataLabService)를 활용한다.
- 운영시간, 입장료, 사진처럼 실제 제공률이 낮거나 변동성이 큰 값은 `missing` 또는 `needs_review` 상태로 관리한다.
- 자동 수집, 공식 사이트 확인, Web Search Worker, 수동 검수를 하나의 취득 파이프라인으로 묶어 처리한다.

# 2. 목표 데이터 모델

## 2.1 관계 구조

```text
Prefecture
 └── City
      ├── Attraction
      ├── Festival
      └── VisitorStatistics
```

| 관계 | 설명 |
| --- | --- |
| `Prefecture 1:N City` | 강원과 경북 같은 광역 단위는 여러 City를 가진다. |
| `City 1:N Attraction` | 하나의 한국 도시는 여러 관광지를 가진다. |
| `City 1:N Festival` | 하나의 한국 도시는 여러 축제·행사를 가진다. |
| `City 1:N VisitorStatistics` | 하나의 한국 도시는 월별 방문객 통계를 가진다. |

## 2.2 City 데이터

City는 추천의 기준 지역이다.
한국 목적지는 시·군·구 단위의 소도시를 기본 단위로 관리한다.
강원과 경북의 40개 도시는 `data/KR/cities.json` 형태로 실제 수집과 검증을 완료한 기준 데이터로 본다.

| 필드 | 수집 방식 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| `city_id` | 내부 생성 | 수집 확인 | 형식: `KR-{도_코드}-{CITY_EN}`. 예: `KR-42-GANGNEUNG`, `KR-47-ANDONG` |
| `city_name_ko` | Wikipedia / 수동 정규화 | 수집 확인 | 한국어 도시명 |
| `prefecture_id` | Wikipedia / Wikidata | 수집 확인 | 광역시·도 단위 외래키. `data/KR/prefectures.json` 참조 |
| `location` | Wikipedia / Wikidata | 수집 확인 | 행정 위치 문자열 |
| `latitude` | Wikipedia / Wikidata | 수집 확인 | 대표 위도 |
| `longitude` | Wikipedia / Wikidata | 수집 확인 | 대표 경도 |
| `description` | Wikipedia 기반 내부 요약 | 수집 확인 | 도시 역사·문화·특징 설명 |
| `climate_table` | Wikipedia | 검토 필요 | Wikipedia 기후 표 wikitext. 자동 취득 실패 시 `needs_review` |
| `site_urls` | 지자체 관광 사이트 / Wikipedia 외부 링크 | 수집 확인 | 도시 공식·관광 사이트 URL 목록 |
| `field_status` | 수집 파이프라인 | 수집 확인 | 필드별 `collected`, `needs_review`, `missing`, `blocked` 상태 |

## 2.3 Attraction 데이터

Attraction은 도시와 1:N 관계를 가지며 일정 카드와 추천 결과 상세 화면의 핵심 소재로 사용한다.
강원·경북 기준 TourAPI 4.0(KorService2) 수집 결과 3,709건을 명세 확인 기준으로 둔다.

| 필드 | TourAPI 원본 필드 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| `attraction_id` | `contentid` 기반 내부 생성 | 수집 확인 | 형식: `KR-{도_코드}-{CITY_EN}-ATT-{contentid}` |
| `city_id` | 내부 매핑 | 수집 확인 | `data/KR/cities.json`의 City와 연결 |
| `contentid` | `contentid` | 수집 확인 | TourAPI 콘텐츠 ID |
| `contenttypeid` | `contenttypeid` | 수집 확인 | 관광지·문화시설·음식점 등 콘텐츠 유형 |
| `name` | `title` | 수집 확인 | 관광지명 |
| `address` | `addr1`, `addr2` | 일부 누락 가능 | 주소 |
| `latitude` | `mapy` | 일부 누락 가능 | 위도 |
| `longitude` | `mapx` | 일부 누락 가능 | 경도 |
| `description` | `detail.common.overview` | 일부 누락 가능 | 관광지 설명 |
| `theme` | TourAPI 분류 코드 / 내부 매핑 | 수집 확인 | 6대 테마 분류 |
| `opening_hours` | `detail.intro` 유형별 필드 | 누락 다수 | 실제 제공률이 낮아 `missing` 가능 |
| `admission_fee` | `detail.intro` 유형별 필드 | 누락 다수 | 실제 제공률이 낮아 `missing` 가능 |
| `photo_url` | `firstimage`, `firstimage2` | 일부 누락 가능 | 대표 이미지 URL |
| `copyright_type` | `cpyrhtDivCd` | 일부 수집 확인 | 이미지 저작권 유형 |
| `source_name` | 내부 지정 | 수집 확인 | `TourAPI 4.0 (KorService2)` |
| `field_status` | 수집 파이프라인 | 수집 확인 | 필드별 취득 상태 |

## 2.4 Festival 데이터

Festival은 월별 추천과 계절성 추천의 주요 근거로 사용한다.
강원·경북 기준 TourAPI 4.0(KorService2) 수집 결과 106건을 명세 확인 기준으로 둔다.
축제 46건은 테마 수동 재분류 결과를 함께 보존한다.

| 필드 | TourAPI 원본 필드 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| `festival_id` | `contentid` 기반 내부 생성 | 수집 확인 | 형식: `KR-{도_코드}-{CITY_EN}-FES-{contentid}` |
| `city_id` | 내부 매핑 | 수집 확인 | 개최 도시 |
| `contentid` | `contentid` | 수집 확인 | TourAPI 행사 콘텐츠 ID |
| `contenttypeid` | `contenttypeid` | 수집 확인 | 축제 유형은 `15` |
| `name` | `title` | 수집 확인 | 축제명 |
| `address` | `addr1`, `addr2` | 일부 누락 가능 | 개최 장소 주소 |
| `period` | `eventstartdate`, `eventenddate` | 수집 확인 | 개최 기간 |
| `description` | `detail.common.overview` | 일부 누락 가능 | 축제 설명 |
| `theme` | TourAPI 분류 코드 / 수동 오버라이드 | 수집 확인 | 축제 테마 |
| `photo_url` | `firstimage`, `firstimage2` | 일부 누락 가능 | 대표 이미지 URL |
| `source_name` | 내부 지정 | 수집 확인 | `TourAPI 4.0 (KorService2)` |
| `field_status` | 수집 파이프라인 | 수집 확인 | 필드별 취득 상태 |

## 2.5 방문객 통계 데이터

방문객 통계는 DataLabService의 이동통신 기반 방문객 통계를 활용한다.
일별 단순 합산은 중복 집계 위험이 있으므로 1달 단위 구간 쿼리로 취득하고, 해당 월의 일수로 나눈 월별 일평균을 최종 지표로 사용한다.

| 필드 | 원본/산출 방식 | 실제 수집 및 명세 확인 상태 | 설명 |
| --- | --- | --- | --- |
| `city_id` | 내부 매핑 | 수집 확인 | 통계 대상 도시 |
| `year_month` | DataLabService 조회 기간 | 수집 확인 | 월 단위 기준 |
| `local_daily_avg` | 월 구간 쿼리 / 월 일수 | 수집 확인 | 현지인 일평균 방문객 |
| `outsider_daily_avg` | 월 구간 쿼리 / 월 일수 | 수집 확인 | 외지인 일평균 방문객 |
| `foreigner_daily_avg` | 월 구간 쿼리 / 월 일수 | 수집 확인 | 외국인 일평균 방문객 |
| `source_name` | 내부 지정 | 수집 확인 | `DataLabService` |

# 3. 데이터 소스 전략

## 3.1 한국관광공사 TourAPI 4.0(KorService2)

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 관광지 정보, 축제 정보, 이미지 정보, 위치 정보, 소개 정보 |
| 주요 엔드포인트 | `/areaBasedList2`, `/searchFestival2`, `/detailCommon2`, `/detailIntro2` |
| 적용 대상 | Attraction, Festival |
| 확인된 특성 | 운영시간·입장료는 콘텐츠 유형별 필드 제공률이 낮아 `missing` 관리가 필요 |
| 적용 방식 | 리스트 수집 후 상세 공통 정보와 유형별 소개 정보를 결합한다. 체크포인트 파일로 재시작을 지원한다. |

## 3.2 한국관광공사 관광 빅데이터 API(DataLabService)

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 도시별 월별 방문객 통계 |
| 주요 엔드포인트 | `/stayAnalysisVisitorList` |
| 적용 대상 | VisitorStatistics |
| 집계 방식 | 1달 단위 구간 쿼리 후 월 일수로 나누어 월별 일평균 산출 |
| 저장 방식 | `data/KR/visitor_statistics.json` 검증 산출물로 보존 후 S3 Raw 적재 대상에 포함 |

## 3.3 Wikipedia / Wikidata

| 항목 | 내용 |
| --- | --- |
| 주 용도 | 도시명, 행정 위치, 설명, 좌표, 기후 표, 공식 링크 후보 |
| 적용 대상 | City |
| 적용 방식 | 강원·경북 산하 City를 기준으로 Wikipedia/Wikidata 데이터를 취득하고 `data/KR/cities.json`으로 검증한다. |
| 기후 처리 | `climate_table`은 Wikipedia 기후 표를 우선 보존하되, 자동 취득 실패 시 `needs_review`로 남긴다. |

## 3.4 기상청 API허브 및 기후통계

| 항목 | 내용 |
| --- | --- |
| 주 용도 | Wikipedia 기반 기후 데이터의 비교 검증, 월별 여행 적합도 보강 |
| 적용 대상 | City `climate_table`, 계절 추천 지표 |
| 적용 방식 | Wikipedia 취득값과 기상청 자료를 비교하고 불일치 여부와 보정 메모를 기록한다. |

## 3.5 공식 사이트 및 보조 공공데이터

| 출처 | 사용 목적 | 적용 방식 |
| --- | --- | --- |
| 대한민국구석구석 | 관광지·축제 상세 링크와 공식 설명 보강 | TourAPI 설명과 링크 확인 |
| 지자체 문화관광 홈페이지 | 운영시간, 입장료, 최신 축제 일정 확인 | 누락·최신성 검수 |
| 행정안전부 행정구역 데이터 | 광역·시군구 코드 정규화 | `prefecture_id`, `city_id` 매핑 보강 |
| 공공데이터포털 지자체 관광 데이터 | 지자체별 관광 자원 보강 | 공식 링크와 누락 데이터 보강 |

# 4. 전체 취득 범위

## 4.1 전체 수집 대상 및 현황

| 구분 | 수집 항목 | 주요 출처 | 실제 수집 및 명세 확인 상태 |
| --- | --- | --- | --- |
| 도시 | 도시명, 위치, 설명, 기후 표, 사이트 링크, 위도, 경도 | Wikipedia, Wikidata | 강원·경북 40개 도시 수집 및 검증 완료 |
| 관광지 | 관광지명, 주소, 위도, 경도, 설명, 운영시간, 입장료, 테마 | TourAPI 4.0 KorService2 | 3,709건 수집 및 명세 확인 완료 |
| 축제 | 축제명, 주소, 기간, 설명, 테마 | TourAPI 4.0 KorService2 | 106건 수집 및 명세 확인 완료 |
| 통계 | 현지인·외지인·외국인 일평균 방문객 | DataLabService | 2025년 12개월 수집 및 명세 확인 완료 |

운영시간과 입장료는 TourAPI 실제 제공률이 낮아 상당수가 `missing` 상태가 될 수 있다.

## 4.2 취득 상태 관리

| 취득 상태 | 기준 | 처리 방식 |
| --- | --- | --- |
| `collected` | 자동 수집 값이 있고 출처가 명확함 | JSON 저장 후 S3 Raw Bucket 적재 |
| `needs_review` | 값은 있으나 표현이 모호하거나 최신성 확인이 필요함 | 공식 사이트 확인 또는 수동 검수 |
| `missing` | 자동 수집에서 값을 찾지 못함 | Web Search Worker 또는 수동 입력 대상 |
| `blocked` | 약관·저작권·접근 제한으로 수집 불가 | 딥링크 또는 빈 값으로 대체하고 사유 기록 |

## 4.3 공식 확인 우선순위

| 항목 | 확인 우선순위 | 사유 |
| --- | --- | --- |
| 운영시간 | 높음 | 일정 구성에 직접 영향을 주며 TourAPI 누락 가능성이 높다. |
| 운영기간 | 높음 | 계절 운영, 휴관일, 임시 중단 등 예외가 많다. |
| 입장료 | 중간 | 무료·유료·계절 요금·패키지 요금이 혼재한다. |
| 사진 | 중간 | 공공누리 유형과 외부 이미지 사용 조건 확인이 필요하다. |
| 기후 표 | 중간 | Wikipedia 자동 취득 실패 시 수동 보정이 필요하다. |
| 위도·경도 | 높음 | 지도 표시와 동선 계산에 필요하다. |

# 5. 수집 전략

## 5.1 자동 수집 전략

| 대상 | 자동 수집 소스 | 처리 방식 |
| --- | --- | --- |
| 도시 | Wikipedia, Wikidata | 강원·경북 40개 City의 도시명, 위치, 설명, 기후, 사이트 링크, 위도, 경도를 추출한다. |
| 관광지 | TourAPI 4.0 KorService2 | `/areaBasedList2` → 테마 분류 → `/detailCommon2` + `/detailIntro2` 순서로 수집한다. |
| 축제 | TourAPI 4.0 KorService2 | `/searchFestival2` → `/detailCommon2` + `/detailIntro2` 순서로 수집한다. |
| 통계 | DataLabService | `/stayAnalysisVisitorList`를 1달 단위로 조회하고 월별 일평균을 산출한다. |

## 5.2 TourAPI 수집 파이프라인 상세

| 순서 | 단계 | 처리 내용 |
| --- | --- | --- |
| 1 | City 목록 확정 | 강원·경북 40개 City 목록과 내부 `city_id` 기준을 확정한다. |
| 2 | TourAPI 리스트 수집 | 관광지·축제 후보를 TourAPI 목록 API로 수집한다. |
| 3 | 테마 자동 분류 | TourAPI 분류 코드와 내부 매핑으로 6대 테마를 자동 분류한다. |
| 4 | 공통 상세 수집 | `detailCommon2`로 설명, 위치, 이미지 등 공통 상세 정보를 수집한다. |
| 5 | 유형별 상세 수집 | `detailIntro2`로 관광지·축제 유형별 상세 필드를 보강한다. |
| 6 | 취득 상태 할당 | 필드별 수집 결과에 따라 `field_status`를 할당한다. |
| 7 | 로컬 검증 산출물 생성 | `data/KR/*.json` 형태로 City, Attraction, Festival, 통계 검증 산출물을 생성한다. |
| 8 | S3 적재 대상 확정 | 검증된 산출물을 S3 Raw Prefix 적재 대상으로 확정한다. |

API Key Rotation은 정상 쿼터 소진 상황에서 다음 키로 전환하는 방식으로 운영한다.
인증 오류나 잘못된 파라미터 오류는 즉시 실패로 처리하고 체크포인트에서 재시작한다.

## 5.3 공식 확인 및 검수 전략

공식 확인과 검수는 자동 수집에서 실패했거나 검수 필요 상태로 분류된 항목에 적용한다.
이 과정은 별도 단계가 아니라 같은 취득 파이프라인의 후속 처리로 본다.

| 확인 항목 | 입력 기준 |
| --- | --- |
| 운영시간 | 공식 사이트에 명시된 최신 운영시간만 입력 |
| 운영기간 | 계절 운영 또는 축제 기간이 명확한 경우 입력 |
| 입장료 | 공식 사이트 또는 공공 관광 페이지에 있는 금액만 입력 |
| 사진 | 공공누리 유형 또는 사용 가능 조건이 명확한 이미지 사용 |
| 기후 표 | Wikipedia와 기상청 자료의 불일치 여부와 보정 메모를 기록 |

## 5.4 데이터 정규화 규칙

- `city_id` 형식은 `KR-{도_코드}-{CITY_EN}`을 사용한다.
- `attraction_id` 형식은 `KR-{도_코드}-{CITY_EN}-ATT-{contentid}`를 사용한다.
- `festival_id` 형식은 `KR-{도_코드}-{CITY_EN}-FES-{contentid}`를 사용한다.
- 강원은 `KR-42`, 경북은 `KR-47` 광역 코드를 사용한다.
- 포항시 남구·북구 레코드는 `KR-47-POHANG`으로 통합한다.
- 도시명은 `city_name_ko`, 필요 시 `city_name_en`을 분리 저장한다.
- 관광지와 축제는 반드시 `city_id`를 가진다.
- TourAPI의 `contentid`, `contenttypeid`, `areacode`, `sigungucode`, `lclsSystm1`, `lclsSystm2`, `lclsSystm3`, `cat1`, `cat2`, `cat3`를 원본 참조 필드로 저장한다.
- 기간 정보는 원문 문자열(`period_text`)과 정규화 값(`start_date`, `end_date`, `month`)을 함께 저장한다.
- 외부 설명문은 원문 복제가 아니라 내부 요약문으로 재작성하거나 TourAPI `overview` 값을 출처와 함께 저장한다.

# 6. 단일 취득 파이프라인

## 6.1 처리 흐름

| 순서 | 단계 | 처리 내용 |
| --- | --- | --- |
| 1 | 자동 수집 | TourAPI, DataLab, Wikipedia/Wikidata에서 원천 데이터를 취득한다. |
| 2 | 캐시·체크포인트 저장 | 중단 후 재시작할 수 있도록 파일 기반 캐시와 체크포인트를 남긴다. |
| 3 | 취득 상태 할당 | 필드별 취득 결과에 따라 `field_status`를 할당한다. |
| 4 | 로컬 검증 산출물 생성 | `data/KR/*.json` 형식의 검증 산출물을 생성한다. |
| 5 | JSON 직렬화 | 수집 데이터와 메타데이터를 재사용 가능한 JSON 원본으로 직렬화한다. |
| 6 | S3 Raw Prefix 확정 | 국가, 출처, 엔티티 유형, 수집일 기준의 Raw Prefix를 확정한다. |
| 7 | S3 Raw Bucket 적재 | 검증된 JSON 산출물을 S3 Raw Bucket 적재 대상으로 확정한다. |

정의된 모든 필드가 JSON 원본에 들어가도록 시도한다.
수집 결과는 먼저 `data/KR/*.json` 로컬 검증 산출물로 확인한 뒤 국가, 출처, 엔티티 유형, 수집일 기준 S3 Raw Prefix에 적재한다.
6.1의 처리 흐름은 ETL 라인 이전의 데이터 취득 범위만 다룬다.
S3 적재 이후의 전처리, 정규화 DB 적재, 운영 중 보완 처리는 본 절의 범위에서 제외한다.
운영시간·입장료·사진도 최초 수집 대상에 포함하며, 자동 수집 실패 시 `missing` 또는 `needs_review` 상태로 JSON에 남긴다.

## 6.2 Web Search Worker 적용 조건

| 조건 | 처리 |
| --- | --- |
| DB에 정보 없음 | 공식 사이트 검색 |
| 운영시간·입장료 값이 오래됨 | 공식 사이트 재확인 |
| 축제 기간이 연도별로 바뀜 | 해당 연도 공식 페이지 확인 |
| 공식 출처가 아닌 블로그·SNS만 존재 | 답변 근거로 사용하지 않거나 낮은 신뢰도로 표시 |

# 7. 저장 구조

## 7.1 핵심 파일과 S3 적재 관계

| 저장 경로 |
| --- |
| `data/KR/prefectures.json` |
| `data/KR/cities.json` |
| `data/KR/attractions.json` |
| `data/KR/festivals.json` |
| `data/KR/visitor_statistics.json` |

위 파일은 실제 수집 검증과 명세 확인을 위한 로컬 JSON 산출물이다.
운영 흐름에서는 이 JSON 산출물과 원본 API 응답을 S3 Raw Bucket에 업로드하고, Lambda 전처리 결과만 DynamoDB 정규화 Item으로 적재한다.

| 로컬 검증 산출물 | 내용 | S3 Raw 적재 역할 |
| --- | --- | --- |
| `prefectures.json` | 광역시·도 레코드. 강원 `KR-42`, 경북 `KR-47` | City 정규화의 상위 행정 단위 입력 |
| `cities.json` | 강원·경북 40개 도시 레코드 | City 정규화 입력 |
| `attractions.json` | 관광지 3,709건 | Attraction 정규화 입력 |
| `festivals.json` | 축제 106건 | Festival 정규화 입력 |
| `visitor_statistics.json` | 40개 도시 × 12개월 방문객 통계 | 통계·추천 보조 지표 입력 |

## 7.2 City 예시

| 필드 | 예시 값 | 비고 |
| --- | --- | --- |
| `city_id` | `KR-42-GANGNEUNG` | 내부 City ID |
| `city_name_ko` | 강릉 | 한국어 도시명 |
| `prefecture_id` | `KR-42` | 강원특별자치도 광역 코드 |
| `location` | 한국 강원특별자치도 | 행정 위치 문자열 |
| `latitude` | `37.7519` | 대표 위도 |
| `longitude` | `128.8761` | 대표 경도 |
| `description` | 강릉시는 강원특별자치도 동해안 중부에 위치한 관광 도시다. | 내부 요약 설명 |
| `climate_table.caption` | 수작업 필요 | 기후 표 캡션 |
| `climate_table.wikitext` | 수작업 필요 | 기후 표 원문 |
| `field_status.climate_table` | `needs_review` | 기후 표 검토 상태 |

## 7.3 Attraction 예시

| 필드 | 예시 값 | 비고 |
| --- | --- | --- |
| `attraction_id` | `KR-42-GANGNEUNG-ATT-126508` | 내부 Attraction ID |
| `city_id` | `KR-42-GANGNEUNG` | 연결 City ID |
| `contentid` | `126508` | TourAPI 콘텐츠 ID |
| `name` | 경포해변 | 관광지명 |
| `address` | 강원특별자치도 강릉시 창해로 514 | 주소 |
| `source_name` | `TourAPI 4.0 (KorService2)` | 취득 출처 |
| `field_status.opening_hours` | `missing` | 운영시간 취득 상태 |
| `field_status.admission_fee` | `missing` | 입장료 취득 상태 |

## 7.4 Festival 예시

| 필드 | 예시 값 | 비고 |
| --- | --- | --- |
| `festival_id` | `KR-42-GANGNEUNG-FES-2762975` | 내부 Festival ID |
| `city_id` | `KR-42-GANGNEUNG` | 연결 City ID |
| `contentid` | `2762975` | TourAPI 행사 콘텐츠 ID |
| `name` | 강릉단오제 | 축제명 |
| `period` | 연도별 공식 일정 확인 필요 | 개최 기간 |
| `source_name` | `TourAPI 4.0 (KorService2)` | 취득 출처 |
| `field_status.period` | `needs_review` | 기간 정보 검토 상태 |

# 8. 6대 테마 분류

관광지와 축제는 기존 문서 기준의 6대 핵심 테마로 분류한다.
테마 자동 분류는 TourAPI의 행정·법정 분류 코드 `lclsSystm1`, `lclsSystm2`, `lclsSystm3`을 기준으로 매핑한다.
축제는 자동 매핑 결과가 넓게 잡힐 수 있으므로 필요 시 수동 오버라이드를 적용한다.

| 테마 | 설명 |
| --- | --- |
| 온천·휴양 | 온천, 스파, 리조트, 힐링 |
| 바다·해안 | 바다, 해안, 해수욕장, 해양 활동 |
| 역사·전통 | 역사, 문화유산, 전통 문화 |
| 미식·노포 | 맛집, 전통 음식점, 식당 |
| 자연·트레킹 | 자연, 등산, 트레킹, 국립공원 |
| 예술·감성 | 예술, 디자인, 감성, 문화, 행사 |

# 9. 품질 검증 기준

| 검증 항목 | 기준 |
| --- | --- |
| City 매핑 | 모든 Attraction과 Festival은 `data/KR/cities.json`에 존재하는 `city_id`를 가져야 한다. |
| 행정구역 정합성 | 강원·경북 코드와 내부 City ID가 일치해야 한다. |
| 포항 통합 | 포항시 남구·북구 레코드는 `KR-47-POHANG`으로 통합되어 있어야 한다. |
| 출처 기록 | 모든 자동 수집 데이터는 `source_name`, `source_url`, `collected_at`을 가진다. |
| 전체 필드 상태 | 정의된 모든 필드는 `collected`, `needs_review`, `missing`, `blocked` 중 하나의 상태를 가진다. |
| 수량 검증 | 도시 40개, 관광지 3,709건, 축제 106건, 월별 통계 12개월 범위를 기준으로 누락을 확인한다. |
| 최신성 | 운영시간, 입장료, 축제 기간은 확인일을 기록한다. |
| 기후 정합성 | `climate_table`은 Wikipedia와 기상청 자료를 비교하고 불일치 여부를 검수 메타데이터로 남긴다. |
| 저작권 | 사진과 설명문은 사용 가능 조건을 확인한다. 설명문은 내부 요약문으로 저장한다. |
| API 키 보안 | API Key는 문서나 산출 JSON에 직접 저장하지 않는다. |

# 10. 법적·운영 제약

- Wikipedia API 및 크롤링 기반 설명은 라이선스 조건에 따라 출처와 원문 링크를 기록한다.
- TourAPI와 공공데이터포털 데이터는 공공누리 유형, API 이용 조건, 출처 표기 조건을 확인한다.
- TourAPI 일일 쿼터 제한을 준수한다.
- API Key는 환경변수 또는 보안 저장소로 관리하고 문서와 산출물에 직접 기록하지 않는다.
- 지자체 관광 페이지는 이용약관과 크롤링 허용 범위를 확인한다.
- 사진은 저작권 위험이 크므로 자동 수집 값이 있더라도 사용 가능 조건을 확인하고, 불명확하면 `needs_review` 또는 `blocked`로 관리한다.
- 운영시간과 입장료는 변경 가능성이 높으므로 서비스 화면에 "확인일 기준" 문구를 표시한다.

# 11. 본 문서 반영 계획

본 문서의 핵심 내용은 한국 데이터 취득 계획의 실제 운영 기준으로 정리한다.
문서 확정 후에는 대표 데이터 취득 계획, 전처리 계획, 공유용 HTML, PDF 산출물이 같은 기준을 바라보도록 순차적으로 동기화한다.

1. 한국 데이터 출처와 수집 범위는 TourAPI 4.0, DataLabService, Wikipedia/Wikidata, 강원·경북 40개 도시 실제 수집 결과를 기준으로 통합한다.
2. 한국 City ID와 산출 JSON 구조는 `KR-{도_코드}-{CITY_EN}` 체계를 기준으로 정리한다.
3. 공유용 HTML은 확정된 데이터 취득 계획을 사용자가 바로 확인할 수 있는 형태로 갱신한다.
4. PDF 산출물은 표, 예시, 페이지 흐름이 읽기 좋게 유지되도록 재생성하고 검수한다.

# 12. 참고 출처

- 한국관광공사 TourAPI 4.0(KorService2): https://www.data.go.kr/data/15101578/openapi.do
- 한국관광공사 관광 빅데이터 API(DataLabService): https://www.data.go.kr/data/15010913/openapi.do
- 대한민국구석구석: https://korean.visitkorea.or.kr/
- 한국관광 데이터랩: https://datalab.visitkorea.or.kr/
- 기상청 API허브: https://apihub.kma.go.kr/
- 공공데이터포털: https://www.data.go.kr/

# 13. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-02 | LLM 파트 | 한국 데이터 취득 계획서 초안 작성 |
| v0.2 | 2026-06-06 | LLM 파트 | 도 간략 정보와 산하 도시 목록 기반 City 크롤링, JSON 원본의 S3 저장, 기후 데이터 비교 검증 방식으로 구체화 |
| v0.3 | 2026-06-06 | LLM 파트 | 강원·경북 40개 도시 실제 수집 결과, TourAPI 4.0, DataLabService, `data/KR/*.json` 검증 산출물과 S3 Raw 적재 흐름 반영 |
| v0.4 | 2026-06-07 | LLM 파트 | 대표 문서와 공유 산출물 동기화 상태에 맞춰 문서 메타 표현 정리 |
| v0.4.1 | 2026-06-08 | LLM 파트 | 기존 문서 기준 6대 테마(온천·휴양, 바다·해안, 역사·전통, 미식·노포, 자연·트레킹, 예술·감성)와 `lclsSystm` 기반 자동 분류 기준 반영 |
