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
- 변환 스크립트: `scripts/markdown_to_tex.py`

## PDF Generation Rule

프로젝트 기획서 PDF는 `docs/00_project_plan/00_project_plan.md`를 참조해 `scripts/markdown_to_tex.py`로 `pdf/project_plan.tex`를 생성한 뒤 `xelatex`로 변환한다. 요구사항 정의서 PDF도 동일하게 Markdown 원본을 TeX로 변환한 뒤 `xelatex`로 변환한다.

본문 의미가 바뀌는 수정은 원본 Markdown과 변환 스크립트에 반영한다. PDF 출력 형식만 맞추는 임시·표현 수정은 `.tex`에 직접 반영할 수 있지만, 이후 재생성하면 덮어써질 수 있으므로 필요한 규칙은 이 파일 또는 변환 스크립트에 남긴다.

프로젝트 기획서 기본 생성 명령은 다음을 사용한다.

```powershell
python scripts\markdown_to_tex.py docs\00_project_plan\00_project_plan.md pdf\project_plan.tex --title "프로젝트 기획서" --author "이창우, 전승권, 전종혁, 조동휘, 최수아" --mentor "멘토: 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스" --section-pagebreak --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"
xelatex -interaction=nonstopmode -halt-on-error -output-directory=pdf pdf\project_plan.tex
```

`.tex` 파일이 이미 `pdf/` 폴더에 있고 PDF만 다시 만들 때는 `pdf` 폴더에서 다음 명령을 실행한다.

```powershell
xelatex -interaction=nonstopmode -halt-on-error project_plan.tex
xelatex -interaction=nonstopmode -halt-on-error project_plan.tex
```

목차, 표 폭, 페이지 번호, longtable 폭이 바뀐 경우에는 `xelatex`를 두 번 실행한다.

## PDF Style Rules

- PDF 폰트는 Windows 기본 문서용 한글 폰트인 `맑은 고딕`을 사용한다.
  - 일반: `C:/Windows/Fonts/malgun.ttf`
  - 굵게: `C:/Windows/Fonts/malgunbd.ttf`
  - 기울임: `C:/Windows/Fonts/malgunsl.ttf`
- 표 헤더는 가운데 정렬한다.
- 표 본문은 긴 설명 열을 왼쪽 정렬하고, 단계·버전·날짜·상태·라벨처럼 짧은 값은 가운데 정렬한다.
- 모든 표는 셀 내용을 세로 가운데 정렬하는 `m{}` 컬럼을 사용한다.
- 표는 가능한 한 페이지 폭을 활용하되, 긴 설명 열에 더 많은 폭을 배정한다.
- 목차는 2단계 깊이까지만 표시한다.
- 큰 섹션은 `--section-pagebreak` 기준으로 새 페이지에서 시작한다.
- CI는 `assets/images/`의 SK Networks, en-core, PlayData 로고를 표지와 헤더에 함께 배치한다.
- PDF 색상은 로브 서비스 CI 색상을 사용한다.
  - `LovvGreen`: `#1B3B32`
  - `LovvGreenDark`: `#10251F`
  - `LovvGold`: `#D4AF37`
  - `LovvPaper`: `#F7F3EA`

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
- `14. 변경 이력`: `버전`, `날짜`, `작성자`는 가운데 정렬, `변경 내용`은 넓게 배치한다.

특정 셀의 줄바꿈이 필요한 경우 Markdown 원본을 깨지 말고 PDF 변환 단계의 `forced_line_breaks` 규칙으로 처리한다.

## Verification Checklist

- `xelatex` 실행 결과가 `Output written on ...pdf`로 끝나는지 확인한다.
- 표 폭 조정 후 `Overfull \hbox`가 새로 생기지 않았는지 확인한다. `Underfull \hbox`는 표 셀 줄바꿈 때문에 발생할 수 있으며, 출력이 정상이라면 허용한다.
- 필요하면 `pdftotext -layout`으로 목차 페이지 번호, 표 줄바꿈, 섹션 시작 위치를 확인한다.
- PDF 전용 작업에서는 `git diff --name-only -- docs pages` 결과가 비어 있어야 한다.
