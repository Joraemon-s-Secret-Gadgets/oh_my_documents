# 로브 (Lovv) 한국(KR) 전처리 설계 — 샘플 코드 기반

> 문서 버전: v0.2
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-09 (v0.2 상세화: 2026-06-09)
> 작성자: 조동휘
> 기준 코드: `Gloveman/tour-api-korea` (main) — 현재 한국 수집 샘플 코드
> 상위 계획서: `docs/08_data_preprocessing/data_preprocessing_plan.md` v0.5
> 관련 상세설계: `docs/08_data_preprocessing/kr_preprocessing_detail_design.md` v0.2
> 불일치 정리: `docs/03_data_collect_plan/korea_acquisition_plan_corrections.md` v0.1

## 1. 문서 개요

### 1.1 목적

본 문서는 **현재 한국 수집 샘플 코드(`tour-api-korea`)가 실제로 산출하는 데이터 구조**를 기준으로 전처리(ELT) 파이프라인을 설계한다. 기존 상세 설계(`kr_preprocessing_detail_design.md` v0.2)가 취득 계획서의 *설계 의도*에 맞춰 작성된 반면, 본 문서는 코드가 만드는 *실제 산출물*(파일 경로·스키마·ID 형식·방문통계 구조)을 입력 정본으로 삼는다.

코드와 기존 문서의 차이는 `korea_acquisition_plan_corrections.md`에 정리했으며, **두 문서가 충돌할 경우 코드 사실을 정본으로 한다.**

### 1.2 적용 범위

| 구분 | 범위 |
| --- | --- |
| 국가 | 한국(KR), 강원(GW)·경북(GB) 40개 도시 |
| 입력 정본 | `data/raw/final/{city_en}.json`(리스트+detail+임베드 통계), `data/city/{city_en}.json`(정규화본) |
| 처리 모델 | ELT (Extract → Load Raw to S3 → Transform → DynamoDB) |
| 수량 | Attraction 3,709, Festival 106, 상세 3,815, VisitorStatistics 40도시×12개월 |
| 제외 | 일본(JP), 추천 알고리즘, 수집(Extract) 단계 내부 로직 |

### 1.3 수집 파이프라인 단계 (코드 사실)

| 단계 | 스크립트 | 입력 → 출력 |
| --- | --- | --- |
| 1 리스트 | `scrape_list.py` | `areaBasedList2`·`searchFestival2` → `data/raw/list/{regn}_{sig}_raw.json`·`_filtered.json` |
| 1.5 그룹화 | `group_lists_by_city.py` | `list/` → `data/raw/list_by_city/{city_en}.json` (40도시) |
| 1.6 테마 | `filter_existing_lists.py` | 테마 매핑 + 축제 오버라이드 46건 적용 |
| 2 상세 | `scrape_details.py` | `detailCommon2`·`detailIntro2` → `data/raw/detail/{contentid}.json` (`{common,intro}`) |
| 3 병합 | `merge_to_final.py` | list_by_city + detail → `data/raw/final/{city_en}.json` |
| 4 통계 | `scrape_and_aggregate_visitor.py` | `locgoRegnVisitrDDList` → final에 `visitor_statistics` 임베드 + `data/visitor/monthly_visitor_averages.json` |
| 5 정규화 | `normalize_details.py` | final/detail → `data/city/{city_en}.json` |

전처리(본 문서)는 **5단계 산출물 이후**, 즉 `data/raw/final/*`와 `data/city/*`를 S3에 적재한 뒤의 변환·검증·DynamoDB 적재를 다룬다.

## 2. 입력 데이터 실구조 (코드 기준)

### 2.1 `data/raw/final/{city_en}.json`

```text
{
  "meta": { "province", "sigungu", "regn_cd", "sigungu_cd", "scraped_at",
            "city_name_ko", "city_name_en" },
  "attractions": [
    { (areaBasedList2 리스트 필드) contentid, contenttypeid, title,
      addr1, addr2, mapx, mapy, firstimage, firstimage2, cpyrhtDivCd,
      areacode, sigungucode, lDongRegnCd, lDongSignguCd,
      lclsSystm1, lclsSystm2, lclsSystm3,
      "_assigned_theme": "<6대 테마>",         # cat1~3는 필터 단계에서 삭제됨
      "detail": { "common": { overview, homepage, addr1, mapx, mapy, firstimage,
                              lDongRegnCd, lDongSignguCd, ... },
                  "intro":  { contenttypeid별 가변 필드 } } }
  ],
  "festivals": [
    { contentid, contenttypeid("15"), title, addr1, addr2, mapx, mapy,
      lclsSystm1("EV"), lclsSystm2, lclsSystm3, "_assigned_theme",
      "detail": { "common": {...},
                  "intro": { eventstartdate, eventenddate, playtime,
                             eventplace, sponsor1, sponsor1tel, program, ... } } }
  ],
  "visitor_statistics": {        # 4단계에서 임베드(독립 파일 아님)
    "year": 2025,
    "annual_totals": { locals, out_of_town, foreigners, total_visitors },
    "annual_daily_averages": { locals, out_of_town, foreigners, total_visitors },
    "monthly_statistics": [
      { "month":"2025-01", "days":31,
        "locals_total", "locals_daily_avg",
        "out_of_town_total", "out_of_town_daily_avg",
        "foreigners_total", "foreigners_daily_avg",
        "total_visitors", "total_daily_avg" } , ... 12개월 ]
  }
}
```

> 핵심: 축제의 `eventstartdate`/`eventenddate`는 리스트가 아니라 **`detail.intro`**에 있다. 좌표는 `detail.common.mapy`(위도)/`mapx`(경도) 우선, 없으면 리스트 `mapy`/`mapx`.

### 2.2 `data/city/{city_en}.json` (정규화본, `normalize_details.py`)

```text
{
  "city": {
    "city_id": "KR-GW-GANGNEUNG",        # KR-{GW|GB}-{CITY_EN_UPPER}
    "city_name_ko", "city_name_en", "province", "district_type"(시/군/구),
    "location", "latitude", "longitude",
    "description": "{도시명} 관광 정보",          # placeholder
    "climate": "기상청 API 연계 예정",            # placeholder
    "site_url": ""
  },
  "attractions": [
    { "attraction_id":"ATT-{contentid}", "city_id", "content_id", "content_type_id",
      "theme"(None 가능), "name", "address"(common.addr1), "description"(overview),
      "site_url"(homepage), "opening_hours", "opening_period",
      "latitude"(mapy), "longitude"(mapx), "admission_fee"(usefee),
      "photo_url"(firstimage), "areacode", "sigungucode",
      "source_name":"TourAPI", "source_url",
      "collected_at", "data_confidence", "verified_at":null,
      "verified_source_url":null, "verification_note":null } ],
  "festivals": [
    { "festival_id":"FEST-{contentid}", "city_id", "content_id", "theme",
      "name", "address", "description"(common.overview), "site_url",
      "photo_url", "period_text"(intro.playtime),
      "start_date"(eventstartdate), "end_date"(eventenddate), "month"(start[4:6]),
      "latitude", "longitude", "areacode", "sigungucode",
      "source_name","source_url","collected_at",
      "verified_at":null, ... } ],
  "metadata": { "status":"collected", "scraped_at" }
}
```

### 2.3 정규화본의 변환 규칙 (코드 사실)

| 대상 | 규칙 |
| --- | --- |
| 운영시간/요금(관광지 12·14) | `opening_hours=intro.usetime`, `admission_fee=intro.usefee` |
| 운영시간(음식점 39) | `opening_hours=intro.opentimefood`, `admission_fee=""`, `treatmenu`는 `description`에 `[대표 메뉴]`로 추가 |
| 운영시간(쇼핑 38) | `opening_hours=intro.opentime` |
| 테마 | `_assigned_theme`가 `"테마 없음"`이면 `theme=None` |
| 좌표 | `latitude=common.mapy or list.mapy`, `longitude=common.mapx or list.mapx`, 파싱 실패 시 0.0 |
| 축제 `month` | `eventstartdate[4:6]` |
| `data_confidence`(관광지) | `opening_hours` 또는 `usefee`가 있으면 `"needs_review"`, 없으면 `"collected"` |
| 연락처(tel) | **출력 없음** — infocenter 폴백 미구현(전처리 단계 보강 대상) |

## 3. 전처리(ELT) 경계와 S3 적재

### 3.1 GitHub vs S3

데이터 정본은 S3, GitHub은 코드·설정·문서. `tour-api-korea`의 `.gitignore`도 원본/캐시/대용량 결과를 제외하고 로컬 생성한다(README). 전처리 입력은 다음을 S3 Raw로 PUT한다.

| 적재 대상 | S3 Raw Prefix(제안) |
| --- | --- |
| `data/raw/final/{city_en}.json` | `raw/KR/final/{city_en}/{yyyy}/{mm}/{dd}/` |
| `data/city/{city_en}.json` | `raw/KR/normalized/{city_en}/{yyyy}/{mm}/{dd}/` |
| `data/visitor/monthly_visitor_averages.json` | `raw/KR/visitor/{yyyy}/{mm}/{dd}/` |
| 입력 사전(`theme_mapping`,`festival_mapping`,`ldong_sigungu`,`classification_dict`) | `config/KR/`(소량, GitHub 병행 허용) |

> 멱등 키: 관광지/축제는 `contentid`, 통계는 `city_en`+`month`.

## 4. Transform 단계 (코드 산출물 → 서비스 데이터)

상위 계획서·상세설계의 8단계(스키마검증→정제→정규화→병합→신뢰도→파생→검수분류→적재)를 따르되, **본 문서는 코드 산출물을 입력으로 한 구체 변환만 기술**한다.

### 4.1 엔티티 분해 (1 final 파일 → N 엔티티)

`data/raw/final/{city_en}.json` 하나에서 다음을 추출한다.

| 추출 엔티티 | 소스 |
| --- | --- |
| City 1건 | `data/city/{city_en}.json`의 `city` (또는 final `meta`) |
| Attraction N건 | `attractions[]` (+`detail`) |
| Festival N건 | `festivals[]` (+`detail`) |
| VisitorStatistics 12건 | `visitor_statistics.monthly_statistics[]` → **월별 독립 엔티티로 분리** |

> 방문통계는 코드에서 final 파일에 임베드되어 있으므로, 전처리에서 `monthly_statistics[]`를 12개의 독립 `VisitorStatistics` 아이템으로 **풀어내는(unnest) 변환**이 필수다.

### 4.2 서비스 표준 변환 규칙

| 항목 | 코드 입력 | 서비스 표준 출력 |
| --- | --- | --- |
| City ID | `KR-GW-GANGNEUNG` | 그대로 사용(정책 확정 시 도 숫자코드로 재매핑) |
| Attraction ID | `ATT-{contentid}` | `attraction_id`는 안정 키. 서비스 PK는 `city_id`+`attraction_id` |
| Festival ID | `FEST-{contentid}` | 동일 |
| 방문통계 필드 | `locals_*`/`out_of_town_*`/`foreigners_*` | 서비스 표준명 매핑: `local`/`outsider`/`foreigner` (매핑 사전 명시) |
| 좌표 | `latitude`/`longitude`(0.0 가능) | 0.0 또는 KR BBOX 이탈 시 `location_review` |
| 테마 | `theme`(None 가능) | None이면 `content_review` |
| tel | (없음) | `detail.intro`의 `infocenter`/`infocenterculture`/`infocenterfood`/`sponsor1tel` 폴백으로 **전처리에서 보강** |
| 날짜 | `start_date`/`end_date`(YYYYMMDD), `month`("MM") | ISO `YYYY-MM-DD`, `season` 파생 |
| 설명 | `description`(placeholder/overview) | City placeholder는 보강 대상, overview는 내부 요약 |

### 4.3 방문통계 변환 (touDivCd 매핑)

`scrape_and_aggregate_visitor.py` 기준 `touDivCd`: **1=현지인, 2=외지인, 3=외국인**. 월별 `touNum` 합을 월 일수로 나눈 일평균이 입력이다. 전처리는 `monthly_statistics[i]`를 다음으로 변환한다.

| 입력 | 출력(VisitorStatistics 아이템) |
| --- | --- |
| `month`("2025-01") | `year_month`="2025-01", `stat_period`="202501" |
| `locals_daily_avg` | `local_daily_avg` |
| `out_of_town_daily_avg` | `outsider_daily_avg` |
| `foreigners_daily_avg` | `foreigner_daily_avg` |
| `total_daily_avg` | `total_daily_avg` (혼잡 지표 산출 기반) |

## 4.4 Attraction 필드 단위 변환 (코드 상세)

`normalize_details.py`가 `attractions[].detail`에서 정규화 레코드를 만드는 규칙을 필드 단위로 정의한다. 운영시간·요금은 **`content_type_id`에 따라 소스 필드가 달라진다.**

| 출력 필드 | 소스(코드) | 비고 |
| --- | --- | --- |
| `attraction_id` | `f"ATT-{contentid}"` | 안정 키 |
| `city_id` | 파일 그룹(도시) → `KR-{GW\|GB}-{CITY_EN}` | 리스트 그룹화로 결정(lDong 아님) |
| `content_id` / `content_type_id` | `contentid` / `contenttypeid` | |
| `theme` | `_assigned_theme`, `"테마 없음"`이면 `None` | None은 `content_review` |
| `name` | `title` | |
| `address` | `detail.common.addr1` → 없으면 리스트 `addr1` | addr2 분해 없음 |
| `description` | `detail.common.overview` | 음식점(39)은 `[대표 메뉴]\n{treatmenu}` 추가 |
| `site_url` | `detail.common.homepage` | HTML 앵커 가능 |
| `opening_hours` | 유형별(아래 표) | |
| `opening_period` | `content_type_id != 39`이면 `intro.usetime`, 39면 `""` | 12·14는 `opening_hours`와 중복될 수 있음(코드 특성) |
| `admission_fee` | 유형별(아래 표) | |
| `latitude` / `longitude` | `common.mapy or list.mapy` / `common.mapx or list.mapx` | 파싱 실패 시 `0.0` |
| `photo_url` | `common.firstimage or list.firstimage` | 없으면 `""` |
| `areacode` / `sigungucode` | 리스트 필드 | 일부 `""` |
| `source_name` | `"TourAPI"` | |
| `source_url` | `.../detailCommon2?contentId={contentid}` | |
| `collected_at` | detail 캐시 파일 mtime(`"%Y-%m-%d %H:%M:%S"`) | |
| `data_confidence` | `opening_hours` 또는 `usefee`가 있으면 `"needs_review"`, 없으면 `"collected"` | 역논리(§4.9) |
| `verified_at`/`verified_source_url`/`verification_note` | `null` | |

운영시간·요금의 `content_type_id`별 소스:

| content_type_id | 유형 | `opening_hours` | `admission_fee` | 비고 |
| --- | --- | --- | --- | --- |
| 12 | 관광지 | `intro.usetime` | `intro.usefee` | |
| 14 | 문화시설 | `intro.usetime` | `intro.usefee` | 코드상 12와 동일 분기(`usetimeculture` 미사용) |
| 38 | 쇼핑 | `intro.opentime` | `""` | |
| 39 | 음식점 | `intro.opentimefood` | `""` | `treatmenu`→description |

> 전처리 보강 포인트: (1) 14(문화시설)는 코드가 `usetime`을 쓰지만 실제 명세는 `usetimeculture`이므로, 전처리에서 `usetimeculture`/`restdateculture`를 보강 검토. (2) `tel`은 출력되지 않으므로 `detail.intro`의 `infocenter`/`infocenterculture`/`infocenterfood` 폴백을 전처리에서 적용.

## 4.5 Festival 필드 단위 변환 (코드 상세)

| 출력 필드 | 소스(코드) | 비고 |
| --- | --- | --- |
| `festival_id` | `f"FEST-{contentid}"` | |
| `city_id` | 파일 그룹(도시) | |
| `content_id` | `contentid` | |
| `theme` | `_assigned_theme`(오버라이드 46건 반영), `"테마 없음"`이면 `None` | |
| `name` | `title` | |
| `address` | `common.addr1 or list.addr1` | |
| `description` | `detail.common.overview` | |
| `site_url` | `detail.common.homepage` | |
| `photo_url` | `common.firstimage or list.firstimage` | |
| `period_text` | `detail.intro.playtime` | 운영 시간 원문 |
| `start_date` / `end_date` | `detail.intro.eventstartdate` / `eventenddate` (YYYYMMDD) | **리스트 아닌 intro** |
| `month` | `eventstartdate[4:6]` (예: `"05"`) | |
| `latitude` / `longitude` | `common.mapy or list.mapy` / `common.mapx or list.mapx` | 실패 시 0.0 |
| `areacode` / `sigungucode` | 리스트 | |
| `source_name`/`source_url`/`collected_at` | `"TourAPI"` / detailCommon2 / mtime | |
| `verified_*` | `null` | |

> 전처리 변환: `start_date`/`end_date`(YYYYMMDD) → ISO `YYYY-MM-DD`, `month`(문자열) → `season` 파생, 반복 축제 `recurrence_rule` 후보.

## 4.6 City 필드 단위 변환 (코드 상세)

`normalize_details.py`의 City 블록은 도시별 집계로 생성한다.

| 출력 필드 | 소스(코드) | 비고 |
| --- | --- | --- |
| `city_id` | `f"KR-{prov_en}-{city_en.upper()}"` | `prov_en`: 강원=`GW`, 경북=`GB` |
| `city_name_ko` / `city_name_en` | 리스트 meta | 영문은 `ENGLISH_NAMES` 음역 사전 |
| `province` | 리스트 meta `province` | 예: 강원특별자치도 |
| `district_type` | `city_ko` 접미사: 시→`시`, 군→`군`, 그 외→`구` | |
| `location` | `f"{province} {city_name_ko}"` | |
| `latitude` / `longitude` | Excel `korea_region_latitude_longitude.xlsx`(시트 `location`, key `(do, city)`) 우선 → 없으면 관광지 좌표 평균(centroid) → 축제 평균 → `(36.5, 128.0)` | |
| `description` | `f"{city_name_ko} 관광 정보"` | **placeholder** |
| `climate` | `"기상청 API 연계 예정"` | **placeholder** |
| `site_url` | `""` | **미보강** |

> 전처리/보강 과제: `description`(Wikipedia 요약), `climate`(기상청 월별), `site_url`(지자체 관광 URL), `prefecture_id`(광역 외래키)는 코드에 없으므로 전처리·후속 수집에서 채운다. 보강 전 City는 `quality_status=needs_review` 권고.

## 4.7 방문통계 상세 (코드 상세)

`scrape_and_aggregate_visitor.py` 기준.

| 항목 | 코드 사실 |
| --- | --- |
| 엔드포인트 | `DataLabService/locgoRegnVisitrDDList` |
| 공통 파라미터 | `MobileOS=ETC`, `MobileApp=Lovv`, `_type=json`, `numOfRows=5000`, `pageNo` 순회 |
| 구간 | 2025년 12개월, 각 월 `startYmd`~`endYmd`(동일 월) |
| 도시 매핑 | `signguCode` → city. `sigungu_map`은 각 final 파일 **첫 관광지의 `detail.common.lDongRegnCd + lDongSignguCd`**(`f"{regn}{signgu}"`)로 구성 |
| 구분 코드 | `touDivCd`: 1=현지인, 2=외지인, 3=외국인. `touNum`을 도시·월·구분별 합산 |
| 월 일평균 | `*_daily_avg = *_total / days`(28~31) |
| 전체 | `total_visitors = locals + out_of_town + foreigners`, `total_daily_avg = total/days` |
| 연간 | `annual_totals`, `annual_daily_averages`(= 연합계 / 연일수) 동반 산출 |
| 저장 | final 파일 `visitor_statistics`에 임베드 + 전역 `data/visitor/monthly_visitor_averages.json`(키 `city_en`, `city_ko`·`signguCode`·`year` 포함) |

전처리 unnest(12개월 → 12 아이템) 변환:

```text
for m in final.visitor_statistics.monthly_statistics:
    VisitorStatistics(
      entity_id   = f"{city_id}-STAT-{m.month.replace('-','')}",
      city_id, year_month = m.month, stat_period = m.month.replace('-',''),
      local_daily_avg     = m.locals_daily_avg,
      outsider_daily_avg  = m.out_of_town_daily_avg,
      foreigner_daily_avg = m.foreigners_daily_avg,
      total_daily_avg     = m.total_daily_avg )
```

> 중복 집계 방지: 일별 단순 합산이 아니라 **월 구간 1회 쿼리 → 월 일수로 나눈 일평균**을 정본으로 한다(코드 설계 의도와 일치).

## 4.8 테마 매핑 상세 (코드 상세)

`scrape_list.py`·`filter_existing_lists.py` 기준.

| 단계 | 규칙 |
| --- | --- |
| 대상 테마 | `온천·휴양`,`바다·해안`,`역사·전통`,`미식·노포`,`자연·트레킹`,`예술·감성` (6) |
| 사전 | `data/theme_mapping.json`(관광지)·`data/festival_mapping.json`(축제). 각 테마의 항목 `code`→테마 역인덱스 구성 |
| 하드 제외 | `lclsSystm1 == "C01"` 항목 무조건 제외 |
| 조회 키 | `code = lclsSystm3 or cat3` (소분류 우선, cat3 폴백) |
| 매핑 | `theme = code_to_theme.get(code)`; 매핑되면 `_assigned_theme` 부여, `cat1/cat2/cat3` 삭제 |
| 축제 오버라이드 | `fest_overrides`(contentid→테마) 우선 적용, 없으면 코드 매핑 |

`should_exclude`(사전 항목 메타 기준):

| 기준 | 제외 값 |
| --- | --- |
| `large_category` | `체험관광` |
| `middle_category` | `기타문화관광지`, `레저스포츠시설`, `교육시설`, `공연시설`, `복합관광시설` |
| `name` | `기타주점`, `클럽`, `기타간이음식`, `북한관광지`, `기타안보관광지`, `기타 종교성지`, `약수터` |

축제 오버라이드 46건 분포(코드 `fest_overrides` 집계): 바다·해안 10, 온천·휴양 1, 미식·노포 11, 자연·트레킹 10, 역사·전통 14 = **46**.

## 4.9 결측·예외·특이 처리 (코드 상세)

| 항목 | 코드 동작 | 전처리 권고 |
| --- | --- | --- |
| `data_confidence` 역논리 | 관광지: `opening_hours`/`usefee`가 **있으면** `needs_review`(변동성 큰 필드 존재=검수 필요), 없으면 `collected` | 문자열 상태로 보존하되, 전처리 신뢰도 점수(0~1, 상세설계 §13.10)와 병행 |
| 좌표 `0.0` | mapx/mapy 파싱 실패 시 `0.0`으로 적재 | `(0.0,0.0)`·KR BBOX 이탈은 `location_review` |
| City 좌표 centroid | 공식 좌표 없으면 관광지 평균, 최후 `(36.5,128.0)` | 폴백 좌표는 낮은 신뢰도, City `needs_review` |
| `tel` 부재 | 출력 안 함 | `detail.intro` infocenter 계열 폴백 보강 |
| 음식점 `treatmenu` | `description`에 `[대표 메뉴]` 추가 | 본문/메뉴 분리 저장 검토 |
| `theme=None` | `"테마 없음"` 매핑 시 | `content_review` 분기 |
| 14(문화시설) 운영시간 | 코드가 `usetime` 사용(명세는 `usetimeculture`) | `usetimeculture`/`restdateculture` 보강 |
| `collected_at` | detail 캐시 파일 mtime 기반 | 신뢰도·최신성 산정 시 수집 시각으로 사용 |

## 4.10 TourAPI 호출·오류 정책 (코드 상세, 재처리 영향)

전처리 자체는 TourAPI를 호출하지 않으나, Raw 보강·재수집 시 코드 정책을 따른다.

| 항목 | 코드 사실 |
| --- | --- |
| 상세 호출 | `detailCommon2`는 `contentId`만, `detailIntro2`는 `contentId`+`contentTypeId` |
| 캐시 | `data/raw/detail/{contentid}.json` = `{common, intro}`(리스트 응답은 `[0]`으로 단건화) |
| 키 풀 | `.env`의 `TOUR_API_KEYS`(디코딩 키, 콤마 구분), 쿼터 초과(`0022`/`22`/LIMIT/EXCEEDED·HTTP 429) 시 로테이션 |
| Fail-Fast | 영구 오류 코드 `10,11,12,30,31,32`는 재시도 없이 즉시 중단 |
| 체크포인트 | `data/download_progress.json`(도시별 진행·완료·실패), 재시작 지원 |

## 5. 품질 검증 (코드 산출물 특화)

| 검증 | 기준 | 실패 상태 |
| --- | --- | --- |
| City 매핑 | 모든 Attraction/Festival의 `city_id`가 40도시 중 하나 | `location_review` |
| 좌표 | `latitude/longitude != 0.0` 이고 KR BBOX 내 | `location_review` |
| 테마 | `theme != None` (`"테마 없음"` 아님) | `content_review` |
| 축제 기간 | `start_date`/`end_date`가 8자리 YYYYMMDD로 파싱 | `date_review` |
| 방문통계 | `monthly_statistics` 12개월 존재, `total_visitors = locals+out_of_town+foreigners` 일치 | `needs_review` |
| 연락처 보강 | tel 폴백 적용 여부 기록(미보강 허용, 상태 표시) | — |
| data_confidence | 코드 문자열(`needs_review`/`collected`) 보존 + 전처리 점수와 병행 | — |
| 수량 정합 | Attraction 3,709 / Festival 106 / 상세 3,815 / 통계 40×12 | 불일치 시 리포트 |

## 6. DynamoDB 적재

`kr_preprocessing_detail_design.md` §7·§12.3의 Single-Table 매핑을 그대로 사용한다. 코드 산출물과의 키 정합만 명시한다.

| 엔티티 | PK | SK | 비고 |
| --- | --- | --- | --- |
| City | `country_code`=`KR` | `city_id`(`KR-GW-*`) | description/climate placeholder는 보강 전까지 `needs_review` |
| Attraction | `city_id` | `attraction_id`(`ATT-*`) | theme None·좌표 0.0은 적재 전 검수 분기 |
| Festival | `city_id` | `festival_id`(`FEST-*`) | 기간 ISO 변환 후 적재 |
| VisitorStatistics | `city_id` | `stat_period`(`yyyyMM`) | monthly_statistics에서 12건 unnest |

## 7. 기존 상세설계(v0.2)와의 관계

| 주제 | `kr_preprocessing_detail_design.md` v0.2 | 본 문서(코드 기반) |
| --- | --- | --- |
| City ID | `KR-42-*`(숫자) | `KR-GW-*`/`KR-GB-*`(코드 사실) |
| ATT/FES ID | `KR-{도}-{CITY}-ATT-{id}` | `ATT-{id}`/`FEST-{id}`(코드 사실) |
| 방문통계 | 독립 파일 입력 가정 | final 임베드 → 전처리 unnest |
| tel 폴백 | 적용 전제 | 코드 미구현 → 전처리 보강 대상 |
| 의사코드/함수 | 일반 설계 | 코드 산출물에 맞춘 입력 계약 |

> 상세설계의 Lambda 오케스트레이션·데이터 계약·검증 프레임은 유효하며, 본 문서는 그 **입력 스키마를 코드 사실로 교체**한 보강판이다. 차이 항목은 `korea_acquisition_plan_corrections.md`로 추적한다.

## 8. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-09 | 조동휘 | `tour-api-korea` 샘플 코드 산출물 기준 전처리 설계 작성: 실제 파일 구조·정규화 스키마·방문통계 임베드/unnest·touDivCd 매핑·코드 사실 기반 ID/필드 정정 반영 |
| v0.2 | 2026-06-09 | 조동휘 | 필드 단위 상세화: Attraction/Festival/City 출력 필드별 소스 매핑표, contenttypeid별 운영시간·요금 소스, 방문통계 sigungu_map·touDivCd·unnest 의사식, 테마 매핑(lclsSystm3/cat3·C01·should_exclude·오버라이드 46건 분포), 결측·예외·data_confidence 역논리, TourAPI 호출·Fail-Fast·체크포인트 정책(§4.4~§4.10) 추가 |
