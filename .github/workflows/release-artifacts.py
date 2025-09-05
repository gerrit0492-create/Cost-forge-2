name: Release offer artifacts

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  build-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Build artifacts (docx/pdf)
        run: |
          mkdir -p artifacts
          python - <<'PY'
          from utils.io import load_materials, load_processes, load_bom, load_quotes
          from utils.quotes import apply_best_quotes
          from utils.pricing import compute_costs
          from utils.docx_export import make_offer_docx
          from utils.pdf_export import make_offer_pdf
          mats = load_materials(); procs = load_processes(); bom = load_bom(); quotes = load_quotes()
          df = compute_costs(apply_best_quotes(mats, quotes), procs, bom)
          open("artifacts/offerte.docx","wb").write(make_offer_docx(df))
          open("artifacts/offerte.pdf","wb").write(make_offer_pdf(df))
          PY

      - name: Zip artifacts
        run: |
          cd artifacts && zip -r ../offer-artifacts.zip . && cd ..

      - name: Create GitHub Release (tag latest)
        uses: softprops/action-gh-release@v2
        with:
          tag_name: latest
          name: Automated Offer Artifacts
          prerelease: true
          files: |
            offer-artifacts.zip
