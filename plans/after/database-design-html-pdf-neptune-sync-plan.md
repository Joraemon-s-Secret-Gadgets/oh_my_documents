---
작성자: Codex
상태: 진행후
---

# 데이터베이스 설계 HTML/PDF 반영 계획

## 목적

`docs/04_database_design/04_database_design.md`에 반영된 RDB ERD 정리와 AWS Neptune Graph DB 추가 내용을 공유 산출물인 HTML과 PDF에 일관되게 반영한다. 원본은 `docs/` Markdown이며, `pages/*.html`, `index.html`, `pdf/*.tex`, `pdf/*.pdf`는 생성물로 취급한다.

## 대상 파일

| 구분 | 파일 | 처리 방향 |
| --- | --- | --- |
| 대표 원본 | `docs/04_database_design/04_database_design.md` | 현재 반영된 RDB/Neptune 내용의 기준 |
| 보조 원본 | `docs/04_database_design/DBMS.md` | DBMS 요약에 AWS Neptune 포함 여부 확인 |
| 보조 원본 | `docs/04_database_design/integrated_draft.md` | 상세 초안의 저장소 방향과 대표 문서 충돌 확인 |
| 연결 원본 | `docs/05_agent_spec/05_agent_spec.md` | Retriever 저장소 계약 확인 |
| 연결 원본 | `docs/06_technical_spec/06_technical_spec.md` | Retrieval 기술 후보 확인 |
| HTML 생성물 | `pages/04_database_design.html`, `pages/05_agent_spec.html`, `pages/06_technical_spec.html`, `index.html` | `scripts/generate_pages.py`로 재생성 |
| PDF TeX 생성물 | `pdf/database_design.tex` | 대표 Markdown에서 재생성 |
| PDF 최종 산출물 | `pdf/database_design.pdf` | `xelatex` 2회 실행으로 재생성 |

## 유지할 범위

- `pdf/data_collect_plan.*`, `pdf/korea_data_acquisition_plan.*`, `pdf/japan_data_acquisition_plan.*`는 현재 작업과 무관한 기존 변경이므로 이번 계획의 반영 대상에서 제외한다.
- `docs/06_database_design/`는 현재 체크아웃에 존재하지 않으므로 반영 대상으로 보지 않는다. 구 번호 HTML인 `pages/06_database_design.html`은 기존 리다이렉트 정책만 확인한다.
- PDF 문구는 Markdown 원본의 의미를 따르며, 표 폭·페이지 나눔 같은 출력 형식 문제만 `scripts/markdown_to_tex.py` 또는 TeX 생성 규칙에서 다룬다.

## 작업 체크리스트

### 1. 원본 동기화 확인

- [x] `rg -n "AWS Neptune|Neptune|Graph DB|S3 vector|social_accounts|plan_reactions" docs/04_database_design docs/05_agent_spec docs/06_technical_spec`로 원본 반영 상태를 확인한다.
- [x] `rg -n "그래프 DB 이관|GraphDB|3개 저장소|user_social_accounts|saved_itineraries|user_feedback" docs/04_database_design docs/05_agent_spec docs/06_technical_spec`로 이전 설계 흔적을 확인한다.
- [x] 대표 문서의 변경 이력에 AWS Neptune 반영 항목이 있는지 확인한다.

### 2. HTML 재생성

- [x] `python scripts\generate_pages.py`를 실행한다.
- [x] `pages/04_database_design.html`에 `AWS Neptune 그래프 논리 모델`, `AWS Neptune 물리 설계 기준`, `Graph DB` 표 항목이 렌더링되는지 확인한다.
- [x] `pages/05_agent_spec.html`과 `pages/06_technical_spec.html`에 S3 vector/Neptune 역할 분리가 반영되는지 확인한다.
- [x] `index.html`의 데이터베이스 설계 카드 상태와 링크가 깨지지 않는지 확인한다.

### 3. PDF 재생성

- [x] `scripts\markdown_to_tex.py`로 `docs/04_database_design/04_database_design.md`를 `pdf/database_design.tex`로 변환한다.
- [x] `pdf/` 폴더에서 `xelatex -interaction=nonstopmode -halt-on-error database_design.tex`를 2회 실행한다.
- [x] `pdf/database_design.pdf`가 새로 생성되고 로그가 `Output written on database_design.pdf`로 끝나는지 확인한다.

권장 명령:

```powershell
python scripts\markdown_to_tex.py docs\04_database_design\04_database_design.md pdf\database_design.tex --title "데이터베이스 설계 명세서" --author "이창우, 전승권, 전종혁, 조동휘, 최수아" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 데이터베이스 설계" --section-pagebreak --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"
Push-Location pdf
xelatex -interaction=nonstopmode -halt-on-error database_design.tex
xelatex -interaction=nonstopmode -halt-on-error database_design.tex
Pop-Location
```

### 4. PDF 품질 검증

- [x] `Select-String -Path pdf\database_design.log -Pattern 'Overfull \\hbox'`로 새 overfull 경고를 확인한다.
- [x] 필요 시 `pdftotext -layout pdf\database_design.pdf pdf\database_design.txt`를 실행한다.
- [x] 추출 텍스트에서 `AWS Neptune`, `Graph DB`, `City`, `Festival`, `Theme`, `Place`, `S3 vector`가 누락 없이 확인되는지 검사한다.
- [x] Mermaid ERD와 Neptune 표가 PDF 폭 안에서 잘리는 경우 Markdown을 고치지 않고 변환 스크립트의 코드 블록/표 폭 규칙을 조정한다.

### 5. 최종 diff 검증

- [x] `python scripts\verify_pages_structure.py`를 실행한다.
- [x] `git diff --check -- docs/04_database_design docs/05_agent_spec docs/06_technical_spec index.html pages/04_database_design.html pages/05_agent_spec.html pages/06_technical_spec.html pdf/database_design.tex`를 실행한다.
- [x] `git status --short`에서 이번 작업 대상과 기존 무관 PDF 변경을 분리해 확인한다.
- [x] 최종 요약에는 이번 계획으로 변경한 HTML/PDF 파일과 검증 명령 결과를 구분해 적는다.

## 검증 기준

- `pages/04_database_design.html`은 대표 Markdown과 같은 AWS Neptune 내용을 제공한다.
- `pdf/database_design.pdf`에는 AWS Neptune이 그래프 관계 인덱스로 표시된다.
- S3 vector와 Neptune의 역할이 각각 의미 검색과 관계 탐색으로 분리되어 있다.
- MySQL RDB ERD는 기존 5개 테이블 구조를 유지한다.
- 기존 무관 PDF 변경은 이번 반영 범위에 섞지 않는다.

## 리스크와 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| Mermaid ERD가 PDF에서 오른쪽으로 잘림 | PDF 가독성 저하 | Markdown 원본 대신 `scripts/markdown_to_tex.py`의 코드 블록 줄바꿈 규칙 조정 |
| Neptune 표가 longtable 폭을 초과함 | PDF 표 잘림 | 표 폭 규칙과 코드 토큰 `allowbreak` 규칙 확인 |
| HTML 재생성으로 여러 페이지가 함께 변경됨 | diff 범위 확대 | `git diff --name-only`와 `rg`로 실제 내용 변경 페이지를 확인 |
| 기존 data collect PDF 변경과 혼재 | 커밋 범위 오염 | `pdf/database_design.*`만 이번 PDF 반영 대상으로 취급 |

## 완료 조건

- [x] HTML 생성물과 PDF 생성물이 모두 최신 Markdown 내용을 반영한다.
- [x] 구조 검증과 PDF 빌드 검증이 통과한다.
- [x] 변경 범위가 DB 설계/연결 문서/생성물로 설명 가능하다.
