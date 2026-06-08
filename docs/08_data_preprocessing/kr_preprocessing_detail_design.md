# 로브 (Lovv) 한국(KR) 데이터 전처리 상세 설계서

> 문서 버전: v0.1
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-08
> 기준 문서: `docs/08_data_preprocessing/data_preprocessing_plan.md` v0.5
> 실데이터 기준: `docs/03_data_collect_plan/korea_data_acquisition_plan_updated.md` v0.2
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
                   → 로컬 검증 산출물(data/KR/*.json, data/raw/final/{city_en}.json)
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
| 크롤링 원본·검증 JSON (`data/KR/*.json`, `data/raw/final/*.json`) | **S3 (크기 무관)** | 작아도 데이터는 S3가 정본 |
| 파이프라인 코드(`scripts/*.py`), 스키마, 매핑 사전, 문서 | GitHub | |
| 테마 오버라이드 등 소량 설정(`festival_theme_overrides.json`) | GitHub 허용 | 재현용 수 KB 설정 |
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
| 적재 전 검증 | `data/KR/*.json` 수량 검증 통과(City 40, Attraction 3,709, Festival 106) 후 적재 확정 |

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

data/KR/
 ├── prefectures.json           광역(강원·경북) 레코드
 ├── cities.json                40개 도시 (prefecture_id 외래키)
 ├── attractions.json
 ├── festivals.json
 └── visitor_statistics.json    월별 도시별 일평균 (독립 엔티티)
```

## 4.2 엔티티별 핵심 입력 필드와 처리 난점

| 엔티티 | 핵심 입력 | 처리 난점 |
| --- | --- | --- |
| City | `city_id`(`KR-{도_코드}-{CITY_EN}`), `prefecture_id`, 좌표, `description`, `climate_table` | `climate_table` 자동 취득 실패 시 `needs_review`. wikitext 원문 보존 후 분리 |
| Attraction | 리스트 필드 + `detail.common.overview` + 유형별 `detail.intro` | `tel` 100% 결측 → `infocenter` 계열 폴백, `cat1~3` 35% 결측 → 테마 매핑 제외 |
| Festival | + `eventstartdate/eventenddate`(YYYYMMDD), `_assigned_theme` | `tel` 100% 결측 → `infocenter`/`sponsor1tel` 폴백, 테마 수동 오버라이드 반영 |
| VisitorStatistics | `city_id`, `year_month`, `local/outsider/foreigner_daily_avg` | 일별 단순 합산 시 중복 집계 → 월 구간 쿼리 후 월 일수로 나눈 일평균 사용 |

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

| 대상 | ID 형식 | 예시 |
| --- | --- | --- |
| City | `KR-{도_코드}-{CITY_EN}` | `KR-42-GANGNEUNG` |
| Attraction | `KR-{도_코드}-{CITY_EN}-ATT-{contentid}` | `KR-42-GANGNEUNG-ATT-126508` |
| Festival | `KR-{도_코드}-{CITY_EN}-FES-{contentid}` | `KR-42-GANGNEUNG-FES-2762975` |
| VisitorStatistics | `KR-{도_코드}-{CITY_EN}-STAT-{yyyyMM}` | `KR-42-GANGNEUNG-STAT-202501` |

ID는 재처리 시에도 불변이어야 한다. `contentid`를 안정 키로 사용한다.

### 5.2.2 연락처 폴백 (tel 100% 결측 대응)

공통 `tel`은 실데이터에서 100% 결측이므로, `detail.intro`의 유형별 연락처 필드를 우선순위로 탐색해 상위 `tel`로 승격한다.

| 엔티티/유형 | 폴백 우선순위 |
| --- | --- |
| 관광지(12) | `infocenter` |
| 문화시설(14) | `infocenterculture` |
| 음식점(39) | `infocenterfood` |
| 축제(15) | `infocenter` → `sponsor1tel` |

폴백으로도 값이 없으면 `tel`은 생략(undefined)하며 `false` 치환하지 않는다.

### 5.2.3 6대 테마 매핑

테마는 결측률 35%인 `cat1~3` 대신 **제공률 100%인 `lclsSystm1·2·3`**을 기준으로 자동 매핑한다. 6대 테마 중 하나로 매핑되지 않는 항목은 수집 단계에서 이미 필터링(Drop)되었으므로, Transform은 매핑 무결성 검증과 축제 오버라이드 반영을 담당한다.

| 테마 | 설명 | 관광지 | 축제 |
| --- | --- | ---: | ---: |
| `온천·휴양` | 온천, 스파, 리조트, 힐링 | 120 | 0 |
| `바다·해안` | 바다, 해안, 해수욕장, 해양 활동 | 249 | 0 |
| `역사·전통` | 역사, 문화유산, 전통 문화 | 1,001 | 10 |
| `미식·노포` | 맛집, 전통 음식점(관광식당 `FD010100` 한정) | 2,480 | 22 |
| `자연·트레킹` | 자연, 등산, 트레킹, 국립공원 | 687 | 13 |
| `예술·감성` | 예술, 디자인, 감성, 문화, 행사 | 374 | 61 |

- 축제는 자동 분류 후 `crawling/KR/targets/festival_theme_overrides.json`의 수동 오버라이드 46건을 적용한다.
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

DataLabService 월 구간 쿼리 결과를 해당 월 일수로 나눈 일평균으로 저장한다. 원천(`{city_en}.json`)과 분리해 독립 엔티티로 적재한다.

| 필드 | 산출 |
| --- | --- |
| `year_month` | `"2025-01"` |
| `local_daily_avg` | 현지인 총합 / 월 일수 |
| `outsider_daily_avg` | 외지인 총합 / 월 일수 |
| `foreigner_daily_avg` | 외국인 총합 / 월 일수 |

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

# 11. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-08 | LLM 파트 | KR 실수집 데이터 기준 ELT 전처리 상세 설계 초안 작성. 15MB→S3 경계 규칙, tel 폴백, 6대 테마 매핑, 멱등·재처리·실패 처리, DynamoDB 적재 조건 반영 |
