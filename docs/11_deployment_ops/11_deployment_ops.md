# 로브 (Lovv) 배포·운영 가이드

> 문서 버전: v0.4
> 문서 상태: 초안 (Draft)
> 작성일: 2026-06-12
> 작성자: llm팀
> 기준 문서: `../06_technical_spec/06_technical_spec.md`, `../07_api_spec/07_api_spec.md`, `../08_data_preprocessing/data_preprocessing_plan.md`, `troubleshooting.md`

---

> **[PRD 반영 v0.1 — 대화형 빌더]** 관측: **OTel + AWS X-Ray + CloudWatch Structured JSON Logs**로
> 노드별 토큰·컨텍스트·레이턴시·I/O 트레이싱(정본: `Lovv-agent/docs/specs/LOVV_AGENTCORE_OBSERVABILITY_SPEC.md`).
> CI/CD: 기존 게이트(pytest·compileall·parity·`agentcore validate`/`deploy --dry-run`) + 빌더 게이트
> (무상태 회귀·state serde round-trip·geo-filter·soft floor 폴백·정합성 게이트·interrupt/resume 스모크).
> 상세: `../98_prd/interactive_builder_prd.md`.

# 1. 문서 개요

이 문서는 로브(Lovv) 서비스의 배포와 운영 절차를 정리하는 대표 문서다. 현재는 상세 운영 절차가 확정되기 전 단계이므로, 운영 중 확인해야 할 기준 문서와 트러블슈팅 문서를 연결하는 역할을 한다.

# 2. 운영 문서 구성

| 문서 | 역할 |
| --- | --- |
| `11_deployment_ops.md` | 배포·운영 대표 문서 |
| `troubleshooting.md` | 프로젝트 진행 중 발생한 주요 이슈와 대응 기준 |
| `../06_technical_spec/06_technical_spec.md` | 인프라와 기술 선택 근거 |
| `../07_api_spec/07_api_spec.md` | API 계약과 오류 응답 기준 |
| `../08_data_preprocessing/` | 데이터 전처리와 적재 운영 기준 |

# 3. 운영 원칙

- 설계 결정의 "왜"는 기술 명세서에 두고, 이 문서는 "어떻게 배포·운영하는가"에 집중한다.
- 환경 변수와 secret은 실제 값을 문서에 쓰지 않고 관리 방식만 기록한다.
- 장애나 의사결정 이슈는 `troubleshooting.md`에 증상, 원인, 판단, 조치, 재발 방지 기준으로 남긴다.
- HTML/PDF 공유 산출물은 원본 Markdown과 함께 검증한 뒤 배포한다.

# 4. 현재 우선 운영 항목

| 영역 | 현재 기준 |
| --- | --- |
| 인증·인가 | Cognito Hosted UI/OIDC가 Social Login을 담당하고 Lovv backend는 `/api/v1/auth/cognito/session` bridge로 세션 shape를 구성 |
| 데이터 적재 | KR 상세 데이터는 `TourKoreaDomainData` 기준 |
| 검색 인덱스 | S3 vector index `kr-tour-domain-v1` 구축 기준 수립 |
| 그래프DB | 현재 직접 도입하지 않고 Lambda 기반 관계 탐색 보조 기능으로 유사 기능 구현 예정. Neptune은 승격 기준 충족 시 재검토 |
| 문서 배포 | `docs/` Markdown 원본 → `pages/*.html` 생성 |
| PDF 배포 | 대응 Markdown 원본 → `pdf/*.tex`/`pdf/*.pdf` 생성 |

# 5. 검증 명령

HTML 문서 구조 검증:

```powershell
python scripts\generate_pages.py
python scripts\verify_pages_structure.py
```

PDF 문서 검증:

```powershell
cd pdf
xelatex -interaction=nonstopmode -halt-on-error <target>.tex
xelatex -interaction=nonstopmode -halt-on-error <target>.tex
```

# 6. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.3 | 2026-06-12 | llm팀 | 그래프DB 직접 도입 대신 Lambda 기반 관계 탐색 보조 기능 구현 예정으로 운영 기준 조정 |
| v0.2 | 2026-06-12 | llm팀 | Cognito/Social Login 운영 기준을 현재 우선 운영 항목에 추가 |
| v0.1 | 2026-06-12 | llm팀 | 배포·운영 대표 문서 초안 작성 및 트러블슈팅 문서 연결 |
