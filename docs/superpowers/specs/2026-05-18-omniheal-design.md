# OmniHeal — 設計文件 (Design Spec)
> 版本：v1.8 | 日期：2026-05-18 | 更新：Claim Verification 兩步驗證（✓ VERIFIED / ? INFERRED / ✗ UNCERTAIN）、"Compound not Compact" 驗證（CC-v3）

---

## 1. 系統概述（用白話說清楚）

**OmniHeal 是一個放進任何專案裡的「AI 代理指令手冊 + 輔助工具箱」。**

很多專案在快速開發後，會累積大量雜亂的東西：
- 程式碼裡有過時的寫法、命名不一致、潛在的錯誤
- 日誌檔（程式執行紀錄）格式混亂、難以分析
- 會議記錄或文字稿被 AI 轉錄錯誤，充滿荒謬的錯字

OmniHeal 的作用是：**讓 AI 代理（Agent）在夜間無人值守時，自動逐一掃描這些雜亂的檔案，用自己的理解能力進行分析，隔天早上產出一份完整報告。**

**關鍵限制：整個掃描過程絕對不能因為單一檔案失敗而中斷。** 遇到任何錯誤，記錄下來，繼續處理下一個檔案。

---

## 2. 核心運作模型（最重要）

```
使用者說：「請閱讀 @OmniHeal 開始進行」
         ↓
Agent 讀取 LAUNCH.md（唯一入口）
         ↓
★ 先讀 progress/scan_plan.md，確認是否有未完成的掃描需要恢復
         ↓
Agent 依照 LAUNCH.md 的里程碑清單，自行閱讀 phases/ 文件
         ↓
Agent 用自己的工具（讀檔、寫檔、執行 Bash）完成所有工作
Agent 本身就是 LLM，直接分析每個檔案，不呼叫第二個模型
         ↓
結果寫入 progress/YYYY-MM-DD-<skill>/，隔天使用者查看報告
```

**沒有任何需要人工安裝或下指令的步驟。**

---

## 3. 使用方式

```bash
# 步驟 1：把 OmniHeal 放進目標專案
cd your-messy-project/
git clone <omniheal-repo-url> OmniHeal/

# 步驟 2：告訴 Agent（任何 coding agent 皆可）
"請閱讀 @OmniHeal 開始進行"
# 或更具體：
"請閱讀 @OmniHeal，對 ./src 目錄執行程式碼健檢，使用 code_lint 技能"
```

**就這樣。Agent 接管一切。**

---

## 4. 目錄結構

```
OmniHeal/                        ← 整個工具箱的根目錄（git clone 進目標專案）
│
├── LAUNCH.md                    ← 唯一入口：Agent 讀這一個就夠，< 500 行
│
├── phases/                      ← 各階段的詳細作業說明（Agent 讀的指令文件）
│   ├── phase0_bootstrap.md      ← 第 0 階段：探測環境、生成「治理規則文件」
│   └── phase1_scanner.md        ← 第 1 階段：夜間全域掃描、產出報告
│
├── skills/                      ← 任務技能（Prompt 模板）
│   ├── skill_code_lint.md       ← 處理程式碼：找命名問題、過時寫法、潛在錯誤
│   ├── skill_log_parse.md       ← 處理日誌：從雜亂紀錄中萃取有用情報
│   └── skill_text_align.md      ← 處理文字稿：修正 AI 轉錄的荒謬錯字
│
├── templates/
│   └── constitution_base.md     ← 「治理規則文件」的基礎模板（Phase 0 會填寫它）
│
├── progress/                    ← 所有掃描狀態與結果（應 commit）
│   ├── scan_plan.md             ← 當前任務狀態（含 next: 與 last_updated: 欄位）
│   ├── file_index.md            ← Phase 0 產出：目標專案所有檔案的一行摘要清單
│   ├── constitution.md          ← Phase 0 產出：「治理規則文件」正本
│   ├── findings.md              ← 跨掃描發現紀錄（學習累積，不隨單次掃描重置）
│   └── YYYY-MM-DD-<skill>/      ← 每次掃描的獨立子目錄（日期+技能命名）
│       ├── findings_index.md    ← 每個分析過的檔案一行摘要（路徑+主要發現+嚴重程度）
│       ├── session_log.md       ← 機器可解析的執行紀錄（ISO 時間+操作類型）
│       ├── summary.md           ← Phase 1.5 產出：executive summary（統計+優先修復清單）
│       └── findings/            ← 只有重大發現的檔案才建立
│           └── [filename].md    ← 附 frontmatter 元資料的詳細發現頁
│
├── research/                    ← 研究用：存放參考 repo 的 git clone（不提交到 git）
│
├── src/                         ← Agent 可以呼叫的輔助腳本（越少越好）
│   └── probe.py                 ← 掃描目標目錄結構，輸出純文字清單供 Agent 讀取
│
├── .gitignore                   ← 排除 research/（progress/ 不排除）
└── README.md                    ← 人類閱讀用的說明文件
```

---

## 5. LAUNCH.md 的結構設計

`LAUNCH.md` 是所有 AI 代理的唯一入口。結構：

```markdown
# OmniHeal 啟動手冊

## 你是誰、你要做什麼
（用白話解釋 OmniHeal，不假設 Agent 認識任何術語）

## ★ 第零步：先確認是否有未完成的工作（必做）
在做任何事之前，先讀 progress/scan_plan.md。
- 若有未完成的掃描（Phase 狀態不是全部 complete）→ 恢復上次進度
- 若沒有或全部完成 → 開始新任務

## 本次任務（若為新任務）
- 目標目錄：[使用者指定，或預設為父目錄]
- 使用技能：[skill_code_lint / skill_log_parse / skill_text_align]
- 輸出目錄：progress/YYYY-MM-DD-<skill>/

## 里程碑（依序執行）
1. 閱讀 phases/phase0_bootstrap.md，執行環境探測
2. 確認 progress/constitution.md 存在（若無則先建立）
3. 閱讀 phases/phase1_scanner.md，開始逐檔掃描
4. 每完成一個 Phase，更新 progress/scan_plan.md 的狀態

## 重啟自我檢查（Context Narrowing 恢復，中斷後必做）
若掃描中斷後重新啟動，**依序**讀以下最小必要 context（不多讀）：
1. `progress/scan_plan.md` → 看 `next:` 欄位（定向，30 秒）
2. `progress/YYYY-MM-DD-<skill>/findings_index.md` 最後 20 行（確認最近掃描狀態）
3. `progress/YYYY-MM-DD-<skill>/session_log.md` 最後 10 行（確認上次做到哪裡）
4. 直接按 `next:` 欄位的指示繼續，**無需詢問使用者**

**嚴禁**：恢復時重新讀取所有 `findings/[filename].md` 詳細頁（context pollution）。

## 絕對不能做的事
- 遇到任何錯誤中斷整個程序（記錄後繼續，見 3-Strike Protocol）
- 跳過更新 `scan_plan.md` 的 `next:` 與 `last_updated:` 欄位
- 恢復後詢問使用者「我應該繼續嗎？」（讀 scan_plan.md 的 next: 即可）
- 把任何設定值寫死（用環境變數）
```

---

## 6. 兩大作業階段

### Phase 0：環境探測與規則建立
**目標**：讓 Agent 了解目標專案的性質，建立「治理規則文件」與「全局檔案索引」。

Agent 執行步驟（標注 D/S/I 動詞型別）：
1. `[D]` 執行 `python OmniHeal/src/probe.py [目標目錄]`，取得目錄結構摘要
2. `[D]` 產出 `progress/file_index.md`：每個目標檔案一行（路徑、副檔名、大小、預估類型）
3. `[S]` 用讀檔工具隨機抽取 5 個文字檔，推斷專案性質與現有規範風格
4. `[I]` 若 `progress/constitution.md` 不存在，詢問使用者確認 1-3 個治理底線問題
5. `[D]` 根據 `templates/constitution_base.md` 模板，填寫並儲存 `progress/constitution.md`
6. `[D]` 在 `progress/scan_plan.md` 標記 Phase 0 為 `complete`

**file_index.md 格式：**
```
| 路徑 | 類型 | 大小 | 預估複雜度 | 掃描深度 |
|------|------|------|----------|---------|
| src/auth.py | python | 4.2KB | high | deep |
| src/utils.py | python | 0.9KB | medium | standard |
| docs/api.md | markdown | 1.1KB | low | fast |
```
`掃描深度` 由 probe.py 根據複雜度自動填寫（high→deep / medium→standard / low→fast）。  
Phase 1 讀此索引決定掃描優先順序與深度；high 優先，可在 context 不足時降級。

### Phase 1：夜間全域掃描
**目標**：無人值守地掃描所有目標檔案，產出結構化報告。

Agent 執行步驟（標注 D/S/I 動詞型別）：
1. `[D]` 執行 `python OmniHeal/src/probe.py [目標目錄] --list-files`，取得純文字檔清單
2. `[D]` 讀取 `progress/file_index.md`，依預估複雜度排序（high 優先）
3. `[D]` 將待掃描檔案依 **20–30 個一批** 分組，在 `scan_plan.md` 記錄批次進度（批次 N / 總批次）
4. 每處理完一個批次前，執行 **Context Budget 檢查**（每批約 20–30 個檔案）：
   - Agent 主觀評估剩餘 context：
     - **> 50%**：繼續 `standard` 或 `deep` 深度
     - **20–50%**：全部降級至 `fast` 深度，繼續掃描
     - **< 20%**：立即更新 `scan_plan.md`（記錄當前批次進度），停止本 session。下次重啟時 Session Recovery 自動從此繼續
   - **嚴禁** context 不足時繼續高深度掃描（輸出品質急劇下降）

5. 對每批（20–30 個檔案）依序處理，每批結束後更新 `scan_plan.md`（已處理 N/Total）：
   - 對每個檔案，根據 `file_index.md` 的掃描深度欄位執行：
     - `fast`（複雜度 low 或 context < 30%）：只套用 skill scope.in 的前 3 條最高優先規則
     - `standard`（預設）：完整執行 skill 的所有分析標準
     - `deep`（複雜度 high）：分段讀取（每段 4000 字元），每段獨立套用 skill，結果合併
   - 對每個檔案，執行以下流程（遵守 3-Strike Protocol）：
     - `[D]` 讀取檔案內容（依深度決定分段或整體讀取）
     - `[D]` 讀取選定 skill 的 Prompt 模板（含 scope.in/scope.out 宣告）
     - `[D]` 讀取 `progress/constitution.md` 摘要（30 行以內）
     - `[S]` 依 skill 規定的分析標準逐條檢查（每條必須原子化，見 Atomic Finding 原則）
     - `[S]` 對每個潛在問題，確認**驗證狀態**：
       - `✓ VERIFIED`：已讀原始檔案，確認問題存在於指定 file:line → 繼續評估信心度
       - `? INFERRED`：只憑 grep/模式推斷，未讀原始碼 → **不得輸出為 finding**；可記入 session_log 的 `inferred:` 條目
       - `✗ UNCERTAIN`：尚未調查 → **不得輸出**
     - `[S]` 每個 `✓ VERIFIED` 發現評估信心度（0–100）；**低於 80 的不輸出到 findings**
     - 輸出條件：**`✓ VERIFIED` + `confidence ≥ 80`** 兩者同時成立，缺一不可
     - `[D]` 若有符合條件的發現：建立 `findings/[filename].md`（附 frontmatter）並更新 `findings_index.md`，每個發現賦予本次掃描全局遞增編號（#1、#2…）
     - `[D]` 追加一行到 `session_log.md`（跳過的檔案必須記錄具體原因，禁止靜默略過）
6. `[D]` 在 `progress/scan_plan.md` 標記 Phase 1 為 `complete`，並寫入跳過檔案統計

### Phase 1.5：發現清理（可選，建議執行）
**目標**：用乾淨的 context（不重新讀原始檔案）整合、清理 Phase 1 的原始發現，產出 executive summary。

Agent 執行步驟：
1. `[D]` 讀取 `findings_index.md`（全部條目，一行一條）
2. `[D]` 讀取所有 `findings/[filename].md`（詳細頁）
3. `[S]` 合併重複發現（同一問題被不同段落各報告一次）
4. `[S]` 移除 confidence 在 75–79 之間的邊界案例（提升整體精確度）
5. `[D]` 重新計算統計：高嚴重度 N 個、中 N 個、已跳過 N 個
6. `[D]` 產出 `progress/YYYY-MM-DD-<skill>/summary.md`：
   ```markdown
   # 掃描摘要
   > Skill: code_lint | 日期: 2026-05-18 | 總計: 157 個檔案
   
   ## 統計
   - 🔴 高嚴重度：8 個（8 個檔案）
   - 🟡 中嚴重度：23 個（15 個檔案）
   - ✅ 無問題：110 個檔案
   - ⏭️ 已跳過：19 個（原因分佈：編碼問題 12、超大檔案 7）
   
   ## 優先修復（高嚴重度摘要）
   #1 src/auth/login.py:23 — SQL 注入風險（confidence:92）
   #5 src/api/users.py:89 — 未處理的例外（confidence:87）
   ...
   ```
7. `[D]` 在 `scan_plan.md` 寫入完成信號：
   ```
   OMNIHEAL_SCAN_COMPLETE | 2026-05-18 06:23 | 157 個檔案 | 高嚴重度 8 個
   ```

完成信號讓使用者和外部監控能夠無歧義判斷掃描是否完成（區別於「中途停止待恢復」）。

#### 確定性優先原則（Deterministic First）
> 能用規則做到的，不浪費 LLM token。
- `probe.py` 負責：路徑、副檔名、大小、行數、複雜度估算（純規則）
- Agent 負責：語義判斷（問題是否存在、嚴重程度、建議如何修正）
- **嚴禁**用 LLM 做確定性任務（如：判斷檔案是否存在、計算行數）

#### 3-Strike Protocol（單一檔案失敗處理）
```
第 1 次失敗 → 記錄錯誤原因，換一種方式重試
第 2 次失敗 → 再換一種方式
第 3 次失敗 → 在 session_log.md 標記「永久跳過：[具體原因]」，繼續下一個檔案
```
跳過原因必須具體（如：「編碼不支援 UTF-8」、「非純文字檔」、「超過大小上限 1MB」），不允許模糊描述。  
**任何情況下不允許整個掃描中斷。**

#### 增量掃描模式（選用）
若 `scan_plan.md` 有記錄上次掃描完成時間，LAUNCH.md 允許使用者要求增量模式：
1. `[D]` 執行 `git diff --name-only <上次掃描時間>` 取得有變動的檔案清單
2. `[D]` 只掃描清單內的檔案（其餘跳過，不重新分析）
3. `[D]` `findings_index.md` 用 surgical append 加入新結果，不覆蓋舊結果
4. `[D]` `session_log.md` 記錄「增量掃描，跳過 N 個未修改檔案」

增量模式適合夜間定期掃描（只分析當日有變動的檔案）。

---

## 7. 進度檔案規格

### `progress/scan_plan.md` 格式
```markdown
## 當前掃描任務
- 目標目錄：./src
- 使用技能：skill_code_lint
- 開始時間：2026-05-18 22:00
- last_updated：2026-05-18 23:42   ← Agent 每次寫入此檔時自動更新
- 輸出目錄：progress/2026-05-18-code_lint/

## Phase 狀態
- Phase 0（環境探測）：complete
- Phase 1（全域掃描）：in_progress（批次 3/8，已處理 42/157 個檔案）
- Phase 1.5（發現清理）：pending

## next
繼續批次 4（第 43–60 個檔案，從 src/payment/ 開始），深度：standard
```
`next:` 欄位讓 Agent 恢復後無需重新推算下一步，直接照做。`last_updated:` 讓使用者判斷掃描是否卡住。

### `progress/file_index.md` 格式（Phase 0 產出）
```markdown
## 目標專案檔案索引
> 產出時間：2026-05-18 | 目標目錄：./src | 總計：157 個純文字檔

| 路徑 | 類型 | 大小 | 預估複雜度 |
|------|------|------|----------|
| src/auth/login.py | python | 4.2KB | high |
| src/utils/format.py | python | 0.8KB | low |
| docs/api.md | markdown | 1.1KB | low |
```

### `progress/YYYY-MM-DD-<skill>/findings_index.md` 格式（index-first，每檔一行）
```markdown
## 掃描發現索引
> 掃描時間：2026-05-18 | Skill：code_lint | 進度：42/157

| 檔案 | 嚴重程度 | 主要發現摘要 | 詳細頁 |
|------|---------|------------|-------|
| src/auth/login.py | 🔴 high | SQL 注入風險、未處理的例外 | [詳細](findings/login_py.md) |
| src/utils/format.py | 🟡 medium | 命名不一致 | — |
| docs/api.md | ✅ clean | 無問題 | — |
```
只有 high/medium 嚴重程度才建立詳細頁；clean 只在 index 留一行。

### `progress/YYYY-MM-DD-<skill>/findings/[filename].md` 格式（詳細發現頁）
```markdown
---
file: src/auth/login.py
type: python
scanned: 2026-05-18
skill: code_lint
severity: high
confidence: 92   # 0-100，低於 80 的發現不應出現在此文件
status: new      # new / reviewed / resolved
---

## 發現詳情

#1 src/auth/login.py:23 — SQL 字串拼接（severity:high, confidence:92）
   問題：第 23 行直接將使用者輸入拼入 SQL 字串，有注入風險
   建議：改用參數化查詢（parameterized query）

#2 src/auth/login.py:45 — 函式命名不符慣例（severity:medium, confidence:88）
   問題：函式名稱 `doLogin` 不符合 Python snake_case 規範
   建議：改名為 `do_login`
```
- 每個發現有本次掃描全局唯一編號（#1、#2…跨檔遞增）
- file:line 精確錨定位置（禁止模糊描述如「某處」）
- confidence < 80 的推測不得輸出
- 頁面軟上限 400 行；超過則拆為 [filename]_part2.md

### `progress/YYYY-MM-DD-<skill>/session_log.md` 格式（機器可解析）
```
## [2026-05-18 22:01] scan | src/auth/login.py | severity:high | 發現 3 個問題
## [2026-05-18 22:03] retry | src/legacy.py | 嘗試 2：編碼改 latin-1 成功
## [2026-05-18 22:05] skip | src/binary_blob.dat | 3-Strike：非純文字檔
```

### Scaling 閾值
| 目標檔案數 | findings 策略 |
|-----------|--------------|
| < 50 個 | findings_index.md 單檔，不建 findings/ 分頁 |
| 50–300 個 | findings_index.md + findings/[filename].md 分頁 |
| > 300 個 | findings_index.md 按類型拆分（_py.md、_md.md 等） |

### `progress/findings.md` 格式（跨掃描發現紀錄）

> 此檔與 session_log.md（執行紀錄）不同。用途：記錄關於**這個目標專案**的結構性學習，在多次掃描間持久保存。

```markdown
# OmniHeal 跨掃描發現紀錄

## [2026-05-18] src/（skill_code_lint）
- src/legacy/ 佔總 high findings 的 60%；下次可只對此目錄執行 deep 深度以節省 token
- 命名慣例混用（camelCase / snake_case）；constitution.md 已更新，加入治理規則

## [2026-05-18] logs/（skill_log_parse）
- 日誌格式 3 種共存；純文字格式導致 skill 信心度普遍偏低（60–75），建議下次用寬鬆門檻 70
```
只追加，不重寫。每次新掃描在此檔末尾加入新段落。

---

## 8. Skill 文件格式規範

每個 `skills/skill_*.md` 必須包含以下三個區塊：

### 區塊 1：Skill 邊界宣告（必填）
```markdown
## Skill 邊界
**負責（scope.in）：**
- [列出本 skill 負責檢查的具體項目]

**不負責（scope.out）：**
- [列出明確排除的項目，避免 Agent 越界]
- ❌ 不報告「這個設計可以更好」（沒有明確標準）
- ❌ 不報告「這段邏輯感覺有問題」（感覺不是證據）
- ❌ 低信心度（< 80）的推測，即使有可能是問題
- ❌ 不報告 grep/模式匹配的推測（? INFERRED）；必須讀原始檔案確認後（✓ VERIFIED）才報告

**誤報優先原則（False-Positive Avoidance）：**
> 寧可漏掉一個真正的問題，也不要輸出一個沒有證據的推測。
> 每個發現必須能回答：「我讀了哪行原始碼，看到什麼，根據什麼標準判斷這是問題。」
> grep 找到模式 ≠ 問題存在；必須讀原始檔案確認（✓ VERIFIED）。
```

### 區塊 2：分析標準（必填，每條必須原子化）

**Atomic Finding 原則**（源自 aixbdd atomic-rule-definition）：

每條分析標準必須通過 5-question 自檢：
| 問題 | 要求 |
|------|------|
| 主體（Who）| 只有一個明確主體 |
| 對象（To What）| 只有一個目標 |
| 動作（Does What）| 只有一個動作，不含 AND |
| 條件（When）| 只有一個前提條件 |
| 結果（Consequence）| 只有一個結果（成功或失敗，非兩者） |

**錯誤示範：**
- ❌ `函式命名不一致且缺少錯誤處理` → 兩個問題，必須拆成兩條
- ❌ `Admin 或 Teacher 可操作` → 兩個主體，必須拆成兩條

**正確示範：**
- ✅ `Python 函式名稱不符合 snake_case 規範`
- ✅ `函式超過 50 行（當前：X 行）`

### 區塊 3：輸出格式（必填）
Agent 分析完一個檔案後，針對每個**原子化發現**輸出一條，格式：
```
#N file/path.py:行號 — 問題描述（一個問題）（severity:level, confidence:分數）[✓ VERIFIED]
   問題：[具體描述，包含行號或位置，不可模糊]
   建議：[一個具體的修正方向]
```
- `#N`：本次掃描全局遞增編號
- `file/path.py:行號`：精確位置（必填，無行號則標明所在函式/類別）
- `[✓ VERIFIED]`：必填標記，代表 Agent 已讀原始檔案確認（非 grep 推斷）
- `confidence` < 80：**不輸出此條**，直接略過
- `? INFERRED`（未讀原始碼確認）：**不輸出為 finding**；可記入 session_log 的 `inferred:` 條目

若整個檔案無任何 confidence ≥ 80 的發現，在 `findings_index.md` 標記為 `✅ clean`，**不建立詳細頁**。

---

## 9. 輔助腳本說明（src/ 資料夾）

### `probe.py`
```
用途：快速掃描目標目錄結構（比 Agent 逐一讀檔快）
呼叫：python OmniHeal/src/probe.py [目標目錄] [--list-files]
輸出：純文字摘要印到 stdout，Agent 讀取後繼續作業
  --list-files：列出所有純文字檔路徑（過濾掉圖片、影片、壓縮檔等）
```

---

## 10. 技術決策清單

| 決策項目 | 選定方案 | 原因 |
|---------|---------|------|
| 語言 | Python（僅 probe.py） | 一行安裝，跨平台 |
| AI 分析執行者 | Agent 本身 | Agent 就是 LLM，不需要第二個模型 |
| 錯誤處理 | 3-Strike Protocol | 結構化，避免無限重試或提早放棄 |
| 進度儲存 | 3-file 模式（scan_plan / findings_index / session_log） | 參考 planning-with-files，磁碟即記憶體 |
| 掃描隔離 | 每次用日期+技能命名的子目錄 | 多次掃描結果不混疊 |
| 設定傳遞 | 環境變數 | 不寫死，跨機器可攜 |
| 批次大小 | 每批 20–30 個檔案 | 避免 context window 爆炸，參考 Understand-Anything |
| 確定性vs語義分工 | probe.py 做確定性提取，Agent 做語義判斷 | 不浪費 LLM token，參考 Understand-Anything |
| 發現品質控制 | 信心度門檻 ≥ 80 才輸出 | 誤報優先設計，參考 code-review plugin |
| 發現格式 | 編號（#N）+ file:line 精確位置 | 可追蹤、可引用，參考 code-review plugin |
| 增量掃描 | 選用模式，依 git diff 篩選變動檔案 | 適合定期夜間掃描，參考 Understand-Anything |
| 分析深度等級 | fast/standard/deep 依複雜度決定 | 避免在低價值檔案浪費 token，參考 ECC repo-scan |
| Context Budget 安全閘 | 每批評估剩餘 context，不足時降級或停止 | 防止 context 爆炸導致末批品質劣化，參考 ECC |
| Phase 1.5 清理 | 可選：乾淨 context 下整合發現、產 summary | De-Sloppify 模式，參考 ECC |
| 完成信號 | 掃描完成後寫入 OMNIHEAL_SCAN_COMPLETE 標記 | 無歧義終止判斷，參考 ECC continuous-claude |
| scan_plan.md next: 欄位 | 每次更新進度時寫入下一步指令 | 恢復後無需推算，直接照做，參考 ARIS |
| scan_plan.md last_updated: | Agent 每次寫入自動更新時間戳 | 讓使用者判斷掃描是否卡住，參考 ARIS |
| 跨掃描 findings.md | progress/ 頂層，跨多次掃描的學習累積 | 與 session_log 分離，參考 ARIS |
| Context Narrowing 恢復 | 只讀 scan_plan + findings_index 末 20 行 + session_log 末 10 行 | 防止 context pollution，參考 ARIS |
| 發現驗證標記 | ✓ VERIFIED / ? INFERRED / ✗ UNCERTAIN 三級標記，? INFERRED 不得輸出 | 杜絕 80% 假聲明率，參考 CC-v3 claim-verification rule |
| 跨掃描學習萃取 | 每次掃描結束萃取結構性學習到 findings.md；新 session 只讀精煉版 | "Compound not Compact" 原則，CC-v3 驗證 ARIS 設計 |

---

## 11. 研究隔離機制

使用者提供參考 repo 網址後：

```
1. git clone <參考repo> OmniHeal/research/<repo名稱>/
2. Agent 依照 reference/DISTILLATION_GUIDE.md 的 SOP 研究並評估
3. 將精華導入本專案，更新 reference/RATIONALE.md 記錄決策
4. research/ 永遠在 .gitignore，不提交
```

`.gitignore`：
```
research/
*.pyc
__pycache__/
.env
```

---

## 12. 里程碑與驗收條件

### Milestone 1：骨架 + 所有 .md 文件
- [ ] 建立完整目錄結構
- [ ] 寫完 `LAUNCH.md`（包含 5-Question Reboot Test 與 Session Recovery 步驟）
- [ ] 寫完 `phases/phase0_bootstrap.md`
- [ ] 寫完 `phases/phase1_scanner.md`（包含 3-Strike Protocol 詳細說明）
- [ ] 寫完三個 `skills/*.md`
- [ ] 寫完 `templates/constitution_base.md`
- [ ] 建立空的 `progress/scan_plan.md`（含格式說明）
- [ ] `.gitignore` 正確排除 `research/`
- **驗收**：Agent 讀 `@OmniHeal/LAUNCH.md` 後能理解完整工作流程，並知道如何恢復中斷的掃描

### Milestone 2：`probe.py` 實作
- [ ] 實作 `src/probe.py`（目錄統計、純文字檔清單、二進位檔過濾）
- **驗收**：`python OmniHeal/src/probe.py . --list-files` 輸出純文字檔清單，無二進位檔

### Milestone 3：Phase 0 完整流程
- [ ] Agent 讀 `phase0_bootstrap.md` 後，完整執行環境探測
- [ ] 生成 `progress/constitution.md`
- [ ] `progress/scan_plan.md` 顯示 Phase 0 complete
- **驗收**：constitution.md 內容能反映目標目錄的實際狀況

### Milestone 4：Phase 1 單檔 + 進度追蹤測試
- [ ] Agent 讀 `phase1_scanner.md` 後，對單一檔案完成分析 → 寫入 findings.md + session_log.md
- [ ] 3-Strike Protocol 在模擬失敗時正確運作
- **驗收**：`progress/YYYY-MM-DD-<skill>/findings.md` 出現有意義的分析結果，session_log.md 格式正確

---

## 13. 尚未決定的事項

- Phase 0 互動問答的具體問題設計（3–5 個治理底線問題的內容）
- Omni-Report 最終彙整格式（目前 findings_index.md 即是報告；未來可考慮彙整摘要頁）
- 信心度門檻（80）是否需要讓使用者可配置（目前寫死在 skill 說明中）
- 批次大小（20–30）是否依專案規模自動調整（目前固定）
- 多代理並行（Milestone 4 後再考慮，參考 Understand-Anything 的 5 並發設計）
- Phase 1.5 是否應該作為獨立 Phase 或整合進 Phase 1 結束步驟（目前為可選）
- context 剩餘估算的具體門檻（50% / 20%）是否需要文件化為可調整參數
- 跨掃描 findings.md 的寫入頻率：每次掃描後強制寫入，或只在有值得記錄的發現時才寫
- 是否需要 `progress/findings.md` 的大小上限（避免多次掃描後無限增長）
