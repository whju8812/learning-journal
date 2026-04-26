import json

json_payload = open('/home/user/learning-journal/draft.json').read().strip()

curl_line = '          RESPONSE=$(curl -s -w "\\n%{http_code}" -X POST \\'
url_line  = '            https://learning-journal.mariposa-lw.xyz/api/entries \\'
hdr1_line = '            -H "X-Journal-Key: $JOURNAL_API_KEY" \\'
hdr2_line = '            -H "Content-Type: application/json; charset=utf-8" \\'
data_line = '            -d @entry.json)'

lines = [
    "name: Write Journal Entry (2026-04-26 20:00)",
    "",
    "on:",
    "  push:",
    "    paths:",
    "      - '.github/workflows/write-journal-entry-20260426-2000.yml'",
    "  workflow_dispatch:",
    "",
    "jobs:",
    "  write-entry:",
    "    runs-on: ubuntu-latest",
    "    steps:",
    "      - name: Write entry JSON",
    "        run: |",
    "          printf '%s' '" + json_payload + "' > entry.json",
    "",
    "      - name: Post entry to journal API",
    "        env:",
    "          JOURNAL_API_KEY: ${{ secrets.JOURNAL_API_KEY }}",
    "        run: |",
    curl_line,
    url_line,
    hdr1_line,
    hdr2_line,
    data_line,
    '          HTTP_CODE=$(echo "$RESPONSE" | tail -1)',
    '          BODY=$(echo "$RESPONSE" | head -1)',
    '          echo "HTTP Status: $HTTP_CODE"',
    '          echo "Response: $BODY"',
    '          if [ "$HTTP_CODE" = "201" ]; then',
    '            echo "SUCCESS: Entry written."',
    '          elif [ "$HTTP_CODE" = "409" ]; then',
    '            echo "SKIP: Entry already exists."',
    "          else",
    '            echo "ERROR: Unexpected status $HTTP_CODE"',
    "            exit 1",
    "          fi",
]

content = "\n".join(lines) + "\n"

with open('/home/user/learning-journal/.github/workflows/write-journal-entry-20260426-2000.yml', 'w', encoding='utf-8') as f:
    f.write(content)

print("Workflow file written successfully.")
