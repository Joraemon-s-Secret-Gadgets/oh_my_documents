# Docs Graph Structure Assessment

> 작성일: 2026-07-03
> 대상: `00_oh_my_documents` 문서 구조
> 결론: 전면 graph 구조 전환은 아직 비용이 크다. 현재 폴더 구조를 유지하고, 문서 간 관계를 별도 graph metadata로 얹는 하이브리드 방식이 적합하다.

## 현재 구조 요약

현재 문서 저장소는 단순 tree가 아니라 아래 네 층이 섞인 구조다.

1. `docs/<번호_도메인>/<대표 문서>.md`
2. `docs/<번호_도메인>/sections/*.md`
3. `docs/<번호_도메인>/supplemental/*.md`
4. `pages/*.html`, `index.html`, `pdf/*` 생성 산출물

`docs/AGENT.md`와 각 하위 `AGENT.md`는 `00_project_plan` 및 `01_requirements`부터 `11_deployment_ops`까지는 `sections/*.md`를 편집 원본으로 보고, 대표 문서를 통합본으로 관리하도록 규정한다. 90번대 문서는 이 강제 구조에서 제외되어 있다.

`scripts/generate_pages.py`는 공개 문서를 자동 탐색하지 않고 `DOCUMENTS` 배열에 등록된 문서만 `pages/*.html`과 `index.html`로 생성한다. 따라서 현재 사이트 구조는 폴더 구조만으로 결정되지 않고, 생성 스크립트의 명시적 목록과 순서에 강하게 묶여 있다.

## 관찰된 문제

현재 tree 구조의 장점은 명확하다. 번호가 붙은 문서 흐름 때문에 발표, GitHub Pages, PDF 생성, 에이전트 편집 규칙이 안정적으로 작동한다. 반면 문서 수가 늘어나면서 아래 문제가 커지고 있다.

- 같은 근거 문서가 여러 대표 문서에 영향을 주지만 관계가 파일 경로와 사람의 기억에 의존한다.
- `supplemental/` 문서가 많아질수록 어떤 보조 문서가 어떤 대표 문서에 반영되었는지 추적하기 어렵다.
- `00_project_plan`은 여러 상세 문서의 요약본인데, 역방향 영향 관계가 기계적으로 드러나지 않는다.
- 공개 HTML 대상은 `DOCUMENTS` 배열에만 있으므로, 새 대표 문서나 주요 보조 문서가 누락되기 쉽다.
- GraphRAG, Agent, DynamoDB, S3 Vector처럼 여러 도메인을 가로지르는 주제는 tree 위치 하나로 표현하기 어렵다.

## Graph 전환 선택지

### 선택지 A: 전면 graph 구조

예시:

```text
docs/
  nodes/
    requirements/*.md
    service-flow/*.md
    data/*.md
    agent/*.md
  edges.yml
  views/
    project-plan.yml
    github-pages.yml
```

이 방식은 관계 표현은 가장 좋지만, 현재 저장소에는 부적합하다. 기존 `AGENT.md` 규칙, `sections/` 기반 편집 흐름, `scripts/generate_pages.py`, `scripts/verify_pages_structure.py`, `pages/*.html`, `pdf/*` 재생성 흐름을 동시에 바꿔야 한다. 전환 중 링크 깨짐, 생성 대상 누락, 대표 문서 정본 혼란이 발생할 가능성이 높다.

### 선택지 B: 현 구조 유지 + graph metadata 추가

예시:

```text
docs/
  _graph/
    nodes.yml
    edges.yml
    views.yml
```

이 방식은 현재 구조를 보존하면서 문서 관계만 명시한다. 각 문서는 기존 위치에 두고, graph metadata가 다음 관계를 설명한다.

- `source_of`: 섹션 또는 보조 문서가 대표 문서의 원천인지
- `summarized_by`: 상세 문서가 프로젝트 기획서에 요약되는지
- `depends_on`: 문서가 다른 문서 결정을 참조하는지
- `publishes_to`: Markdown이 어떤 HTML/PDF 산출물로 생성되는지
- `supersedes`: 오래된 보조 문서를 대체하는지
- `related_to`: 동일 주제이지만 정본 관계는 아닌지

이 방식이 현재 저장소에 가장 적합하다. 기존 편집 규칙과 생성 스크립트를 유지하면서, 문서 관계 검색과 누락 검증만 추가할 수 있다.

### 선택지 C: 대표 문서 front matter에 관계 직접 삽입

예시:

```yaml
---
doc_id: agent_spec
depends_on:
  - requirements
  - technical_spec
publishes_to:
  - pages/05_agent_spec.html
---
```

문서와 metadata가 가까워지는 장점이 있지만, 현재 Markdown 상단은 이미 `>` 메타데이터 형식을 사용한다. front matter를 섞으면 기존 생성기와 사람이 읽는 문서 형식이 흔들릴 수 있다. 단기 도입안으로는 별도 `_graph/*.yml`보다 리스크가 크다.

## 권장 구조

전환한다면 다음 형태가 좋다.

```text
docs/
  _graph/
    nodes.yml
    edges.yml
    views.yml
    README.md
```

`nodes.yml`은 문서 식별자와 실제 파일 위치를 관리한다.

```yaml
nodes:
  project_plan:
    path: docs/00_project_plan/00_project_plan.md
    kind: representative
    domain: planning
    publishes_to:
      - index.html
      - pages/00_project_plan.html
  agent_spec:
    path: docs/05_agent_spec/05_agent_spec.md
    kind: representative
    domain: agent
    publishes_to:
      - pages/05_agent_spec.html
```

`edges.yml`은 문서 간 관계를 관리한다.

```yaml
edges:
  - from: requirements
    to: project_plan
    type: summarized_by
  - from: service_flow
    to: requirements
    type: refines
  - from: agent_spec
    to: requirements
    type: depends_on
  - from: agent_spec_v2_architecture_final
    to: agent_spec
    type: source_of
```

`views.yml`은 현재 `DOCUMENTS` 배열을 대체하거나 보조할 공개 뷰를 정의한다.

```yaml
views:
  github_pages:
    - project_plan
    - requirements
    - service_flow
    - data_collect_plan
    - data_preprocessing
    - database_design
    - agent_spec
    - technical_spec
    - api_spec
    - ui_ux_guide
    - test_plan
    - deployment_ops
```

## 기대 효과

- `supplemental/` 문서가 어느 대표 문서에 반영되어야 하는지 자동 점검할 수 있다.
- 새 대표 문서가 `pages/*.html` 생성 대상에서 빠졌는지 검증할 수 있다.
- 프로젝트 기획서와 상세 문서 사이의 동기화 대상을 명시할 수 있다.
- GraphRAG, Agent, 데이터 전처리처럼 여러 문서에 걸친 주제를 파일 이동 없이 연결할 수 있다.
- 나중에 검색 UI, Mermaid 관계도, 문서 영향도 분석으로 확장하기 쉽다.

## 리스크

- 관계 metadata가 수동 관리되면 금방 낡을 수 있다.
- `nodes.yml`과 `scripts/generate_pages.py`의 `DOCUMENTS` 배열이 중복되면 두 곳을 같이 수정해야 한다.
- 모든 보조 문서를 처음부터 graph node로 등록하면 관리 부담이 크다.
- 문서 관계 타입이 과하게 늘어나면 검색보다 분류 비용이 커진다.

## 도입 순서

1. `docs/_graph/README.md`, `nodes.yml`, `edges.yml`, `views.yml`을 추가한다.
2. 먼저 공개 대표 문서와 중요 supplemental 문서만 graph node로 등록한다.
3. `scripts/verify_pages_structure.py`에 graph metadata 검증을 추가한다.
4. 검증이 안정화되면 `scripts/generate_pages.py`의 `DOCUMENTS` 배열을 `views.yml` 기반으로 바꾼다.
5. 마지막에 `index.html`에 graph view 또는 관련 문서 링크를 노출한다.

## 판단

지금 바로 문서 폴더를 graph 중심으로 재배치하는 것은 권장하지 않는다. 이 저장소의 실제 정본 체계는 이미 `docs/AGENT.md`, 각 폴더 `AGENT.md`, `sections/*.md`, 대표 문서, HTML/PDF 생성물에 분산되어 있고, 이 체계가 문서 운영 안정성을 제공하고 있다.

다만 graph metadata는 도입 가치가 있다. 현재 구조의 약점은 파일 위치가 아니라 관계 추적 부재이기 때문이다. 따라서 최적안은 "tree를 폐기하는 graph 전환"이 아니라 "tree는 보존하고 graph를 색인 계층으로 추가"하는 방식이다.
