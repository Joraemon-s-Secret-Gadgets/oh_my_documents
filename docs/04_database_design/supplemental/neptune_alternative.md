# 로브 (Lovv) Neptune 대체 설계 명세서

> 문서 성격: 보조 Markdown
> 대표 문서: `../04_database_design.md`

> 문서 버전: v0.2
> 문서 상태: 검토 중 (Review)
> 기준 문서: 데이터베이스 설계 명세서 v0.6, 데이터 수집 계획서 v0.7, Agent 명세서 v0.6, API 명세서 v0.3
> 관련 문서: 데이터베이스 설계 명세서, 데이터베이스 보존 기간·Neptune 비용 업데이트 초안

# 1. 배경

데이터베이스 설계 명세서는 다단계 관계 탐색용 그래프 인덱스로 AWS Neptune을 정의한다(1.2·3.5·4.6절).
그러나 Neptune은 **상시 가동 비용**(Serverless 최소 1 NCU도 0으로 축소되지 않음, 월 약 $80+)이
발생해, 월 30만원(약 $193) 예산에서는 고정비 비율이 높다.

본 문서는 Neptune 없이 기존 스택(MySQL·DynamoDB·S3 vector·Lambda)으로 동일 그래프 용도를
대체하는 설계를 정의한다. 현재 구현 방향은 그래프DB 직접 도입이 아니라 Lambda 기반 관계 탐색 보조 기능이다.
그래프 규모·질의 복잡도가 커지면 Neptune 도입(고도화 단계)으로 승격한다.

# 2. 전제

- 본 서비스 그래프는 **공용 콘텐츠 관계**(도시·축제·테마·장소)이며 규모가 작다.
- 그래프는 S3 Raw 원본 기준 **배치로 재생성**되는 읽기 위주 인덱스다(실시간 그래프 쓰기 아님).
- 사용자 개인정보·대화 전문·최종 원장은 그래프에 저장하지 않는다(대표 문서 3.5절 원칙 유지).

# 3. Neptune 사용 패턴 → 대체 매핑

데이터베이스 설계 명세서 3.5절(그래프 논리 모델)·4.6절(조회 패턴)의 요소를 1:1로 대응한다.

| Neptune 요소 | 용도 | 대체 방법 | 사용 저장소 |
| --- | --- | --- | --- |
| `NEAR_CITY` | 인접 도시 후보 탐색 | 좌표(lat/long) Haversine 거리로 배치 사전계산 → 도시별 최근접 N개 저장 | DynamoDB(또는 MySQL) |
| `HAS_THEME`, `SEASONAL_FIT` | 필수·선호 테마/시즌 적합 필터 | `theme_tags`, `recommended_months` 속성 필터(기존 보유) | S3 vector metadata + DynamoDB 속성 |
| `HOSTS_FESTIVAL` | 축제 포함 추천·날짜 검증 | 도시별 축제 조회 + 검증 캐시 | DynamoDB(`lovv_festival_verify_cache`, 정규화 문서) |
| `HAS_PLACE` | 일정 항목 후보 확장 | 도시별 장소 조회 | DynamoDB 정규화 문서 |
| 2-hop 확장 + 그래프 재랭킹 | 다단계 후보 확장·재정렬 | 배치 사전계산 머티리얼라이즈 또는 요청 시 Lambda 인메모리 그래프 탐색 | DynamoDB / Lambda 인메모리 |

`SEASONAL_FIT`/`recommended_months`는 수집 계획서 4.1절의 `ComfortScore` 산식과 연결된다.

# 4. 후보 기술 비교

| 옵션 | 개요 | 다단계 탐색 | 추가 비용 | 적합 상황 |
| --- | --- | --- | --- | --- |
| MySQL 엣지 테이블 + 재귀 CTE | `edges(from_id, to_id, rel_type, weight)` 저장, MySQL 8 재귀 CTE로 2-hop | 가능(소규모) | 없음(기존 RDS) | 관계 명시·정합성 중요 |
| DynamoDB 인접 리스트 패턴 | 단일 테이블에 노드·엣지(`pk=NODE#id`, `sk=EDGE#...`) | 1-hop 빠름, 다단계는 앱 반복 조회 | 없음(기존 DynamoDB) | 빠른 1-hop·키 조회 |
| 사전계산 후보 테이블(권고) | 배치로 도시별 2-hop 후보·점수 사전계산, 조회는 단건 read | 배치 처리, 조회 O(1) | 거의 없음 | 그래프가 천천히 변할 때 |
| 인메모리 그래프(NetworkX/igraph) | 작은 그래프를 메모리에 로드 후 탐색 | 자유로운 다단계·재랭킹 | 거의 없음(Lambda/앱 내) | 유연한 그래프 알고리즘 |
| Apache AGE / Neo4j Community | 오픈소스 그래프 엔진 자체 호스팅 | 완전 지원 | EC2/운영 비용 | 그래프 규모·복잡도 증가 후 |

# 5. 권고 대체 아키텍처 (Neptune 없이)

1. **관계 적재**: S3 Raw → Lambda 배치로 콘텐츠 관계를 산출하고 DynamoDB 인접 리스트
   (+필요 시 MySQL 엣지 테이블 보조)에 저장.
2. **인접 도시**: 좌표 Haversine 거리로 도시별 최근접 N개를 배치 사전계산해 저장.
3. **테마/시즌**: S3 vector metadata + DynamoDB 속성 필터로 충족 판정.
4. **축제/장소**: DynamoDB 조회 + `lovv_festival_verify_cache`로 날짜 검증.
5. **2-hop 확장·재랭킹**: 배치 시점에 도시별 후보·점수를 **사전계산 머티리얼라이즈**,
   유연한 알고리즘이 필요하면 요청 시 Lambda **인메모리 그래프**로 보강.
6. **승격 기준**: 3-hop 이상 임의 경로 탐색·대규모 실시간 그래프 쓰기가 필요해지면
   Neptune 도입(고도화 단계).

## 5.1 데이터 구조 예시

DynamoDB 인접 리스트(단일 테이블):

| 항목 | pk | sk | 주요 속성 |
| --- | --- | --- | --- |
| 노드 | `NODE#CITY#{city_id}` | `META` | `country`, `region`, `lat`, `lng` |
| 인접 도시 엣지 | `NODE#CITY#{city_id}` | `EDGE#NEAR#{rank}#{dst_city_id}` | `distance_km`, `weight` |
| 테마 엣지 | `NODE#CITY#{city_id}` | `EDGE#THEME#{theme_id}` | `weight`, `source_id` |
| 축제 엣지 | `NODE#CITY#{city_id}` | `EDGE#FESTIVAL#{festival_id}` | `travel_year`, `date_status` |
| 장소 엣지 | `NODE#CITY#{city_id}` | `EDGE#PLACE#{content_id}` | `content_type`, `weight` |

사전계산 후보(머티리얼라이즈) 테이블:

| pk | sk | 주요 속성 |
| --- | --- | --- |
| `CAND#CITY#{city_id}` | `RANK#{score_desc}#{candidate_id}` | `candidate_type`, `score`, `reason`, `computed_at` |

## 5.2 인접 도시 사전계산 (수식)

두 도시 좌표 `(φ1, λ1)`, `(φ2, λ2)`의 Haversine 거리:

```
a = sin²(Δφ/2) + cos φ1 · cos φ2 · sin²(Δλ/2)
d_km = 2R · atan2(√a, √(1−a))      # R = 6371 km
```

도시별 `d_km` 오름차순 상위 N개를 `EDGE#NEAR`로 저장한다(N 권고: 5~8).

# 6. 비용 비교 (2026-06 공개가 기준, 월)

| 구성 | Neptune 사용 | 대체 아키텍처 |
| --- | --- | --- |
| 그래프 컴퓨트 | Serverless 최소 1 NCU 상시 ≈ $80+ | 없음(기존 DynamoDB/Lambda 재사용) |
| 추가 인프라 | 클러스터+인스턴스 상시 | 없음 |
| 예산($193) 영향 | 약 40%+ 고정 점유 | 거의 0 추가 |

신뢰도: AWS 공개가 기준(중~상), 리전·사용량·환율에 따라 변동. 도입 전 AWS Pricing Calculator로 재산정.

# 7. 한계 및 승격 기준

- 매우 깊은(3-hop+) 임의 경로 탐색, 복잡한 그래프 알고리즘(커뮤니티 탐지·최단경로 대량 질의),
  대규모 실시간 그래프 쓰기에는 대체 아키텍처가 부적합하다.
- 위 요건이 검증되면 현재 Lambda 관계 탐색 보조 기능을 Neptune(고도화 단계)으로 승격할지 결정한다.

# 8. 데이터베이스 설계 명세서 연계

- 1.2절 설계 기준 표 `관계 탐색 보조 / Lambda 기반 관계 탐색` 비고: "그래프DB 직접 도입 보류, Lambda 기반 보조 기능 구현, Neptune은 승격 옵션".
- 1.3절 저장소 책임 표 Lambda 관계 탐색 행: "DynamoDB 인접 리스트와 Lambda 인메모리 그래프 우선".
- 3.5·4.6절: "PoC/Prod 1차 관계 탐색은 Lambda 기반 보조 기능으로 구현한다" 각주.
- 6장 전환 표: Neptune은 `Production 고도화` 유지, 이전 단계는 대체 아키텍처 명시.
- 9장 변경 이력에 항목 추가.

# 9. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.2 | 2026-06-12 | 로브 기획팀 | 현재 구현 방향을 그래프DB 직접 도입 대신 Lambda 기반 관계 탐색 보조 기능으로 명확화 |
| v0.1 | 2026-06-08 | 로브 기획팀 | Neptune 대체 설계 초안: 사용 패턴 매핑, 기술 비교, 권고 아키텍처, 비용 비교, 승격 기준 작성 |

# 10. 참고

- [Amazon Neptune Pricing (AWS)](https://aws.amazon.com/neptune/pricing/)
- [Amazon Neptune Serverless scales down to 1 NCU (AWS)](https://aws.amazon.com/about-aws/whats-new/2023/03/amazon-neptune-serverless-scales-down-1-ncu-costs/)
