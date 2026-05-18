# 專案啟動文件：OmniHeal

## 1. 專案概述 (Project Overview)

**OmniHeal** 是一個通用的「資訊與技術債治理框架」，底層由強大的 **DebtWatcher Engine** 驅動。

本專案旨在解決各類型專案中，因時間推移、快速迭代或龐大資料堆積所產生的「架構腐化、格式混亂、上下文流失」等問題。透過極致發揮本地大型語言模型（Local LLM）「隱私安全、零 Token 成本、無限上下文推演」的非對稱優勢，OmniHeal 能在無人值守的夜間，以系統化、File-by-file 的方式，對堆積如山且無人願碰的龐雜資料進行宏觀到微觀的徹底淨化與重構。

## 2. 核心理念 (Core Philosophy)

* **Domain Agnostic (領域無關)：** 萬物皆文本。無論是 `.py` 程式碼、`.log` 系統日誌、還是 `.md` 逐字稿，引擎統一將其視為待處理的資訊區塊。
* **Zero to One 憲法發掘 (Constitution Bootstrap)：** 解決冷啟動障礙。工具能自動探測目標工作區現狀，逆向工程產出「領域憲法 (Domain Constitution)」，並透過簡潔的互動與人類對齊標準。
* **Macro guides Micro (宏觀引導微觀)：** 所有的單檔處理與檢查，皆受「領域憲法」約束，確保模型在處理海量微觀細節時，大腦始終維持全局架構觀。
* **Local-First & Cost-Free (本地優先)：** 專為無網路環境與高隱私要求的本地算力（如 Ollama, llama.cpp）打造，徹底解放 Token 焦慮，實現真正的「算力換取整潔」。

## 3. 核心應用場景 (Core Use Cases)

1. **程式碼庫重構 (Codebase Refactoring)：** 統一新舊系統的命名慣例、設計模式，盤點潛在 Bug 與過度複雜的函式。
2. **開源情報與數位鑑識梳理 (OSINT & Forensics Logging)：** 面對龐雜、格式不一的數位足跡或側錄日誌，依照憲法（如：時間序、實體關聯、特定網域追蹤）進行徹夜掃描，將碎片化線索轉化為結構化情報摘要。
3. **知識庫與語音轉文字除錯 (Knowledge Base & STT Correction)：** 大量檢閱會議紀錄或影片腳本，修正 AI 轉錄時產生的荒謬錯誤，確保大型多 Agent 知識平台（如內容產製引擎）的用詞一致性與專業度。

## 4. 系統架構與流程 (Architecture & Workflow)

系統分為兩大核心階段（Phases）：

### Phase 0: 初始化與概念對齊 (Bootstrap & Alignment)

此階段負責建立或更新 `domain_constitution.md`，確立淨化基準。

1. **通用探路模組 (Universal Context Probe)：** 自動掃描目標目錄的檔案類型分佈、目錄結構與現存說明文件，產出現狀輪廓。
2. **逆向工程模組 (Reverse Engineering)：** 隨機抽樣 5-10 個目標檔案，分析現有的格式特徵、常見錯誤或寫作風格，產出《現狀觀察報告》。
3. **互動對齊 (Human-in-the-Loop)：** 透過終端機問答（選擇題/是非題），向使用者確認治理底線，最終生成並鎖定領域憲法。

### Phase 1: 徹夜巡查模式 (Nightly Scan - DebtWatcher Engine)

此階段執行無人值守的全域掃描與修復。

1. **異質走訪器 (Agnostic File Walker)：** 遞迴走訪指定目錄，過濾不需處理的二進位檔，讀取純文本區塊。
2. **動態 Prompt 組裝器 (Prompt Builder)：** 將 `[領域憲法摘要] + [特定任務 Skill] + [目標檔案內容]` 動態組合。
3. **本地推理引擎 (Local LLM Engine)：** 介接本地模型 API，支援高併發或佇列處理。
4. **Omni-Report 產生器：** 隔天清晨將各檔案的處理結果統一編譯為結構化 Markdown 報告（包含：修改建議、發現之異常、或直接生成可套用的 Patch）。

## 5. CLI 指令設計 (CLI Design)

專案對外的執行檔名稱為 `omniheal` (可設定縮寫 alias 為 `oh`)。

* `omniheal init [target_dir]`：啟動 Phase 0，進行環境探測並生成領域憲法。
* `omniheal scan [target_dir] --skill [skill_name] --nightly`：啟動 Phase 1，載入指定的 Skill 與憲法，開始徹夜走訪並生成報告。

## 6. 目錄結構規劃 (Directory Structure)

```text
omniheal/
├── bin/
│   └── omniheal             # CLI 入口執行檔
├── skills/                  # 任務技能庫 (Prompts Framework)
│   ├── skill_code_lint.md   # 針對程式碼的健檢 prompt
│   ├── skill_log_parse.md   # 針對雜亂日誌的情報萃取 prompt
│   └── skill_text_align.md  # 針對文本/逐字稿的上下文校對 prompt
├── src/
│   ├── phase0_bootstrap/    # 探測與憲法生成邏輯
│   ├── phase1_scanner/      # 走訪器與 Prompt 組裝邏輯
│   ├── llm_client/          # 封裝對 OpenAI 相容 API (Ollama/LM Studio) 的呼叫
│   └── utils/               # 檔案讀寫、編碼解析等輔助工具
├── templates/
│   └── constitution_base.md # 領域憲法基礎模板
├── pyproject.toml           # 依賴管理 (假設使用 Python)
└── README.md

```

## 7. 給 Coding Agent 的開發指引 (Instructions for AI Agents)

* **技術選型：** 請使用 **Python** 作為主要開發語言。CLI 框架請優先採用 `Typer` 或 `Click` 以確保終端機互動體驗優良。
* **LLM 介接：** 實作端必須以 OpenAI API 格式為主，預設 Endpoint 應指向本地（如 `http://localhost:11434/v1` 供 Ollama 使用），確保開箱即用且無 API 費用。請使用 `litellm` 或官方 `openai` 套件來封裝呼叫。
* **容錯與穩定性 (Critical)：** 作為「徹夜運行」的工具，最高指導原則是 **「永不中斷」**。無論模型產生幻覺、回傳格式破裂、或遭遇無法讀取的亂碼檔案，走訪器必須具備嚴格的 `try-catch` 機制，記錄 Error Log 後強制推進到下一個檔案。
* **開發里程碑 (MileStones)：**
1. 建立基礎目錄結構與 `pyproject.toml`。
2. 實作 `src/llm_client` 並完成與本地 Ollama 模型的連線測試。
3. 實作 `omniheal init` 的雛形（Universal Context Probe），能正確讀取目標目錄結構並化簡輸出。
4. 實作 `omniheal scan` 的雛形，完成 Phase 1 單一檔案的 Prompt 組合與結果輸出測試。



