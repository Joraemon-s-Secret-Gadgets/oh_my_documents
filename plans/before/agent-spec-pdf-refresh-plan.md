---
작성자: Codex
상태: 진행전
작성일: 2026-06-07
---

# Agent 명세서 PDF 최신화 계획

## 목적

최신화된 `docs/05_agent_spec/05_agent_spec.md`를 기준으로 공유용 PDF 산출물을 생성한다.
PDF는 Markdown 원본의 의미를 바꾸지 않고, `scripts/markdown_to_tex.py`와 `xelatex`로 `pdf/agent_spec.tex`, `pdf/agent_spec.pdf`를 만드는 생성물로 관리한다.

## 대상 파일

| 구분 | 경로 | 역할 |
| --- | --- | --- |
| 원본 Markdown | `docs/05_agent_spec/05_agent_spec.md` | PDF 내용의 source of truth |
| 보조 원본 | `docs/05_agent_spec/langgraph_flow.md`, `agent_harness_design.md` | 정본과 충돌 여부 확인용 |
| TeX 생성물 | `pdf/agent_spec.tex` | Markdown에서 변환된 PDF 중간 산출물 |
| PDF 산출물 | `pdf/agent_spec.pdf` | 최종 공유 파일 |
| 변환 스크립트 | `scripts/markdown_to_tex.py` | Markdown → TeX 변환 |
| PDF 지침 | `pdf/AGENT.md` | 표지, 표 폭, 코드 블록, 검증 규칙 |

## 작업 체크리스트

- [ ] `docs/05_agent_spec/05_agent_spec.md`의 문서 버전, 상태, 변경 이력이 최신인지 확인한다.
- [ ] Mermaid와 Python 코드 블록이 PDF 폭 안에서 줄바꿈될 수 있는지 `pdf/AGENT.md`의 차트/코드 블록 규칙을 확인한다.
- [ ] `scripts/markdown_to_tex.py`로 `pdf/agent_spec.tex`를 생성한다.
- [ ] `pdf/` 폴더에서 `xelatex`를 2회 실행해 목차와 페이지 번호를 안정화한다.
- [ ] `Select-String -Path pdf\agent_spec.log -Pattern 'Overfull \\hbox'`로 오른쪽 잘림을 확인한다.
- [ ] 필요 시 `pdftotext -layout pdf\agent_spec.pdf pdf\agent_spec.txt`로 제목, 표, 코드 블록이 누락 없이 출력되는지 확인한다.
- [ ] PDF 전용 레이아웃 문제가 있으면 Markdown 원본을 임의 줄바꿈하지 않고 변환 스크립트 또는 TeX 규칙으로 해결한다.
- [ ] `git diff --name-only -- docs pages`로 PDF 전용 작업 중 의도하지 않은 Markdown/HTML 변경이 없는지 확인한다.

## 생성 명령 초안

```powershell
python scripts\markdown_to_tex.py docs\05_agent_spec\05_agent_spec.md pdf\agent_spec.tex --title "Agent 명세서" --author "이창우, 전승권, 전종혁, 조동휘, 최수아" --mentor "멘토 최민수" --team "조라에몽의 만능 도구들" --service-label "로브 서비스 Agent 명세" --section-pagebreak --ci-images "../assets/images/SK-Networks-logo.png" "../assets/images/en-core-logo.png" "../assets/images/playdata-logo.png"
Push-Location pdf
xelatex -interaction=nonstopmode -halt-on-error agent_spec.tex
xelatex -interaction=nonstopmode -halt-on-error agent_spec.tex
Select-String -Path agent_spec.log -Pattern 'Overfull \\hbox'
Pop-Location
```

## 검증 기준

| 검증 | 기준 |
| --- | --- |
| 빌드 | `agent_spec.pdf`가 생성되고 `xelatex` 출력이 `Output written on ...pdf`로 끝난다. |
| 목차 | 2단계 깊이 목차가 생성되고 주요 장 번호가 누락되지 않는다. |
| 표 | 장표의 오른쪽 잘림이 없고 긴 필드명은 줄바꿈된다. |
| 코드/차트 | Mermaid, Python 상태 스키마, JSON 예시가 본문 폭 안에서 줄바꿈된다. |
| 내용 정합성 | PDF의 문서 버전이 `05_agent_spec.md`와 일치한다. |

## 리스크 및 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| Mermaid 다이어그램이 PDF 폭을 초과 | 오른쪽 잘림 또는 읽기 어려움 | Markdown을 바꾸지 않고 변환 스크립트의 코드 블록 줄바꿈 규칙을 조정 |
| 표의 긴 필드명이 줄바꿈되지 않음 | 표 폭 초과 | `_`, `-`, `.`, `:` 토큰 줄바꿈 규칙 확인 |
| PDF 전용 수정이 Markdown과 충돌 | 원본/산출물 불일치 | 의미 변경은 반드시 `docs/05_agent_spec/05_agent_spec.md`에 먼저 반영 |
| 번호 재정렬 후 링크가 오래된 경로를 참조 | PDF 내 경로 혼선 | `rg -n "07_agent_spec|05_technical_spec|06_api_spec" docs/05_agent_spec pdf/agent_spec.tex`로 확인 |
