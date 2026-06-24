# 2. 입력 데이터 범위

## 2.1 입력 데이터셋

| 입력 구분 | 주요 내용 | 전처리 목적 |
| --- | --- | --- |
| City Raw | 도시명, 행정구역, 좌표, 설명, 기후, 공식 사이트 | 지역 기준 엔티티 정규화 |
| Attraction Raw | 관광지명, 주소, 설명, 운영시간, 운영기간, 입장료, 좌표, 사진 | 일정 후보 데이터 정규화 |
| Festival Raw | 축제명, 개최지, 기간, 설명, 사진, 공식 링크 | 월별·계절성 추천 후보 정규화 |
| Climate Raw | 월별 평균 기온, 강수량, 계절 메모 | 여행 적합도와 계절 태그 생성 |
| Statistics Raw | 방문자 수, 관광 동향, 지역 통계 | 혼잡도·인지도 보조 지표 생성 |
| Verification Raw | 공식 사이트 확인값, 수동 검수 결과, 검수 메모 | 최신성·신뢰도 보정 |
| Korea Local Validation | `data/KR/prefectures.json`, `cities.json`, `attractions.json`, `festivals.json`, `visitor_statistics.json` | S3 Raw 적재 전 한국 실제 수집 구조와 수량 검증 |

## 2.2 기준 관계

전처리 후에도 수집 계획서의 기본 관계를 유지한다.

```text
City
 ├── Attraction
 ├── Festival
 └── VisitorStatistics
```

| 관계 | 전처리 기준 |
| --- | --- |
| `City 1:N Attraction` | 모든 관광지는 하나의 대표 City에 연결한다. 경계 지역은 주소와 좌표를 기준으로 대표 City를 결정하고 예외 메모를 남긴다. |
| `City 1:N Festival` | 모든 축제는 개최 장소 기준 City에 연결한다. 광역 개최 축제는 주 개최지와 보조 개최지를 분리한다. |
| `City 1:N VisitorStatistics` | 방문·관광 통계는 월별 또는 지역별 기준으로 City에 연결한다. 출처별 집계 단위가 다른 경우 원본 단위와 정규화 단위를 모두 남긴다. |
