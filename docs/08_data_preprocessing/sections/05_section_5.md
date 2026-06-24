# 5. 공통 정규화 규칙

## 5.1 식별자 규칙

| 대상 | ID 형식 | 예시 |
| --- | --- | --- |
| 한국 City | `KR-{GW 또는 GB}-{CITY_EN}` | `KR-GW-GANGNEUNG` |
| 일본 City | `JP-{도도부현}-{도시명}` | `JP-ISHIKAWA-KANAZAWA` |
| 한국 Attraction | `ATT-{contentid}` (City는 `city_id`로 연결) | `ATT-126508` |
| 한국 Festival | `FEST-{contentid}` | `FEST-2762975` |
| 한국 VisitorStatistics | `{city_id}-STAT-{yyyyMM}` (전처리 파생) | `KR-GW-GANGNEUNG-STAT-202501` |
| 일본 Attraction/Festival | `{country_code}-{entity_type}-{source_or_hash}` | `JP-FEST-HASH-001` |
| 일본 VisitorStatistics | `JP-{prefecture_or_city}-STAT-{period_or_hash}` | `JP-TOKYO-STAT-202501` |

ID는 재처리 시에도 바뀌지 않아야 한다. 원본 ID가 없는 일본 공식 사이트·지자체 페이지 기반 데이터는 URL 정규화 해시를 보조 식별자로 사용한다.

## 5.2 명칭 정규화

| 구분 | 처리 기준 |
| --- | --- |
| 한국어명 | 불필요한 괄호 설명, 지역 홍보 문구, 축제 회차 표기를 분리한다. |
| 일본어 원문명 | 한자·가나 표기를 원문 필드로 보존한다. |
| 한국어 표기 | 일본 도시·관광지·축제는 서비스 표시용 한국어 표기를 별도 관리한다. |
| 검색명 | 공백 제거, 소문자화, 특수문자 제거, 별칭을 포함한 검색 키를 생성한다. |

## 5.3 주소와 행정구역 정규화

| 국가 | 처리 기준 |
| --- | --- |
| 한국 | 광역시·도, 시·군·구, 읍·면·동을 분리하고 행정구역 코드와 매핑한다. |
| 일본 | 도도부현, 시·정·촌·구를 분리하고 e-Stat 또는 Statistical LOD 기준 코드와 매핑한다. |
| 공통 | 주소가 없거나 모호한 경우 좌표, 공식 사이트 설명, 지도 링크를 보조 근거로 사용한다. |

## 5.4 좌표 정규화

- 위도·경도는 WGS84 기준 decimal degree로 저장한다.
- 좌표 범위가 국가 영역을 벗어나면 `needs_review`로 분류한다.
- City 대표 좌표와 Attraction/Festival 좌표 간 거리가 과도하게 크면 City 매핑 오류 후보로 분류한다.
- 좌표가 없는 데이터는 주소 기반 지오코딩 후보로 분류하되, 자동 지오코딩 결과는 검수 전까지 낮은 신뢰도로 둔다.

## 5.5 날짜와 기간 정규화

| 입력 유형 | 정규화 필드 |
| --- | --- |
| 단일 날짜 | `start_date`, `end_date` 동일 값 |
| 기간 | `start_date`, `end_date`, `period_text` |
| 매년 반복 축제 | `month`, `season`, `recurrence_rule`, `period_text` |
| 연도별 변동 축제 | `event_year`, `start_date`, `end_date`, `verified_at` |
| 불명확한 기간 | `period_text` 보존 후 `needs_review` |
