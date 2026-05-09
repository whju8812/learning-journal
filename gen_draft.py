import json

tech_content = (
    "**Ollama 讓本地 LLM 部署變得像 Docker 一樣簡單**\n\n"
    "Ollama 是 2026 年最受開發者歡迎的本地 LLM 執行工具，核心定位是「AI 界的 Docker」——透過單一指令即可拉取、執行並管理各類量化後的大型語言模型，框架自動處理 GPU 加速與記憶體分配，將以往需要手動設定 CUDA、量化格式與推理環境的高門檻流程簡化為 `ollama run llama3.2` 一行指令。Ollama 在 2026 年特別值得學習的原因有三：雲端 LLM API 成本持續攀升，本地推理成為有效的成本控制手段；企業資料隱私合規需求促使敏感工作流程轉向自架模型；加上 Ollama 已原生支援 MCP（Model Context Protocol），可將本地模型直接與工具、資料庫整合，讓開發者以私有硬體建構完整的 AI Agent 管線。\n\n"
    "**OpenTofu：開源 IaC 工具在 2026 年已全面成熟**\n\n"
    "OpenTofu 是 Linux Foundation 旗下的開源 Infrastructure as Code 工具，誕生於 2023 年 HashiCorp 將 Terraform 授權由 MPL 改為限制性 BSL 之後，由 Gruntwork、Spacelift 等公司主導的社群分支項目。截至 2026 年，OpenTofu 已累積超過 3,900 個 provider 與 23,600 個模組，是 Terraform 1.5.x 的 100% 相容替代方案，並新增了 Terraform 企業版才有的 state 加密與原生測試框架功能。對於已在使用 Terraform 的團隊，遷移成本幾乎為零：只需將指令由 terraform 改為 tofu，現有的 .tf 設定檔、state 檔與模組均可直接沿用，且完全免費開放授權，是 DevOps 團隊擺脫商業授權束縛的最務實路徑。\n\n"
    "**n8n：結合 AI 能力的自架工作流程自動化平台**\n\n"
    "n8n 採用「公平程式碼（Fair-code）」授權，允許開發者在個人或企業環境中自行部署，核心優勢在於將超過 400 個服務整合（GitHub、Slack、資料庫、AWS 等）與可視化流程編輯器結合，讓工程師能快速搭建複雜的自動化管線。2026 年 n8n 最大的競爭力在於深度 AI 節點整合：原生支援 OpenAI、Anthropic、Hugging Face 多個供應商的憑證管理，並可透過 Ollama 節點直接串接本地模型，在單一工作流程中混搭雲端與本地 AI 服務。典型場景如「每日定時分析系統日誌、用 LLM 產生摘要並發送至 Discord」，僅需拖拉三個節點設定即可完成，不需撰寫任何 Python 腳本，是後端工程師高效自動化內部維運工作的最佳入口之一。"
)

tech_application = (
    "**① 5 分鐘用 Ollama 在本機執行 LLaMA 3.2**\n\n"
    "適合任何想在本機測試 LLM、保護資料隱私或降低 API 費用的開發者。Ollama 支援 macOS、Linux 與 Windows，安裝後即可在本機推理，不需任何雲端帳號。\n\n"
    "```bash\n"
    "# macOS 安裝\n"
    "brew install ollama\n\n"
    "# Linux 安裝\n"
    "curl -fsSL https://ollama.com/install.sh | sh\n\n"
    "# 啟動服務（背景執行）\n"
    "ollama serve &\n\n"
    "# 拉取並執行 Llama 3.2（需約 4GB 磁碟，建議 8GB RAM 以上）\n"
    "ollama run llama3.2\n"
    "```\n\n"
    "透過 Python 呼叫本地 API（與 OpenAI SDK 格式相容）：\n\n"
    "```python\n"
    "import requests\n\n"
    "response = requests.post(\n"
    "    \"http://localhost:11434/api/generate\",\n"
    "    json={\n"
    "        \"model\": \"llama3.2\",\n"
    "        \"prompt\": \"請解釋什麼是 Transformer 架構\",\n"
    "        \"stream\": False\n"
    "    }\n"
    ")\n"
    "print(response.json()[\"response\"])\n"
    "```\n\n"
    "服務啟動後監聽 `localhost:11434`，API 格式與 OpenAI 相容，可直接替換現有程式碼的 endpoint。\n\n"
    "**② 從 Terraform 零成本遷移至 OpenTofu**\n\n"
    "適合已在使用 Terraform 管理雲端基礎架構的 DevOps 工程師，現有 .tf 設定檔與 state 檔無需修改即可直接使用。\n\n"
    "```bash\n"
    "# macOS 安裝\n"
    "brew install opentofu\n\n"
    "# Linux 安裝（官方腳本）\n"
    "curl -fsSL https://get.opentofu.org/install-opentofu.sh | bash\n\n"
    "# 在現有 Terraform 專案目錄中，以 tofu 取代 terraform\n"
    "tofu init\n"
    "tofu plan\n"
    "tofu apply\n"
    "```\n\n"
    "OpenTofu 獨有的 state 加密功能（防止 state 檔中的敏感資料以明文儲存）：\n\n"
    "```hcl\n"
    "terraform {\n"
    "  encryption {\n"
    "    key_provider \"pbkdf2\" \"main\" {\n"
    "      passphrase = var.state_passphrase\n"
    "    }\n"
    "    method \"aes_gcm\" \"default\" {\n"
    "      keys = key_provider.pbkdf2.main\n"
    "    }\n"
    "    state {\n"
    "      method = method.aes_gcm.default\n"
    "    }\n"
    "  }\n"
    "}\n"
    "```"
)

learning_analysis = {
    "AI / 機器學習": {
        "summary": "Ollama 讓本地 LLM 推理在 2026 年成為主流開發工具，透過 MCP 整合可建構私有 AI Agent，不依賴雲端 API 即可完成複雜推理任務。",
        "items": [
            "Ollama 原生支援 llama3.2、mistral、phi-3 等主流開源模型，指令格式統一為 ollama run <model>",
            "本地推理搭配 MCP 可讓 AI 存取本地工具（資料庫、檔案系統、API），建構私有 Agent 管線",
            "量化模型（Q4_K_M、Q8_0）讓 4-bit 推理可在消費級 GPU（8GB VRAM）上流暢執行"
        ]
    },
    "雲端與基礎架構": {
        "summary": "OpenTofu 在 2026 年已成為 IaC 領域最成熟的開源選擇，對 Terraform 完全相容且新增 state 加密功能，適合需要合規要求的雲端基礎架構管理。",
        "items": [
            "OpenTofu 是 Terraform 的 drop-in 替換，只需將 terraform 指令改為 tofu 即可完成遷移",
            "state 加密功能防止 .tfstate 中的 API 金鑰、密碼等敏感資訊以明文儲存",
            "3,900 個以上 provider 生態系覆蓋 AWS、GCP、Azure 及所有主流 SaaS 服務"
        ]
    },
    "前端開發": {
        "summary": "前端框架生態在 2026 年持續穩定，Server Components 模式已在 Next.js 與 Nuxt 中成熟，重點在於理解渲染邊界的選擇策略以最佳化效能。",
        "items": [
            "React Server Components（RSC）讓資料抓取邏輯移至伺服器端，減少客戶端 bundle 大小",
            "Islands Architecture（Astro、Fresh）適合內容導向網站，最小化 JavaScript 執行成本",
            "Web Components 標準在框架無關場景（設計系統、微前端）的採用率持續上升"
        ]
    },
    "後端 / 系統設計": {
        "summary": "n8n 代表了一種新型後端工作流程設計模式——以可視化 DAG 取代手寫排程腳本，搭配 AI 節點讓自動化管線具備推理能力，適合快速實踐事件驅動架構。",
        "items": [
            "n8n 的 Workflow 即 DAG（有向無環圖），每個節點是一個整合服務或邏輯運算單元",
            "自架 n8n 搭配 PostgreSQL backend 可在 2-core 4GB VPS 上穩定運行 50 個以上活躍工作流程",
            "n8n 的 Code 節點支援 JavaScript 與 Python，可在工作流程中嵌入自訂邏輯而不失彈性"
        ]
    },
    "開發者工具 / DevOps": {
        "summary": "OpenTofu 與 n8n 共同代表了 2026 年開源開發者工具的成熟化趨勢：以社群維護取代商業授權，以可視化介面降低上手門檻，同時保持高度可自訂性。",
        "items": [
            "OpenTofu 在 Linux Foundation 旗下持續開發，社群活躍度已超過原版 Terraform",
            "n8n 自架版完全免費，每個工作流程可設定 webhook、cron 排程或訊息佇列觸發",
            "兩者皆支援 GitOps 工作流程：設定版本化後，變更可透過 PR 加 CI 審核流程套用"
        ]
    }
}

sources = [
    {"title": "Run Your Own AI Model Locally: A Practical Ollama Setup Guide (2026)", "url": "https://dev.to/primghostdev/run-your-own-ai-model-locally-a-practical-ollama-setup-guide-2026-2kk9"},
    {"title": "Ollama + MCP: Connect Local AI to Your Tools (Complete 2026 Guide)", "url": "https://localaimaster.com/blog/ollama-mcp-integration"},
    {"title": "What is OpenTofu? The Open-Source Terraform Fork Explained (2026)", "url": "https://scalr.com/learning-center/what-is-opentofu/"},
    {"title": "OpenTofu and Terraform IaC Best Practices in 2026", "url": "https://devstarsj.github.io/2026/02/26/opentofu-terraform-iac-best-practices-2026/"},
    {"title": "How to Self-Host n8n with Docker — AI Workflow Automation Guide 2026", "url": "https://dev.to/jangwook_kim_e31e7291ad98/how-to-self-host-n8n-with-docker-ai-workflow-automation-guide-2026-3lec"},
    {"title": "Self-Hosted AI in 2026: Automating Your Linux Workflow with n8n and Ollama", "url": "https://dev.to/lyraalishaikh/self-hosted-ai-in-2026-automating-your-linux-workflow-with-n8n-and-ollama-4934"}
]

entry = {
    "entry_date": "2026-05-09",
    "session_label": "20:00",
    "tech_content": tech_content,
    "tech_application": tech_application,
    "learning_analysis": learning_analysis,
    "sources": sources
}

output = json.dumps(entry, ensure_ascii=False, separators=(',', ':'))

# Verify no single quotes
assert "'" not in output, "ERROR: single quote found in JSON output!"

with open("draft.json", "w", encoding="utf-8") as f:
    f.write(output)

print("draft.json written successfully")
print(f"Length: {len(output)} chars")
