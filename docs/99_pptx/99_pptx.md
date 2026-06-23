# 로브 (Lovv) 발표 자료 대표 문서

> 문서 버전: v0.1
> 문서 상태: 검토 중 (Review)
> 작성일: 2026-06-23
> 문서 성격: 대표 Markdown
> 기준 문서: `../00_project_plan/00_project_plan.md`, `../05_agent_spec/05_agent_spec.md`, `../96_market_research/travel_ai_service_market_research.md`

# 1. 문서 목적

이 문서는 `docs/99_pptx/` 하위 발표 자료의 대표 문서다. 발표용 Markdown, 페이지별 슬라이드 문서, 발표 가이드, 참고 자료, 아카이브를 한 폴더 안에서 관리하되, 실제 발표 흐름은 각 발표 단위의 대표 문서를 기준으로 유지한다.

# 2. 발표 자료 구조

| 경로 | 역할 | 대표 문서 |
| --- | --- | --- |
| `01_midterm_presentation/` | 중간발표 Markdown, 페이지별 슬라이드 문서, 발표 기준 메타 자료 | `01_midterm_presentation/01_midterm_presentation.md` |
| `midterm_vs_final_presentation_guide.md` | 중간발표와 최종발표 구성 차이, 재사용 전략, 발표 원칙 | 본 문서의 보조 Markdown |

# 3. 중간발표 구조

`01_midterm_presentation/`은 00번 문서 구조와 같은 방식으로 관리한다.

- 대표 문서: `01_midterm_presentation.md`
- 페이지별 보조 문서: `pages/*.md`
- 페이지 맵: `pages/slide_map.md`
- 발표 규칙·피드백: `meta/*.md`
- 참고 원본: `references/*.md`
- 이전 작업 보관: `archive/`
- 로컬 백업: `bak/` (`.gitignore`에 의해 Git 추적 제외)

# 4. 편집 원칙

- 발표 메시지를 바꾸면 먼저 대표 Markdown 또는 페이지별 Markdown을 갱신한다.
- PPTX, HTML 발표본, 캡처 이미지는 산출물로 보고 원본 Markdown과 충돌하지 않게 관리한다.
- `bak/`는 로컬 백업 전용이며 GitHub에 업로드하지 않는다.
- 새 발표 단위를 만들면 하위 폴더에 대표 Markdown과 `AGENT.md`를 함께 둔다.

# 5. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.1 | 2026-06-23 | 로브 기획팀 | 발표 자료 폴더 대표 문서 생성, 중간발표 하위 구조와 백업 관리 기준 정리 |
