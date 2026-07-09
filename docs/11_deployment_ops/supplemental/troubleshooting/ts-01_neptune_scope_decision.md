# TS-01 Neptune 도입 범위 판단

> 문서 성격: 트러블슈팅 하위 Markdown
> 상위 문서: `../troubleshooting.md`

> 문서 버전: v0.2
> 문서 상태: 초안 (Draft)
> 작성일: 2026-07-09
> 작성자: llm팀
> 문서 목적: `TS-01` 이슈의 문제, 원인, 판단, 조치, 재발 방지 기준을 본 문서에서 분리해 상세 관리한다.

---

## 1. 요약

| 항목 | 내용 |
| --- | --- |
| 문제 | 추천 후보 확장에 도시, 축제, 테마, 장소 관계가 필요해 Neptune 도입을 검토했다. |
| 조사 결론 | 현재 Lovv의 관계 탐색은 대부분 1~2-hop, 읽기 위주, 배치 재생성 가능한 공용 콘텐츠 관계라 전용 그래프DB를 바로 둘 필요성이 낮다. 비용 측면에서도 Neptune은 최소 NCU 기반 고정비와 storage/I/O 비용 축이 추가되어 초기 예산 대비 부담이 크다. |
| 결정 | PoC와 Production 1차에서는 Neptune을 직접 도입하지 않고 Lambda 관계 탐색 보조 기능으로 대체한다. |
| 대체 구성 | DynamoDB 인접 리스트, 사전계산 후보 테이블, Lambda 인메모리 그래프, S3 vector metadata filter를 조합한다. |
| 승격 조건 | 3-hop 이상 임의 경로 탐색, 대규모 실시간 그래프 쓰기, 복잡한 그래프 알고리즘이 실제 병목으로 확인될 때 Neptune을 재검토한다. |

## 2. 증상

추천 시스템에서 도시, 테마, 축제, 인접 도시 관계를 다루기 때문에 그래프DB인 Neptune을 도입할 수 있다는 의견이 있었다.

그러나 중간발표 PoC 범위에서는 대부분의 관계 탐색이 1~2-hop 수준이었다. 이 단계에서 Neptune을 바로 넣으면 기능 검증보다 운영 비용과 복잡도가 먼저 증가할 위험이 있었다.

## 3. 조사 범위

이번 조사는 다음 질문에 답하는 방식으로 진행했다.

| 질문 | 확인한 기준 |
| --- | --- |
| Neptune이 필요한 질의인가? | 현재 질의가 깊은 임의 경로 탐색인지, 단순 후보 확장인지 확인 |
| 현재 데이터 성격은 무엇인가? | 실시간 쓰기 그래프인지, S3 Raw/DynamoDB 기준으로 배치 재생성 가능한 관계 인덱스인지 확인 |
| 비용 부담이 합리적인가? | 초기 예산과 Neptune 최소 운영 형상의 고정비를 비교 |
| 대체 구현이 가능한가? | DynamoDB 인접 리스트, 사전계산 후보, Lambda 인메모리 그래프, S3 vector metadata filter로 대체 가능한지 확인 |
| 언제 승격할 것인가? | Neptune 도입을 다시 판단할 측정 기준 정의 |

## 4. 원인

| 항목 | 내용 |
| --- | --- |
| 관계 깊이 | PoC의 주요 질의는 도시-테마, 도시-축제, 도시-장소 수준이다. |
| 비용 | Neptune Serverless는 최소 시작 용량이 1 NCU이며, 저장소와 I/O도 별도 과금된다. 초기 저트래픽에서는 고정비 비율이 커진다. |
| 운영 복잡도 | DynamoDB, S3 vector, Lambda 외에 별도 그래프 저장소 운영이 추가된다. |
| 재생성성 | 현재 관계 데이터는 원본 저장소보다 파생 인덱스로 두는 편이 안전하다. |
| 질의 패턴 | 추천 후보 확장은 대부분 필터링, 1-hop 조회, 제한된 2-hop 확장, 재랭킹으로 끝난다. |
| 원본성 | 관계 탐색 결과는 원장이 아니라 DynamoDB 정규화 문서와 S3 Raw 원본에서 재생성 가능한 파생 데이터다. |

## 5. AWS 서비스 조사 결과

| 항목 | 조사 결과 | Lovv 판단 |
| --- | --- | --- |
| Neptune 성격 | Neptune은 property graph와 RDF graph를 지원하고 Gremlin, openCypher, SPARQL 질의에 적합한 관리형 그래프DB다. | 깊은 관계 그래프를 운영할 때는 적합하지만, 현재 후보 확장에는 과하다. |
| Neptune Serverless 용량 | Serverless는 NCU 기준으로 과금되며 시작 용량은 1 NCU다. 공식 문서상 최소 NCU도 1.0이다. | scale-to-zero로 볼 수 없으므로 초기 저트래픽 PoC의 비용 절감 수단으로 보기 어렵다. |
| Neptune 비용 구조 | 데이터베이스 인스턴스/용량 외에 storage, I/O, backup, data transfer 비용을 고려해야 한다. | 기존 DynamoDB, S3 vector, Lambda에 비해 별도 운영 비용 축이 추가된다. |
| S3 vector 역할 | S3 vector는 embedding similarity search와 metadata filtering을 제공한다. | 의미 검색과 1차 metadata filter는 S3 vector로 처리하고, 그래프 관계 확정은 별도 관계 탐색 보조에서 수행한다. |
| S3 vector 한계 | S3 vector는 유사도 검색과 metadata filter에 강하지만 그래프 경로 탐색 엔진은 아니다. | S3 vector 결과를 단독 확정하지 않고 DynamoDB 정규화 문서와 Lambda 관계 탐색으로 검증한다. |

## 6. 현재 Lovv 질의 패턴 분석

| 질의/기능 | 그래프 관점 | 현재 대체 방식 |
| --- | --- | --- |
| 도시별 축제 후보 | `City -> Festival` 1-hop | DynamoDB 정규화 문서, 축제 검증 캐시 |
| 도시별 장소 후보 | `City -> Place` 1-hop | DynamoDB 조회, S3 vector metadata filter |
| 테마/계절 적합성 | `City/Place -> Theme`, `SeasonalFit` | S3 vector metadata의 `theme_tags`, `recommended_months`, DynamoDB 속성 |
| 인접 도시 후보 | `City -> NearCity` 1-hop | 좌표 기반 Haversine 거리 배치 사전계산 |
| 후보 확장·재랭킹 | 제한된 2-hop | 사전계산 후보 테이블 또는 Lambda 인메모리 그래프 |
| 자연어 유사 장소 검색 | 그래프 질의 아님 | S3 vector similarity search |

현재 범위에서는 임의 길이 경로 탐색보다, 이미 정의된 관계 타입을 기준으로 후보를 좁히고 재랭킹하는 일이 중심이다.

## 7. 대체 아키텍처

PoC와 Production 1차에서는 Neptune을 직접 도입하지 않는다. 현재 방향은 그래프DB와 유사한 관계 탐색 기능을 Lambda로 구현하는 것이다.

현재는 다음 대체 방식으로 충분하다.

| 대체 방식 | 적용 범위 |
| --- | --- |
| DynamoDB 인접 리스트 | 도메인 item 단위 빠른 조회와 서비스 운영 조회 |
| 사전계산 후보 테이블 | 추천 후보 확장과 반복 질의 비용 절감 |
| Lambda 인메모리 그래프 | 요청 시 소규모 관계 탐색, 2-hop 확장, 그래프 재랭킹 보조 |
| S3 vector index | 자연어·분위기 기반 후보 검색 |

### 7.1 관계 데이터 예시

| 관계 | 저장 방식 | 재생성 기준 |
| --- | --- | --- |
| `City -> Theme` | DynamoDB 인접 리스트 또는 S3 vector metadata | 수집 정규화 문서 |
| `City -> Festival` | DynamoDB 정규화 문서, 검증 캐시 | 축제 원천 데이터, S3 Raw |
| `City -> Place` | DynamoDB 정규화 문서 | 관광지/장소 원천 데이터 |
| `City -> NearCity` | 배치 사전계산 edge | 도시 좌표 |
| `Candidate -> Candidate` | 사전계산 후보 테이블 | scoring batch 결과 |

### 7.2 요청 처리 흐름

```text
사용자 조건
↓
S3 vector similarity search + metadata filter
↓
DynamoDB 정규화 문서 재조회
↓
Lambda 관계 탐색 보조로 도시·축제·테마·장소 관계 확장
↓
사전계산 후보 또는 인메모리 그래프 재랭킹
↓
최종 후보 반환
```

## 8. 판단

현재 단계에서는 Neptune을 도입하지 않는 판단이 타당하다.

| 판단 기준 | 결론 |
| --- | --- |
| 기능 적합성 | 현재 요구는 대부분 1~2-hop 후보 확장이라 DynamoDB/Lambda/S3 vector 조합으로 구현 가능하다. |
| 비용 효율 | Neptune은 최소 용량과 storage/I/O 비용 축이 추가되어 초기 예산에서 고정비 부담이 크다. |
| 운영 단순성 | 기존 저장소와 Lambda를 재사용하면 배포, 모니터링, 장애 대응 표면을 줄일 수 있다. |
| 데이터 원본성 | 그래프는 원장이 아니라 재생성 가능한 파생 관계 인덱스이므로 전용 그래프DB의 내구 원장 역할이 필요하지 않다. |
| 확장성 | 추후 3-hop 이상 경로 탐색이나 실시간 그래프 쓰기가 병목이 되면 Neptune으로 승격할 수 있다. |

## 9. 조치

- Neptune은 원본 저장소가 아니라 향후 승격 가능한 파생 관계 인덱스로만 정의한다.
- 현재 설계는 DynamoDB, S3 vector index, Lambda 관계 탐색 보조 기능을 기준으로 작성한다.
- Lambda는 DynamoDB 인접 리스트와 사전계산 후보를 읽어 그래프DB와 유사한 후보 확장·재랭킹 기능을 수행한다.
- 발표에서는 "도입 실패"가 아니라 "비용·범위 검토 후 보류한 기술 판단"으로 설명한다.

## 10. 승격 기준

다음 조건 중 하나가 실제 요구사항으로 확인되면 Neptune 도입을 재검토한다.

| 승격 조건 | 설명 |
| --- | --- |
| 3-hop 이상 임의 경로 탐색 | 사용자-도시-테마-축제-인접도시처럼 경로가 깊어짐 |
| 대규모 실시간 그래프 쓰기 | 사용자 행동, co-visit, 선호 관계가 지속적으로 누적됨 |
| 복잡한 그래프 알고리즘 | PageRank류 중요도, 커뮤니티 탐지, 경로 추천이 필요해짐 |
| DynamoDB/Lambda 대체 구현 한계 | 인접 리스트 조회, 사전계산 후보, Lambda 인메모리 그래프 방식이 운영상 병목이 됨 |

추가로 다음 지표를 관찰한다.

| 지표 | 재검토 신호 |
| --- | --- |
| 요청당 관계 탐색 depth | 평균 2-hop을 넘어 3-hop 이상이 상시 필요 |
| 후보 확장 latency | Lambda 관계 탐색과 DynamoDB 반복 조회가 목표 latency를 지속 초과 |
| 관계 edge 수 | 배치 사전계산 후보 테이블이 관리하기 어려운 수준으로 증가 |
| 그래프 업데이트 빈도 | 관계 쓰기가 실시간 사용자 행동 기반으로 지속 발생 |
| 알고리즘 요구 | 최단경로, 중심성, 커뮤니티 탐지 등 그래프 전용 알고리즘이 서비스 핵심 기능이 됨 |

## 11. 조사 결론

TS-01의 결론은 기존과 동일하게 유지한다.

Neptune은 그래프 질의 자체에는 적합한 서비스지만, 현재 Lovv의 PoC/Production 1차 범위에서는 관계 규모와 질의 깊이가 작고, 관계 데이터도 재생성 가능한 파생 인덱스다.

비용 측면에서도 Neptune을 바로 도입하면 최소 NCU 기반 고정비, storage, I/O, backup, data transfer 비용 축이 기존 DynamoDB, S3 vector, Lambda 스택 위에 추가된다. 초기 트래픽과 예산 규모에서는 이 고정비가 기능 검증보다 먼저 부담으로 작용할 가능성이 높다.

따라서 현재는 DynamoDB 인접 리스트, 사전계산 후보 테이블, Lambda 인메모리 그래프, S3 vector metadata filter를 조합해 구현하고, Neptune은 고도화 단계의 승격 옵션으로 둔다.

## 12. 출처 및 근거

| 구분 | 근거 |
| --- | --- |
| 로컬 설계 | `docs/04_database_design/supplemental/neptune_alternative.md` |
| 로컬 비용 검토 | `docs/04_database_design/supplemental/database_design_retention_neptune_update.md` |
| Agent 검색 계약 | `docs/05_agent_spec/05_agent_spec.md` |
| 기술 명세 | `docs/06_technical_spec/06_technical_spec.md` |
| AWS Neptune 공식 문서 | [What Is Amazon Neptune?](https://docs.aws.amazon.com/neptune/latest/userguide/intro.html) - Gremlin, openCypher, SPARQL을 지원하는 관리형 그래프DB |
| AWS Neptune 비용 문서 | [Amazon Neptune pricing](https://aws.amazon.com/neptune/pricing/) - Serverless NCU 과금, 시작 용량 1 NCU, storage/I/O 별도 과금 |
| AWS Neptune Serverless scaling | [Capacity scaling in a Neptune Serverless DB cluster](https://docs.aws.amazon.com/neptune/latest/userguide/neptune-serverless-capacity-scaling.html) - 최소 NCU 1.0, 최대 NCU 128.0 기준 |
| AWS S3 Vectors 공식 문서 | [Working with S3 Vectors and vector buckets](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html) - embedding similarity search와 metadata filtering 제공 |
| AWS S3 Vectors metadata filter | [Metadata filtering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-metadata-filtering.html) - similarity 조건과 metadata 조건을 함께 필터링 가능 |

## 13. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.2 | 2026-07-09 | llm팀 | Neptune 도입 판단의 로컬 설계 근거, AWS 공식 근거, 대체 아키텍처, 승격 지표를 상세화 |
| v0.1 | 2026-07-09 | llm팀 | 본 트러블슈팅 문서에서 TS-01 상세 내용을 하위 문서로 분리 |
