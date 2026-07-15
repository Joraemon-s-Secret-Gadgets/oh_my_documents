# 로브 (Lovv) 팀원 포트폴리오 가이드라인

> 문서 버전: v0.1
> 문서 상태: 검토 중 (Review)
> 작성일: 2026-07-03
> 문서 성격: 팀원 포트폴리오 작성 가이드
> 기준 문서: `../00_project_plan/00_project_plan.md`, `../01_requirements/01_requirements.md`, `../02_service_flow/02_service_flow.md`, `../03_data_collect_plan/03_data_collect_plan.md`, `../04_database_design/04_database_design.md`, `../05_agent_spec/05_agent_spec.md`, `../06_technical_spec/06_technical_spec.md`, `../07_api_spec/07_api_spec.md`, `../08_data_preprocessing/data_preprocessing_plan.md`, `../10_test_plan/10_test_plan.md`, `../11_deployment_ops/11_deployment_ops.md`

# 1. 목적

이 문서는 로브(Lovv) 프로젝트 팀원이 각자 포트폴리오를 만들 때, 현재 OMD(`00_oh_my_documents`) 문서 저장소와 LOVV 개발 관련 repo 전체를 기준으로 본인 파트와 근거를 정리하는 가이드라인이다.

핵심은 모든 팀원이 같은 문장으로 프로젝트를 소개하는 것이 아니다. 각자가 맡은 파트를 확인하고, 본인 역할에 맞는 문서·산출물·검증 근거를 찾아 개인 포트폴리오 안에 자연스럽게 넣는 것이다.

# 2. 작성 흐름

| 단계 | 해야 할 일 | 산출물 |
| --- | --- | --- |
| 1 | 본인이 맡은 파트를 먼저 확인한다. | 담당 파트 목록 |
| 2 | LOVV 개발 관련 repo 전체를 확인한다. | repo별 근거 후보 목록 |
| 3 | OMD에서 해당 파트와 연결된 대표 문서와 보조 문서를 찾는다. | 기준 문서 목록 |
| 4 | 구현 repo에서 본인 파트와 연결된 코드, 설정, 데이터, 테스트, 운영 근거를 찾는다. | 구현 근거 목록 |
| 5 | 본인 파트를 문서 관계 Graph 관점의 개체, 관계, 증거로 분해한다. | 포트폴리오 내용 구조 |
| 6 | 개인 기여와 팀 전체 산출물을 구분한다. | 역할 설명 |
| 7 | 공개 가능한 화면, 문서, 코드, 검증 결과만 골라 넣는다. | 공개용 포트폴리오 초안 |

# 3. LOVV 개발 repo 확인 범위

포트폴리오를 작성할 때는 OMD 문서만 보지 않는다. 각자 파트가 실제로 어느 repo의 코드, 데이터, 배포, Agent 동작과 연결되는지 확인한 뒤 작성한다.

아래 GitHub 확인 대상은 2026-07-03에 `gh repo view`로 조회한 팀 organization 기준 repo다. 모든 확인 대상의 default branch는 `main`이며 public repo로 확인했다.

| 로컬 폴더 | GitHub 확인 대상 | GitHub 설명 | 확인 관점 | 포트폴리오에 넣을 수 있는 근거 |
| --- | --- | --- | --- | --- |
| `00_oh_my_documents` | [Joraemon-s-Secret-Gadgets/oh_my_documents](https://github.com/Joraemon-s-Secret-Gadgets/oh_my_documents) | 파이널 프로젝트 문서 배포 사이트 | 프로젝트 문서, 요구사항, 설계, 발표, PDF/HTML 산출물 | 문제 정의, 요구사항, 설계 근거, 발표 자료, 문서화 기여 |
| `02_lovv_data_collect` | [Joraemon-s-Secret-Gadgets/lovv_data_collect](https://github.com/Joraemon-s-Secret-Gadgets/lovv_data_collect) | GitHub 설명 없음 | 데이터 수집 이후 전처리, 품질 검증, DynamoDB/S3 Vector 적재 | 정제 규칙, 적재 결과, vector 검색, 데이터 품질 개선 근거 |
| `03_lovv_BE` | [Joraemon-s-Secret-Gadgets/Lovv_BE](https://github.com/Joraemon-s-Secret-Gadgets/Lovv_BE) | AWS SAM BE | 백엔드 API, 인프라, 인증/권한, 배포 운영 | API 계약 구현, DB 연동, 운영 자동화, 보안/권한 처리 근거 |
| `04_Lovv-agent` | [Joraemon-s-Secret-Gadgets/Lovv-agent](https://github.com/Joraemon-s-Secret-Gadgets/Lovv-agent) | LangGraph로 Lovv multi agent 구현 | Agent, RAG, 추천 흐름, AgentCore/LangGraph runtime | Intent, 검색, 후보 선정, 점수화, 일정 생성, Agent 평가 근거 |

로컬 작업 remote에는 일부 개인 fork(`nobrain711/*`)도 연결되어 있을 수 있다. 포트폴리오 기준으로는 팀 organization repo를 우선 확인하고, 개인 fork는 본인 작업 branch, PR, commit 증거를 찾을 때 보조 근거로 사용한다.

repo 확인은 모든 파일을 전부 읽는다는 뜻이 아니다. 본인이 맡은 파트와 연결되는 대표 문서, 핵심 코드 경로, 테스트, 실행 결과, 운영 기록을 찾아 포트폴리오의 근거로 삼는다는 뜻이다.

각 repo를 볼 때는 아래 질문을 사용한다.

- 이 repo에서 내 파트와 직접 연결되는 산출물은 무엇인가?
- OMD의 어떤 요구사항 또는 설계 문서와 연결되는가?
- 코드, 데이터, 테스트, 운영 결과 중 공개 가능한 증거는 무엇인가?
- 팀 전체 결과와 내 개인 기여를 어떻게 구분할 수 있는가?
- 포트폴리오에 공개하면 안 되는 경로, 계정 정보, 운영 식별자, 로그는 없는가?

# 4. OMD를 문서 관계 Graph 관점으로 보는 방법

여기서 문서 관계 Graph는 실제 Graph DB로 변환한다는 뜻이 아니다. 현재 OMD 문서 구조를 `무엇이 존재하는가`, `서로 어떻게 연결되는가`, `무엇으로 증명되는가`의 관계형 색인처럼 읽는 방식이다.

OMD는 포트폴리오의 기준 문서 관계 Graph 역할을 한다. 구현 repo에서 찾은 코드·데이터·테스트 근거는 OMD의 요구사항, 설계, 테스트, 운영 문서 중 하나에 연결해 설명한다.

## 4.1 핵심 개체

| 개체 | OMD에서의 위치 | 포트폴리오에서의 의미 |
| --- | --- | --- |
| Project | `docs/00_project_plan/00_project_plan.md` | 내가 참여한 서비스의 목적, 범위, 가치 |
| Requirement | `docs/01_requirements/01_requirements.md` | 내가 해결한 요구사항과 수용 기준 |
| User Flow | `docs/02_service_flow/02_service_flow.md` | 사용자가 기능을 만나는 과정 |
| Data Source | `docs/03_data_collect_plan/03_data_collect_plan.md` | 추천 품질을 만들기 위한 원천 데이터 |
| Data Model | `docs/04_database_design/04_database_design.md` | 저장 구조, 관계, 보존 기준 |
| Agent | `docs/05_agent_spec/05_agent_spec.md` | 조건 분류, 검색, 후보 선정, 일정 생성 책임 |
| Architecture | `docs/06_technical_spec/06_technical_spec.md` | 전체 기술 구조와 선택 이유 |
| API | `docs/07_api_spec/07_api_spec.md` | 프론트엔드, 백엔드, Agent 사이의 계약 |
| Data Pipeline | `docs/08_data_preprocessing/data_preprocessing_plan.md` | 수집 이후 정제, 적재, 품질 검증 흐름 |
| Test Evidence | `docs/10_test_plan/10_test_plan.md` | 결과를 어떻게 검증했는지 |
| Operation | `docs/11_deployment_ops/11_deployment_ops.md` | 배포, 운영, 장애 대응 기준 |
| Presentation | `docs/99_pptx/` | 프로젝트를 외부에 설명하는 발표·포트폴리오 자료 |

## 4.2 핵심 관계

| 관계 | 읽는 방법 | 포트폴리오에 쓰는 방식 |
| --- | --- | --- |
| Project defines Requirement | 프로젝트 목적이 요구사항을 만든다. | 왜 이 기능이 필요했는지 설명한다. |
| Requirement drives Flow | 요구사항이 사용자 흐름으로 구체화된다. | 기능이 사용자 화면 또는 행동과 어떻게 연결되는지 보여준다. |
| Flow calls API | 사용자 흐름이 API 계약을 필요로 한다. | 화면, 백엔드, Agent의 연결 지점을 설명한다. |
| API reads/writes Data Model | API가 데이터 모델을 조회하거나 변경한다. | 저장 구조와 요청/응답의 연결을 보여준다. |
| Agent uses Data Pipeline | Agent 추천 품질은 수집·전처리 데이터에 의존한다. | 추천 결과가 데이터 준비와 어떻게 연결되는지 설명한다. |
| Test verifies Requirement | 테스트가 요구사항 충족 여부를 확인한다. | 검증 결과를 포트폴리오의 근거로 사용한다. |
| Operation supports Project | 배포·운영 기준이 서비스 지속성을 뒷받침한다. | 운영 경험과 장애 대응 역량을 설명한다. |

## 4.3 증거로 쓸 수 있는 것

| 증거 유형 | 예시 | 주의 사항 |
| --- | --- | --- |
| 문서 근거 | 요구사항, 설계서, 테스트 계획, 운영 가이드 | 내부 경로를 그대로 공개해도 되는지 확인한다. |
| 화면 근거 | UI 캡처, 발표 슬라이드, 플로우 이미지 | 개인정보와 내부 URL을 제거한다. |
| 코드 근거 | 핵심 함수, API handler, Agent node, 데이터 변환 코드 | 본인이 직접 기여한 범위를 구분한다. |
| 데이터 근거 | 수집 결과, 전처리 결과, 품질 검증 표 | 원본 데이터의 민감 정보를 제거한다. |
| 운영 근거 | 배포 로그, 장애 원인 분석, runbook | 계정 ID, host, IP, 토큰, 리소스 ID를 마스킹한다. |

# 5. 파트별 포트폴리오 작성 기준

## 5.1 기획·요구사항 파트

확인할 문서:

- `docs/00_project_plan/00_project_plan.md`
- `docs/01_requirements/01_requirements.md`
- `docs/96_market_research/96_market_research.md`
- `docs/98_prd/*.md`

넣을 내용:

- 어떤 사용자 문제를 정의했는지
- 어떤 기능을 PoC, P1, 후보 범위로 나눴는지
- 요구사항의 수용 기준을 어떻게 정리했는지
- 시장 조사나 경쟁 서비스 분석이 기능 범위에 어떻게 반영됐는지

작성 구조:

```text
문제 정의 -> 요구사항 정리 -> 우선순위 결정 -> 포트폴리오에 보여줄 근거
```

## 5.2 서비스 흐름·UI/UX 파트

확인할 문서:

- `docs/02_service_flow/02_service_flow.md`
- `docs/09_ui_ux_guide/09_ui_ux_guide.md`
- `docs/95_aha_moment/*.md`
- `docs/99_pptx/01_midterm_presentation/pages/*.md`

넣을 내용:

- 사용자가 어떤 흐름으로 추천 결과를 받는지
- 빈 상태, 오류 상태, 권한 없는 상태를 어떻게 다뤘는지
- 화면 구성이 요구사항과 어떻게 연결되는지
- 발표 자료 또는 화면 설계가 사용자 이해를 어떻게 돕는지

작성 구조:

```text
사용자 상황 -> 화면/흐름 설계 -> 상태 처리 -> 결과 캡처 또는 발표 근거
```

## 5.3 데이터 수집·전처리 파트

확인할 문서:

- `docs/03_data_collect_plan/03_data_collect_plan.md`
- `docs/03_data_collect_plan/supplemental/korea_data_acquisition_plan_updated.md`
- `docs/03_data_collect_plan/supplemental/kr_data_acquisition_report_20260629.md`
- `docs/08_data_preprocessing/data_preprocessing_plan.md`
- `docs/08_data_preprocessing/supplemental/kr_20260630_preprocessing_completion_report.md`
- `docs/08_data_preprocessing/supplemental/kr_20260629_preprocessing_redesign_spec.md`
- `docs/08_data_preprocessing/supplemental/vector_search_v2_guide.md`
- `data_collect_documents_20260702/TRANSFER_MANIFEST.md`

넣을 내용:

- `raw/KR/details/20260629/` 기준으로 어떤 KR 데이터를 왜 취득했는지
- raw 취득 문서와 V2 전처리 문서의 역할을 어떻게 분리했는지
- `processed/KR/details/20260629/passed/` 산출물을 DynamoDB V2와 Vector V2 입력으로 어떻게 연결했는지
- `TourKoreaDomainDataV2`, `kr-tour-domain-v2`, 8,010 DDB items, 7,606 unique vectors 같은 완료 근거를 어떻게 확인했는지
- 데이터 품질 이슈를 `review/`, `failed/`, vector duplicate key, Wikipedia/image 보강 상태로 어떻게 분류했는지

작성 구조:

```text
수집 대상 -> raw 취득 근거 -> V2 전처리 규칙 -> DynamoDB V2/Vector V2 적재·검증 결과
```

## 5.4 데이터베이스·저장 구조 파트

확인할 문서:

- `docs/04_database_design/04_database_design.md`
- `docs/04_database_design/supplemental/*.md`
- `docs/04_database_design/supplemental/dynamodb_v2_query_guide.md`
- `docs/04_database_design/supplemental/dynamodb_vector_v2_usage_guide.md`
- `docs/08_data_preprocessing/supplemental/vector_search_v2_guide.md`
- `docs/08_data_preprocessing/supplemental/s3_vector_index_plan.md`

넣을 내용:

- 어떤 데이터를 어떤 저장소에 둬야 했는지
- 현재 KR 운영 기준이 `TourKoreaDomainDataV2`와 `lovv-vector-dev/kr-tour-domain-v2`임을 어떻게 확인했는지
- DynamoDB source of truth와 S3 Vector semantic search를 어떻게 분리했는지
- `ddb_pk`, `ddb_sk`로 vector 결과를 DynamoDB 원문 record로 hydrate하는 구조를 어떻게 설명할지
- 인덱스, TTL, 보존 정책, query pattern, vector metadata allowlist를 어떻게 판단했는지
- 추천 품질과 저장 구조가 어떻게 연결되는지

작성 구조:

```text
데이터 성격 -> DynamoDB V2 source of truth -> S3 Vector V2 검색 -> 추천 또는 운영 활용
```

## 5.5 Agent·RAG 파트

확인할 문서:

- `docs/05_agent_spec/05_agent_spec.md`
- `docs/05_agent_spec/sections/*.md`
- `docs/05_agent_spec/supplemental/*.md`
- `docs/05_agent_spec/supplemental/v2/*.md`
- `docs/10_test_plan/supplemental/*.md`

넣을 내용:

- Agent를 어떤 책임 단위로 나눴는지
- Intent, 검색, 후보 선정, 점수화, 일정 생성이 어떻게 연결되는지
- RAG 또는 도구 호출이 왜 필요한지
- 테스트나 평가 결과로 추천 품질을 어떻게 확인했는지

작성 구조:

```text
사용자 입력 -> Agent 책임 분리 -> 검색/검증/랭킹 -> 추천 결과와 평가
```

## 5.6 백엔드·API·운영 파트

확인할 문서:

- `docs/06_technical_spec/06_technical_spec.md`
- `docs/07_api_spec/07_api_spec.md`
- `docs/07_api_spec/supplemental/*.md`
- `docs/11_deployment_ops/11_deployment_ops.md`
- `docs/11_deployment_ops/supplemental/*.md`

넣을 내용:

- API 계약이 화면, 데이터, Agent와 어떻게 연결되는지
- 인증, 권한, 오류 응답, 관리자 기능을 어떻게 다뤘는지
- 배포 또는 운영 이슈를 어떻게 확인하고 대응했는지
- runbook, troubleshooting, 검증 로그를 어떻게 정리했는지

작성 구조:

```text
요청/응답 계약 -> 인증/권한 -> 데이터 또는 Agent 연결 -> 운영 검증
```

## 5.7 테스트·품질 검증 파트

확인할 문서:

- `docs/10_test_plan/10_test_plan.md`
- `docs/10_test_plan/supplemental/*.md`
- 각 파트의 결과 보고서 또는 검증 문서

넣을 내용:

- 무엇을 테스트했는지
- 테스트 기준을 어디서 가져왔는지
- 자동 테스트, 수동 검증, 정성 평가 중 무엇을 사용했는지
- 실패나 한계를 어떻게 다음 개선 과제로 정리했는지

작성 구조:

```text
검증 대상 -> 검증 기준 -> 실행 결과 -> 한계와 개선 방향
```

# 6. 개인 포트폴리오 템플릿

아래 템플릿은 각자 맡은 파트에 맞게 줄이거나 확장한다.

```markdown
# Lovv 프로젝트 포트폴리오

## 1. 내가 맡은 파트

- 담당 영역:
- 연결된 OMD 문서:
- 직접 만든 산출물:
- 협업한 파트:

## 2. 파트의 문서 관계 Graph 정리

- 핵심 개체:
- 연결 관계:
- 사용한 근거:
- 최종 산출물:

## 3. 문제와 해결 과정

- 문제:
- 제약:
- 선택한 접근:
- 선택 이유:
- 포기한 대안:

## 4. 포트폴리오에 넣을 증거

- 문서:
- 코드:
- 화면:
- 데이터:
- 테스트/운영 결과:

## 5. 결과와 회고

- 결과:
- 배운 점:
- 한계:
- 다음 개선 방향:
```

# 7. 공개 전 점검

- 본인이 맡은 파트와 팀 전체 산출물을 구분했는가?
- 포트폴리오 주장마다 OMD 문서 또는 실제 산출물 근거가 있는가?
- 내부 계정 ID, host, private IP, token, 운영 리소스 ID를 제거했는가?
- 코드나 로그를 공개할 때 민감 정보가 없는가?
- 실패나 한계를 숨기지 않고 해결 과정으로 정리했는가?
- 발표용 문장보다 채용 담당자나 면접관이 확인할 수 있는 근거 중심으로 작성했는가?

# 8. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-07-03 | 로브 기획팀 | 팀원별 파트 확인, LOVV 개발 repo 확인 범위, OMD 문서 관계 Graph 관점 정리, 개인 포트폴리오 작성 템플릿 초안 작성 |
