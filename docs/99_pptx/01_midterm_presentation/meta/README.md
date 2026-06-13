# 중간발표 PPT 문서 정리

이 폴더는 Lovv 중간발표 자료의 원본 Markdown, 보조 근거 문서, 발표 산출물, 백업을 관리한다.

## 루트 기준

`../01_midterm_presentation.md`만 루트 대표 문서로 둔다. 나머지 문서와 산출물은 성격별 하위 폴더에 보관한다.

| 구분 | 경로 | 용도 |
| --- | --- | --- |
| 대표 문서 | `../01_midterm_presentation.md` | 디자인 도구와 발표본 생성의 기준이 되는 통합 원본 |
| 운영 문서 | `../meta/` | 가이드라인, 리뷰 피드백, 폴더 정리 설명 |
| 근거 문서 | `../references/` | 서론, 문제 근거, 외부 기사, 에이전트 딥다이브, 경쟁 비교 |
| 페이지별 문서 | `../pages/` | 슬라이드별 분리 작업 문서 |
| 보관 문서 | `../archive/` | 대표 문서에 흡수되었거나 구버전이 된 초안 |
| 백업 문서 | `../bak/` | 특정 정리 작업 전후 스냅샷 |
| 산출물 | `../artifacts/` | PPTX, SVG 등 발표 산출물 |
| HTML 산출물 | `../html_export/` | JSON, 이미지, 캡처 산출물. HTML 파일은 `../bak/2026-06-13_html_transfer/`로 이관 |

## 운영 문서

| 파일 | 용도 |
| --- | --- |
| `presentation_guidelines.md` | 발표 톤, 문서 운영, 페이지별 문서 작성 규칙 |
| `presentation_review_feedback_2026-06-13.md` | 2026-06-13 PPT 리뷰 피드백 정리와 후속 개편 체크리스트 |
| `README.md` | 이 폴더 구조 설명 |

## 근거 문서

| 파일 | 용도 |
| --- | --- |
| `../references/revision_plan_s1_s2_s3_s5_2026-06-12.md` | 2026-06-12 기준 슬라이드 수정 계획 |
| `../references/intro_revision_proposal.md` | S1~S5 서론 개편 근거 |
| `../references/s3_problem_axes_revision.md` | 오버투어리즘 문제 축과 사례 근거 |
| `../references/external_evidence_slides_2articles.md` | 기사 기반 문제·시장 근거 |
| `../references/agent_deep_dive_slides_condensed.md` | B3/B4 에이전트 딥다이브 압축안 |
| `../references/agent_deep_dive_slides_condensed_agent_spec_update_proposal.md` | 최신 Agent 명세 반영 제안 |
| `../references/lovv_vs_triple.md` | 트리플 대비 차별점 상세 근거 |

## 페이지별 문서

`../pages/`에는 대표 문서의 16개 슬라이드를 슬라이드별 Markdown으로 분리해 둔다. 특정 장표를 고칠 때는 해당 페이지 문서에서 먼저 초안을 정리한 뒤, 최종 결정 사항을 `../01_midterm_presentation.md`에 반영한다.

## 보관 문서

`../archive/2026-06-13_cleanup/`에는 대표 문서에 흡수되었거나 구버전이 된 초안·제안서를 보관한다. 삭제하지 않고 이동해 과거 판단 근거를 추적할 수 있게 둔다.

| 파일 | 보관 사유 |
| --- | --- |
| `midterm_presentation_draft_5slides.md` | 5장 구버전 초안 |
| `body_revision_proposal.md` | 본론 원안. 대표 문서와 후속 딥다이브 문서로 흡수 |
| `agent_deep_dive_revision_proposal.md` | 초기 에이전트 딥다이브 원안. 압축안과 최신 Agent 반영안으로 분화 |
| `system_flow_slides.md` | 분리된 시스템 흐름 초안. 대표 문서에 통합 |
| `user_flow_slides.md` | 분리된 유저 플로우 초안. 대표 문서에 통합 |

## 백업 문서

| 폴더 | 내용 |
| --- | --- |
| `../bak/2026-06-13_before_page_split/root/` | 페이지별 문서 분리 전 루트 Markdown 백업 |
| `../bak/2026-06-13_before_page_split/archive/2026-06-13_cleanup/` | 페이지별 문서 분리 전 archive Markdown 백업 |
| `../bak/2026-06-13_html_transfer/` | HTML 발표본과 HTML 캡처 인덱스 이관본 |

## 산출물

- `../artifacts/pptx/`: PPTX 산출물
- `../artifacts/system_flow_b1.svg`: 시스템 흐름 SVG 산출물
- `../html_export/`: 발표용 JSON, 이미지, 캡처 산출물
- `../html_export/captures/`: 화면 검증 캡처. 발표 검증 목적으로 보관할 수 있다.
