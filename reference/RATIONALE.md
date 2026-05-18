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
