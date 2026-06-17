# 슬라이드 B12.5 — Production 개발 계획

> 원본 위치: `../01_midterm_presentation.md`
> 상태: Slide Content
> 역할: 중간 발표(6/16) 이후 최종·Production(7/16)까지, 남은 기간을 어떻게 개발할지 스프린트 단위 로드맵으로 보여준다
> 위치: 슬라이드 "확장 방향"과 "출처" 사이

## 화면 문구

**Production 개발 계획 — 영역별 핵심 작업**

| 영역 | 핵심 작업 |
| --- | --- |
| 에이전트·추천 | 통합 5종 에이전트 · 결정적 Skill군 정식화 · Planner 동선·대체 일정 |
| 통합·개인화 | 피드백 기반 추천 가감점 · 일정·기상 대체 토글 · 인증·저장·선호 API |
| 테스트·고도화 | 통합·외부 API 테스트 · RAG 평가 고도화 · 마이페이지·모바일 반응형 |
| 배포·운영 | AWS 실서비스화(SAM·Bedrock·Cognito) · HTTPS·보안·비용 모니터링 · 운영 가이드·README |

> 좋아요/싫어요 입력은 이미 구현됨 → 남은 작업은 그 이력을 추천에 반영하는 가감점·DB 영속화. 데모 QA·최종 발표는 별도 발표 슬라이드로 다룬다.

> 에이전트 카드 외 3개는 WBS(`sooa/wbs_revision_plan.md` §4.8)의 실제 남은 작업으로 구성한다. 이미 구현된 아키텍처 항목(OAuth·Lambda 라우팅·CloudFront 등)은 화면에 넣지 않는다.

**Production 목표:** 에이전트 5종 · 일정 · 개인화 · 인증 · 화면 완성 + AWS 실서비스화

## 레이아웃

| 영역 | 내용 |
| --- | --- |
| 상단 | "Production 개발 계획" 제목(별도 부제 없음) |
| 중앙 | 영역 카드 4장 2×2 배치(에이전트·추천 / 개인화·인증 / 백엔드·데이터 / 배포·운영·테스트), 각 카드에 영역 아이콘 + 좌측 컬러 바 |
| 하단 | Production 목표 한 줄(풀블리드 밴드) |

## 발표자 노트

- **프레임** — 마일스톤은 외부 고정일 2개(6/16 중간 발표·7/16 최종)뿐. 그 사이는 주 단위 스프린트로 끊어 운영하되, 화면에는 스프린트·날짜 대신 영역별 작업으로 보여준다.
- **에이전트·추천** — 통합 5종(Intent·Supervisor·Candidate_Evidence·Festival·Planner) + 결정적 Skill 분리(Scoring·Matrix Transition·Validation·Link Builder·Weather·Output Packaging) / Planner 동선·대체 일정 고도화·Festival 검증 마감 / 프롬프트 최적화 (근거: `agent_build_target.md`)
- **개인화** — 온보딩 선호 테마 1~3개 / 좋아요·싫어요 이력 기반 가감점 / PoC 로컬 스토리지 → DB 장기 선호 테이블 (근거: `agent_build_target.md`, DB 보존 업데이트)
- **백엔드·인증** — Google·Kakao OAuth + JWT / Lambda 라우팅(Auth-Function·Map-Function·AgentCore-Function) / 온보딩·선호·지도·저장 일정·마이페이지 API / 프론트 정적·localStorage → 백엔드 API를 Source of Truth로 전환(adapter layer) (근거: `product_api_transition_supplement.md`)
- **데이터·검색** — 한국 전국 + 일본 전국 확장 / 축제·날씨·장소 자동 갱신 파이프라인 / S3 Vector index 운영 + 보존·TTL 정책 확정 (근거: `18_expansion_tasks.md`, `s3_vector_index_plan.md`, DB 보존 업데이트)
- **배포·운영·테스트** — AWS 실서비스화(SAM/Lambda·Bedrock/AgentCore·Cognito)·HTTPS·보안·비용 모니터링(Amazon Q) / 통합·외부 API 테스트·RAG 평가 고도화 / 배포·운영 가이드 (근거: `11_deployment_ops.md`, WBS EPIC 13·14)
- **연결** — PoC에서 검증한 한 줄(추천+일정)을 위 영역들로 확장해 제품화한다. 운영자·관리자 화면 등 비핵심은 Production 단계로 이연.

## 제작 체크

- [ ] 영역 카드 5장으로 보여준다(스프린트·날짜·이슈 번호·담당자는 화면에서 뺀다).
- [ ] 하단에 Production 목표(에이전트 5종·일정·개인화·인증·화면 + AWS 실서비스화)를 한 줄로 둔다.
- [ ] 확장 방향 슬라이드(무엇을 확장)와 중복되지 않게, 이 장은 "영역별로 어떻게 만들지"에 집중한다.

## 근거·출처

- 에이전트 빌드 타깃: `../../../05_agent_spec/agent_build_target.md` (통합 5종, 결정적 Skill 분리, 개인화 피드백 가감점)
- API Product 전환: `../../../07_api_spec/product_api_transition_supplement.md` (OAuth·Lambda 라우팅·정적/localStorage → 백엔드 API 정합)
- DB 보존/TTL·Neptune: `../../../04_database_design/database_design_retention_neptune_update.md` (MySQL 원장·DynamoDB TTL·S3 Vector·Lambda 관계 탐색)
- 데이터 확장·자동 갱신: `18_expansion_tasks.md`, `../../../08_data_preprocessing/s3_vector_index_plan.md`
- 배포·운영: `../../../11_deployment_ops/11_deployment_ops.md` (Cognito·S3 Vector index·Lambda 관계 탐색)
- 일정 기준(노트용): WBS 재편안 `../../../../sooa/wbs_revision_plan.md` — M1 중간 발표(6/16) → M2 최종(7/16), Sprint 5~8
