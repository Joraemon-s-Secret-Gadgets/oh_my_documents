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
