#!/usr/bin/env python3
import json

tech_content = (
    "**Cloudflare Workflows v2：為 AI Agent 時代重新設計工作流引擎**\n\n"
    "Cloudflare 在 Agents Week 2026 發布了 Workflows v2，核心動機是一個量變引發質變的趨勢：workflow 的觸發者正從人類（每小時數次）轉為 AI Agent（每秒數百次）。"
    "原本以單一 Durable Object 作為帳號級中央 registry 的 V1 架構，在機器速度的觸發壓力下出現嚴重瓶頸。"
    "V2 引入兩個新的水平擴展元件，支援量提升至 50,000 concurrent instances 與 200 萬 queued instances，底層建立在 SQLite-backed Durable Objects 之上，並以 zero-downtime 方式完成線上遷移。"
    "對後端工程師而言，這次升級最值得學習的是：如何在不中斷服務的前提下，從垂直擴展的中央化架構遷移至水平擴展的分散式架構，以因應 agentic workload 的機器速度需求。\n\n"
    "**Gemma 4：可在本機執行的開源多模態 LLM**\n\n"
    "Google DeepMind 於 2026 年 4 月 2 日發布 Gemma 4，採 Apache 2.0 授權，是目前消費級硬體可執行的最強開源模型之一。"
    "模型有 E2B、E4B、26B-A4B、31B 四個變體，其中 E4B 以 4-bit 量化僅需約 5GB RAM 即可在筆電本機運行，透過 Ollama 一行指令完成部署。"
    "Gemma 4 支援文字、圖片、影片、音訊多模態輸入，140 種以上語言，以及最高 256K context window，並內建可設定的 thinking 模式。"
    "對開發者而言最大的實用意義在於：可在不依賴付費雲端 API 的情況下，於本機進行 AI 功能開發與敏感資料處理實驗，顯著降低原型開發的成本與隱私風險。\n\n"
    "**GitHub Actions 4 月更新：OIDC 細粒度信任策略與 Service Container 彈性設定**\n\n"
    "GitHub 於 2026 年 4 月初推出兩項 Actions 實用改進。"
    "第一，Service Container 現支援 entrypoint 與 command override，語法與 Docker Compose 相容，讓 CI pipeline 使用自訂映像作為服務容器時更有彈性。"
    "第二，Actions OIDC token 正式 GA 支援 repository custom properties 作為 claims，"
    "開發者可在 AWS、GCP 的 IAM trust policy 中以 repository 自訂屬性（如 environment=production）建立屬性導向存取控制，"
    "不再需要為每個 repo 個別管理 IAM role，大幅降低多 repo 環境下的 CI/CD 安全管理複雜度。"
)

tech_application = (
    "**① 用 Ollama 在本機執行 Gemma 4**\n\n"
    "適合想要在本機開發 AI 功能、測試 prompt engineering、或因資料隱私需求不適合傳送至雲端的開發者。"
    "E4B 版本以 4-bit 量化僅需 5GB RAM，一般開發筆電即可運行，完全免費且無 API 呼叫限制。\n\n"
    "```bash\n"
    "# 安裝 Ollama（Linux/macOS）\n"
    "curl -fsSL https://ollama.ai/install.sh | sh\n\n"
    "# 下載 Gemma 4 E4B 並啟動互動對話\n"
    "ollama run gemma4:e4b\n"
    "```\n\n"
    "```python\n"
    "# 透過 OpenAI 相容 API 在 Python 中呼叫本地模型\n"
    "import openai\n"
    "client = openai.OpenAI(base_url=\"http://localhost:11434/v1\", api_key=\"ollama\")\n"
    "resp = client.chat.completions.create(\n"
    "    model=\"gemma4:e4b\",\n"
    "    messages=[{\"role\": \"user\", \"content\": \"解釋 zero-downtime 遷移的設計模式\"}]\n"
    ")\n"
    "print(resp.choices[0].message.content)\n"
    "```\n\n"
    "**② GitHub Actions OIDC 結合 Repository Custom Properties 實現細粒度 AWS 存取**\n\n"
    "適合維護多個 repository 且需要對 dev/staging/production 環境設定不同 AWS 權限的團隊。"
    "在 AWS IAM trust policy 中加入 repository 屬性條件，取代逐 repo 的 IAM role 一對一綁定。\n\n"
    "```yaml\n"
    "# .github/workflows/deploy.yml\n"
    "permissions:\n"
    "  id-token: write\n"
    "  contents: read\n\n"
    "jobs:\n"
    "  deploy:\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - name: Configure AWS credentials via OIDC\n"
    "        uses: aws-actions/configure-aws-credentials@v4\n"
    "        with:\n"
    "          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole\n"
    "          aws-region: ap-northeast-1\n"
    "# AWS IAM trust policy 條件範例：\n"
    "# token.actions.githubusercontent.com:repository_custom_properties.environment = production\n"
    "```"
)

learning_analysis = {
    "AI / 機器學習": {
        "summary": "Gemma 4 的發布標誌著開源本地端 LLM 進入多模態與長 context 的新階段，Apache 2.0 授權使其成為商業應用的可行選項，開發者可免費在本機建立完整 AI 開發環境。",
        "items": [
            "Gemma 4 具備 E2B/E4B/26B/31B 四種規模，E4B 以 4-bit 量化僅需 5GB RAM 本機執行",
            "支援文字、圖片、影片、音訊多模態輸入，256K context window，內建 thinking 推理模式",
            "透過 Ollama 部署後提供 OpenAI 相容 REST API，可無縫替換付費雲端 API 呼叫",
            "Apache 2.0 授權允許商業使用與微調，適合需要資料隱私的企業內部 AI 應用開發"
        ]
    },
    "雲端與基礎架構": {
        "summary": "Cloudflare Workflows v2 的架構演進展示了雲端基礎設施如何從人機互動規模升級至 machine-speed agentic 規模，zero-downtime 線上遷移策略值得後端工程師深入研究。",
        "items": [
            "V1 單一 Durable Object 中央 registry 架構在 agent 機器速度觸發下成為效能瓶頸",
            "V2 以兩個新水平擴展元件解決，支援 50,000 concurrent 與 200 萬 queued instances",
            "底層使用 SQLite-backed Durable Objects，以漸進式狀態遷移實現 zero-downtime 升級",
            "架構啟示：為 agentic workload 設計時，需以機器速度（每秒數百次）而非人類速度規劃容量"
        ]
    },
    "前端開發": {
        "summary": "2026 年前端技術棧已高度標準化，Next.js/Nuxt 成為元框架入口，TypeScript 是專業開發基線，AI coding assistant 正在重塑前端開發工作流，建議鞏固 TypeScript 泛型與條件型別實際應用。",
        "items": [
            "Next.js 與 Nuxt 整合 routing、data fetching、caching 與 server functions，成為全端開發標準入口",
            "TypeScript 已是 2026 年前端專業開發基線，純 JavaScript 新專案被視為 legacy",
            "Playwright 已成瀏覽器端對端測試主流選擇，auto-wait 機制大幅降低 flaky test 比例",
            "AI coding assistant 現可處理新創公司 30-40% 的生產程式碼，改變前端開發工作節奏"
        ]
    },
    "後端 / 系統設計": {
        "summary": "Temporal 工作流程協調框架持續是複雜業務流程的可靠選擇，其 Workflow/Activity 分層設計解決分散式系統的重試與故障恢復問題，可與 Cloudflare Workflows 形成互補的技術選型。",
        "items": [
            "Temporal 以 Workflow（協調）與 Activity（執行）分層，解決分散式系統重試、等待與崩潰恢復",
            "事件驅動架構將長時間任務（AI 推理、圖片處理）卸載至 background worker，提升主 API 吞吐量",
            "Temporal Python SDK 支援 cancellation 處理、child workflow、continue-as-new 等生產級模式",
            "選型參考：Temporal 適合複雜有狀態業務流程；Cloudflare Workflows 適合 serverless 輕量任務"
        ]
    },
    "開發者工具 / DevOps": {
        "summary": "GitHub Actions 4 月更新帶來 Service Container override 與 OIDC custom properties GA，直接提升多 repo 環境下的 CI/CD 靈活性與安全性，配合屬性導向存取控制可簡化雲端權限管理。",
        "items": [
            "Service Container 支援 entrypoint 與 command override，語法與 Docker Compose 相容，即可使用",
            "OIDC token 支援 repository custom properties 作為 claims（GA），實現 attribute-based cloud 存取控制",
            "可在 AWS IAM trust policy 中設定 environment=production 等條件，取代逐 repo 的 IAM role 管理",
            "注意：2026 年 4 月 24 日起 Copilot Free/Pro 互動資料預設用於模型訓練，可至帳號設定頁面退出"
        ]
    }
}

sources = [
    {"title": "Rearchitecting the Workflows control plane for the agentic era - Cloudflare Blog", "url": "https://blog.cloudflare.com/workflows-v2/"},
    {"title": "Gemma 4 - Google DeepMind", "url": "https://deepmind.google/models/gemma/gemma-4/"},
    {"title": "How to Run Gemma 4 Locally with Ollama - MindStudio", "url": "https://www.mindstudio.ai/blog/how-to-run-gemma-4-locally-ollama"},
    {"title": "GitHub Actions: Early April 2026 updates - GitHub Changelog", "url": "https://github.blog/changelog/2026-04-02-github-actions-early-april-2026-updates/"},
    {"title": "Actions OIDC tokens now support repository custom properties - GitHub Changelog", "url": "https://github.blog/changelog/2026-03-12-actions-oidc-tokens-now-support-repository-custom-properties/"},
    {"title": "Developers Guide to Running LLMs Locally: Ollama, Gemma 4 - DEV Community", "url": "https://dev.to/kennedyraju55/the-developers-guide-to-running-llms-locally-ollama-gemma-4-and-why-your-side-projects-dont-54oe"}
]

entry = {
    "entry_date": "2026-04-24",
    "session_label": "20:00",
    "tech_content": tech_content,
    "tech_application": tech_application,
    "learning_analysis": learning_analysis,
    "sources": sources
}

# 輸出單行 JSON（ensure_ascii=False 保留 UTF-8）
output = json.dumps(entry, ensure_ascii=False, separators=(",", ":"))

# 確認無單引號
assert "'" not in output, "ERROR: JSON contains single quote!"

with open("draft.json", "w", encoding="utf-8") as f:
    f.write(output)

print("draft.json written successfully")
print(f"Length: {len(output)} chars")
print(f"Contains single quote: {chr(39) in output}")
