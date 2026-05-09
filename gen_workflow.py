import json

json_payload = open("draft.json", encoding="utf-8").read().strip()

# Double-check: no single quotes allowed (would break printf '%s' '...')
assert "'" not in json_payload, "ERROR: single quote found in JSON payload!"

workflow = f"""name: Write Journal Entry (2026-05-09 20:00)

on:
  push:
    paths:
      - '.github/workflows/write-journal-entry-20260509-2000.yml'
  workflow_dispatch:

jobs:
  write-entry:
    runs-on: ubuntu-latest
    steps:
      - name: Write entry JSON
        run: |
          printf '%s' '{json_payload}' > entry.json

      - name: Post entry to journal API
        env:
          JOURNAL_API_KEY: ${{{{ secrets.JOURNAL_API_KEY }}}}
        run: |
          RESPONSE=$(curl -s -w "\\n%{{http_code}}" -X POST \\
            https://learning-journal.mariposa-lw.xyz/api/entries \\
            -H "X-Journal-Key: $JOURNAL_API_KEY" \\
            -H "Content-Type: application/json; charset=utf-8" \\
            -d @entry.json)
          HTTP_CODE=$(echo "$RESPONSE" | tail -1)
          BODY=$(echo "$RESPONSE" | head -1)
          echo "HTTP Status: $HTTP_CODE"
          echo "Response: $BODY"
          if [ "$HTTP_CODE" = "201" ]; then
            echo "SUCCESS: Entry written."
          elif [ "$HTTP_CODE" = "409" ]; then
            echo "SKIP: Entry already exists."
          else
            echo "ERROR: Unexpected status $HTTP_CODE"
            exit 1
          fi
"""

outpath = ".github/workflows/write-journal-entry-20260509-2000.yml"
with open(outpath, "w", encoding="utf-8") as f:
    f.write(workflow)

print(f"Written: {outpath}")
