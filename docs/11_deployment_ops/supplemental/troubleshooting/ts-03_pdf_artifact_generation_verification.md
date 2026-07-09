# TS-03 PDF 산출물 생성·검증

> 문서 성격: 트러블슈팅 하위 Markdown
> 상위 문서: `../troubleshooting.md`

> 문서 버전: v0.2
> 문서 상태: 초안 (Draft)
> 작성일: 2026-07-09
> 작성자: llm팀
> 문서 목적: `TS-03` 이슈의 문제, 원인, 판단, 조치, 재발 방지 기준을 본 문서에서 분리해 상세 관리한다.

---


## 1. 증상

새 결과보고서 Markdown을 추가했지만 PDF/TeX 산출물 또는 `pdf/AGENT.md` 목록이 함께 갱신되지 않으면 배포용 문서와 원본 문서가 어긋난다.

## 2. 조치

새 PDF 문서를 추가할 때는 다음을 함께 갱신한다.

| 항목 | 경로 예시 |
| --- | --- |
| 원본 Markdown | `docs/08_data_preprocessing/supplemental/korea_data_preprocessing_result_report.md` |
| TeX 산출물 | `pdf/korea_data_preprocessing_result_report.tex` |
| PDF 산출물 | `pdf/korea_data_preprocessing_result_report.pdf` |
| 산출물 목록 | `pdf/AGENT.md` |

PDF는 다음처럼 2회 빌드한다.

```powershell
cd pdf
xelatex -interaction=nonstopmode -halt-on-error korea_data_preprocessing_result_report.tex
xelatex -interaction=nonstopmode -halt-on-error korea_data_preprocessing_result_report.tex
```

## 3. 재발 방지

- 목차와 outline 경고가 있으면 2회 빌드한다.
- `pdf/*.aux`, `pdf/*.log`, `pdf/*.out`, `pdf/*.toc`는 중간 산출물이므로 커밋하지 않는다.
- PDF 본문 의미가 바뀌면 먼저 대응 Markdown을 수정한다.

## 4. 출처 및 근거

| 출처 | 확인 내용 | TS-03 반영 |
| --- | --- | --- |
| [LaTeX2e reference - Command line options](https://latexref.xyz/Command-line-options.html) | `nonstopmode`는 오류가 발생해도 가능한 범위에서 처리를 계속하며, `halt-on-error`는 첫 오류에서 중단하도록 하는 실행 옵션이다. | 자동 빌드에서는 `-interaction=nonstopmode -halt-on-error` 조합을 사용해 로그를 남기되 실패를 명확히 중단한다. |
| [TeX Live Guide](https://www.tug.org/texlive/portable.html) | TeX Live 실행과 오류 처리 옵션은 로그 파일과 명령행 실행 결과로 확인할 수 있다. | PDF 생성 실패 시 `.log`를 확인하고, 성공 산출물만 목록에 반영한다. |
| [pdf/AGENT.md](../../../../pdf/AGENT.md) | `pdf/` 디렉터리의 관리 대상 산출물 목록과 생성물 관리 기준을 제공한다. | 새 PDF/TeX 산출물을 추가할 때 `pdf/AGENT.md` 목록을 함께 갱신한다. |
| [korea_data_preprocessing_result_report.md](../../../08_data_preprocessing/supplemental/korea_data_preprocessing_result_report.md) | PDF로 변환되는 원본 Markdown 결과보고서다. | PDF 본문 의미 변경은 먼저 원본 Markdown에서 수행하고, 이후 TeX/PDF 산출물을 갱신한다. |

## 5. 변경 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v0.2 | 2026-07-09 | llm팀 | XeLaTeX 실행 옵션, TeX Live 오류 처리, 로컬 PDF 산출물 관리 기준 근거 추가 |
| v0.1 | 2026-07-09 | llm팀 | PDF 산출물 생성·검증 이슈 초안 작성 |
