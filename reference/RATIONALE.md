# OmniHeal 研究決策紀錄 (Research Rationale)

記錄每次參考研究的來源、評估結果、與導入決策。

---

## 2026-05-18 — planning-with-files

**來源**：https://github.com/OthmanAdi/planning-with-files  
**研究目的**：評估其「以檔案做為 Agent 記憶體」的設計模式對 OmniHeal 進度管控的參考價值

### 核心發現

planning-with-files 是 Manus（Meta 旗下 AI 公司）內部驗證過的 Agent 記憶體模式，核心概念：
> 把 Agent 的工作狀態永久寫入磁碟上的 .md 檔案，而非依賴 context window。
> Agent 在每次重啟後讀取這些檔案，即可無縫銜接上次進度。

### 採用項目

**1. 3-file 進度結構**  
原設計：`task_plan.md` + `findings.md` + `progress.md`  
OmniHeal 採用（改名符合本專案語境）：
- `progress/scan_plan.md`：當前掃描的目標目錄、使用 Skill、Phase 狀態
- `progress/findings.md`：結構化的分析發現（問題清單、建議、異常）
- `progress/session_log.md`：逐條執行紀錄（取代原 run_log.md）

**2. 5-Question Reboot Test**  
Agent 在掃描中斷重啟後，必須先自問：
1. 我在掃描哪個目錄？（從 scan_plan.md 讀取）
2. 現在跑到哪個 Phase？（scan_plan.md 的 Phase 狀態）
3. 這次的任務目標是什麼？（從 LAUNCH.md 或 scan_plan.md 讀取）
4. 我已經發現了什麼？（findings.md）
5. 我上次做到哪裡？（session_log.md 的最後幾行）
→ 加入 `phases/phase1_scanner.md` 的重啟恢復章節

**3. 3-Strike Protocol**  
單一檔案處理失敗時：
- 第 1 次：記錄錯誤，換方式重試
- 第 2 次：換另一種方式
- 第 3 次：記錄「永久跳過」，繼續下一個檔案
→ 強化 OmniHeal「永不中斷」原則，比原本的 try/except 更有結構

**4. 掃描先讀進度（Session Recovery）**  
LAUNCH.md 必須告訴 Agent：**開始前先讀 `progress/scan_plan.md`**，若有未完成的掃描，優先恢復而非重新開始。
→ 加入 LAUNCH.md 的第一個步驟

**5. 日期隔離目錄（Slug-mode 概念）**  
每次掃描結果存入 `progress/YYYY-MM-DD-<skill>/` 子目錄，避免多次掃描結果混疊。
→ 更新 progress/ 目錄結構規格

### 放棄項目

| 項目 | 放棄原因 |
|------|---------|
| Hook 基礎設施（PreToolUse 自動注入） | OmniHeal 零安裝，不依賴 IDE 插件 |
| SHA-256 attestation | 超出目前範疇 |
| 19 個 IDE 適配檔案 | OmniHeal 是 Agent 指令手冊，非 IDE 插件 |
| ClawHub / marketplace 整合 | 不適用 |
| session-catchup.py（掃 IDE session store）| OmniHeal 用自己的 progress/ 追蹤，不需掃 IDE |

---

## 2026-05-18 — PageIndex + llm-wiki-plugin（並行研究）

**來源 A**：https://github.com/VectifyAI/PageIndex  
**來源 B**：https://github.com/praneybehl/llm-wiki-plugin  
**研究目的**：評估大型內容的索引與知識組織方式，解決 OmniHeal 掃描大型專案時的脈絡管理問題

### 核心發現

**PageIndex 核心概念：**
> 先建立文件的階層式目錄索引（全局結構），Agent 讀取摘要決定哪些部分值得深入，再懶載入（lazy-load）具體內容。
> 兩層取用：Level 1 掃索引（便宜）→ Level 2 取內容（只讀需要的）

**llm-wiki-plugin 核心概念：**
> 把 LLM 的分析結果編譯成 wiki 頁面。每個概念一頁，附 frontmatter 元資料。
> index.md 存所有頁面的一行摘要 → 查詢先看 index，不盲目全讀。
> 新增內容用 surgical append（手術式追加），不重寫整個文件。

### 採用項目

**1. Map-before-dive（掃描前先建索引）**  
來源：PageIndex 的兩層取用模式  
Phase 0 除了建 constitution.md，還要產出 `progress/file_index.md`：
- 每個目標檔案一行：路徑、類型、大小、預估複雜度
- Phase 1 讀此索引決定優先順序，而非盲目逐一掃描

**2. findings 改為 index + per-file 分頁**  
來源：llm-wiki-plugin 的 index-first + 頁面原子化設計  
原本單一 `findings.md` 太大會失控。改為：
- `progress/YYYY-MM-DD-<skill>/findings_index.md`：每個分析過的檔案一行摘要（路徑 + 主要發現 + 嚴重程度）
- `progress/YYYY-MM-DD-<skill>/findings/[filename].md`：只有當該檔案有重大發現時才建立，詳細展開
- 頁面大小上限：findings 單頁軟上限 400 行，超過就拆

**3. Frontmatter per 發現條目**  
來源：llm-wiki-plugin 的 YAML frontmatter 設計  
findings/[filename].md 的開頭加入結構化元資料：
```yaml
---
file: src/legacy/auth.py
type: python
scanned: 2026-05-18
skill: code_lint
severity: high   # high / medium / low / clean
status: new      # new / reviewed / resolved
---
```
讓未來 Agent 可快速過濾「只看 high severity」或「只看 unresolved」

**4. Surgical append（手術式追加）**  
來源：llm-wiki-plugin 的 surgical update 哲學  
session_log.md 和 findings_index.md 只追加，不重寫：
- 使用 `>> file` 或 Agent 讀取後只在尾部加新行
- 若同一檔案被掃描兩次（不同 skill），不覆蓋，加新條目並標注 skill 差異

**5. Scaling 閾值**  
來源：llm-wiki-plugin 的 scaling-playbook  
在 phases/phase1_scanner.md 加入：
- 目標檔案 < 50 個：findings_index.md 單檔即可
- 50–300 個：建 findings/[filename].md 分頁
- > 300 個：findings_index.md 按類型分拆（findings_index_py.md、findings_index_md.md 等）

**6. Operation log 格式標準化**  
來源：llm-wiki-plugin 的 append-only log  
session_log.md 改用機器可解析格式：
```
## [YYYY-MM-DD HH:MM] scan | src/auth.py | severity:high | 發現 3 個問題
## [YYYY-MM-DD HH:MM] skip | src/binary.dat | 原因：非純文字
## [YYYY-MM-DD HH:MM] error | src/legacy.py | 3-Strike 放棄：編碼無法解析
```

### 放棄項目

| 項目 | 放棄原因 |
|------|---------|
| PageIndex JSON tree 基礎設施 | OmniHeal 只寫 .md，不需要完整的 JSON 索引引擎 |
| llm-wiki graph 層（ontology.yaml, nodes.jsonl） | 超出目前範疇，過度工程 |
| BM25 搜尋腳本 | OmniHeal 掃描場景不需要複雜查詢 |
| Obsidian 整合 | 不相關 |
| PageIndex 的嵌入向量 / RAG 組件 | Agent 本身就是 LLM，不需要向量搜尋 |

---

## 2026-05-18 — Waterball Software Academy / aixbdd

**來源**：https://github.com/Waterball-Software-Academy/aixbdd  
**研究目的**：評估其基於 CS 學術研究最佳實踐的 AI 輸出品質控制方法，對 OmniHeal skill prompt 設計與輸出驗證的啟發

### 核心發現

AIBDD 是一套「規格先行、逐相驗收」的 AI 工作流程框架。核心洞見：
> AI Agent 失敗的原因幾乎都是「規格不清楚就開始工作」。
> 解法：讓每個產出物只負責一件事，每個步驟都有明確的正確性驗證方式。

三個對 OmniHeal 最有用的設計：
1. **D/S/I 動詞模型** — 明確區分「照做」vs「需要推理」vs「需要問人」的步驟
2. **Atomic Rule 5-question 自檢** — 每個分析標準原子化，一個問題一個答案
3. **Skill 邊界宣告** — 每個 skill 明確宣告負責什麼、不負責什麼

### 採用項目

**1. D/S/I 動詞模型**  
來源：AIBDD skill 的 SOP 步驟標注系統
- **D（Deterministic）**：確定性操作，照做即可，不需要推理（READ、WRITE、PARSE）
- **S（Semantic）**：語義操作，需要 Agent 推理判斷（ANALYZE、JUDGE、CLASSIFY）
- **I（Interactive）**：互動操作，需要暫停等待使用者輸入（ASK）

OmniHeal 的 phases/ 文件每個步驟加上 `[D]`/`[S]`/`[I]` 標注：
```
[D] 執行 probe.py，取得檔案清單
[S] 分析檔案內容，套用 skill prompt 判斷嚴重程度
[D] 將結果追加寫入 session_log.md
[I] （若 constitution.md 不存在）詢問使用者確認治理底線
```
讓 Agent 清楚哪些步驟「照辦」、哪些需要「動腦」。

**2. Atomic Finding 原則（源自 Atomic Rule 5-question 自檢）**  
AIBDD 規定每條規則必須通過 5 問自檢：Who / To What / Does What / When / Consequence 各只有一個。  
OmniHeal 的 findings/[file].md 每條發現條目必須通過同樣的原子性檢查：
- ❌ 非原子：「命名不一致且缺少錯誤處理」（兩個問題）
- ✅ 原子：「函式名稱 doLogin 不符合 Python snake_case 規範」（一個問題）
- ❌ 非原子：「Admin 或 Teacher 可以操作此功能」（兩個主體）

每條發現 = 一個主體 + 一個問題 + 一個位置 + 一個建議。

**3. Skill 邊界宣告（scope.in / scope.out）**  
來源：AIBDD 的 boundary-profile-contract  
每個 OmniHeal skill_*.md 開頭加入明確邊界宣告：
```markdown
## Skill 邊界
**負責（scope.in）：**
- 命名慣例一致性
- 函式複雜度（巢狀層數、行數）
- 明顯的邏輯錯誤

**不負責（scope.out）：**
- 安全漏洞（交給 security skill）
- 效能優化（超出本次範疇）
- 測試覆蓋率（另一個 skill 的職責）
```
避免 Agent 越界分析，也讓使用者知道每個 skill 的精確用途。

**4. Report Contract（人讀散文 / Agent 讀結構）**  
來源：AIBDD 的 report-contract.md  
OmniHeal findings 格式強化：
- findings/[file].md 的**散文段落** = 給人讀的解釋（為什麼這是問題、如何修正）
- findings/[file].md 的 **frontmatter** = 給 Agent 讀的結構化元資料（severity、status、file）
- findings_index.md = 給人快速瀏覽的一行摘要表

### 放棄項目

| 項目 | 放棄原因 |
|------|---------|
| 完整 BDD pipeline（feature / DSL / activity） | OmniHeal 是掃描工具，不是 BDD 框架 |
| L1-L4 DSL binding | 不需要 Gherkin 步驟定義，不適用 |
| Reconcile 級聯傳播 | 超出目前範疇 |
| Walking skeleton generator | 不適用 |
| Activity diagram DSL | 不適用 |

---

## 2026-05-18 — Understand-Anything

**來源**：https://github.com/Lum1104/Understand-Anything  
**研究目的**：評估其 7 階段 pipeline 對大型程式庫的系統性理解方法，對 OmniHeal Phase 1 掃描策略的啟發

### 核心發現

Understand-Anything 是一套多代理程式庫理解流水線，核心洞見：
> 對大型程式庫不能「盲目逐行掃描」，必須先建立全局結構認知，再逐層深入。
> 解法：7 個順序 Phase（Scan → Structure → Semantic → Architecture → Learning → Validation），每層輸出供下層使用。

三個對 OmniHeal 最有用的設計：
1. **分批處理（Batching）** — 每批 20–30 個檔案，避免 context window 爆炸
2. **增量指紋（Incremental Fingerprint）** — 用 git 狀態判斷哪些檔案已變動，只重新分析有變動的檔案
3. **確定性優先（Deterministic First）** — 結構提取（路徑、類型、大小）用確定性方法；語義推理才用 LLM

### 採用項目

**1. 分批掃描策略（Batch Scanning）**  
來源：Understand-Anything 的並行代理分批設計  
OmniHeal Phase 1 加入明確的批次處理：
- 每批處理 20–30 個檔案（而非無限流水）
- 每批結束後更新 `scan_plan.md`（已處理 N/Total）
- 超大專案（>300 檔）必須分批；中型（50–300）建議分批
- 單批失敗不影響下一批（與 3-Strike Protocol 配合）

**2. 增量掃描（Incremental Scan）**  
來源：Understand-Anything 的 git 指紋機制  
LAUNCH.md 增加可選的增量模式：
- 若 `scan_plan.md` 記載上次掃描時間，可先執行 `git diff --name-only <上次掃描時間>` 取得變動檔案清單
- 增量模式下，`file_index.md` 不重建，只更新有變動的行
- `findings_index.md` 用 surgical append 加入新結果，不覆蓋舊結果
- 適用場景：夜間定期掃描（只需分析當天新增/修改的檔案）

**3. 確定性優先原則（Deterministic First）**  
來源：Understand-Anything 的「tree-sitter 先解析，LLM 後語義」設計  
OmniHeal 明確化兩層操作的分工：
- `probe.py` 做確定性提取：路徑、副檔名、檔案大小、行數（不需 LLM）
- Agent（LLM）只做語義判斷：這段程式碼是否有問題、嚴重程度為何
- Phase 0 的 `file_index.md` 預估複雜度欄位由 probe.py 用啟發式規則填寫（行數 × 巢狀深度估算），不依賴 LLM
- 原則：能用規則做到的事，絕不浪費 LLM token

**4. 錯誤透明化（Error Transparency）**  
來源：Understand-Anything 的 Warning 而非 Silent Drop 設計  
強化現有 3-Strike Protocol：
- 任何跳過的檔案，`session_log.md` 必須記錄跳過原因（不允許靜默略過）
- 最終報告摘要必須包含「跳過檔案統計」（N 個檔案被跳過，原因分佈）
- 不允許用「無法分析」作為原因，必須具體：「編碼不支援」、「非純文字」、「超過大小上限」

### 放棄項目

| 項目 | 放棄原因 |
|------|---------|
| 21 種節點型別（Node types）的知識圖譜 | OmniHeal 是健檢工具，不需要建立完整的程式庫知識圖 |
| Tour pattern（依賴序學習路徑）| OmniHeal 掃描不需要理解模組間依賴關係 |
| 7-Phase 全套 pipeline | OmniHeal 只需 Phase 0（探測）+ Phase 1（掃描），更多 Phase 是過度工程 |
| 並行多代理派遣（5 個並發 Agent）| OmniHeal 設計為單一 Agent 執行，不依賴多 Agent 基礎設施 |
| Validation Phase（交叉驗證）| 超出目前範疇；可作為未來 Milestone 5 研究 |

---

## 2026-05-18 — anthropics/claude-plugins-official / code-review

**來源**：https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review  
**研究目的**：評估 Anthropic 官方 Code Review Plugin 的審查策略，對 OmniHeal skill 發現品質與誤報控制的啟發

### 核心發現

Anthropic 官方 Code Review Plugin 的核心洞見：
> AI code review 最大的失敗模式是誤報（False Positive）。一個誤報足以讓工程師永遠忽視所有後續建議。
> 解法：只報告高信心度（≥80）的問題；寧可漏掉，不要亂報。

三個對 OmniHeal 最有用的設計：
1. **信心度門檻（Confidence Gate）** — 每個發現標注 0–100 信心度，低於 80 不輸出
2. **誤報優先設計（False-Positive-First）** — 主要設計目標是避免誤報，而非最大化問題偵測
3. **編號發現 + 位置錨定（Numbered Findings）** — 每個問題編號（#1, #2...），附 file:line 精確位置

### 採用項目

**1. 信心度門檻（Confidence Gate）**  
來源：code-review plugin 的 confidence score 機制  
OmniHeal findings/[file].md frontmatter 增加 `confidence` 欄位：
```yaml
---
severity: high
confidence: 85   # 0-100，低於 80 的發現不輸出到 findings
---
```
Skill 文件明確規定：Agent 對某個發現不確定時，**寧可不報告，不可亂報**。  
這讓 OmniHeal 的輸出成為「高精度」工具，而非「高召回率」工具。

**2. 誤報優先設計（False-Positive Avoidance as Primary Goal）**  
來源：code-review plugin 的設計哲學  
在每個 `skills/skill_*.md` 的 scope.out 區塊加入明確的「不報告清單」：
- ❌ 不報告：「這個設計可以更好」（沒有明確標準）
- ❌ 不報告：「這段邏輯感覺有問題」（感覺不是證據）
- ✅ 報告：「第 X 行的 SQL 字串拼接，符合 OWASP A03 注入漏洞模式」（有標準、有位置）

Skill 文件必須明確說明：「若沒有足夠證據，標記為 `confidence < 80`，不輸出」。

**3. 編號發現 + 位置錨定（Numbered Findings with File:Line）**  
來源：code-review plugin 的輸出格式  
OmniHeal 發現條目格式升級：
```
#1 src/auth/login.py:23 — SQL 字串拼接（severity:high, confidence:92）
   問題：第 23 行直接將使用者輸入拼入 SQL 字串
   建議：改用參數化查詢（parameterized query）
```
- 每個發現有唯一編號（在本次掃描內全局遞增）
- file:line 精確錨定問題位置（不可模糊，如「某處」、「部分地方」）
- severity + confidence 同行顯示

**4. 範圍鎖定（Scope to Delta）— 增量模式延伸**  
來源：code-review plugin 的「只 review 變動的部分」設計  
OmniHeal 增量掃描模式（Incremental Scan）下，僅分析 git diff 顯示為變動的檔案，明確跳過未修改的檔案。  
若使用者未啟用增量模式，掃描全部，但在 session_log.md 標記「全量掃描」以區別。

### 放棄項目

| 項目 | 放棄原因 |
|------|---------|
| 5 個並行代理角色（CLAUDE.md compliance / bug scan / git history / PR patterns / comments）| OmniHeal 單 Agent 執行；多角色分析是未來 Milestone 5 可研究的擴展 |
| Git history context agent（分析歷史 PR 模式）| OmniHeal 的主要場景是夜間全量掃描，不侷限於 PR review |
| Previous PR patterns agent | 同上 |
| GitHub line link 格式（`file.py#L23`）| OmniHeal 輸出的是本地路徑，不是 GitHub URL |

---

## 2026-05-18 — affaan-m/everything-claude-code（ECC）

**來源**：https://github.com/affaan-m/everything-claude-code  
**研究目的**：評估黑客松冠軍作者的 AI Agent harness 系統，對 OmniHeal 自主執行迴圈設計、context 管理、與掃描品質控制的啟發

### 核心發現

ECC 是一套生產就緒的 Claude Code 插件，47 個代理、181 個 skills、60 個命令。核心洞見：

**1. 自主迴圈的三大失敗模式（Autonomous Loop Anti-Patterns）：**
> - 無限重試同一個失敗（沒有改變上下文）
> - 跨迭代沒有 context bridge（每次重啟都從零開始）
> - 用「負面指令」約束行為（比「分離任務」更差）

**2. De-Sloppify 模式：**
> 「兩個有焦點的 Agent 勝過一個受限的 Agent。」
> 與其在分析 prompt 裡加「不要越界」，不如在分析完成後，**用另一個乾淨的 context** 做發現清理。

**3. Analysis Depth Levels（分析深度等級）：**
> 同一個技能，對不同複雜度的檔案用不同深度：fast / standard / deep / full
> 這讓大型專案可以合理分配 LLM token

**4. Context Budget（上下文預算追蹤）：**
> 每次 Agent 迭代前，估計剩餘 context 空間。
> 若 context 不足，**降級深度（deep → standard → fast）**，而非盲目繼續直到爆掉。

**5. SHARED_TASK_NOTES 模式（ECC 稱為「跨迭代 context bridge」）：**
> 每個迭代開始時讀、結束時寫一個共享筆記檔，橋接獨立 `claude -p` 呼叫間的進度。
> → 這正是 OmniHeal 的 scan_plan.md 已在做的事，驗證了我們的設計正確。

### 採用項目

**1. 分析深度等級（Analysis Depth Levels）**  
來源：ECC repo-scan skill 的 fast/standard/deep/full + Ralphinho 的 tier model  
OmniHeal Phase 1 根據 `file_index.md` 的複雜度欄位，對每個檔案選擇掃描深度：

| 深度 | 觸發條件 | Agent 行為 |
|-----|---------|-----------|
| `fast` | 複雜度 `low` 或剩餘 context < 30% | 只掃 scope.in 的前 3 條最高優先規則 |
| `standard` | 複雜度 `medium`（預設） | 完整執行 skill 的所有分析標準 |
| `deep` | 複雜度 `high` | 分段讀取（每段 4000 字元），對每段獨立套用 skill |

Phase 0 的 `file_index.md` 已有複雜度欄位，直接作為深度決策依據，無需額外步驟。

**2. Context Budget 檢查（Context Window 安全閘）**  
來源：ECC context-budget skill 的 token 估算與降級邏輯  
Phase 1 每處理完一個批次（20–30 個檔案），執行 context check：
- **估算剩餘 context**：Agent 主觀評估「我還有多少 context 空間？」（不需要精確計算）
- 若評估為 **> 50%**：繼續 `standard` 深度
- 若評估為 **20–50%**：切換至 `fast` 深度，繼續掃描
- 若評估為 **< 20%**：立即更新 `scan_plan.md`（記錄當前進度），結束本次 session。下次重啟時從此批次繼續（Session Recovery）
- **嚴禁**：不評估就繼續直到 context 爆炸，導致最後幾個批次品質急劇下降

**3. De-Sloppify 作為 Phase 1.5（發現清理階段）**  
來源：ECC 的 De-Sloppify Pattern（「負面指令 < 分離任務」）  
Phase 1 結束後，加入可選的 Phase 1.5（Findings Consolidation）：
- **目的**：用乾淨的 context（不需重新讀原始檔案），只讀 `findings_index.md` 和 `findings/` 裡的條目，執行：
  - 合併重複發現（同一問題被不同段落各報告一次）
  - 刪除 confidence 邊界案例（75–79 的條目）
  - 重新計算 session 統計（高嚴重度 N 個、中 N 個、已跳過 N 個）
  - 產出 `progress/YYYY-MM-DD-<skill>/summary.md`（一頁 executive summary）
- **對應 OmniHeal 原則**：Phase 1.5 是純 `[D]` + `[S]` 操作，不需要任何 `[I]` 互動

**4. 迴圈終止信號（Completion Signal）**  
來源：ECC continuous-claude 的 `--completion-signal` 機制  
Phase 1 結束時（或 Phase 1.5 結束時），Agent 在 `scan_plan.md` 寫入明確的完成信號：
```markdown
## 完成信號
OMNIHEAL_SCAN_COMPLETE | 2026-05-18 06:23 | 共 157 個檔案 | 高嚴重度發現 8 個
```
這讓使用者（或外部監控）能夠無歧義地判斷掃描是否完成（區別於「中途停止等待恢復」）。

### 放棄項目

| 項目 | 放棄原因 |
|------|---------|
| 完整 Loop 架構（sequential pipeline / continuous-PR / Ralphinho DAG）| 需要 `claude -p` CLI + 多程序，OmniHeal 必須在任何 Agent 執行，不依賴特定 CLI |
| 多模型路由（Haiku → Sonnet → Opus 每步切換）| OmniHeal 領域無關且模型無關，不能假設特定模型的可用性 |
| NanoClaw REPL | 需要 Node.js + 特定 ECC 安裝 |
| Hook 基礎設施（PreToolUse / PostToolUse / SessionStart）| 同前，零安裝原則 |
| MCP 設定 | 同前 |
| 47 個專業代理 + 181 個 skill 的完整目錄 | OmniHeal 追求最小化，3 個核心 skill 足夠 |
| ECC 的 12-layer Agent Stack 診斷框架 | 是除錯工具，不是掃描工具，不適用 |

---

## 2026-05-18 — wanshuiyin/Auto-claude-code-research-in-sleep（ARIS）

**來源**：https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep  
**研究目的**：評估其「睡眠中自動 AI 研究」系統的持續自動化設計，對 OmniHeal 夜間全自動掃描的長程穩健性啟發

### 核心發現

ARIS 是一套 ML 研究自動化 harness，讓 Agent 在無人值守的情況下執行完整研究流程（發現想法 → 實驗 → 自動評審 → 撰寫論文）。最核心的洞見：

> **「Pipeline Status 是協議，Hook 是實作。協議不需要 Hook 也能運作。」**
> 只要在 CLAUDE.md 維護一個結構化的 `## Pipeline Status` 區塊，任何 Agent 在任何平台（Claude Code、Cursor、Trae、OpenClaw）都能在 30 秒內恢復工作狀態。

三個對 OmniHeal 最有用的設計：
1. **`next:` 欄位** — Pipeline Status 的最重要欄位：「我接下來應該做什麼？」，防止 Agent 恢復後茫然停頓
2. **`last_updated:` 時間戳** — 每次 Agent 寫入進度檔時自動更新，讓使用者判斷掃描是否卡住
3. **Findings.md 作為跨 session 發現紀錄** — 與執行紀錄（session_log）分開，記錄「關於這個專案我學到了什麼」，跨多次掃描持久保存

### 採用項目

**1. scan_plan.md 加入 `next:` 欄位與 `last_updated:` 時間戳**  
來源：ARIS 的 `## Pipeline Status` 區塊設計

OmniHeal 的 `scan_plan.md` 格式升級，加入兩個欄位：
```markdown
## 當前掃描任務
- 目標目錄：./src
- 使用技能：skill_code_lint
- 開始時間：2026-05-18 22:00
- last_updated：2026-05-18 23:42   ← 每次 Agent 更新此檔時自動填寫
- 輸出目錄：progress/2026-05-18-code_lint/

## Phase 狀態
- Phase 0（環境探測）：complete
- Phase 1（全域掃描）：in_progress（批次 3/8，已處理 42/157 個檔案）

## next
繼續批次 4（第 43–60 個檔案，從 src/payment/ 開始），深度：standard
```

**`next:` 欄位讓 Agent 恢復後不需要重新推算「現在要做什麼」**，直接照做即可。  
`last_updated:` 讓使用者早晨查看報告時，能判斷掃描是「正常完成」還是「中途卡住超過 N 小時」。

**2. 跨掃描 Findings.md（Cross-Scan Discovery Log）**  
來源：ARIS 的 `findings.md` 設計（分 Research Findings / Engineering Findings 兩層）

OmniHeal 的 `progress/` 增加一個頂層 `findings.md`（不在 YYYY-MM-DD-skill/ 子目錄下）：
- **用途**：記錄「關於這個專案我在掃描中學到的事情」，跨多次掃描保持持久
- **不是** session_log（執行紀錄）；**不是** findings_index（單次掃描的問題清單）
- 只記錄**跨次都有意義**的發現（例如：「此專案的 Python 檔案幾乎都不遵守 snake_case」、「src/legacy/ 目錄的程式碼品質系統性偏低，每次掃描都觸發大量 high findings」）

格式：
```markdown
# OmniHeal 跨掃描發現紀錄

## [2026-05-18] 掃描：src/（skill_code_lint）
- src/legacy/ 目錄佔總 high findings 的 60%；建議下次只對 legacy/ 執行 deep 深度
- 此專案使用混合命名慣例（部分模組 camelCase，部分 snake_case）；constitution.md 已更新治理規則

## [2026-05-18] 掃描：logs/（skill_log_parse）
- 日誌格式共 3 種（JSON / 純文字 / 混合）；skill_log_parse 對純文字格式的信心度普遍偏低（60–75）
```

**3. 恢復時的 Context Narrowing（最小必要 context）**  
來源：ARIS 的「research_contract.md = 只讀當前任務的聚焦文件，而非全部原始紀錄」設計

OmniHeal 的 LAUNCH.md 第零步（Session Recovery）明確規定讀取順序與範圍：
1. 讀 `progress/scan_plan.md` → 看 `next:` 欄位（30 秒定向）
2. 讀 `progress/YYYY-MM-DD-<skill>/findings_index.md` **最後 20 行**（只看當前 session 最近的進度，不是全部）
3. 讀 `progress/YYYY-MM-DD-<skill>/session_log.md` **最後 10 行**（確認上次做到哪裡）
4. **嚴禁**：恢復時重新載入所有 findings/[filename].md 詳細頁（context pollution）

「聚焦恢復」原則：Agent 恢復工作狀態只需要「next 欄位 + 最近幾行進度」，不需要重新讀取整個掃描歷史。

### 放棄項目

| 項目 | 放棄原因 |
|------|---------|
| Watchdog daemon（watchdog.py）| 需要 Python daemon 持續在 GPU 伺服器執行，OmniHeal 不依賴任何持續運行的程序 |
| Hook 自動化（session-restore.sh / context-refresh.sh）| Claude Code 專屬；OmniHeal 在任何 Agent 執行，Protocol（CLAUDE.md 中的 Pipeline Status）比 Hook 實作更重要，直接採用協議設計即可 |
| 跨模型對抗評審（Executor / Reviewer 不同家族）| OmniHeal 單 Agent 執行，不假設有第二個模型可用 |
| 完整 ARIS 研究 pipeline（W1 → W4）| OmniHeal 是程式碼/日誌/文字稿健檢工具，不是 ML 研究自動化框架，定位不同 |
| CronCreate 定時排程 | 超出 OmniHeal 的零安裝設計原則；使用者可自行用 OS 排程器配合 |
| Effort levels（lite/balanced/max/beast）| OmniHeal 已有等效的 fast/standard/deep 深度等級，不需要重複抽象層 |

---

## 2026-05-18 — parcadei/Continuous-Claude-v3（CC-v3）

**來源**：https://github.com/parcadei/Continuous-Claude-v3  
**研究目的**：評估其多 Agent 持續執行架構、5 層程式碼分析工具鏈（TLDR）、與跨 session 記憶系統，對 OmniHeal 分析品質與長程執行穩健性的啟發

### 核心發現

CC-v3 是一套生產就緒的 Claude Code harness，109 個 skills、32 個 agents、30 個 hooks，搭配 TLDR 5 層程式碼分析工具（AST→CallGraph→CFG→DFG→PDG）與 PostgreSQL 向量記憶體系統。

三個對 OmniHeal 最有用的洞見：

**1. 80% 假聲明率（Claim Verification Rule）：**
> 「只用 grep 結果，不讀檔案確認」導致 80% 的程式碼聲明是錯的。
> 每個存在性聲明必須標注信心標記：✓ VERIFIED（已讀原始碼）/ ? INFERRED（推論）/ ✗ UNCERTAIN（未確認）。
> 沒有讀檔案就報告的發現，必須標記為 ? INFERRED，不得進入 findings。

**2. Compound not Compact（複合而非壓縮）：**
> 「session 快結束時壓縮 context」比「開始新 session 時帶入精華」更差。
> 正確做法：從每個 session 萃取可遷移的學習，然後在新 session 用精煉 context 重新開始。
> → 直接驗證了 ARIS 的跨掃描 findings.md 設計：把學習萃取出來，下次掃描用精煉後的 findings.md 作為 context，不是把整個 session_log 帶入。

**3. YAML Handoff（token 效率觀察）：**
> session 間傳遞的狀態用 YAML 比 Markdown 段落節省 30-40% token。
> OmniHeal 已有等效機制（scan_plan.md 的 `next:` 欄位），效益邊際，不作為採用項目。

### 採用項目

**1. Claim Verification 兩步驗證（強化 Atomic Finding 與信心度機制）**  
來源：CC-v3 的 claim-verification rule（80% false claim rate incident）

OmniHeal 的 findings/[file].md 每條發現必須標注驗證狀態：

| 標記 | 含義 | 能否輸出為 finding |
|-----|------|---------|
| `✓ VERIFIED` | Agent 讀了原始檔案，確認問題存在於指定行 | ✅ 同時 confidence ≥ 80 才可輸出 |
| `? INFERRED` | 基於 grep/模式推斷，未讀原始檔案確認 | ❌ 不得輸出，可記入 session_log |
| `✗ UNCERTAIN` | 尚未調查 | ❌ 不得輸出 |

具體規則：
- Agent 若只用 grep 找到「似乎有問題的模式」，標記為 `? INFERRED`
- `? INFERRED` 發現不計入 findings；可記錄在 session_log 的 `inferred:` 條目供後續驗證
- 從 `? INFERRED` 升級為 `✓ VERIFIED`：必須讀取原始檔案，找到 file:line，確認問題存在
- **兩條件同時成立** 才能輸出：`✓ VERIFIED` + `confidence ≥ 80`

→ 導入 spec Section 8 的 Skill 格式規範與 Phase 1 的分析步驟

**2. "Compound not Compact" 設計驗證**  
來源：CC-v3 的工作流程哲學，直接驗證 ARIS 已導入的跨掃描 findings.md 設計。

CC-v3 的洞見：
- 「把整個掃描歷史帶入新 session」= Compact（壓縮舊 context）= 劣化
- 「萃取精華到 findings.md，新 session 只讀精華」= Compound（複合學習）= 正確做法

OmniHeal 的 `progress/findings.md` 已實作此模式：每次掃描結束萃取結構性學習，下次恢復只讀 findings.md 精煉版。無需對現有設計做修改，此條目正式記錄為 CC-v3 驗證。

### 放棄項目

| 項目 | 放棄原因 |
|------|---------|
| TLDR 5 層程式碼分析工具鏈（AST→DFG→PDG） | 需要 `pip install tldr-code`、daemon、PostgreSQL——違反零安裝原則 |
| PostgreSQL + pgvector 向量記憶體系統 | 同上，需要資料庫 daemon 持續運行 |
| 109 skills / 32 agents / 30 hooks 完整基礎設施 | OmniHeal 追求最小化設計，3 個核心 skills 足夠 |
| Hook 驅動的 skill 啟動機制 | Claude Code 專屬，OmniHeal 必須在任何 Agent 執行 |
| Cross-terminal coordination DB（PostgreSQL） | 需要 Docker + PostgreSQL，違反零安裝原則 |
| Continuity Ledger（CONTINUITY_*.md） | OmniHeal 已有等效機制（scan_plan.md + next: + cross-scan findings.md） |
| YAML Handoff 格式優化 | 現有 scan_plan.md Markdown 格式已足夠，避免過早優化 |
| Premortem（TIGERS & ELEPHANTS 風險分析） | OmniHeal 的 Phase 0 constitution.md 已有等效治理底線機制 |
