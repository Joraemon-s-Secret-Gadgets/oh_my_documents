# 데이터베이스 설계 명세서 업데이트 초안 — 보존 기간/TTL 및 Neptune 비용

> 보조 문서 (AGENT.md 워크플로 기준 초안)
> 대상 원본: `04_database_design.md` (v0.4)
> 작성일: 2026-06-08
> 상태: Review 대기 (값 확정 후 대표 문서 반영)

> 최신 반영 메모(2026-06-12): 대표 문서는 Neptune 직접 도입 대신 Lambda 기반 관계 탐색 보조 기능 구현 예정으로 조정되었다. 아래 Neptune 비용 검토는 "왜 직접 도입을 보류했는가"의 근거로 유지한다.

이 문서는 두 가지 피드백을 대표 문서에 반영하기 위한 초안이다. 값 확정 후
`04_database_design.md`의 해당 섹션에 옮기고, `pages/` HTML 생성물을 최신화한다.

피드백 원문:

1. 보존 정책들은 좋은데 실제 보존 기간을 얼마로 할지 정해지면 작성해 둘 것(TTL 포함).
2. Neptune은 비용적으로 다소 높을 수 있어 감안할 필요가 있어 보임.

---

## 0. 대화형 빌더 메모리 계층 + TTL 라인 (PRD v0.1 반영)

대화형 빌더(`../98_prd/interactive_builder_prd.md`)의 상태/메모리 결정을 본 보조 문서에 반영한다.

- **단기 (AgentCore Memory)**: 빌더 상태 + 세션 + checkpoint, `event_expiry`로 자동 정리(일 단위).
- **장기 ① 파생 개인화 프로필 (DynamoDB 핫, TTL 없음)**: 가명 ID PK, 선호 요약. 지우지 않음.
- **장기 ② raw 이벤트 로그 (DynamoDB TTL → S3 콜드)** — TTL 라인:
  1. 이벤트 아이템 `ttl`(epoch 초)=`now+N일`. best-effort 삭제 → "N일 후 반드시"면 `expires_at` 필드 + 읽기 시 앱레벨 필터.
  2. DynamoDB Streams(NEW_AND_OLD_IMAGES) → Lambda가 TTL 삭제만 필터(`userIdentity.principalId=="dynamodb.amazonaws.com"`).
  3. OLD_IMAGE(가명)를 S3 콜드 적재(날짜/actor-해시 파티션). 용도: 프로필 재계산·분석·학습.
  4. 고볼륨 시 Kinesis→Firehose→S3 확장.
- **hard line**: 매핑(가명ID↔실제신원)·raw PII는 미저장(별도 KMS·IAM). 삭제권은 DynamoDB+S3 양쪽 삭제.

> 단기 `event_expiry` / raw 이벤트 TTL의 보존 일수 N은 아래 §2 "확정값"과 함께 정한다.

---

## 1. 현재 반영 상태 (갭 분석)

| 피드백 | 현재 상태 | 판정 |
| --- | --- | --- |
| 실제 보존 기간/TTL 명시 | 축제 검증 캐시만 구체값 존재(`confirmed` 30일, `tentative` 7일, `unknown/outdated` 1일, 원본 3.3절). 그 외 테이블·계정은 `expires_at`/"단기 보존"으로 기간 미정. 8장 후속작업 #2도 "TTL 기간을 확정한다"로 남아 있음 | 부분 반영 (확정 필요) |
| Neptune 비용 고려 | 명세 전반에 Neptune 사용은 정의돼 있으나 비용 언급·대안 없음 | 미반영 |

신뢰도 안내: 아래 권고 보존 기간은 일반적 운영 관행과 PoC 비용 절감 기준의 **권고값**이며,
법무/보안/개인정보 검토로 확정해야 한다. (권고값 신뢰도: 중)

---

## 2. 보존 기간/TTL 확정 표 (대표 문서 5장 보강안)

`확정값` 컬럼을 비워 두었다. 담당자가 값을 채우면 대표 문서에 반영한다.
`expires_at`은 레코드 생성 시각 + 보존 기간으로 계산해 저장한다.

### 2.1 DynamoDB TTL 테이블

| 테이블 | 데이터 성격 | 권고 보존 기간(TTL) | 권고 근거 | 확정값 |
| --- | --- | --- | --- | --- |
| `lovv_user_event_logs` | 사용자 행동 이벤트(분석용) | 90일 | 분석·퍼널 집계에 충분, 장기 보관은 비용·개인정보 부담 | |
| `lovv_agent_runs` | Agent 실행 trace(디버깅) | 30일 | 장애 분석은 단기, 원문 비저장이라 장기 보관 가치 낮음 | |
| `lovv_async_jobs` | 비동기 작업 상태 | 14일 | 완료/실패 확인 후 단기 보관이면 충분 | |
| `lovv_api_logs` | API 호출 로그 | 30일 (장기 필요 시 S3 아카이브) | 운영/보안 추적 단기, 장기 감사는 S3 저비용 보관으로 분리 | |
| `lovv_festival_verify_cache` | 축제 날짜 검증 캐시 | `confirmed` 30일 / `tentative` 7일 / `unknown·outdated` 1일 | 원본 3.3절 기존값 유지 | (기존 확정) |
| `lovv_content_documents` | 수집 정규화 문서 | TTL 없음 (S3 Raw 기준 재생성) | 조회 모델, 원본에서 재적재 가능 | (해당 없음) |
| `lovv_visitor_statistics` | 방문 통계 정규화 | TTL 없음 (S3 Raw 기준 재생성) | 조회 모델, 원본에서 재적재 가능 | (해당 없음) |

### 2.2 MySQL 원장 / 기타 저장소 보존

| 데이터 | 권고 보존 정책 | 권고 근거 | 확정값 |
| --- | --- | --- | --- |
| 사용자 계정 | 탈퇴 후 30일 유예 → 익명화. 유예 기간 내 복구 가능 | 분쟁/오삭제 대비 단기 유예, 개인정보 최소보관 원칙 (법무 확인 필요) | |
| 저장 일정/항목/반응 | 사용자 삭제 시 즉시 삭제(연관 포함). 계정 익명화 시 함께 처리 | 사용자 통제 데이터, 원장 기준 | |
| S3 Raw 수집 원본 | 운영 보존(라이선스·재색인 기준). 권고 기본 365일 후 재검토 | 재색인·재생성 기준 데이터 | |
| S3 vector record | TTL 없음, 원본 재색인 기준 운영 보존 | 원본 아님, 재생성 가능 | (해당 없음) |
| Lambda 관계 탐색 캐시 | TTL 없음, 원본 재생성 기준 운영 보존 | 원본 아님, 재생성 가능 | (해당 없음) |
| 대화 전문 | 장기 저장하지 않음(기존 NFR-013) | 요구사항 준수 | (기존 확정) |

### 2.3 대표 문서 반영 위치

- 5장 보존 정책 표에 위 `권고 보존 기간`/`확정값`을 컬럼으로 추가.
- 4.3절 DynamoDB 물리 설계 기준의 `TTL` 행에 테이블별 확정 기간 링크.
- 8장 후속작업 #2는 값 확정 시 "완료"로 갱신.

---

## 3. Neptune 비용 고려 (대표 문서 1.2절/6장 보강안)

### 3.1 비용 구조 요약

Neptune은 상시 가동 비용이 발생하는 점이 핵심 부담이다. Serverless도 0으로
스케일다운되지 않고 최소 용량이 항상 과금된다.

| 항목 | 개요(2026-06 기준 us-east-1 공개가) | 비고 |
| --- | --- | --- |
| Serverless 컴퓨트 | 약 $0.1098 / NCU-시, 최소 1 NCU ~ 최대 128 NCU | 최소 1 NCU 상시 가동 시 월 약 $80 |
| 스토리지 | 약 $0.10 / GB-월 | |
| I/O | 약 $0.20 / 백만 요청 | |
| 최소 운영 형상 | 클러스터 + 최소 1 인스턴스 상시 가동 필요 | scale-to-zero 미지원 |

신뢰도: AWS 공개 가격 페이지 기준(중~상). 리전·환율·할인에 따라 변동하므로
도입 전 AWS Pricing Calculator로 재산정 필요.

### 3.2 영향

PoC/초기 Production은 그래프 질의량이 적어도 최소 인스턴스 상시 비용(월 $80+ 수준)이
고정 발생한다. 트래픽 대비 고정비 비율이 높아 초기 단계에서 비효율적일 수 있다.

### 3.2-1 예산 대비 분석 (월 30만원 기준)

가정: 30만원은 **월 인프라 예산**으로 본다(아니면 재산정 필요).
환율 약 1,555원/USD(2026-06 기준) 적용 시 예산 ≈ **$193/월**.

| 구성요소 | 권고 형상 | 월 비용(추정) | 비고 |
| --- | --- | --- | --- |
| RDS MySQL | db.t4g.micro~small | $15 ~ $30 | 원장 트랜잭션 |
| DynamoDB | On-demand, 저트래픽 | $5 ~ $25 | TTL 로그·정규화 문서 |
| S3 + S3 vector | 저용량 | $5 ~ $20 | 원본·검색 인덱스 |
| Lambda | 저호출 | $0 ~ $5 | 수집 전처리 |
| **소계 (Neptune 제외)** | | **$25 ~ $80** | 약 4만~12.5만원 |
| **Neptune Serverless** | 최소 1 NCU 상시 | **$80 ~ $110+** | 약 12.5만~17만원 |
| **합계 (Neptune 포함)** | | **$105 ~ $190+** | 약 16만~30만원 |

판정: Neptune을 **제외하면** 핵심 스택은 예산의 약 1/4~2/3 수준으로 충분한 여유가 있다.
Neptune을 포함하면 합계가 예산 상한($193)에 근접·초과해, 트래픽 증가·여유분이 거의 없다.
즉 30만원 예산에서 Neptune 상시 가동은 비용 효율이 낮고, **옵션 A(도입 보류)가 예산상 합리적**이다.

신뢰도: 구성요소별 비용은 인스턴스 선택·트래픽에 따라 변동하는 **개략 추정(신뢰도 하~중)**.
환율도 최근 변동성이 큼(최근 1개월 원화 약세). 도입 전 AWS Pricing Calculator와 실환율로 재산정 필요.

### 3.3 대안 및 권고

| 옵션 | 내용 | 적용 단계 권고 |
| --- | --- | --- |
| A. 도입 보류(권고) | PoC/Production 1차에서는 Neptune 미도입. 관계 탐색은 Lambda, DynamoDB 인접 리스트, MySQL 관계 테이블, 사전계산 후보 테이블로 구현 | PoC ~ Prod 1차 |
| B. 지연 도입 | 그래프 다단계 탐색 효용이 검증된 고도화 단계에서만 Neptune 활성화 | Prod 고도화 |
| C. 최소 형상 + 모니터링 | 도입 시 Serverless 최소 NCU로 시작하고 사용량·비용 알람 설정 | 도입 시 공통 |

권고: 월 30만원 예산에서는 옵션 A(도입 보류)를 우선하고, 현재 구현은 Lambda 기반 관계 탐색 보조 기능으로 둔다.
그래프 효용이 검증되고 3-hop 이상 임의 경로 탐색이 실제 병목이 되면 옵션 B로 승격한다.

### 3.4 대표 문서 반영 위치

- 1.2절 설계 기준 표 `관계 탐색 보조 / Lambda 기반 관계 탐색` 비고에 비용 주의 + Neptune 승격 조건 명시.
- 1.3절 저장소 책임 표 Lambda 관계 탐색 행에 "DynamoDB 인접 리스트와 Lambda 인메모리 그래프 우선" 주석.
- 6장 전환 표에는 Neptune을 현재 적용 범위가 아니라 `Production 고도화` 승격 옵션으로 명시.
- 9장 변경 이력에 v0.5 항목 추가.

### 3.5 Neptune 대체 방안 (상세)

전제: 본 서비스의 그래프는 **공용 콘텐츠 관계**(도시·축제·테마·장소)이며 규모가 작고,
S3 Raw 원본 기준 **배치로 재생성**된다. 사용자 개인정보·실시간 쓰기 그래프가 아니다.
따라서 상시 가동 그래프 DB 없이도 기존 스택(MySQL·DynamoDB·S3 vector·Lambda)으로 대체 가능하다.

#### 3.5.1 Neptune 사용 패턴 → 대체 매핑

원본 3.5절(그래프 논리 모델)·4.6절(조회 패턴)의 요소를 1:1로 대응한다.

| Neptune 요소 | 용도 | 대체 방법 | 사용 저장소 |
| --- | --- | --- | --- |
| `NEAR_CITY` 관계 | 인접 도시 후보 탐색 | 좌표(lat/long) Haversine 거리로 배치 사전계산 → 도시별 최근접 N개 저장 | DynamoDB(또는 MySQL) |
| `HAS_THEME`, `SEASONAL_FIT` | 필수·선호 테마/시즌 적합 필터 | `theme_tags`, `recommended_months` 속성 필터 (이미 보유) | S3 vector metadata + DynamoDB 속성 |
| `HOSTS_FESTIVAL` | 축제 포함 추천·날짜 검증 연결 | 도시별 축제 조회 + 검증 캐시 | DynamoDB(`lovv_festival_verify_cache`, 정규화 문서) |
| `HAS_PLACE` | 일정 항목 후보 확장 | 도시별 장소 조회 | DynamoDB 정규화 문서 |
| 2-hop 확장 + 그래프 재랭킹 | 다단계 후보 확장·재정렬 | (A) 배치 사전계산 후보 머티리얼라이즈, 또는 (B) 요청 시 인메모리 그래프 탐색 | DynamoDB / Lambda 인메모리 |

#### 3.5.2 후보 대체 기술 비교

| 옵션 | 개요 | 다단계 탐색 | 추가 비용 | 적합도 |
| --- | --- | --- | --- | --- |
| MySQL 엣지 테이블 + 재귀 CTE | `edges(from_id,to_id,rel_type,weight)`에 관계 저장, MySQL 8 재귀 CTE로 2-hop | 가능(소규모) | 없음(기존 RDS) | 관계가 명시적·정합성 중요할 때 |
| DynamoDB 인접 리스트 패턴 | 단일 테이블에 노드·엣지 저장(`pk=NODE#id`, `sk=EDGE#...`) | 1-hop 빠름, 다단계는 앱에서 반복 조회 | 없음(기존 DynamoDB) | 빠른 1-hop·키 조회 |
| 사전계산 후보 테이블(권고) | 배치로 도시별 2-hop 후보·점수를 미리 계산해 저장, 조회는 단건 read | 배치에서 처리, 조회 O(1) | 거의 없음 | 그래프가 천천히 변할 때 최적 |
| 인메모리 그래프(NetworkX/igraph) | DynamoDB/S3에서 작은 그래프를 메모리에 로드 후 탐색 | 자유로운 다단계·재랭킹 | 거의 없음(Lambda/앱 내) | 유연한 그래프 알고리즘 필요 시 |
| Apache AGE / Neo4j Community | 오픈소스 그래프 엔진 자체 호스팅 | 완전 지원 | EC2/운영 비용·관리 부담 | 그래프 규모·복잡도가 커진 뒤 |

#### 3.5.3 권고 대체 아키텍처 (Neptune 없이, 예산 적합)

1. 관계 적재: S3 Raw → Lambda 배치로 콘텐츠 관계를 산출하고
   DynamoDB 인접 리스트(+필요 시 MySQL 엣지 테이블 보조)에 저장.
2. 인접 도시: 좌표 Haversine 거리로 도시별 최근접 N개를 **배치 사전계산**해 저장.
3. 테마/시즌: S3 vector metadata + DynamoDB 속성 필터로 충족 여부 판정.
4. 축제/장소: DynamoDB 조회 + `lovv_festival_verify_cache`로 날짜 검증.
5. 2-hop 확장·재랭킹: 배치 시점에 도시별 후보·점수를 **사전계산 머티리얼라이즈**,
   유연한 알고리즘이 필요하면 요청 시 Lambda **인메모리 그래프**로 보강.
6. 추후 그래프 규모·질의 복잡도가 커지면 옵션 B(Neptune 도입)로 승격.

비용: 위 구성은 모두 기존 스택을 재사용하므로 **추가 상시 비용이 거의 없다**.
한계: 매우 깊은(3-hop+) 임의 경로 탐색이나 대규모 실시간 그래프 쓰기에는 부적합 →
그 시점이 Neptune 도입(옵션 B) 판단 기준이 된다.

신뢰도: 기술 매핑은 표준 패턴 기반(중~상). 실제 성능·후보 품질은 데이터 규모로 검증 필요.

#### 3.5.4 대표 문서 반영 위치

- 3.5절 Lambda 관계 탐색 논리 모델에 "PoC/Prod 1차 대체 방안(3.5.3)" 주석 추가.
- 4.6절 Lambda 관계 탐색 물리 설계 기준에 "Neptune은 승격 옵션" 각주.
- 6장 전환 표: Neptune은 `Production 고도화` 유지, 그 이전 단계는 대체 아키텍처 명시.

---

## 3.6 운영 대시보드(모니터링) 구현 방안

Neptune 제거와 무관하게, 데이터 스택(MySQL·DynamoDB·S3 vector·Lambda)과 비용을
Grafana류 운영 대시보드로 시각화할 수 있다. 기존 AWS 스택 기준 옵션은 다음과 같다.

### 3.6.1 옵션 비교 (2026-06 공개가 기준)

| 옵션 | 개요 | 월 비용(추정) | 비고 |
| --- | --- | --- | --- |
| CloudWatch Dashboards (권고) | AWS 네이티브. RDS·DynamoDB·Lambda·S3·API GW 지표 + Logs Insights + 알람 | 대시보드 3개까지 무료, 이후 $3/개. 사실상 $0~10 | 추가 인프라 없음, 최저 비용 |
| Grafana Cloud 무료 티어 | 실제 Grafana UI, CloudWatch를 데이터소스로 연결 | $0 (10k series·50GB 로그·3 user·14일 보존 한도 내) | 한도 초과 시 종량 과금 |
| Amazon Managed Grafana | 관리형 Grafana. CloudWatch 백엔드 별도 | Editor $9·Viewer $5 /user·월 + CloudWatch 비용 | 사용자 1~2명 ~ $9~18, 다인·고급 대시보드용 |
| Grafana OSS 자체 호스팅 | EC2/컨테이너에 직접 설치 | EC2 약 $10~15 + 운영 부담 | SW 무료지만 관리 비용 발생, 비권고 |

### 3.6.2 권고 (예산 월 30만원)

기준: **CloudWatch Dashboards + Alarms + AWS Budgets**.
- AWS Budgets로 월 30만원의 80%/100% 도달 시 알림(통지형 예산은 무료).
- 대시보드 3개 이내로 시작하면 사실상 $0 수준.
- Grafana UI가 꼭 필요하면 **Grafana Cloud 무료 티어**에 CloudWatch를 데이터소스로 연결(추가 $0, CloudWatch API 호출 비용만 소액).
- 다인 협업·고급 패널이 필요해지면 Amazon Managed Grafana로 승격.

### 3.6.3 대시보드에 담을 핵심 지표

| 영역 | 지표 예시 |
| --- | --- |
| DynamoDB | 소비 RCU/WCU, throttle, TTL 삭제 항목 수, 오류율 |
| RDS MySQL | CPU, 연결 수, 슬로우 쿼리, 스토리지 |
| Lambda(수집/Agent) | 호출 수, 오류, 지속시간, throttle |
| API | p50/p95 지연, 5xx 비율, 요청 수 |
| 비용 | 서비스별 월 누적, 예산 대비 소진율(AWS Budgets) |

신뢰도: 비용·티어는 AWS/Grafana 공개 페이지 기준(중~상). 리전·사용량·티어 정책에 따라 변동하므로
도입 전 재확인 필요.

### 3.6.4 대표 문서 반영 위치

- 6장 전환 표 `Production 운영` 단계에 "CloudWatch 기반 운영 대시보드·예산 알람" 추가.
- (선택) 별도 운영/관측 섹션 또는 기술 명세서(`../06_technical_spec`)로 분리 가능.

## 4. 적용 체크리스트

- [ ] 2.1/2.2 보존 기간 `확정값` 확정(법무·보안 검토 포함)
- [ ] 5장 보존 정책 표에 확정 기간 반영
- [ ] 4.3절 TTL 기준에 테이블별 기간 반영
- [ ] 1.2/1.3/6장에 Neptune 비용 주의·도입 단계 반영
- [ ] 3.5/4.6장에 Neptune 대체 아키텍처(3.5.3) 반영
- [ ] 6장에 운영 대시보드(3.6.2) 반영
- [ ] 8장 후속작업 #2 상태 갱신
- [ ] 9장 변경 이력 v0.5 추가
- [ ] `pages/` HTML 생성물 최신화

---

## 5. 참고 (Neptune 비용 출처)

- [Amazon Neptune Pricing (AWS)](https://aws.amazon.com/neptune/pricing/)
- [Amazon Neptune Serverless now scales down to 1 NCU (AWS)](https://aws.amazon.com/about-aws/whats-new/2023/03/amazon-neptune-serverless-scales-down-1-ncu-costs/)
- [Capacity scaling in a Neptune Serverless DB cluster (AWS Docs)](https://docs.aws.amazon.com/neptune/latest/userguide/neptune-serverless-capacity-scaling.html)
- [Cost optimization pillar — Neptune Well-Architected (AWS Docs)](https://docs.aws.amazon.com/prescriptive-guidance/latest/neptune-well-architected-framework/cost-optimization-pillar.html)
- 환율: [USD/KRW (Wise)](https://wise.com/us/currency-converter/usd-to-krw-rate/history) — 2026-06 약 1,555원/USD
- [Amazon CloudWatch Pricing (AWS)](https://aws.amazon.com/cloudwatch/pricing/)
- [AWS Budgets Pricing (AWS)](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/)
- [Amazon Managed Grafana Pricing (AWS)](https://aws.amazon.com/grafana/pricing/)
- [Grafana Cloud Free Tier (Grafana)](https://grafana.com/products/cloud/free-tier/)
