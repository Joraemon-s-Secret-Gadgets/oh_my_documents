# 로브 (Lovv) 한국(KR) 데이터 전처리 상세 설계서

> 문서 버전: v0.3
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-08 (v0.2 심화: 2026-06-09, v0.3 코드대조: 2026-06-09)
> 작성자: 조동휘
> 기준 문서: `docs/08_data_preprocessing/data_preprocessing_plan.md` v0.5
> 실데이터 기준: `docs/03_data_collect_plan/korea_data_acquisition_plan_updated.md` v0.3
> 코드 대조: `Gloveman/tour-api-korea` (main), `docs/08_data_preprocessing/kr_preprocessing_code_based_design.md` v0.1
> 불일치 정리: `docs/03_data_collect_plan/korea_acquisition_plan_corrections.md` v0.1

> **[v0.3 코드대조 요약]** 실제 수집 샘플 코드(`tour-api-korea`)와 대조하여 ID 형식(`KR-{GW\|GB}-*`, `ATT-`/`FEST-{contentid}`), 방문통계 구조(final 임베드→unnest, `locals_*`/`out_of_town_*`/`foreigners_*`), 데이터 파일 구조(`data/raw/*`·`data/city/*`·`data/visitor/*`), 테마 키(`lclsSystm3 or cat3`)를 코드 사실로 정정한다. 코드 미구현 항목(tel 폴백, `prefecture_id`, City 보강)은 **전처리 단계 보강 대상**임을 명시한다.
> 적재 설계 기준: `docs/04_database_design/nosql_schema_design.md`
> 예산 기준: `docs/08_data_preprocessing/preprocessing_budget_estimate.md` v0.1

# 1. 문서 개요

## 1.1 목적

본 문서는 한국(강원·경북) 실제 수집 데이터를 대상으로, 수집 산출물을 S3에 적재(Load)한 뒤 AWS Lambda로 변환(Transform)하여 DynamoDB 서비스 데이터로 만드는 **ELT 파이프라인의 상세 설계**를 정의한다.

상위 계획서(`data_preprocessing_plan.md` v0.5)가 한국·일본 공통 전처리 원칙과 아키텍처를 다룬다면, 본 문서는 그 원칙을 **한국 실수집 데이터 구조(TourAPI 4.0 KorService2 / DataLabService)에 맞춰 필드 단위로 구체화**하고, 단계별 입출력·변환 규칙·실패 처리·멱등성 기준을 구현 가능한 수준으로 기술한다.

## 1.2 적용 범위

| 구분 | 범위 |
| --- | --- |
| 국가 | 한국(KR) 우선. 강원(GW)·경북(GB) |
| 엔티티 | City 40, Attraction 3,709, Festival 106, VisitorStatistics(월별 도시별) |
| 처리 모델 | ELT (Extract → Load Raw → Transform-in-place) |
| 저장 계층 | 로컬 검증 산출물 → S3(Raw/Processed/Quality/Review/Failed) → DynamoDB |
| 제외 | 일본(JP) 상세 규칙, 추천 알고리즘, 사용자 로그(별도 문서) |

## 1.3 ETL이 아니라 ELT인 이유

본 설계는 변환을 적재 이전이 아니라 **S3 적재 이후**에 수행하는 ELT를 채택한다.

| 근거 | 설명 |
| --- | --- |
| 원본 보존 | TourAPI 응답·detail 원문을 손실 없이 S3 Raw에 먼저 적재해 재처리·감사 추적을 보장한다. |
| 재처리 유연성 | 테마 매핑 규칙, tel 폴백, 요약 규칙이 바뀌어도 원본 재수집 없이 Transform만 재실행한다. |
| 비용 효율 | Raw를 누적한 뒤 배치로 Lambda 변환을 수행해 호출 단가를 낮춘다(예산서 §3 기준 주당 약 2만 원 내외). |
| 상태 전파 | `collected/needs_review/missing/blocked` 상태를 원본 단계부터 부여하고 변환 결과까지 전파한다. |

# 2. ELT 단계 정의

## 2.1 전체 흐름

```text
[E] Extract        Collector / Web Search Worker / Manual Review
                   → 로컬 산출물(data/raw/final/{city_en}.json, data/city/{city_en}.json)
                          │  (15MB 경계 규칙 적용: §3.2)
                          ▼
[L] Load (Raw)     S3 Raw Bucket  raw/KR/{source}/{entity_type}/{yyyy}/{mm}/{dd}/
                          │  (Raw 누적 / 배치 기준 충족)
                          ▼
[T] Transform      AWS Lambda Preprocessor
                   스키마 검증 → 필드 정제 → 정규화 → 중복 병합
                   → 품질 점수 → 파생 필드 → 검수 분류
                          ▼
[Load Service]     DynamoDB Single-Table  +  S3 Processed/Quality/Review/Failed
```

## 2.2 단계별 책임 분리

| 단계 | 실행 주체 | 입력 | 출력 | 멱등성 키 |
| --- | --- | --- | --- | --- |
| Extract | 크롤러/검수자 | TourAPI, DataLab, 수동 입력 | 로컬 검증 JSON | `contentid` / `city_id`+`year_month` |
| Load(Raw) | 적재 스크립트 | 로컬 검증 JSON | S3 Raw Object | S3 Key(날짜·출처·엔티티) |
| Transform | Lambda | S3 Raw Prefix/Manifest | 정규화 결과, 품질 리포트 | `entity_id` |
| Load(Service) | Lambda | 정규화 결과 | DynamoDB Item | `PK`+`SK` |

# 3. Extract → Load 경계 (GitHub vs S3)

## 3.1 저장소 역할 분리 원칙

데이터의 정본(System of Record)은 **S3**이며, GitHub은 코드·문서·설정 저장소로 한정한다. 이는 GitHub의 파일 크기 정책(50MB 경고, 100MB push 차단, 저장소 권장 1GB 미만)과 Git이 대용량·고빈도 갱신 데이터의 영구 히스토리를 누적해 저장소를 비대화시키는 특성을 회피하기 위한 결정이다.

| 대상 | 위치 | 비고 |
| --- | --- | --- |
| 크롤링 원본·정규화 JSON (`data/raw/final/*.json`, `data/city/*.json`, `data/visitor/*.json`) | **S3 (크기 무관)** | 작아도 데이터는 S3가 정본 |
| 파이프라인 코드(`scripts/*.py`), 스키마, 매핑 사전, 문서 | GitHub | |
| 테마 매핑 사전(`data/theme_mapping.json`·`data/festival_mapping.json`) | GitHub 허용 | 재현용 수 KB 설정 |
| 소량 테스트 픽스처 | GitHub 허용 | 단위 테스트 재현용 |

## 3.2 15MB 임계값 규칙

Extract 산출물은 **15MB를 임계값**으로 적재 경로를 분기한다. 15MB는 GitHub 하드 리밋(100MB)보다 보수적이지만, "데이터는 Git에 넣지 않는다"는 원칙을 강제하는 안전 임계값으로 사용한다.

| 조건 | 처리 |
| --- | --- |
| 산출물 ≤ 15MB 이고 데이터가 아닌 설정/픽스처 | GitHub 커밋 허용 |
| 산출물 > 15MB 또는 데이터 성격(크롤링 결과·검증 JSON) | **GitHub 커밋 금지, S3 Raw로 직접 PUT** |

> **권장 안전장치**
> - `.gitignore`에 `data/`를 추가해 데이터 디렉터리의 우발적 커밋을 차단한다(현재 `.gitignore`에는 미포함).
> - pre-commit 훅으로 15MB 초과 파일 또는 `data/` 경로 커밋을 거부한다.
> - 크롤러가 GitHub Actions에서 동작한다면 워크플로 artifact를 경유하지 말고 워커에서 **S3로 직접 PUT**한다.

## 3.3 Load(Raw) 적재 규칙

| 항목 | 규칙 |
| --- | --- |
| Prefix | `raw/KR/{source}/{entity_type}/{yyyy}/{mm}/{dd}/` |
| `source` | `tourapi`, `datalab`, `wikipedia`, `manual` |
| `entity_type` | `city`, `attraction`, `festival`, `visitor_statistics` |
| 객체 단위 | 도시별 원천(`{city_en}.json`)은 엔티티 유형별로 분해해 적재하되, 원본 묶음도 함께 보존 |
| 멱등 적재 | 동일 `contentid`·수집일 객체는 덮어쓰지 않고 버전 Prefix로 누적 |
| 적재 전 검증 | `data/raw/final/*`·`data/city/*` 수량 검증 통과(City 40, Attraction 3,709, Festival 106) 후 적재 확정 |

# 4. 입력 데이터 실구조 (KR)

## 4.1 도시별 원천 파일 구조

각 관광지·축제 레코드는 TourAPI 리스트 필드, `_assigned_theme`, `detail.common`, `detail.intro`로 구성된다. `detail.intro`의 필드명은 `contenttypeid`에 따라 달라진다.

```text
data/raw/final/{city_en}.json
 ├── attractions[]   (contenttypeid: 12·14·28·32·38·39)
 │     ├── (list)      contentid, title, addr1/2, mapx, mapy, lclsSystm1~3 ...
 │     ├── _assigned_theme
 │     ├── detail.common  overview, homepage, cat1~3(결측 35%)
 │     └── detail.intro   유형별 필드 (usetime / usetimeculture / opentimefood ...)
 └── festivals[]     (contenttypeid: 15)
       ├── (list)      ... eventstartdate, eventenddate, lclsSystm1="EV"
       ├── _assigned_theme  (수동 오버라이드 46건)
       ├── detail.common
       └── detail.intro   usetimefestival, playtime, eventplace, sponsor1 ...

data/city/{city_en}.json          정규화본 (city/attractions/festivals/metadata)
data/visitor/monthly_visitor_averages.json   방문통계 전역 요약
```

> [코드정정] v0.2의 `data/KR/{prefectures,cities,attractions,festivals,visitor_statistics}.json` 분리 구조는 코드에 없다. 방문통계는 별도 파일이 아니라 final 파일의 `visitor_statistics`에 임베드되며(전처리에서 unnest), City는 `data/city/{city_en}.json`의 `city` 블록이다.

## 4.2 엔티티별 핵심 입력 필드와 처리 난점

| 엔티티 | 핵심 입력 | 처리 난점 |
| --- | --- | --- |
| City | `city_id`(`KR-{GW\|GB}-{CITY_EN}`), 좌표 | `description`·`climate`·`site_url`이 코드 placeholder → 전처리 보강 대상. `prefecture_id`·`climate_table`은 코드 미구현 |
| Attraction | 리스트 필드 + `detail.common.overview` + 유형별 `detail.intro` | `tel` 미출력(코드) → 전처리에서 `infocenter` 계열 폴백, `cat1~3`는 필터 후 삭제 |
| Festival | `detail.intro.eventstartdate/eventenddate`(YYYYMMDD), `_assigned_theme` | `tel` 미출력 → 전처리에서 `infocenter`/`sponsor1tel` 폴백, 테마 수동 오버라이드 반영 |
| VisitorStatistics | final 임베드 `visitor_statistics.monthly_statistics[]` | 임베드 12개월을 도시별 독립 아이템으로 unnest. `locals_*`/`out_of_town_*`/`foreigners_*` → 표준명 매핑 |

# 5. Transform 단계 상세 (Lambda)

## 5.1 처리 순서와 산출물

| 순서 | 단계 | 처리 내용 | 산출물 |
| --- | --- | --- | --- |
| 1 | 스키마 검증 | 필수 필드 존재, 타입, 인코딩, 날짜 포맷 점검 | `schema_validation_result` |
| 2 | 필드 정제 | HTML 태그·제어문자·공백·깨진 URL 제거, 중복 문장 정리 | `cleaned_fields` |
| 3 | 엔티티 정규화 | 식별자·명칭·주소·좌표·날짜·테마 표준화 | `normalized_entities` |
| 4 | 중복 병합 | 동일 `contentid` 다중 출처를 대표 엔티티로 병합 | `merged_entities` |
| 5 | 품질 점수 | 출처 공식성·최신성·충족률·일치도·검수 반영 | `data_confidence` |
| 6 | 파생 필드 | 테마·계절·추천 월·혼잡도·일정 적합도·검색 문서 | `feature_dataset` |
| 7 | 검수 분류 | 누락·충돌·저작권 위험을 검수 큐로 이동 | `review_queue` |
| 8 | 서비스 적재 | DynamoDB Item 변환 후 적재 | `DynamoDB Item` |

## 5.2 KR 고유 변환 규칙

### 5.2.1 식별자 정규화

| 대상 | ID 형식 (코드정정) | 예시 |
| --- | --- | --- |
| City | `KR-{GW\|GB}-{CITY_EN}` | `KR-GW-GANGNEUNG` |
| Attraction | `ATT-{contentid}` | `ATT-126508` |
| Festival | `FEST-{contentid}` | `FEST-2762975` |
| VisitorStatistics | `{city_id}-STAT-{yyyyMM}` (전처리 파생) | `KR-GW-GANGNEUNG-STAT-202501` |

ID는 재처리 시에도 불변이어야 한다. `contentid`를 안정 키로 사용한다. City 연결은 별도 `city_id` 필드로 유지하며, DynamoDB 서비스 키는 `city_id`(PK)+`attraction_id`/`festival_id`(SK)로 구성한다. (도 코드를 영문 `GW`/`GB` 대신 숫자 `42`/`47`로 전환할지는 미정 정책 사항)

### 5.2.2 연락처 폴백 (tel 100% 결측 대응)

> [코드정정] 수집 정규화 코드(`normalize_details.py`)는 `tel`을 출력하지 않는다. 따라서 연락처 폴백은 **전처리(Transform) 단계에서 신규 적용**한다. 입력은 final 파일의 `detail.intro`다.

공통 `tel`은 실데이터에서 100% 결측이므로, `detail.intro`의 유형별 연락처 필드를 우선순위로 탐색해 상위 `tel`로 승격한다.

| 엔티티/유형 | 폴백 우선순위 |
| --- | --- |
| 관광지(12) | `infocenter` |
| 문화시설(14) | `infocenterculture` |
| 음식점(39) | `infocenterfood` |
| 축제(15) | `infocenter` → `sponsor1tel` |

폴백으로도 값이 없으면 `tel`은 생략(undefined)하며 `false` 치환하지 않는다.

### 5.2.3 6대 테마 매핑

테마는 결측률 35%인 `cat1~3` 대신 **`lclsSystm3`(소분류) 코드를 우선 키로, 없으면 `cat3` 폴백**하여 자동 매핑한다(코드 기준). `lclsSystm1 == "C01"` 항목은 제외한다. 6대 테마 중 하나로 매핑되지 않는 항목은 수집 단계에서 이미 필터링(Drop)되었으므로, Transform은 매핑 무결성 검증과 축제 오버라이드 반영을 담당한다.

| 테마 | 설명 | 관광지 | 축제 |
| --- | --- | ---: | ---: |
| `온천·휴양` | 온천, 스파, 리조트, 힐링 | 120 | 0 |
| `바다·해안` | 바다, 해안, 해수욕장, 해양 활동 | 249 | 0 |
| `역사·전통` | 역사, 문화유산, 전통 문화 | 1,001 | 10 |
| `미식·노포` | 맛집, 전통 음식점(관광식당 `FD010100` 한정) | 2,480 | 22 |
| `자연·트레킹` | 자연, 등산, 트레킹, 국립공원 | 687 | 13 |
| `예술·감성` | 예술, 디자인, 감성, 문화, 행사 | 374 | 61 |

- 축제는 자동 분류 후 `filter_existing_lists.py`의 `fest_overrides`(contentid→테마, 46건, 코드 내 하드코딩) 수동 오버라이드를 적용한다.
- 매핑 실패 항목이 Transform 단계에서 발견되면(수집 필터 누락분) `content_review` 큐로 이동한다.

> **⚠️ 수량 불일치 (신뢰도: 확인 필요)**
> 위 테마별 관광지 합계는 **4,911건**(120+249+1,001+2,480+687+374)이나, 동일 출처 문서와 수집 계획서가 명시하는 실제 수집 Attraction 수는 **3,709건**이다(City 40 / Festival 106은 문서 간 일치). 차이 1,202건의 원인(수집 전 후보 집계 vs 필터·중복 제거 후 최종 적재 수, 음식점 분류 범위 차이 등)이 출처 문서에서 해소되지 않았다. **본 설계는 적재 기준 수량으로 3,709건을 정본으로 삼으며**, 테마 합계는 분류 분포 참고용으로만 둔다. Transform의 수량 정합성 검증(§6.1, §8) 단계에서 테마별 실적재 수를 재집계해 두 값을 일치시킬 것을 권고한다.

### 5.2.4 명칭·주소·좌표·날짜 정규화

| 대상 | 규칙 |
| --- | --- |
| 명칭 | 홍보 문구·괄호 부가설명·축제 회차 표기를 대표명과 분리, 검색명(공백 제거·소문자·특수문자 제거·별칭) 생성 |
| 주소 | `addr1`/`addr2` 분해, 법정동 코드(`lDongRegnCd`·`lDongSignguCd`) 기준 City 매핑 |
| 좌표 | `mapx`(경도)·`mapy`(위도) 문자열 → WGS84 decimal, GeoJSON Point + Geohash 생성. 국가 범위 이탈 시 `needs_review` |
| 날짜 | 축제 `eventstartdate/eventenddate`(YYYYMMDD) → ISO `start_date`/`end_date`, `month`·`season` 파생, 반복 축제 `recurrence_rule` |
| 운영정보 | `usetime`/`usetimeculture`/`opentimefood` 등 원문 문자열 + 구조화 영업시간 병행 저장, HTML 태그 제거 |

### 5.2.5 방문객 통계 정규화

> [코드정정] 통계는 `DataLabService/locgoRegnVisitrDDList`로 수집되어 final 파일의 `visitor_statistics.monthly_statistics[]`에 **임베드**된다. 전처리는 임베드 12개월을 도시별 독립 `VisitorStatistics` 아이템으로 **unnest**하고, 코드 필드명을 서비스 표준명으로 매핑한다. (`touDivCd`: 1=현지인, 2=외지인, 3=외국인)

| 입력 필드(코드) | 표준 출력 필드 |
| --- | --- |
| `month` | `year_month` (`"2025-01"`), `stat_period`(`202501`) |
| `locals_daily_avg` | `local_daily_avg` |
| `out_of_town_daily_avg` | `outsider_daily_avg` |
| `foreigners_daily_avg` | `foreigner_daily_avg` |
| `total_daily_avg` | `total_daily_avg` (혼잡 지표 기반) |

## 5.3 결측·타입 처리 원칙

| 원칙 | 적용 |
| --- | --- |
| 결측 왜곡 방지 | 빈 값을 일괄 `false` 치환하지 않고 생략(undefined) 또는 `null` 유지 |
| 100% 결측 필드 제외 | `bookingplace`, `discountinfofestival`, `eventhomepage` 등 저장 구조에서 배제 또는 Optional |
| 리스트 정규화 | 줄바꿈/콤마 구분 텍스트(예: 취급 메뉴)를 배열로 파싱 |
| 저작권 | `cpyrhtDivCd`(공공누리 Type) 보존, 사용 조건 불명확 이미지는 노출 후보 제외 |

# 6. 품질 검증 및 검수 큐

## 6.1 자동 검증 기준

| 검증 항목 | 기준 | 실패 상태 |
| --- | --- | --- |
| 필수 필드 | `entity_id`, 이름, City 매핑, 출처 URL 존재 | `missing`/`needs_review` |
| City 매핑 | 모든 Attraction/Festival/Stat이 단일 City와 연결 | `needs_review` |
| 좌표 범위 | 한국 좌표 범위 내, City-개체 거리 이상치 아님 | `needs_review` |
| 날짜 | YYYYMMDD → ISO 변환 가능 또는 반복 규칙 | `needs_review` |
| 테마 | 6대 테마 중 하나로 매핑됨 | `content_review` |
| 저작권 | 이미지·설명 사용 조건 확인 가능 | `blocked`/`needs_review` |
| 최신성 | 운영시간·입장료·축제기간 확인일 존재 | `needs_review` |

## 6.2 검수 큐

| 큐 | 대상 |
| --- | --- |
| `location_review` | City 매핑 충돌, 좌표 이상치, 주소 누락 |
| `date_review` | 축제 기간 불명확, 연도별 일정 미확인 |
| `license_review` | 사진·설명 사용 조건 불명확 |
| `content_review` | 테마 매핑 실패, 설명 품질 낮음 |
| `source_review` | 공식 출처 부재 |

## 6.3 신뢰도 점수 (`data_confidence`)

출처 공식성(공식 API·지자체 사이트 가중), 최신성(`verified_at`), 필드 충족률, 다중 출처 일치도, 수동 검수 완료 여부를 가중 합산한다.

# 7. 서비스 적재 (DynamoDB)

## 7.1 적재 타깃

Single-Table Design을 기준으로 하되, 상위 계획서의 테이블 후보를 KR 적재 관점에서 매핑한다.

| 테이블/엔티티 | Partition Key | Sort Key | 저장 내용 |
| --- | --- | --- | --- |
| `LovvCity` | `country_code`(`KR`) | `city_id` | 도시 정규화 |
| `LovvAttraction` | `city_id` | `attraction_id` | 관광지 정규화 |
| `LovvFestival` | `city_id` | `festival_id` | 축제 정규화 |
| `LovvVisitorStats` | `city_id` | `stat_period`(`yyyyMM`) | 월별 일평균 통계 |
| `LovvDataQuality` | `entity_id` | `checked_at` | 품질·신뢰도·실패 사유 |
| `LovvReviewQueue` | `queue_name` | `entity_id` | 검수 대상·상태 |

## 7.2 Item 공통 속성

`entity_id`, `entity_type`, `country_code`, `source_name`, `source_url`, `s3_raw_uri`(재처리 추적), `normalized_payload`, `quality_status`, `data_confidence`, `collected_at`, `processed_at`, `verified_at`.

## 7.3 적재 조건

| 대상 | 최소 적재 조건 |
| --- | --- |
| City | ID, 도시명, 국가, `prefecture_id`, 출처 URL |
| Attraction | ID, 이름, City 매핑, 출처 URL, 주소 또는 좌표, 테마 |
| Festival | ID, 이름, City 매핑, 기간(원문 또는 개최 월), 출처 URL, 테마 |
| VisitorStatistics | ID, City 매핑, `year_month`, 일평균 지표, 출처명 |
| 서비스 노출 | 필수 필드 충족, 저작권 위험 없음, `blocked` 아님 |

# 8. 멱등성·재처리·실패 처리

## 8.1 멱등성

| 단계 | 멱등 키 | 보장 방식 |
| --- | --- | --- |
| Load(Raw) | S3 Key | 동일 수집일·`contentid` 객체는 버전 Prefix 누적, 덮어쓰기 금지 |
| Transform | `entity_id` | 재실행 시 동일 ID 산출, `processed_at`만 갱신 |
| Load(Service) | `PK`+`SK` | 조건부 쓰기로 핵심 필드 변경 시에만 갱신 + 변경 이력 후보 기록 |

## 8.2 부분 재처리

특정 S3 Prefix / 출처 / City 단위로 Lambda 재실행이 가능해야 한다. 테마 규칙·요약 규칙 변경 시 원본 재수집 없이 Transform만 재실행한다.

## 8.3 실패 처리

| 실패 유형 | 처리 |
| --- | --- |
| 스키마 오류 | DynamoDB 미적재, `failed/KR/...` Prefix와 품질 리포트에 사유 기록 |
| 필수 필드 누락 | `LovvReviewQueue` 등록 |
| 조건부 쓰기 실패 | 기존 Item과 충돌 확인 후 변경 이력 후보 분류 |
| Lambda 타임아웃 | 더 작은 배치로 분할 재시도 |
| 일시적 AWS 오류 | 재시도 후 DLQ 또는 실패 Prefix 보존 |

# 9. S3 경로 요약 (KR)

| 영역 | Prefix |
| --- | --- |
| Raw | `raw/KR/{source}/{entity_type}/{yyyy}/{mm}/{dd}/` |
| Processed | `processed/KR/{entity_type}/{yyyy}/{mm}/{dd}/` |
| Quality | `quality/KR/{entity_type}/{yyyy}/{mm}/{dd}/` |
| Review | `review/{queue_name}/{yyyy}/{mm}/{dd}/` |
| Failed | `failed/KR/{source}/{entity_type}/{yyyy}/{mm}/{dd}/` |

# 10. 법적·운영 유의사항

- Wikipedia 기반 설명은 출처·원문 링크 보존, 서비스 본문은 내부 요약문 사용.
- TourAPI/DataLab 이용 조건과 출처 표기 조건 보존.
- 사진은 `cpyrhtDivCd` 사용 조건이 확인된 경우만 노출 후보.
- 운영시간·입장료·축제 기간은 변동성이 커 서비스 응답에 확인일 문구 연결.
- TourAPI 키는 디코딩 키만 사용하고 Pool 로테이션은 쿼터 초과(`0022`)에서만 수행하며 인증·파라미터 오류는 Fail-Fast.

# 11. Lambda 함수 구성 및 오케스트레이션

## 11.1 설계 원칙

Transform 단계는 **단일 책임 Lambda 다단계(stateless) 구성**을 기본으로 한다. 한국 PoC 규모(City 40, Attraction 3,709, Festival 106, VisitorStatistics 480)는 1회 풀 배치가 수천 건 수준이므로, 상시 가동 인프라(EMR·Glue 상시 클러스터) 대신 **이벤트 기반 배치 Lambda**로 충분하다(예산서 §3 기준 주당 약 2만 원 내외).

| 원칙 | 적용 |
| --- | --- |
| Stateless | Lambda는 외부 상태를 갖지 않고 입력(S3 Manifest)→출력(S3 Processed + DynamoDB)만 책임진다. |
| 멱등 | 동일 Manifest 재실행 시 동일 `entity_id`·동일 결과(§8.1). `processed_at`만 갱신. |
| 엔티티 분리 실행 | City/Attraction/Festival/VisitorStatistics는 **엔티티 유형별로 분리된 호출 단위**로 실행해 실패 격리와 부분 재처리를 쉽게 한다. |
| 작은 배치 | 타임아웃·메모리 한계를 피하기 위해 한 번의 호출은 1개 City 또는 N개 객체 묶음(기본 500건) 단위. |

## 11.2 함수 분해

| 함수 | 트리거 | 입력 | 책임 | 출력 |
| --- | --- | --- | --- | --- |
| `lovv-preprocess-dispatcher` | EventBridge(스케줄) 또는 수동 | Raw Prefix 범위, 배치 기준 | Raw Prefix 스캔 → 처리 대상 객체를 묶어 **Batch Manifest** 생성 → 워커 fan-out | `manifest.json`(S3), 워커 호출 이벤트 |
| `lovv-preprocess-worker` | dispatcher 호출(또는 Step Functions Map) | Batch Manifest 1조각 | 스키마검증→정제→정규화→병합→점수→파생→검수분류 (§5, §13) | Processed/Quality JSON(S3), DynamoDB 적재 |
| `lovv-preprocess-loader` | worker 내부 호출(동일 함수 통합 가능) | `normalized_entities` | DynamoDB 조건부 쓰기, 변경 이력 후보 기록 | DynamoDB Item, 적재 리포트 |

> PoC 단계에서는 `worker`와 `loader`를 **단일 Lambda 함수**로 통합해 호출 비용과 지연을 줄인다. 트래픽·데이터가 커지면 `loader`를 분리해 쓰기 스로틀링과 재시도를 독립 제어한다.

## 11.3 오케스트레이션 옵션

```text
[기본] EventBridge(주간/수동)
        → dispatcher (Manifest 생성)
        → worker × N  (엔티티·City 단위 fan-out, 동시성 제한)
        → DynamoDB / S3 Processed
        → 실패분 → SQS DLQ / failed/ Prefix

[확장] Step Functions
        Map(maxConcurrency=K) 로 Manifest 조각을 병렬 처리
        Catch → 실패 격리, Retry(지수 백오프) 내장
```

| 항목 | 기본값 | 근거 |
| --- | --- | --- |
| 워커 메모리 | 512MB | 객체 묶음 JSON 파싱·정규화에 충분, 비용 최소 |
| 워커 타임아웃 | 300s(5분) | 500건/배치 정규화 + DynamoDB BatchWrite 여유 |
| 배치 크기 | 500 객체 | 타임아웃·DynamoDB 25건/BatchWrite 청크 정합 |
| 동시성 한도 | 5 | DynamoDB 쓰기 스로틀·TourAPI 무관(읽기 없음) 고려한 보수값 |
| 재시도 | 2회(지수 백오프) | 일시적 AWS 오류 흡수, 초과 시 DLQ |

## 11.4 호출 단위(멱등 키)와 Manifest

Batch Manifest는 워커의 입력 계약이다. 동일 Manifest는 동일 출력을 보장한다.

```json
{
  "manifest_id": "KR-attraction-20260609-0001",
  "country": "KR",
  "entity_type": "attraction",
  "source": "tourapi",
  "batch_size": 500,
  "raw_objects": [
    "raw/KR/tourapi/attraction/2026/06/05/ATT-126508.json"
  ],
  "city_scope": ["KR-GW-GANGNEUNG"],
  "created_at": "2026-06-09T10:00:00+09:00",
  "reprocess": false
}
```

| 필드 | 의미 |
| --- | --- |
| `entity_type` | 워커가 적용할 스키마·정규화 규칙 분기 키 |
| `raw_objects` | 처리 대상 S3 Raw Key 목록(멱등 단위) |
| `city_scope` | 부분 재처리 범위 한정(§8.2) |
| `reprocess` | true면 기존 `processed_at` 무시하고 강제 재변환, ID·핵심 필드는 불변 |

# 12. 데이터 계약 (스키마)

본 절은 단계 간 입출력을 **고정 계약**으로 정의한다. 모든 워커는 입력을 §12.1 스키마로 검증하고, §12.2 정규화 산출물과 §12.3 DynamoDB Item을 출력한다. 표기는 `필드: 타입(제약)` 형식이며 `?`는 Optional이다.

## 12.1 Raw 입력 스키마 (Load 결과, 엔티티별)

도시별 원천(`{city_en}.json`)을 엔티티 유형으로 분해 적재한 단위 객체를 입력으로 한다(§3.3).

```text
AttractionRaw / FestivalRaw  (공통 골격)
  contentid: string(필수, 멱등 키)
  contenttypeid: string(필수; ATT=12·14·28·32·38·39, FES=15)
  title: string(필수)
  addr1: string(필수)         addr2: string?
  mapx: string(필수, 경도)    mapy: string(필수, 위도)
  tel: string?               # 실데이터 100% 결측 → §13.5 폴백
  firstimage: string?        firstimage2: string?
  cpyrhtDivCd: string?       # 공공누리 유형
  lDongRegnCd: string(필수)  lDongSignguCd: string(필수)   # City 매핑 키
  lclsSystm1/2/3: string(필수)   # 테마 매핑 기준(제공률 100%)
  cat1/cat2/cat3: string?    # 결측 35%, 보조 참조용
  _assigned_theme: string(필수, 6대 테마 중 1)
  detail:
    common: { overview: string?, homepage: string? }
    intro:  { ... contenttypeid별 가변 필드 (§14.2) }
  # Festival 전용
  eventstartdate: string(YYYYMMDD)   eventenddate: string(YYYYMMDD)
  progresstype: string?

CityRaw
  city_id: string(필수, KR-{GW|GB}-{CITY_EN})
  city_name_ko: string(필수)   prefecture_id: string(필수)
  location: string?  latitude: number(필수)  longitude: number(필수)
  description: string?
  climate_table: { caption: string, wikitext: string }   # 미취득 시 "수작업 필요"
  site_urls: string[]
  source_name/source_url/collected_at: string
  field_status: { <field>: "collected|needs_review|missing|blocked" }

VisitorStatisticsRaw
  city_id: string(필수)   year_month: string(YYYY-MM, 필수)
  local_daily_avg: number   outsider_daily_avg: number   foreigner_daily_avg: number
  source_name: "DataLabService"
```

## 12.2 Normalized 출력 스키마 (Transform 결과)

```text
NormalizedEntity (S3 Processed JSON, 엔티티 공통 봉투)
  entity_id: string          entity_type: "city|attraction|festival|visitor_statistics"
  country_code: "KR"         city_id: string(stat·att·fes 필수)
  source_name/source_url: string      s3_raw_uri: string
  collected_at/processed_at: string   verified_at: string?
  quality_status: "collected|needs_review|missing|blocked"
  data_confidence: number(0.0~1.0)
  normalized_payload: <엔티티별 본문>
  review_queues: string[]    # 분류된 검수 큐(없으면 [])

normalized_payload(Attraction)
  name: string   name_search: string   theme: string
  address: { full: string, sido: string?, sigungu: string?, detail: string? }
  geo: { lat: number, lon: number, geohash: string }     # WGS84
  tel: string?                # 폴백 결과(없으면 생략)
  description_summary: string   description_full: string?
  opening: { raw: string?, structured: object? }
  admission_fee: { status: "free|paid|variable|unknown", raw: string? }
  photo: { url: string?, thumb: string?, copyright: string?, exposable: boolean }
  features: { theme_tags: string[], season_tags: string[], visit_months: int[],
              itinerary_fit: string?, crowding_score: number?, novelty_score: number? }

normalized_payload(Festival)
  name / name_search / theme / address / geo / tel    # Attraction과 동일 골격
  period: { start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD",
            month: int, season: string, recurrence_rule: string?, period_text: string? }
  description_summary / description_full
  features: { theme_tags, season_tags, visit_months }

normalized_payload(City)
  city_name_ko: string   city_name_local: string   prefecture_id: string
  geo: { lat, lon, geohash }   description_summary: string
  climate: { monthly: object?, summary: string? }     # climate_table에서 분리
  climate_table_raw: string?   site_urls: string[]

normalized_payload(VisitorStatistics)
  year_month: string   local_daily_avg/outsider_daily_avg/foreigner_daily_avg: number
  total_daily_avg: number   crowding_index: number?     # 파생(§14.4)
```

## 12.3 DynamoDB Item 스키마 (Load 결과)

상위 계획서 테이블 후보(§7.1)를 Single-Table 관점으로 매핑한다. 공통 속성은 §7.2를 따른다.

| 엔티티 | PK | SK | 주요 비-키 속성 |
| --- | --- | --- | --- |
| City | `country_code`=`KR` | `city_id` | `normalized_payload`, `quality_status`, `data_confidence`, `s3_raw_uri`, `processed_at` |
| Attraction | `city_id` | `attraction_id` | + `theme`, `geohash`(GSI 후보), `quality_status` |
| Festival | `city_id` | `festival_id` | + `theme`, `period.month`(GSI 후보), `quality_status` |
| VisitorStatistics | `city_id` | `stat_period`(`yyyyMM`) | `total_daily_avg`, `crowding_index` |
| DataQuality | `entity_id` | `checked_at` | `failed_reason`, `confidence_breakdown` |
| ReviewQueue | `queue_name` | `entity_id` | `review_status`, `assigned_to` |

> GSI 후보: `theme-index`(PK `theme`, SK `city_id`)와 `month-index`(축제 월별 추천)는 추천 조회 패턴 확정 후 `04_database_design`과 합의해 확정한다(현 시점 신뢰도: 설계 제안).

# 13. 단계별 함수 설명

본 절은 워커 변환 로직을 **함수 단위 설명**으로 기술한다. 실제 코드는 작성하지 않으며, 각 함수의 책임·입력·출력·핵심 규칙만 계약 수준으로 고정한다. 구현은 `scripts/`(개발) 및 Lambda 패키지로 분리한다.

## 13.1 워커 핸들러

`handler(event, ctx)` — 워커 진입점. Manifest를 읽어 엔티티 유형별 규칙을 주입하고, 대상 Raw 객체를 순회하며 변환 단계를 오케스트레이션한다.

| 항목 | 내용 |
| --- | --- |
| 입력 | `event.manifest_s3_uri` (S3 Manifest 위치) |
| 출력 | `{ok, failed}` 카운트, S3 Processed/Quality 기록, DynamoDB 적재 |
| 처리 순서 | ①스키마검증 → ②정제 → ③정규화 → ⑤신뢰도 → ⑥파생 → ⑦검수분류 → (객체 순회 종료) → ④중복병합 → ⑧적재 |
| 실패 처리 | 객체 단위 `TransformError`는 격리(`route_failed`) 후 다음 객체 계속, 배치 전체는 중단하지 않음 |

## 13.2 스키마 검증 / 필드 정제 함수

`validate_schema(raw, rules)` — 필수 필드 존재·타입, 축제 날짜 포맷(YYYYMMDD), 좌표 파싱 가능 여부를 점검해 검증 결과(`ok`, `errors`)를 반환한다. 실패 객체는 `route_failed`로 격리한다.

`clean_fields(raw, rules)` — 원문 손상 없이 표현만 정제한다. HTML 태그(`<br>`·앵커)·제어문자·연속 공백 제거, 100% 결측 필드 제거(§14.3), 깨진 URL 보정/제거를 수행한다. `detail` 원문은 보존한다.

`normalize_entity(c, rules, s3_key)` — 정제된 레코드를 `NormalizedEntity` 봉투(§12.2)로 변환하는 정규화 총괄 함수. 다음 하위 함수를 순서대로 호출해 `normalized_payload`를 채운다.

| 호출 | 결과 필드 | 참조 |
| --- | --- | --- |
| `build_id` | `entity_id`(불변) | §13.4 |
| `normalize_name` | `name`, `name_search`(회차·괄호 분리 + 검색키) | — |
| `verify_theme` | `theme`(무결성 검증) | §13.6 |
| `normalize_address` | `address`, `city_id`(City 매핑) | §13.7 |
| `normalize_coords` | `geo`(WGS84 + geohash) | §13.8 |
| `resolve_tel` | `tel`(폴백, 없으면 생략) | §13.5 |
| `normalize_period` | `period`(축제만) | §13.9 |
| `summarize` / `normalize_opening` | `description_summary`, `opening` | — |
| `initial_status` | `quality_status` 초기값 | — |

## 13.4 불변 ID 생성

`build_id(rules, c)` — 엔티티 유형별 `entity_id`를 생성한다. `contentid`(또는 `year_month`)를 안정 키로 사용해 재처리 시에도 동일 ID를 보장한다(§8.1).

| 엔티티 | ID 형식 (코드정정) |
| --- | --- |
| City | `{city_id}` (`KR-{GW\|GB}-{CITY_EN}`) |
| Attraction | `ATT-{contentid}` |
| Festival | `FEST-{contentid}` |
| VisitorStatistics | `{city_id}-STAT-{yyyyMM}` (전처리 파생) |

## 13.5 연락처 폴백 (tel 100% 결측)

`resolve_tel(c, rules)` — 공통 `tel`이 100% 결측이므로, `contenttypeid`별 우선순위(§14.2)에 따라 `detail.intro`의 연락처 필드를 탐색해 상위 `tel`로 승격한다. 값이 있으면 `clean_phone`으로 정제 후 반환하고, 끝까지 없으면 생략(undefined)한다. **`false` 치환은 금지**한다(§5.3). 폴백 사전(`TEL_FALLBACK`)은 §14.2 표로 관리한다.

## 13.6 테마 무결성 검증

`verify_theme(assigned, c)` — 수집 단계에서 이미 6대 테마로 필터링된 `_assigned_theme`의 무결성만 검증한다. 6대 테마(`SIX_THEMES`)에 속하면 축제 수동 오버라이드 46건(`apply_festival_override`)을 반영해 반환하고, 속하지 않으면(수집 필터 누락분) `content_review` 큐로 분기한다(§5.2.3).

## 13.7 주소·City 매핑 / 13.8 좌표

`normalize_address(c)` — `addr1`/`addr2`를 시도·시군구·상세로 분해하고, 법정동 코드(`lDongRegnCd`·`lDongSignguCd`)를 우선 기준으로 City를 매핑한다(실패 시 주소 문자열 매핑으로 폴백). 어떤 기준으로도 매핑되지 않으면 `location_review` 큐(`city_unmapped`)로 분기한다. 반환은 분해된 주소 객체와 `city_id`.

`normalize_coords(mapx, mapy)` — `mapx`(경도)·`mapy`(위도) 문자열을 WGS84 decimal로 변환한다. 한국 좌표 범위(`KR_BBOX`, §14.5)를 벗어나면 `location_review`(`coord_out_of_range`)로 분기하고, 정상이면 `geohash`(정밀도 §14.5)를 포함한 `geo` 객체를 반환한다.

## 13.9 날짜·기간 정규화 (Festival)

`normalize_period(start, end)` — 축제 `eventstartdate`/`eventenddate`(YYYYMMDD)를 ISO `start_date`/`end_date`로 변환하고 `month`·`season`(§14.4)을 파생한다. 동일 축제가 연도만 다르게 반복되면 `recurrence_rule` 후보를 설정한다. 파싱 불가 시 `date_review`(`period_unparseable`)로 분기한다.

## 13.10 신뢰도 / 파생 / 검수 분류 / 적재

`score_confidence(n)` — 출처 공식성·최신성·필드 충족률·다중 출처 일치도·수동 검수 여부를 가중 합산(가중치 §14.5)해 `data_confidence`(0.0~1.0)를 산정한다.

`derive_features(n, rules)` — `normalized_payload`에 추천용 파생 필드(`theme_tags`·`season_tags`·`visit_months`·혼잡도 등, §14.4)를 채운다.

`classify_review(n)` — 앞 단계에서 누적된 검수 플래그에 더해, 설명 품질 저하 시 `content_review`, 저작권 불명확 시 `license_review`를 추가해 검수 큐 목록을 반환한다.

`load_dynamodb(items)` — 정규화 결과를 DynamoDB BatchWrite 제한(25건)에 맞춰 청크 단위로 적재한다. 핵심 필드 변경 또는 신규일 때만 적용되는 조건부 쓰기를 사용하고(§8.1), 충돌 시 변경 이력 후보로 기록한다.

# 14. 매핑 사전 · 설정 · 파생 규칙

## 14.1 contenttypeid 정의

| 코드 | 유형 | intro 필드셋 키 |
| --- | --- | --- |
| 12 | 관광지 | `usetime, restdate, usefee, parking, infocenter` |
| 14 | 문화시설 | `usetimeculture, restdateculture, usefee, parkingculture, parkingfee, spendtime, infocenterculture` |
| 15 | 축제·행사 | `usetimefestival, playtime, eventplace, sponsor1, sponsor1tel, program, discountinfofestival` |
| 28 | 레포츠 | (좌표·설명 위주, 운영정보 Optional) |
| 32 | 숙박 | (수집 대상 외, 존재 시 `source_review`) |
| 38 | 쇼핑 | (좌표·설명 위주) |
| 39 | 음식점 | `treatmenu, firstmenu, opentimefood, restdatefood, packing, reservationfood, parkingfood, infocenterfood` |

## 14.2 연락처 폴백 우선순위 (재확인)

| contenttypeid | 폴백 순서 | 실패 시 |
| --- | --- | --- |
| 12 | `infocenter` | tel 생략 |
| 14 | `infocenterculture` | tel 생략 |
| 39 | `infocenterfood` | tel 생략 |
| 15 | `infocenter` → `sponsor1tel` | tel 생략 |

## 14.3 100% 결측 → 제거/Optional 목록

`clean_fields`의 `always_drop`에 포함해 스키마 정합성을 확보한다(§5.3, 취득 계획서 §5.4).

```text
음식점(39): scalefood
축제(15):   bookingplace, discountinfofestival, eventhomepage,
            festivalgrade, sponsor2tel, subevent
공통:       tel(원본, 폴백 후 별도 처리)
```

Boolean 류(유모차/카드/반려동물 등)는 결측을 `false`로 치환하지 않고 생략. 원문에 명시적 거부(`N`/`불가`/`없음`)가 있을 때만 `false`.

## 14.4 파생 규칙

| 파생 필드 | 산출 규칙 |
| --- | --- |
| `season_tags` / `season` | `SEASON_OF_MONTH = {12,1,2:겨울; 3,4,5:봄; 6,7,8:여름; 9,10,11:가을}`. 축제는 `period.month` 기준, 관광지는 테마·실내외 휴리스틱 |
| `visit_months` | 축제: `[start.month..end.month]`. 관광지: 테마별 기본 추천월(예: `바다·해안`→[6,7,8]) + 기후 보정(City `climate`) |
| `recurrence_rule` | 동일 `title`이 연도만 다른 기간으로 반복되면 `FREQ=YEARLY;BYMONTH=…` 후보. 단건이면 미설정 |
| `crowding_score`(att/fes) | VisitorStatistics `total_daily_avg`를 City 단위로 정규화(0~1)해 연결. 대도시 편중 보정 |
| `crowding_index`(stat) | `total_daily_avg = local+outsider+foreigner`를 전체 City 분포 대비 백분위로 환산 |
| `novelty_score` | `1 - 정규화(인지도)` ≈ 방문자 적을수록↑. 소도시 추천 가중 |
| `itinerary_fit` | 운영시간·소요시간(`spendtime`)·테마로 반나절/1일/1박2일 후보 태깅 |

## 14.5 설정값 (config)

```text
KR_BBOX            = { lat: 33.0~38.7, lon: 124.5~131.9 }   # 한국 좌표 범위
GEOHASH_PRECISION  = 7                                       # ≈150m 격자
BATCH_SIZE         = 500
DDB_BATCH_CHUNK    = 25
CONFIDENCE_WEIGHTS = { official:0.35, fresh:0.20, fill:0.20, agree:0.15, review:0.10 }
SIX_THEMES = ["온천·휴양","바다·해안","역사·전통","미식·노포","자연·트레킹","예술·감성"]
FESTIVAL_OVERRIDES = filter_existing_lists.py::fest_overrides  # 코드 내 하드코딩, 46건
```

> 가중치·BBOX·geohash 정밀도는 설계 제안값(신뢰도: 중)이다. 추천 조회 패턴과 검수 결과로 보정한다.

# 15. 관측성 · 테스트 · 수량 정합

## 15.1 관측성

| 항목 | 방식 |
| --- | --- |
| 구조화 로그 | 호출당 `manifest_id`, `entity_type`, `ok/failed`, 큐별 분류 수를 JSON 로그로 CloudWatch 전송 |
| 지표 | `ProcessedCount`, `FailedCount`, `ReviewQueued{queue}`, `DDBThrottle`, `Duration`을 CloudWatch Metric으로 게시 |
| 추적 | 실패 객체는 `failed/KR/...` Prefix + `LovvDataQuality`에 `failed_reason` 기록(§8.3) |
| 경보 | `FailedCount > 0` 또는 `DDBThrottle > 0` 시 알림(운영 임계는 추후 확정) |

## 15.2 단위 테스트 픽스처

GitHub 허용 소량 픽스처(§3.1)로 변환 함수를 검증한다.

| 테스트 | 입력 픽스처 | 기대 |
| --- | --- | --- |
| tel 폴백 | `tel:""`, `infocenter:"033-..."` (type 12) | `payload.tel == "033-..."` |
| tel 전무 | 모든 연락처 결측 | `payload`에 `tel` 키 없음(생략) |
| 테마 무결성 | `_assigned_theme` 비-6대 | `content_review` 큐 분류 |
| 좌표 범위 | `mapy:"10.0"` | `location_review`, `coord_out_of_range` |
| 축제 기간 | `eventstartdate:"20250525"` | `start_date:"2025-05-25"`, `month:5`, `season:봄` |
| City 매핑 | 포항 남구/북구 `lDong` | `city_id == "KR-GB-POHANG"` (통합) |
| Boolean 결측 | 반려동물 필드 결측 | `false` 치환 아님(생략/null) |

## 15.3 수량 정합 검증

배치 종료 후 적재 수를 취득 기준(취득 계획서 §9)과 대조한다.

| 대상 | 기준 수량 | 검증 |
| --- | --- | --- |
| City | 40 | `count(LovvCity where country_code=KR) == 40` |
| Attraction | 3,709 | 적재 수 == 3,709 (필터·중복 제거 후 정본) |
| Festival | 106 | 적재 수 == 106 |
| VisitorStatistics | 480 | 40 City × 12개월 |

### 15.3.1 테마 합계 4,911 vs 적재 3,709 불일치 검증 (신뢰도: 확인 필요)

§5.2.3에서 명시한 대로 테마별 관광지 합계 **4,911건**은 적재 정본 **3,709건**과 1,202건 차이가 있다. 본 설계는 적재 기준 **3,709건을 정본**으로 삼고, 변환 종료 시 다음을 자동 산출해 차이 원인을 확정한다.

```text
1) 테마별 실적재 수 재집계: GROUP BY theme on LovvAttraction
2) Σ(테마별 실적재) == 3,709 검증
3) 4,911(분류 분포 참고값)과의 차이를 리포트:
   - 다중 테마 중복 카운트분
   - 미식·노포 FD010100 한정 필터 이전/이후 차이
   - should_exclude 제외분
4) 리포트를 quality/KR/attraction/.../theme_reconciliation.json 으로 저장
```

검증 통과 기준은 "Σ(테마별 실적재) == 3,709"이며, 4,911은 분류 분포 **참고용**으로만 유지한다.

# 16. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-08 | 조동휘 | KR 실수집 데이터 기준 ELT 전처리 상세 설계 초안 작성. 15MB→S3 경계 규칙, tel 폴백, 6대 테마 매핑, 멱등·재처리·실패 처리, DynamoDB 적재 조건 반영 |
| v0.2 | 2026-06-09 | 조동휘 | 구현 가능 수준 심화: Lambda 함수 분해·오케스트레이션·Manifest 계약(§11), Raw/Normalized/DynamoDB 데이터 계약 스키마(§12), 단계별 함수 설명(§13, 코드 미작성·함수 책임/입출력/규칙만 기술), 매핑 사전·설정·파생 규칙(§14), 관측성·단위테스트·수량 정합 검증 및 테마 4,911↔3,709 불일치 검증 절차(§15) 추가. HTML/PDF 재생성은 보류 |
| v0.3 | 2026-06-09 | 조동휘 | `tour-api-korea` 코드 대조 정정: ID 형식(City `KR-{GW\|GB}-*`, Attraction `ATT-`, Festival `FEST-{contentid}`), 방문통계(엔드포인트 `locgoRegnVisitrDDList`, `touDivCd` 1/2/3, final 임베드→unnest, `locals_*`/`out_of_town_*`/`foreigners_*`→표준명), 데이터 파일 구조(`data/raw/*`·`data/city/*`·`data/visitor/*`), 테마 키(`lclsSystm3 or cat3`+`C01` 제외), 오버라이드 위치(`filter_existing_lists.py` 하드코딩), tel 폴백·City 보강을 전처리 단계 보강 대상으로 명시. Manifest·build_id·테스트 예시 ID 정정. 코드 기반 동반 문서: `kr_preprocessing_code_based_design.md` |
