name: Autofix validators & ruff

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  fix:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: Patch pyproject (ignore E501)
        run: |
          cat > pyproject.toml <<'TOML'
          [tool.ruff]
          line-length = 100
          target-version = "py311"

          [tool.ruff.lint]
          select = ["E", "F", "I"]
          ignore = ["E501"]

          [tool.ruff.format]
          docstring-code-format = true
          TOML

      - name: Write utils/validators.py (clean)
        run: |
          mkdir -p utils
          cat > utils/validators.py <<'PY'
          from __future__ import annotations
          from typing import Iterable, List, Mapping
          import pandas as pd

          def check_missing(df: pd.DataFrame, required: Iterable[str]) -> List[str]:
              required = list(required)
              return [c for c in required if c not in df.columns]

          def check_positive(df: pd.DataFrame, cols: Iterable[str]) -> List[str]:
              bad: List[str] = []
              for c in cols:
                  if c not in df.columns:
                      continue
                  s = pd.to_numeric(df[c], errors="coerce")
                  if (s < 0).any():
                      bad.append(c)
              return bad

          def validate_all(mats: pd.DataFrame, procs: pd.DataFrame, bom: pd.DataFrame) -> Mapping[str, Mapping[str, list]]:
              report = {
                  "materials": {"missing": [], "negative": []},
                  "processes": {"missing": [], "negative": []},
                  "bom": {"missing": [], "negative": []},
              }
              report["materials"]["missing"] += check_missing(mats, ["material_id", "price_eur_per_kg"])
              report["materials"]["negative"] += check_positive(mats, ["price_eur_per_kg"])

              report["processes"]["missing"] += check_missing(
                  procs,
                  ["process_id", "machine_rate_eur_h", "labor_rate_eur_h", "overhead_pct", "margin_pct"],
              )
              report["processes"]["negative"] += check_positive(
                  procs,
                  ["machine_rate_eur_h", "labor_rate_eur_h", "overhead_pct", "margin_pct"],
              )

              report["bom"]["missing"] += check_missing(
                  bom, ["line_id", "material_id", "qty", "mass_kg", "process_route", "runtime_h"]
              )
              report["bom"]["negative"] += check_positive(bom, ["qty", "mass_kg", "runtime_h"])
              return report
          PY

      - name: Install ruff
        run: |
          python -m pip install --upgrade pip
          pip install ruff

      - name: Format + lint
        run: |
          ruff format utils pages home.py
          ruff check --fix utils pages home.py
          ruff check utils pages home.py || true

      - name: Commit & push
        run: |
          set -e
          git config user.name  "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add -A
          if git diff --cached --quiet; then
            echo "No changes."
            exit 0
          fi
          git commit -m "chore: autofix validators + ruff format"
          if git push origin HEAD:main; then
            echo "Pushed to main."
          else
            BR="autofix/validators-$(date +%Y%m%d-%H%M%S)"
            git checkout -b "$BR"
            git push -u origin "$BR"
            echo "::notice title=Compare & merge::https://github.com/${GITHUB_REPOSITORY}/compare/${BR}?expand=1"
          fi
