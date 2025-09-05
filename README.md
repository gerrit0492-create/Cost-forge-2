# Cost Forge 2.2 — First-Time-Right
![Smoke Test](https://github.com/gerrit0492-create/Cost-tool-pages/actions/workflows/smoke-test.yml/badge.svg)
Alles om meteen te draaien:
- **Quick Cost** met automatische supplier quotes
- **Scenario Planner**
- **Data Quality**
- **Supplier Quotes** selectie
- **Offerte export** naar **DOCX** en **PDF**
- **Download Center** voor CSV-templates
- **Smoke Test** workflow (lichte CI)

## Snel starten (zonder terminal)
1. Upload alle **uitgepakte** bestanden naar je GitHub repo (Add file → Upload files).
2. Koppel de repo aan Streamlit Cloud en kies `home.py` als start.
3. (Optioneel) Run **Actions → Smoke test pages**.

## Structuur
```
utils/      # io, pricing, quotes, pdf/docx export, validators, safe, compat
pages/      # 01 Quick Cost, 05 Data Quality, 06 Scenario, 07 Quotes, 18 DOCX, 19 PDF, 20 Download Center
data/       # voorbeeld CSV's
tools/      # smoke_test.py
.github/workflows/smoke.yml  # compile-check
home.py
requirements.txt
```
