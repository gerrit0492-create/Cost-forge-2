name: Deploy to Render (manual)

on:
  workflow_dispatch:
    inputs:
      deploy:
        description: "Deploy now to Render"
        required: true
        default: "yes"

permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Print how-to
        run: |
          echo "::notice title=Render Deploy::"
          echo "1) Ga naar https://dashboard.render.com/  (log in met GitHub)."
          echo "2) Kies 'New +', 'Blueprint', selecteer je repo 'Cost-forge-2'."
          echo "3) Render leest render.yaml en maakt de service 'cost-forge-2' aan."
          echo "4) Klik 'Deploy'. Na ~1-2 min staat je app live."
          echo ""
          echo "Tip: daarna kun je autodeploy aanzetten in Render -> Settings."

      # Optioneel: check bestanden
      - name: Validate render.yaml exists
        run: test -f render.yaml
