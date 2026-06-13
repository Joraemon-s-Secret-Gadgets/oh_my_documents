# 슬라이드 B7 — 이슈/트러블슈팅: Neptune 도입 판단

> 원본 위치: `
../01_midterm_presentation.md
`
> 상태: Draft
> 역할: 대표 문서에서 분리한 슬라이드별 작업 문서

**핵심 메시지 (화면 카피)**
Neptune은 지금 넣는 기술이 아니라, 조건이 맞을 때 승격하는 선택지다

**서브 카피**
그래프DB가 멋있어서 쓰는 것이 아니라, 다단계 관계 탐색이 실제 병목이 될 때만 도입한다.

**화면 구성 — 이슈 → 판단 → 대응 → 승격 기준**

| 구분 | 발표 화면 문구 |
| --- | --- |
| 이슈 | 도시·테마·축제·인접도시 관계를 그래프로 풀 수 있지만, PoC 관계는 대부분 1~2-hop 수준 |
| 비용 | Neptune Serverless도 최소 1 NCU부터 시작해 월 30만원 예산에서 고정비 비중이 큼 |
| 판단 | PoC/Production 1차는 Neptune 미도입. Lambda로 그래프DB 유사 기능을 구현하고 RDS JOIN, DynamoDB 인접 리스트, 사전계산 후보 테이블을 조합 |
| 트러블슈팅 | 관계 탐색을 원본 저장소가 아닌 Lambda 기반 재생성 가능 보조 기능으로 정의해 vendor lock-in과 비용 리스크를 낮춤 |
| 승격 기준 | 3-hop 이상 임의 경로 탐색, 대규모 실시간 그래프 쓰기, 복잡한 그래프 알고리즘이 필요해질 때 Neptune 도입 |

**화면 도식**

```text
문제 인식      비용 검토        대체 구현                 승격 기준
관계 탐색 필요 → Neptune 고정비 → Lambda/RDS/DynamoDB/사전계산 → 3-hop+·실시간 그래프
```

**하단 출처**
내부: `04_database_design.md`, `neptune_alternative.md` / 외부: AWS Neptune Pricing

**발표자 노트**
- “Neptune을 못 쓴다”가 아니라 “지금 쓰면 오버엔지니어링이라 보류했다”로 말한다.
- PoC의 목적은 추천 흐름과 근거 제시 검증이다. 현재 규모에서는 RDS JOIN, DynamoDB 인접 리스트, 사전계산, Lambda 인메모리 그래프로 충분하다.
- 그래프DB는 다도시 일정, 사용자 행동 기반 co-visitation, 3-hop 이상 관계 순회가 실제 요구가 될 때 승격한다.
- 질문 대비: “왜 처음부터 Neptune을 안 쓰나?” → 비용 대비 효용이 낮고, 현재 관계 깊이는 Lambda/RDS/DynamoDB로 방어 가능하다.

---
