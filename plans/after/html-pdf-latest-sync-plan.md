---
작성자: Codex
상태: 진행후
---

# HTML/PDF 최신화 실행 계획

## 목적

`docs/` Markdown 원본을 기준으로 공유용 HTML과 PDF 산출물을 최신 상태로 동기화한다.

HTML과 PDF는 생성물이므로 직접 의미를 수정하지 않고, 원본 Markdown 변경 사항이 반영된 결과인지 검증한다.

## 대상 범위

| 구분 | 대상 |
| --- | --- |
| 원본 문서 | `docs/04_data_collect_plan/04_data_collect_plan.md`, `docs/04_data_collect_plan/korea_data_acquisition_plan.md`, `docs/04_data_collect_plan/japan_data_acquisition_plan.md`, `docs/04_data_collect_plan/data_preprocessing_plan.md` |
| HTML 산출물 | `pages/04_data_collect_plan.html`, `index.html` |
| PDF 산출물 | `pdf/data_collect_plan.tex`, `pdf/data_collect_plan.pdf`, `pdf/korea_data_acquisition_plan.tex`, `pdf/korea_data_acquisition_plan.pdf`, `pdf/japan_data_acquisition_plan.tex`, `pdf/japan_data_acquisition_plan.pdf`, `pdf/data_preprocessing_plan.tex`, `pdf/data_preprocessing_plan.pdf` |
| 검증 기준 | `AGENT.md`, `docs/04_data_collect_plan/AGENT.md`, `pdf/AGENT.md`, `plans/AGENT.md` |

## 제외 범위

- `docs/06_database_design/**`
- `pages/06_database_design.html`
- `scripts/generate_pages.py`의 DB 설계 상태 문구 변경
- 데이터 취득 문서와 무관한 기존 untracked plan 파일

위 항목은 현재 작업 트리에 남아 있더라도 HTML/PDF 최신화 계획의 커밋 또는 검증 범위에 포함하지 않는다.

## 작업 체크리스트

- [x] 현재 작업 트리에서 데이터 취득 문서 변경과 unrelated 변경을 분리한다.
- [x] `docs/04_data_collect_plan` 원본 Markdown의 버전, 상태, 핵심 용어가 최신인지 확인한다.
- [x] `python scripts\generate_pages.py`로 `pages/04_data_collect_plan.html`과 `index.html`을 재생성한다.
- [x] HTML에서 `VisitorStatistics`, `data/JP/*.json`, `관동 지역 지자체`, `data/KR/*.json`이 원본 문서와 같은 의미로 노출되는지 확인한다.
- [x] `scripts\markdown_to_tex.py`로 데이터 취득 관련 TeX 4종을 재생성한다.
- [x] `xelatex`를 각 TeX 파일에 2회 실행해 PDF 4종을 재생성한다.
- [x] PDF 로그에서 `Overfull \hbox`가 없는지 확인한다.
- [x] PDF 전체 페이지를 이미지로 렌더링하고 contact sheet로 표, 차트, 코드 블록, 흐름도 잘림 여부를 확인한다.
- [x] `git diff --check`를 실행한다.
- [x] `git status --short`로 데이터 취득 HTML/PDF 최신화 대상 파일만 후속 커밋 범위에 포함되는지 확인한다.

## 실행 명령

### HTML 재생성

```powershell
python scripts\generate_pages.py
```

### PDF TeX 재생성

```powershell
python scripts\markdown_to_tex.py docs\04_data_collect_plan\04_data_collect_plan.md pdf\data_collect_plan.tex --title "데이터 수집 계획서" --author "LLM 파트" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 데이터 수집 계획" --section-pagebreak --body-pagebreak-before "2.3 City 수집 항목" "2.4 Attraction 수집 항목" "2.6 데이터 출처" "2.6.2 일본 데이터 출처" --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"

python scripts\markdown_to_tex.py docs\04_data_collect_plan\korea_data_acquisition_plan.md pdf\korea_data_acquisition_plan.tex --title "한국 데이터 취득 계획서" --author "LLM 파트" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 데이터 수집 계획" --section-pagebreak --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"

python scripts\markdown_to_tex.py docs\04_data_collect_plan\japan_data_acquisition_plan.md pdf\japan_data_acquisition_plan.tex --title "일본 데이터 취득 계획서" --author "LLM 파트" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 데이터 수집 계획" --section-pagebreak --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"

python scripts\markdown_to_tex.py docs\04_data_collect_plan\data_preprocessing_plan.md pdf\data_preprocessing_plan.tex --title "데이터 전처리 계획서" --author "LLM 파트" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 데이터 수집 계획" --section-pagebreak --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"
```

### PDF 빌드

```powershell
Push-Location pdf
$files = @(
  "data_collect_plan.tex",
  "korea_data_acquisition_plan.tex",
  "japan_data_acquisition_plan.tex",
  "data_preprocessing_plan.tex"
)

foreach ($file in $files) {
  xelatex -interaction=nonstopmode -halt-on-error $file
  xelatex -interaction=nonstopmode -halt-on-error $file
}

Select-String -Path data_collect_plan.log,korea_data_acquisition_plan.log,japan_data_acquisition_plan.log,data_preprocessing_plan.log -Pattern 'Overfull \\hbox'
Pop-Location
```

## 검증 기준

### HTML 수용 기준

- [ ] `pages/04_data_collect_plan.html`의 문서 버전과 본문이 `04_data_collect_plan.md`와 일치한다.
- [ ] `index.html`의 데이터 수집 계획서 카드가 최신 버전과 상태를 표시한다.
- [ ] 내부 링크와 이전/다음 문서 링크가 상대 경로로 유지된다.
- [ ] 데이터 취득 원본에 없는 의미가 HTML에 새로 생기지 않는다.

### PDF 수용 기준

- [x] PDF 4종이 모두 새 TeX 기준으로 생성된다.
- [x] 표가 좌우 폭을 벗어나지 않는다.
- [x] 표 제목, 설명 문단, 표 본문이 페이지 경계에서 부자연스럽게 끊기지 않는다.
- [x] `text`, `json`, `mermaid` 성격의 코드 블록과 처리 흐름도가 페이지 오른쪽에서 잘리지 않는다.
- [x] `Overfull \hbox`가 남아 있지 않다.

### Git 수용 기준

- [x] `git diff --check`가 통과한다.
- [x] 데이터 취득 HTML/PDF 최신화 대상과 DB 설계 관련 기존 변경이 분리되어 있다.
- [x] 후속 커밋 요청 시 데이터 취득 문서, HTML, PDF, 이 계획 파일만 스테이징한다.

## 리스크와 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| HTML 생성 스크립트가 모든 페이지를 함께 갱신 | unrelated 페이지가 작업 범위에 섞일 수 있음 | `git diff --name-only`로 `pages/04_data_collect_plan.html`, `index.html` 외 변경을 분리한다. |
| PDF 변환 중 표 폭이 다시 넓어짐 | PDF 표 또는 코드 블록 잘림 | `pdf/AGENT.md` 기준으로 Markdown이 아니라 변환 스크립트 또는 TeX 출력 규칙을 조정한다. |
| MiKTeX 사용자 로그 디렉터리 경고 | 로그 쓰기 경고가 출력될 수 있음 | PDF 생성 성공 여부와 각 `.log` 파일의 Overfull 여부를 우선 확인한다. |
| 기존 DB 설계 변경과 혼재 | 커밋 범위 오염 | `docs/06_database_design/**`, `pages/06_database_design.html`, 관련 plan 파일은 제외한다. |

## 체크포인트

### Checkpoint 1: HTML 최신화 후

- [x] `pages/04_data_collect_plan.html`에 최신 핵심 용어가 반영되어 있다.
- [x] `index.html`의 카드 상태와 링크가 정상이다.

### Checkpoint 2: PDF 재생성 후

- [x] PDF 4종 생성이 완료됐다.
- [x] `Overfull \hbox`가 없다.
- [x] contact sheet에서 표와 흐름도 잘림이 없다.

### Checkpoint 3: 후속 커밋 전

- [x] 변경 파일 목록이 데이터 취득 HTML/PDF 최신화 범위로 제한되어 있다.
- [x] unrelated DB 설계 변경은 스테이징하지 않는다.

## 실행 결과

- `pages/04_data_collect_plan.html`과 `index.html`을 재생성하고 `v0.6`, `VisitorStatistics`, `data/JP/*.json`, `관동 지역 지자체`, `data/KR/*.json` 반영을 확인했다.
- 데이터 취득 관련 TeX 4종과 PDF 4종을 재생성했다.
- PDF 로그에서 `Overfull \hbox`가 없음을 확인했다.
- PDF 4종을 이미지로 렌더링하고 contact sheet로 표, 차트, 코드 블록, 흐름도 잘림이 없음을 확인했다.
- `git diff --check`는 공백 오류 없이 통과했으며 CRLF 경고만 출력됐다.
- 후속 커밋 범위는 데이터 취득 문서, `index.html`, `pages/04_data_collect_plan.html`, 관련 PDF/TeX, 이 계획 파일로 분리했다.
- 기존 DB 설계 변경, CSS 변경, DB 시각검증 산출물, 기타 plan 파일은 unrelated 항목으로 유지했다.
