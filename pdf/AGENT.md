# Agent Instructions for PDF Generation

이 폴더의 역할은 `docs/` 아래 Markdown 원본 문서를 참조해 PDF 산출물을 생성하고 관리하는 것이다. PDF 내용의 기준은 항상 `docs/`의 Markdown이며, `pdf/` 안의 `.tex`와 `.pdf`는 생성물로 취급한다.

PDF 문구를 바꿔야 할 때는 먼저 대응하는 `docs/` Markdown 원본을 수정한다. 단, 사용자가 MD/HTML을 건드리지 말라고 명시했거나 페이지 나눔, 표 폭, 헤더/푸터, 폰트, CI 로고, PDF 전용 상세 설명처럼 출력 형식에만 해당하는 변경을 요청한 경우에는 `pdf/` 안의 `.tex`와 `.pdf`만 수정한다.

`pdf/` 작업 중에는 사용자가 명시하지 않은 `docs/`와 `pages/` 변경을 만들지 않는다. PDF 전용 편집 후에는 `git diff --name-only -- docs pages`로 MD/HTML이 변경되지 않았는지 확인한다.

## Source and Outputs

- 프로젝트 기획서 원본: `docs/00_project_plan/00_project_plan.md`
- 프로젝트 기획서 TeX: `pdf/project_plan.tex`
- 프로젝트 기획서 PDF: `pdf/project_plan.pdf`
- 요구사항 정의서 원본: `docs/01_requirements/01_requirements.md`
- 요구사항 정의서 TeX: `pdf/requirements_definition.tex`
- 요구사항 정의서 PDF: `pdf/requirements_definition.pdf`
- 기능·비기능 요구사항 보조 원본: `pdf/requirements_functional_nonfunctional.md`
- 기능·비기능 요구사항 보조 TeX: `pdf/requirements_functional_nonfunctional.tex`
- 기능·비기능 요구사항 보조 PDF: `pdf/requirements_functional_nonfunctional.pdf`
- 데이터 수집 계획서 원본: `docs/03_data_collect_plan/03_data_collect_plan.md`
- 데이터 수집 계획서 TeX: `pdf/data_collect_plan.tex`
- 데이터 수집 계획서 PDF: `pdf/data_collect_plan.pdf`
- 한국 데이터 취득 계획서 원본: `docs/03_data_collect_plan/korea_data_acquisition_plan.md`
- 한국 데이터 취득 계획서 TeX: `pdf/korea_data_acquisition_plan.tex`
- 한국 데이터 취득 계획서 PDF: `pdf/korea_data_acquisition_plan.pdf`
- 일본 데이터 취득 계획서 원본: `docs/03_data_collect_plan/japan_data_acquisition_plan.md`
- 일본 데이터 취득 계획서 TeX: `pdf/japan_data_acquisition_plan.tex`
- 일본 데이터 취득 계획서 PDF: `pdf/japan_data_acquisition_plan.pdf`
- 데이터 전처리 계획서 원본: `docs/08_data_preprocessing/data_preprocessing_plan.md`
- 데이터 전처리 계획서 TeX: `pdf/data_preprocessing_plan.tex`
- 데이터 전처리 계획서 PDF: `pdf/data_preprocessing_plan.pdf`
- 전처리 예산 추정 원본: `docs/08_data_preprocessing/preprocessing_budget_estimate.md`
- 전처리 예산 추정 TeX: `pdf/preprocessing_budget_estimate.tex`
- 전처리 예산 추정 PDF: `pdf/preprocessing_budget_estimate.pdf`
- 한국 데이터 전처리 결과보고서 원본: `docs/08_data_preprocessing/korea_data_preprocessing_result_report.md`
- 한국 데이터 전처리 결과보고서 TeX: `pdf/korea_data_preprocessing_result_report.tex`
- 한국 데이터 전처리 결과보고서 PDF: `pdf/korea_data_preprocessing_result_report.pdf`
- 데이터베이스 설계서 원본: `docs/04_database_design/04_database_design.md`
- 데이터베이스 설계서 TeX: `pdf/database_design.tex`
- 데이터베이스 설계서 PDF: `pdf/database_design.pdf`
- 변환 스크립트: `scripts/markdown_to_tex.py`

## PDF Generation Rule

PDF는 대응하는 Markdown 원본을 참조해 `scripts/markdown_to_tex.py`로 `.tex`를 생성한 뒤 `xelatex`로 변환한다. 프로젝트 기획서와 요구사항 정의서뿐 아니라 데이터 수집, 데이터 전처리, 데이터베이스 설계 PDF도 같은 흐름을 따른다.

본문 의미가 바뀌는 수정은 원본 Markdown과 변환 스크립트에 반영한다. PDF 출력 형식만 맞추는 임시·표현 수정은 `.tex`에 직접 반영할 수 있지만, 이후 재생성하면 덮어써질 수 있으므로 필요한 규칙은 이 파일 또는 변환 스크립트에 남긴다.

사용자가 특정 PDF만 고치라고 한 경우에도 변경 성격을 먼저 구분한다.

- 문장 의미, 범위, 요구사항, 설계 결정, 수치, 일정, 담당자, 상태가 바뀌면 `docs/` 원본을 우선 수정하고 필요한 HTML/PDF 산출물을 동기화한다.
- 페이지 넘김, 표 폭, 코드 블록 줄바꿈, 표지 밀도, 로고 위치, 폰트, 색상 적용, PDF-only 풀어쓰기처럼 출력 가독성만 바뀌면 `pdf/`와 `scripts/markdown_to_tex.py` 범위에서 처리한다.
- PDF-only 변경 후에는 `git diff --name-only -- docs pages`가 비어 있는지 확인해 원본/HTML을 의도치 않게 건드리지 않았음을 검증한다.

프로젝트 기획서 기본 생성 명령은 다음을 사용한다.

```powershell
python scripts\markdown_to_tex.py docs\00_project_plan\00_project_plan.md pdf\project_plan.tex --title "프로젝트 기획서" --author "이창우, 전승권, 전종혁, 조동휘, 최수아" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스" --section-pagebreak --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"
xelatex -interaction=nonstopmode -halt-on-error -output-directory=pdf pdf\project_plan.tex
```

`.tex` 파일이 이미 `pdf/` 폴더에 있고 PDF만 다시 만들 때는 `pdf` 폴더에서 다음 명령을 실행한다.

```powershell
xelatex -interaction=nonstopmode -halt-on-error project_plan.tex
xelatex -interaction=nonstopmode -halt-on-error project_plan.tex
```

목차, 표 폭, 페이지 번호, longtable 폭이 바뀐 경우에는 `xelatex`를 두 번 실행한다.

## Frequently Used PDF Workflows

PDF 작업에서 반복적으로 사용하는 기본 기능은 다음과 같다.

- Markdown 원본을 `scripts/markdown_to_tex.py`로 TeX 산출물로 변환한다.
- TeX 파일은 `xelatex -interaction=nonstopmode -halt-on-error`로 2회 빌드한다.
- 빌드 후 `.log`에서 `Overfull \hbox`, `Missing character`, `! LaTeX Error`를 확인한다.
- 필요하면 `pdftotext -layout`으로 목차, 페이지 번호, 표 줄바꿈, 섹션 시작 위치를 확인한다.
- 최종 PDF는 이미지 또는 contact sheet로 렌더링해 제목, 설명, 표, 차트, 코드 블록이 잘리지 않았는지 확인한다.
- PDF-only 작업에서는 `git diff --name-only -- docs pages` 결과가 비어 있어야 한다.
- 반복 적용할 레이아웃 보정은 개별 `.tex`보다 `scripts/markdown_to_tex.py`에 반영한다.

## PDF Style Rules

- PDF 폰트는 Windows 기본 문서용 한글 폰트인 `맑은 고딕`을 사용한다.
  - 일반: `C:/Windows/Fonts/malgun.ttf`
  - 굵게: `C:/Windows/Fonts/malgunbd.ttf`
  - 기울임: `C:/Windows/Fonts/malgunsl.ttf`
- 표 헤더는 가운데 정렬한다.
- 표 본문은 긴 설명 열을 왼쪽 정렬하고, 단계·버전·날짜·상태·라벨처럼 짧은 값은 가운데 정렬한다.
- 모든 표는 셀 내용을 세로 가운데 정렬하는 `m{}` 컬럼을 사용한다.
- 표는 가능한 한 페이지 폭을 활용하되, 긴 설명 열에 더 많은 폭을 배정한다.
- 표는 본문 폭을 끝까지 채우지 않고 좌우 여백이 남도록 생성한다. `scripts/markdown_to_tex.py`의 `table_target_width`는 열 수에 따라 약 0.83~0.94 `\linewidth` 범위를 사용하고, longtable은 `\LTleft=\fill`, `\LTright=\fill`로 가운데 정렬한다.
- 목차는 2단계 깊이까지만 표시한다.
- 큰 섹션은 `--section-pagebreak` 기준으로 새 페이지에서 시작한다.
- CI는 `assets/images/`의 SK Networks, en-core, PlayData 로고를 표지와 헤더에 함께 배치한다.
- PDF 색상은 저장소 루트의 `color-map.md`를 기준으로 사용한다.
  - 제목과 본문 기본 텍스트는 `Dark Charcoal`을 우선 사용한다.
  - 표지 구분선, 핵심 강조, 주요 포인트에는 `Main Orange`를 사용한다.
  - 배경 또는 옅은 강조 영역이 필요하면 `Soft Beige`와 `Card Peach`를 사용한다.
  - 보조 설명, 캡션, 상태 문구에는 `Sub Text Gray`를 사용한다.
  - 색상 HEX 값을 직접 새로 정의하지 말고, 먼저 `color-map.md`의 색상명을 확인한다.
  - 색상 기준을 바꿔야 할 경우 PDF 파일만 고치지 말고 `color-map.md` 기준 변경 여부를 사용자에게 확인한다.

## PDF Cover Page Rules

새 PDF 문서를 만들거나 기존 PDF 표지를 수정할 때는 `pdf/project_plan.tex`와 `pdf/requirements_definition.tex`의 표지 형식을 기준으로 한다.

- 표지 상단에는 SK Networks, en-core, PlayData 로고 3개를 같은 줄에 배치한다.
- 로고 아래에는 `color-map.md`의 `Main Orange` 색상 가로 구분선을 넣는다.
- 표지 중앙에는 문서 제목을 크게 표시한다.
  - 예: `프로젝트 기획서`, `요구사항 명세서`, `일본 데이터 취득 계획서`
- 제목 아래에는 문서 적용 범위 또는 서비스 라벨을 한 줄로 표시한다.
  - 예: `로브 서비스`, `로브 서비스 전체`, `로브 서비스 데이터 수집 계획`
- 표지에 인터넷 템플릿, 참조 양식, 참고 양식 같은 출처성 문구를 넣지 않는다. 참조 출처가 필요하면 본문 참고 출처 섹션에만 둔다.
- 표지 하단에는 팀명을 먼저 표시한다.
  - 팀명: `조라에몽의 만능 도구들`
- 팀명 아래에는 팀원 이름을 한 줄에 표시한다.
  - 팀원: `이창우, 전승권, 전종혁, 조동휘, 최수아`
- 멘토는 팀원과 구분해 다음 줄에 `멘토 최민수`로 표시한다.
  - `최민수`만 단독 표기하거나 `멘토:`처럼 다른 표기법을 섞지 않는다.
- 표지 날짜는 문서 작성일 또는 사용자가 지정한 기준일을 사용한다. PDF 양식만 수정한 경우에도 기존 문서 날짜와 충돌하지 않도록 필요하면 개정일을 문서 관리표에 별도 표기한다.
- 표지 구성은 불필요한 부제, 버전 라벨, 초안 설명을 과하게 넣지 않고 기존 PDF들과 같은 밀도와 여백을 유지한다.
- 표지 변경 후에는 PDF를 다시 빌드하고, 목차가 영향을 받는 경우 `xelatex`를 두 번 실행한다.

## PDF Document Format Rules

PDF 문서 양식은 기존 `project_plan`, `requirements_definition`, `data_collect_plan`, `database_design` PDF의 공통 구성을 기준으로 맞춘다.

- 문서 기본 순서는 표지, 목차, 본문, 변경 이력 순서를 우선한다.
- 표지는 로고 영역, 문서 제목, 서비스 라벨, 팀 정보, 작성일을 한 화면 안에서 균형 있게 배치한다.
- 목차는 본문 시작 전에 배치하고, 2단계 제목까지만 표시해 과도하게 길어지지 않게 한다.
- 본문 큰 섹션은 문서 흐름을 해치지 않는 범위에서 새 페이지 시작을 우선한다.
- 문서 상단 메타데이터 또는 문서 정보 표를 둘 경우 문서명, 기준 문서, 작성자, 상태, 버전, 작성일을 같은 양식으로 유지한다.
- 변경 이력 표는 문서 마지막에 두고 최신 버전이 위에 오도록 정렬한다.
- 변경 이력의 `버전`, `날짜`, `작성자`는 가운데 정렬하고, `변경 내용`은 가장 넓은 설명 열로 배치한다.
- 표 제목과 표 본문은 가능한 한 같은 페이지에서 시작한다. 제목만 페이지 하단에 남으면 `\DocNeedspace{...}` 또는 섹션 pagebreak 규칙을 조정한다.
- 표와 설명 문단이 이어지는 경우 설명 일부만 앞 페이지에 남지 않도록 이미지 검토 후 필요하면 TeX 변환 규칙을 조정한다.
- PDF 양식만 바꾸는 작업은 문서 의미 변경이 아니므로, 사용자가 별도 지시하지 않는 한 Markdown 원본의 문장과 표 구조를 바꾸지 않는다.

## Current Project Plan Page Break Rules

`pdf/project_plan.tex`는 PDF 가독성을 위해 다음 제목이 새 페이지에서 시작하도록 관리한다.

- `2.2 시장·운영 문제`
- `3. 프로젝트 목표`
- `4. 서비스 개념`
- `4.2 사용자 흐름`
- `5. 주요 사용자 및 이해관계자`
- `6. 프로젝트 범위`
- `7. 기능 구성`
- `8. 데이터 및 외부 연동`
- `9. 기술 방향`
- `10. 추진 일정`
- `11. 기대 효과`
- `12. 리스크 및 대응`
- `13. 후속 문서`
- `14. 변경 이력`

페이지 넘김 요청은 본문 의미 변경이 아니므로 사용자가 별도 지시하지 않는 한 `pdf/project_plan.tex`와 `pdf/project_plan.pdf`만 수정한다.

## PDF-Only Content Rules

아래 항목은 Markdown 원본의 표 구조를 유지하되, PDF에서는 가독성을 위해 풀어서 작성한다.

- `2.1 사용자 문제`
- `2.2 시장·운영 문제`

PDF-only로 풀어쓴 내용은 `scripts/markdown_to_tex.py`의 변환 로직에서 관리한다. 사용자가 Markdown 원본 수정도 요청하지 않은 경우, PDF 전용 설명 때문에 `00_project_plan.md`의 표를 풀어쓰지 않는다.

## Current Table Layout Rules

`scripts/markdown_to_tex.py` 또는 PDF 전용 TeX에는 다음 표별 폭 조정 규칙을 유지한다.

- `3.2 성공 기준`: `구분`은 좁게, `성공 기준`은 넓게 배치한다.
- `4.2 사용자 흐름`: `단계`는 좁고 가운데 정렬, `시스템 처리`는 가장 넓게 배치한다.
- `5. 주요 사용자 및 이해관계자`: `구분`과 `역할`은 줄이고 `주요 니즈`를 넓힌다.
- `6.1 PoC 범위`: `기능 범위`를 가장 넓게 두고, `우선순위`, `PoC`, `Production`, `상태`는 가운데 정렬한다.
- `7.2 추천 기능`: `기능`은 좁고 가운데 정렬, `설명`은 넓게 배치한다.
- `8.1 필요 데이터`, `8.2 외부 연동`, `13. 후속 문서`: 첫 열은 좁고 가운데 정렬, 설명 열은 넓게 배치한다.
- `10. 추진 일정`: `단계`와 `기간`은 가운데 정렬, `주요 산출물`은 넓게 배치한다.
- `12. 리스크 및 대응`: `리스크`는 가운데 정렬, `영향`과 `대응`은 설명 폭을 확보한다.
- `14. 변경 이력`: 최신 버전이 위에 오도록 최신순으로 정렬한다. `버전`, `날짜`, `작성자`는 가운데 정렬하고, `변경 내용`은 넓게 배치한다.

특정 셀의 줄바꿈이 필요한 경우 Markdown 원본을 깨지 말고 PDF 변환 단계의 `forced_line_breaks` 규칙으로 처리한다.

## PDF Table Harness Rules

표가 페이지 오른쪽에서 잘리거나 셀 내부 텍스트가 밖으로 밀려나는 문제는 Markdown 원본을 수정해서 해결하지 않는다. 먼저 `scripts/markdown_to_tex.py`의 표 변환 규칙을 조정한 뒤 TeX와 PDF를 재생성한다.

- 4열 이상 표는 PDF 변환 단계에서 `footnotesize`를 사용해 폭을 확보한다.
- 코드형 토큰, JSON 필드명, 상태값처럼 공백이 없는 긴 문자열은 `_`, `-`, `/`, `.`, `:` 위치에 `\allowbreak{}`를 넣어 줄바꿈 가능하게 유지한다.
- `province_or_prefecture`, `district_type`, `needs_review`, `Processed`처럼 셀을 넘칠 수 있는 값은 Markdown에 임의 `<br>`를 넣지 말고 변환 스크립트의 토큰 줄바꿈 규칙으로 처리한다.
- 15행 이하의 작은 표는 한 페이지에 들어갈 수 있으면 분리하지 않는다. `scripts/markdown_to_tex.py`의 `table_to_latex`에서 행 수 기반 `\DocNeedspace{...}`를 먼저 계산해 공간이 부족하면 표 전체를 다음 페이지에서 시작하게 한다.
- 표 직전 소제목이 페이지 하단에 단독으로 남지 않도록 `scripts/markdown_to_tex.py`의 2단계 제목 변환은 `\DocNeedspace{24\baselineskip}`를 사용한다. 이 값은 제목, 짧은 설명 문단, 뒤따르는 표 시작부가 함께 보일 수 있도록 조정한 기준이다.
- PDF를 생성한 뒤에는 PDF 페이지를 이미지로 렌더링해 제목, 설명 문단, 표가 서로 다른 페이지로 어색하게 분리되지 않았는지 확인한다. 제목만 페이지 하단에 남거나, 제목과 표가 분리되거나, 표 첫 행만 다음 페이지로 밀리면 Markdown 원본이 아니라 `\DocNeedspace{...}`, 표 행 수 기준, longtable 배치 규칙을 조정한 뒤 PDF를 다시 생성한다.
- 평문 설명 문단은 PDF 변환 단계에서 마침표 뒤 공백을 `\newline`으로 변환해 긴 문단이 한 줄로 붙어 보이지 않게 한다. 표, 목록, 코드 블록은 별도 규칙을 우선한다.
- 특정 표에서만 줄바꿈이 필요하면 `table_to_latex(..., forced_line_breaks=...)` 또는 해당 호출부의 `forced_line_breaks` 딕셔너리를 사용한다.
- 표 폭 변경 뒤에는 대상 PDF의 `.log`에서 `Overfull \hbox`가 남아 있는지 확인한다. `Underfull \hbox`는 표 셀 줄바꿈 과정에서 발생할 수 있으므로 실제 출력이 정상이라면 허용한다.
- 현재 PDF 전체를 재생성할 때는 모든 `.pdf`를 이미지로 렌더링한 뒤 페이지 썸네일 contact sheet로 확인한다. 표가 좌우 페이지 끝에 붙거나 한쪽으로 치우치면 Markdown 원본 대신 변환 스크립트의 표 목표 폭과 longtable 좌우 정렬을 먼저 조정한다.

데이터 수집 계획 PDF 묶음의 기본 검증 하네스는 다음 순서로 실행한다.

```powershell
python scripts\markdown_to_tex.py docs\03_data_collect_plan\03_data_collect_plan.md pdf\data_collect_plan.tex --title "데이터 수집 계획서" --author "이창우, 전승권, 전종혁, 조동휘, 최수아" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 데이터 수집 계획" --section-pagebreak --body-pagebreak-before "2.3 City 수집 항목" "2.4 Attraction 수집 항목" "2.6 데이터 출처" "2.6.2 일본 데이터 출처" --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"
Push-Location pdf
xelatex -interaction=nonstopmode -halt-on-error data_collect_plan.tex
xelatex -interaction=nonstopmode -halt-on-error data_collect_plan.tex
Select-String -Path data_collect_plan.log -Pattern 'Overfull \\hbox'
Pop-Location
```

## PDF Chart Harness Rules

Markdown의 `mermaid`, `text`, `json`, `sql` 등 코드 펜스는 PDF에서 차트·구조도·예시 블록으로 취급한다. PDF에서 차트 또는 코드 블록이 오른쪽으로 잘리는 경우 Markdown 원본에 임의 줄바꿈을 넣지 말고 `scripts/markdown_to_tex.py`의 코드 블록 변환 규칙을 먼저 조정한다.

- 코드 펜스는 `verbatim`으로 직접 출력하지 않는다. `verbatim`은 긴 행을 자동 줄바꿈하지 않아 PDF 오른쪽에서 잘릴 수 있다.
- `scripts/markdown_to_tex.py`의 `code_block_to_latex`가 코드 펜스를 `scriptsize`, `ttfamily`, `RaggedRight` 블록으로 변환하고, `-`, `/`, `.`, `:`, `|`, `>` 같은 차트 연결 문자에서 줄바꿈 가능하게 처리한다.
- `data_collect_plan`의 `3.1 처리 흐름`은 ASCII 흐름도를 그대로 출력하지 않고 `acquisition_pipeline_flow_to_latex` 단계 표로 변환한다. Markdown 원본의 의미를 유지하되 PDF에서는 순서, 단계, 처리 내용이 한눈에 보이도록 한다.
- 문서 예시용 JSON 객체는 PDF에서 코드 블록으로 유지하지 않고 Markdown 원본에서 `필드 / 예시 값 / 비고` 형식의 표로 변환한다. 중첩 객체는 `field_status.period`, `climate_table.caption`처럼 점 표기법으로 평탄화한다.
- ASCII 트리, Mermaid 텍스트, S3 Prefix 예시, JSON/SQL 샘플은 PDF 폭 안에 들어가도록 변환 단계에서 축소·줄바꿈한다.
- 차트 의미가 바뀌지 않는 출력 형식 조정은 Markdown이 아니라 변환 스크립트 또는 PDF 전용 TeX에서 처리한다.
- 이미지로 렌더링한 차트를 PDF에 넣는 경우에는 `\includegraphics[width=\linewidth,height=0.72\textheight,keepaspectratio]{...}`처럼 가로·세로 상한을 모두 지정한다.
- 차트 폭 변경 뒤에는 대상 PDF의 `.log`에서 `Overfull \hbox`를 검색하고, 필요하면 `pdftotext -layout`으로 차트 블록이 본문 폭 안에서 줄바꿈되는지 확인한다.

차트/코드 블록 잘림 검증 하네스는 다음 명령을 사용한다.

```powershell
Push-Location pdf
Select-String -Path *.log -Pattern 'Overfull \\hbox'
pdftotext -layout data_preprocessing_plan.pdf data_preprocessing_plan.txt
Select-String -Path data_preprocessing_plan.txt -Pattern 'S3 Raw Bucket','AWS Lambda Preprocessor','DynamoDB Normalized Tables'
Pop-Location
```

## Verification Checklist

- `xelatex` 실행 결과가 `Output written on ...pdf`로 끝나는지 확인한다.
- 표 폭 조정 후 `Overfull \hbox`가 새로 생기지 않았는지 확인한다. `Underfull \hbox`는 표 셀 줄바꿈 때문에 발생할 수 있으며, 출력이 정상이라면 허용한다.
- 15행 이하 표가 페이지 경계에서 분리되면 `table_to_latex`의 `table_needspace` 계산을 조정한 뒤 PDF를 재생성한다.
- 표 직전 제목과 설명만 페이지 하단에 남으면 2단계 제목의 `\DocNeedspace{24\baselineskip}` 기준을 조정한 뒤 PDF를 재생성한다.
- 차트·코드 블록 폭 조정 후에도 `Overfull \hbox`가 남아 있지 않은지 확인한다.
- 필요하면 `pdftotext -layout`으로 목차 페이지 번호, 표 줄바꿈, 섹션 시작 위치를 확인한다.
- PDF 묶음을 갱신할 때는 각 PDF 첫 페이지와 표가 많은 페이지를 이미지 또는 contact sheet로 확인한다. 특히 제목, 설명 문단, 표가 페이지 경계에서 분리되지 않았는지 확인하고, 분리되면 변환 스크립트의 페이지 구성 규칙을 조정해 다시 생성한다.
- 새 PDF를 추가하면 `Source and Outputs` 목록, `.gitignore`의 LaTeX 중간 산출물 규칙, 관련 생성 명령이 함께 맞는지 확인한다.
- PDF 전용 작업에서는 `git diff --name-only -- docs pages` 결과가 비어 있어야 한다.
