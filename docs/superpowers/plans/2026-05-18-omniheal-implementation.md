# OmniHeal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build OmniHeal — a zero-install AI instruction toolkit that, when git-cloned into any target project, enables an AI agent to autonomously perform full project health-check scans from a single natural-language prompt.

**Architecture:** Primarily Markdown instruction files that guide any AI agent through a structured scan pipeline (Phase 0 bootstrap → Phase 1 scan → Phase 1.5 summary), plus one Python helper script (`probe.py`) for deterministic directory scanning. The agent IS the analysis engine — no second model or external API required.

**Tech Stack:** Markdown (agent instructions), Python 3 (probe.py only, stdlib only — zero dependencies)

---

## File Structure

Files to create (all under `D:\Myproject\OmniHeal\`):

| File | Purpose |
|------|---------|
| `LAUNCH.md` | Single entry point: agent reads this and takes over |
| `phases/phase0_bootstrap.md` | Phase 0 detailed instructions (bootstrap + governance) |
| `phases/phase1_scanner.md` | Phase 1 + 1.5 detailed instructions (scan + summary) |
| `skills/skill_code_lint.md` | Code health-check skill |
| `skills/skill_log_parse.md` | Log analysis skill |
| `skills/skill_text_align.md` | AI transcription error detection skill |
| `templates/constitution_base.md` | Governance rules template (Phase 0 fills this in) |
| `progress/scan_plan.md` | Scan state file (starter template) |
| `progress/findings.md` | Cross-scan learning accumulator (starts empty) |
| `src/probe.py` | Deterministic directory scanner |
| `tests/test_probe.py` | Tests for probe.py |
| `README.md` | Human-readable overview |

Files already exist — do NOT overwrite:
- `.gitignore` (has `research/` exclusion)
- `reference/RATIONALE.md`
- `reference/DISTILLATION_GUIDE.md`
- `docs/superpowers/specs/2026-05-18-omniheal-design.md`

---

## Task 1: Directory Scaffold + README.md

**Files:**
- Create dirs: `phases/`, `skills/`, `templates/`, `progress/`, `src/`, `tests/`
- Create: `README.md`
- Create: `progress/findings.md` (empty accumulator)

- [ ] **Step 1: Create directories**

On Windows PowerShell:
```powershell
New-Item -ItemType Directory -Force phases, skills, templates, progress, src, tests | Out-Null
```

- [ ] **Step 2: Write README.md**

Write the following content to `README.md`:

```markdown
# OmniHeal

**Zero-install AI project health-check toolkit.**

Git-clone OmniHeal into any project, then tell any AI coding agent:
> "請閱讀 @OmniHeal 開始進行"

The agent reads `LAUNCH.md` and autonomously scans your project overnight.

## Usage

```bash
# Step 1: Clone OmniHeal into your project
cd your-project/
git clone <omniheal-repo-url> OmniHeal/

# Step 2: Tell any AI agent (Claude, Copilot, etc.)
"請閱讀 @OmniHeal 開始進行"
# Or more specific:
"請閱讀 @OmniHeal，對 ./src 目錄執行程式碼健檢，使用 code_lint 技能"
```

The agent handles everything from there.

## What It Does

| Phase | What happens |
|-------|-------------|
| Phase 0 | Scans directory structure, asks 1–3 governance questions, creates `progress/constitution.md` |
| Phase 1 | Scans every text file in batches of 20–30, writes findings to `progress/YYYY-MM-DD-<skill>/` |
| Phase 1.5 | Cleans up findings, produces `progress/YYYY-MM-DD-<skill>/summary.md` |

## Skills

| Skill | Use for |
|-------|---------|
| `skill_code_lint` | Code files: naming, security risks, outdated patterns |
| `skill_log_parse` | Log files: format inconsistency, high-frequency errors, anomalies |
| `skill_text_align` | Transcripts: AI transcription errors, wrong homophones, brand name mistakes |

## Key Design Principles

- **Zero install**: only dependency is Python 3 (stdlib only)
- **Never aborts**: 3-Strike Protocol ensures a single file failure never stops the scan
- **False-positive first**: only reports findings with `✓ VERIFIED` (file read) + confidence >= 80
- **Resumable**: interrupted scans resume from `progress/scan_plan.md`'s `next:` field
```

- [ ] **Step 3: Write progress/findings.md (empty accumulator)**

Write the following content to `progress/findings.md`:

```markdown
# OmniHeal 跨掃描發現紀錄

> 此檔案記錄關於目標專案的結構性學習，在多次掃描間持久保存。
> 每次掃描結束後追加新段落（surgical append，不重寫歷史）。
> 格式：## [YYYY-MM-DD] <目標目錄>（<技能>）

<!-- 第一次掃描完成後，在此追加發現摘要 -->
```

- [ ] **Step 4: Commit**

```bash
git add README.md progress/findings.md
git commit -m "chore: scaffold OmniHeal directory structure and README"
```

---

## Task 2: LAUNCH.md

**Files:**
- Create: `LAUNCH.md`

- [ ] **Step 1: Write LAUNCH.md**

Write the following content to `LAUNCH.md`:

```markdown
# OmniHeal 啟動手冊

## 你是誰、你要做什麼

你是一個 AI 代理（Agent），被要求對某個專案執行「健康檢查」（Health Check）。

OmniHeal 是放進目標專案裡的「AI 代理指令手冊 + 輔助工具箱」。你的任務：
1. 探測目標目錄的結構與性質（Phase 0）
2. 逐一掃描所有文字檔，依照選定技能進行分析（Phase 1）
3. 整合發現，產出結構化報告（Phase 1.5）

**你使用的工具都是標準工具**：讀檔、寫檔、執行 Bash 指令。你不需要呼叫任何外部 API 或第二個模型。你本身就是分析引擎。

**最關鍵的原則**：**掃描永遠不能因為單一檔案失敗而中斷。** 遇到任何錯誤，記錄下來，繼續處理下一個檔案。

---

## ★ 第零步：先確認是否有未完成的工作（必做）

在做任何事之前，**先讀 `progress/scan_plan.md`**。

```
如果 Phase 1 狀態是 in_progress → 恢復上次掃描（見「重啟自我檢查」章節）
如果沒有 scan_plan.md，或所有 Phase 都是 complete → 開始新任務（繼續往下讀）
```

---

## 本次任務（若為新任務）

- **目標目錄**：使用者指定的目錄（例如 `../src`）；若未指定，預設為 OmniHeal 父目錄
- **使用技能**：使用者指定（`skill_code_lint` / `skill_log_parse` / `skill_text_align`）；若未指定，預設為 `skill_code_lint`
- **輸出目錄**：`progress/YYYY-MM-DD-<skill>/`（用今天日期和技能名稱命名）

可用技能：

| 技能名稱 | 適用對象 |
|---------|---------|
| `skill_code_lint` | 程式碼檔案（命名、安全、過時寫法） |
| `skill_log_parse` | 日誌檔案（格式不一致、高頻錯誤、異常） |
| `skill_text_align` | 文字稿（AI 轉錄錯誤、同音字替換） |

---

## 里程碑（依序執行）

1. 閱讀 `phases/phase0_bootstrap.md`，執行環境探測，建立 `progress/constitution.md` 和 `progress/file_index.md`
2. 確認 `progress/scan_plan.md` 的 Phase 0 狀態已標記為 `complete`
3. 閱讀 `phases/phase1_scanner.md`，開始逐批掃描
4. 每完成一個批次，更新 `progress/scan_plan.md` 的 `next:` 與 `last_updated:` 欄位
5. 掃描完成後，執行 Phase 1.5（見 `phases/phase1_scanner.md` 末段），產出 `summary.md`

---

## 重啟自我檢查（中斷後必做）

若掃描中斷後重新啟動，**依序**讀以下最小必要 context（不多讀）：

1. `progress/scan_plan.md` → 看 `next:` 欄位（定向，30 秒）
2. `progress/YYYY-MM-DD-<skill>/findings_index.md` **最後 20 行**（確認最近掃描狀態）
3. `progress/YYYY-MM-DD-<skill>/session_log.md` **最後 10 行**（確認上次做到哪裡）
4. **直接按 `next:` 欄位的指示繼續，無需詢問使用者**

**嚴禁**：恢復時重新讀取所有 `findings/[filename].md` 詳細頁（context pollution，讓你沒有足夠 context 繼續掃描）。

### 5-Question Reboot Test（恢復前自問）

在按照 `next:` 指示繼續前，確認你能回答這 5 個問題：
1. 我在掃描哪個目錄？（從 `scan_plan.md` 讀取）
2. 現在跑到哪個 Phase？（`scan_plan.md` 的 Phase 狀態）
3. 這次的任務目標是什麼？（`scan_plan.md` 的目標目錄與使用技能）
4. 我已經發現了什麼？（`findings_index.md` 的最後 20 行）
5. 我上次做到哪裡？（`session_log.md` 的最後 10 行）

若能回答全部 5 題，直接按 `next:` 繼續，**不需詢問使用者**。

---

## 絕對不能做的事

- ❌ 遇到任何錯誤中斷整個掃描（記錄後繼續，見 Phase 1 的 3-Strike Protocol）
- ❌ 跳過更新 `scan_plan.md` 的 `next:` 與 `last_updated:` 欄位
- ❌ 恢復後詢問使用者「我應該繼續嗎？」（讀 `scan_plan.md` 的 `next:` 即可）
- ❌ 把設定值（目標目錄、技能名稱）寫死在任何地方
- ❌ 恢復時重新讀取所有歷史 findings 詳細頁
- ❌ 輸出 `? INFERRED`（只靠 grep 推斷，未讀原始碼）的發現到 findings
```

- [ ] **Step 2: Verify key sections present**

```bash
python -c "
content = open('LAUNCH.md').read()
sections = ['第零步', '5-Question Reboot Test', '重啟自我檢查', '絕對不能做的事']
missing = [s for s in sections if s not in content]
print('MISSING:', missing) if missing else print('LAUNCH.md OK')
"
```

Expected: `LAUNCH.md OK`

- [ ] **Step 3: Commit**

```bash
git add LAUNCH.md
git commit -m "feat: add LAUNCH.md — single agent entry point with 5-Question Reboot Test"
```

---

## Task 3: phase0_bootstrap.md

**Files:**
- Create: `phases/phase0_bootstrap.md`

- [ ] **Step 1: Write phases/phase0_bootstrap.md**

Write the following content to `phases/phase0_bootstrap.md`:

```markdown
# Phase 0：環境探測與規則建立

**目標**：了解目標專案的性質，建立「治理規則文件」(`progress/constitution.md`) 與「全局檔案索引」(`progress/file_index.md`)。

**完成條件**：`progress/scan_plan.md` 中 Phase 0 狀態為 `complete`，且兩個輸出檔案都已建立。

**動詞型別說明**：`[D]` = 確定性操作（不需 LLM 判斷）；`[S]` = 語意分析（需 LLM）；`[I]` = 互動（暫停等使用者回應）

---

## 執行步驟

### 步驟 1 `[D]`：掃描目標目錄，取得檔案清單

執行：
```bash
python OmniHeal/src/probe.py <目標目錄> --list-files
```

probe.py 輸出格式（每行一個純文字檔，5 個 pipe 分隔欄位）：
```
路徑 | 類型 | 大小 | 複雜度 | 掃描深度
src/auth.py | python | 4.2KB | high | deep
src/utils.py | python | 0.9KB | low | fast
docs/api.md | markdown | 1.1KB | low | fast
```

同時執行以下取得統計：
```bash
python OmniHeal/src/probe.py <目標目錄>
```

### 步驟 2 `[D]`：建立 `progress/file_index.md`

將輸出目錄建立為 `progress/YYYY-MM-DD-<skill>/`（今天日期+技能名稱，例如 `progress/2026-05-18-code_lint/`）。

根據 probe.py --list-files 輸出，建立 `progress/file_index.md`：

```markdown
## 目標專案檔案索引
> 產出時間：[YYYY-MM-DD] | 目標目錄：[目標路徑] | 總計：[N] 個純文字檔

| 路徑 | 類型 | 大小 | 預估複雜度 |
|------|------|------|----------|
| src/auth.py | python | 4.2KB | high |
| src/utils.py | python | 0.9KB | low |
| docs/api.md | markdown | 1.1KB | low |
```

掃描深度對應（供 Phase 1 使用）：
- `high` 複雜度 → `deep` 深度（分段讀取，每段 4000 字元）
- `medium` 複雜度 → `standard` 深度（整體讀取，完整分析標準）
- `low` 複雜度 → `fast` 深度（只做前 3 條最高優先規則）

### 步驟 3 `[S]`：隨機抽取 5 個文字檔，推斷專案性質

從 `file_index.md` 中隨機選取 5 個文字檔，讀取內容，推斷：
- **主要語言**：Python / JavaScript / TypeScript / Go / 混合
- **現有命名風格**：snake_case / camelCase / PascalCase / 混合
- **現有規範**：README 或 .editorconfig 中有無 Code Style 說明
- **安全邊界**：有無認證模組、外部 API 呼叫、資料庫存取

將推斷結果追加到 `progress/YYYY-MM-DD-<skill>/session_log.md`（新建若不存在）：
```
## [ISO時間] phase0 | 隨機抽樣完成 | 主要語言：[語言] | 命名風格：[風格]
```

### 步驟 4 `[S]`：MECE 分解問題空間（若 constitution.md 不存在）

**若 `progress/constitution.md` 已存在，跳過步驟 4 和 5，直接到步驟 6。**

根據步驟 3 的推斷，對目標專案的問題空間做 MECE 分解，找出最重要的 1–3 個治理維度：

**MECE 要求：**
- **互斥**（Mutually Exclusive）：任意兩個維度不能問同一個面向
  - ❌ 錯誤：「你用 snake_case？」和「命名慣例是什麼？」→ 同一維度
  - ✅ 正確：「命名慣例」和「錯誤處理策略」→ 不同維度
- **集體窮盡**（Collectively Exhaustive）：這組維度合起來必須涵蓋目標專案最關鍵的治理面向

**常見治理維度（從以下選出最相關的 1–3 個）：**
- 命名慣例（函式、變數、類別的命名風格）
- 錯誤處理策略（是否強制 try/except、異常傳播規則）
- 安全邊界（哪些模組處理外部輸入，需特別審查）
- 程式碼長度限制（函式行數上限、檔案行數上限）
- 日誌格式（何時必須記錄日誌，用什麼格式）
- 測試覆蓋率要求（哪些功能必須有測試）

**MECE 自檢（詢問使用者前先做）：**
1. 「這組問題有沒有維度重疊？」
2. 「是否有明顯更重要的治理維度被遺漏？」

若自檢不通過，調整問題後再繼續。

### 步驟 5 `[I]`：詢問使用者治理問題

每個維度問一個問題，共 1–3 個問題。暫停等待使用者回答。

**問題格式範例：**

命名慣例：「關於**命名慣例**：這個專案的 Python 函式和變數命名，使用 snake_case 還是 camelCase？有沒有例外？」

錯誤處理：「關於**錯誤處理**：這個專案對 Exception 的態度是什麼？所有函式都要 try/except，還是讓異常向上傳播？」

安全邊界：「關於**安全邊界**：哪些目錄或模組處理外部輸入（使用者輸入、外部 API 回應）？是否有需要重點審查的部分？」

收到使用者回答後繼續到步驟 6。

### 步驟 6 `[D]`：建立 `progress/constitution.md`

根據 `OmniHeal/templates/constitution_base.md` 模板，填入以下資訊後儲存為 `progress/constitution.md`：
- 目標目錄、主要語言、掃描日期（來自步驟 1–2）
- 命名慣例、錯誤處理、安全邊界（來自步驟 5 使用者回答）
- 掃描排除清單：根據步驟 3 判斷的非業務目錄（vendor/、node_modules/ 等）
- 備註：步驟 3 發現的重要背景資訊

對使用者未回答的欄位，填入「未指定，依 [推斷結果] 處理」。

### 步驟 7 `[D]`：初始化輸出目錄並建立 findings_index.md

建立 `progress/YYYY-MM-DD-<skill>/findings_index.md`：

```markdown
## 掃描發現索引
> 掃描時間：[YYYY-MM-DD] | Skill：[skill名稱] | 進度：0/[M]

| 檔案 | 嚴重程度 | 主要發現摘要 | 詳細頁 |
|------|---------|------------|-------|
```

（Phase 1 以 surgical append 方式逐行加入，不重寫此標頭）

### 步驟 8 `[D]`：更新 `progress/scan_plan.md`，標記 Phase 0 完成

更新 `progress/scan_plan.md`（若不存在則新建，使用 `OmniHeal/progress/scan_plan.md` 的格式）：

```markdown
## 當前掃描任務
- 目標目錄：[目標路徑]
- 使用技能：[skill名稱]
- 開始時間：[YYYY-MM-DD HH:MM]
- last_updated：[YYYY-MM-DD HH:MM]
- 輸出目錄：progress/[YYYY-MM-DD-skill]/

## Phase 狀態
- Phase 0（環境探測）：complete
- Phase 1（全域掃描）：pending
- Phase 1.5（發現清理）：pending

## next
執行 Phase 1：閱讀 OmniHeal/phases/phase1_scanner.md，從批次 1 開始

## 追蹤欄位
- last_finding_number：0
- last_updated：[YYYY-MM-DD HH:MM]
```

---

## Phase 0 完成檢查

在繼續 Phase 1 前，確認：
- [ ] `progress/file_index.md` 存在且有資料列
- [ ] `progress/constitution.md` 存在且已填寫治理規則（不是空白模板）
- [ ] `progress/scan_plan.md` 的 Phase 0 狀態為 `complete`
- [ ] `progress/YYYY-MM-DD-<skill>/findings_index.md` 已建立（含表頭）
- [ ] `progress/YYYY-MM-DD-<skill>/session_log.md` 已建立（含步驟 3 的紀錄）
```

- [ ] **Step 2: Verify**

```bash
python -c "
content = open('phases/phase0_bootstrap.md').read()
checks = ['MECE 要求', '步驟 5', '[I]', 'Phase 0 完成檢查', 'MECE 自檢']
missing = [c for c in checks if c not in content]
print('MISSING:', missing) if missing else print('phase0_bootstrap.md OK')
"
```

Expected: `phase0_bootstrap.md OK`

- [ ] **Step 3: Commit**

```bash
git add phases/phase0_bootstrap.md
git commit -m "feat: add phase0_bootstrap.md — MECE governance questions and file_index generation"
```

---

## Task 4: phase1_scanner.md

**Files:**
- Create: `phases/phase1_scanner.md`

- [ ] **Step 1: Write phases/phase1_scanner.md**

Write the following content to `phases/phase1_scanner.md`:

```markdown
# Phase 1：夜間全域掃描

**目標**：無人值守掃描所有目標檔案，對每個檔案執行選定技能的分析，產出結構化報告。

**完成條件**：所有批次掃描完畢，`scan_plan.md` Phase 1 狀態為 `complete`。

**動詞型別說明**：`[D]` = 確定性；`[S]` = 語意分析；`[I]` = 互動

---

## 執行步驟

### 步驟 1 `[D]`：讀取 file_index.md，依複雜度排序

讀取 `progress/file_index.md`，依 `預估複雜度` 欄位排序：high > medium > low。

先掃描高複雜度檔案，確保 context 充足時處理最需要深度分析的部分。

### 步驟 2 `[D]`：制定批次計畫

將待掃描檔案依 **20–30 個一批** 分組。更新 `progress/scan_plan.md`：

```markdown
## Phase 1 批次計畫
- 總批次：[N] 批
- 每批檔案數：20–30 個
- 總檔案數：[M] 個

## next
開始批次 1（第 1–30 個檔案，從 [第一個檔案路徑] 開始），深度：standard

## 追蹤欄位
- last_finding_number：0
- last_updated：[YYYY-MM-DD HH:MM]
```

### 步驟 3：Context Budget 安全閘（每批**開始前**執行）

主觀評估目前剩餘 context：

| Context 剩餘 | 行動 |
|------------|-----|
| **> 50%** | 繼續 `standard` 或 `deep` 深度（依 file_index.md 的複雜度欄位） |
| **20–50%** | 全部降級至 `fast` 深度，繼續掃描 |
| **< 20%** | 立即更新 `scan_plan.md` 的 `next:` 欄位，停止本 session |

**停止時 `next:` 欄位範例：**
```
繼續批次 4（第 61–90 個檔案，從 src/payment/checkout.py 開始），深度：standard
```

**嚴禁**：在 context < 20% 時繼續高深度掃描（輸出品質急劇下降，不如乾淨重啟）。

### 步驟 4：逐批掃描主迴圈

#### 4a `[D]`：讀取本批次前置資料（每批一次）

1. 讀取 `OmniHeal/skills/<選定技能>.md`（取得分析標準與輸出格式）
2. 讀取 `progress/constitution.md` **前 30 行**（治理底線參考，不多讀）

#### 4b：對每個檔案執行掃描（3-Strike Protocol 保護）

根據 `file_index.md` 的複雜度決定掃描深度：

| 深度 | 觸發條件 | 做法 |
|-----|---------|-----|
| `fast` | 複雜度 low 或 context < 30% | 只套用 skill 分析標準的**前 3 條**最高優先規則 |
| `standard` | 複雜度 medium（預設） | 完整執行 skill 的所有分析標準 |
| `deep` | 複雜度 high | 分段讀取（每段 <= 4000 字元），每段獨立套用 skill，結果合併去重 |

**3-Strike Protocol 執行流程：**

```
★ 嘗試 1：
  [D] 讀取檔案（依深度決定分段或整體）
  [S] 依 skill 分析標準逐條檢查
  → 成功：進入 Claim Verification（步驟 4c）
  → 失敗：記錄錯誤到 session_log，執行嘗試 2

★ 嘗試 2（失敗後）：
  [S] 執行「Level-2 方向自檢」：
      自問：「我現在的方式是根本方向錯誤，還是只是參數調整？」
      ‣ 根本方向錯誤（如：用 UTF-8 讀 Latin-1 檔案）
        → 換完全不同策略（如：先 detect encoding）
      ‣ 只是參數調整（如：嘗試不同 codec 組合）
        → 仍算嘗試 2，完整換策略後才算嘗試 3
      原則：在錯誤方向上堅持比停下來更糟糕
  換策略後重試
  → 成功：進入 Claim Verification
  → 失敗：執行嘗試 3

★ 嘗試 3（再失敗）：
  [D] 在 session_log.md 標記「永久跳過：[具體原因]」
  原因必須具體：
    ✅ 「編碼不支援（UTF-8 / UTF-16 / Latin-1 均失敗）」
    ✅ 「非純文字檔（讀取返回二進位內容）」
    ✅ 「超過大小上限（>1MB）」
    ❌ 「無法分析」（過於模糊，不允許）
  [D] 在 findings_index.md 追加：
      | [檔案路徑] | ⏭️ skipped | [具體原因] | — |
  繼續下一個檔案（任何情況下不允許整個掃描中斷）
```

#### 4c：Claim Verification（每個潛在問題必做）

對分析中發現的每個潛在問題，確認驗證狀態：

| 狀態 | 含義 | 能否輸出 |
|------|------|---------|
| `✓ VERIFIED` | 已讀原始檔案，確認問題存在於指定 file:line | 還需 confidence >= 80 |
| `? INFERRED` | 只憑 grep / 模式推斷，未讀原始碼確認 | 不得輸出為 finding |
| `✗ UNCERTAIN` | 尚未調查 | 不得輸出 |

**輸出條件**：`✓ VERIFIED` **且** `confidence >= 80`，缺一不可。

`? INFERRED` 的處理：記入 session_log 的 `inferred:` 條目，供後續手動確認：
```
## [時間] inferred | src/auth.py | ? INFERRED：第 23 行疑似 SQL 拼接（未讀原始碼，不輸出）
```

#### 4d `[D]`：記錄發現

**有符合條件的發現（`✓ VERIFIED` + confidence >= 80）：**

1. 從 `scan_plan.md` 的 `last_finding_number:` 讀取當前編號 N，新發現用 N+1
2. 建立或更新 `progress/YYYY-MM-DD-<skill>/findings/[filename].md`：

```markdown
---
file: src/auth/login.py
type: python
scanned: 2026-05-18
skill: code_lint
severity: high
confidence: 92
status: new
---

## 發現詳情

#1 src/auth/login.py:23 — SQL 字串拼接（severity:high, confidence:92）[✓ VERIFIED]
   問題：第 23 行直接將使用者輸入拼入 SQL 字串：`query = "SELECT * FROM users WHERE id=" + user_id`
   建議：改用參數化查詢：`cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))`
   ⚠️ Pattern Alert：SQL 注入通常為系統性問題，建議掃描 src/auth/ 和 src/api/ 下所有資料庫存取點
```

3. 在 `findings_index.md` 追加（surgical append，不重寫）：
```
| src/auth/login.py | 🔴 high | SQL 字串拼接、未處理例外 | [詳細](findings/login_py.md) |
```

4. 更新 `scan_plan.md` 的 `last_finding_number:` 為最新 N。

**Pattern Alert 條件**（同時滿足才加）：
- severity:high
- confidence >= 85
- 必須具體指出建議掃描的目錄或類型（不得寫「請查看相關檔案」）

**無符合條件的發現：**
在 `findings_index.md` 追加：
```
| src/utils/format.py | ✅ clean | 無問題 | — |
```
**不建立詳細頁**。

**每個檔案處理後**，追加一行到 `session_log.md`：
```
## [ISO時間] scan | src/auth/login.py | severity:high | 2 個發現（#1, #2）
## [ISO時間] scan | src/utils/format.py | clean | 0 個發現
## [ISO時間] skip | src/binary.dat | 3-Strike：非純文字檔
## [ISO時間] retry | src/legacy.py | 嘗試 2：換 latin-1 編碼成功
## [ISO時間] inferred | src/api.py | ? INFERRED：疑似 SQL 拼接（未讀原始碼）
```

#### 4e `[D]`：批次結束後更新 scan_plan.md

每批處理完畢後：
```markdown
## Phase 狀態
- Phase 1（全域掃描）：in_progress（批次 [N]/[Total]，已處理 [M]/[Total] 個檔案）

## next
繼續批次 [N+1]（第 [X]–[Y] 個檔案，從 [下個檔案路徑] 開始），深度：[standard]

## 追蹤欄位
- last_finding_number：[當前最大編號]
- last_updated：[YYYY-MM-DD HH:MM]
```

### 步驟 5 `[D]`：Phase 1 完成後標記

所有批次完畢後：
```markdown
## Phase 狀態
- Phase 1（全域掃描）：complete（共 [M] 個檔案，跳過 [S] 個）

## 跳過統計
- 編碼問題：[N] 個
- 非純文字：[N] 個
- 超大檔案（>1MB）：[N] 個

## next
執行 Phase 1.5：讀取 findings_index.md 和 findings/ 詳細頁，產出 summary.md
```

---

## Phase 1.5：發現清理（建議執行）

**目標**：用乾淨的 context（不重新讀原始檔案）整合 Phase 1 原始發現，產出 executive summary。

### 步驟 0 `[S]`：Conclusion Integrity 自檢（寫任何結論前先做）

在開始撰寫 `summary.md` 前，明確回答以下 4 個問題：

1. **資料來源**：結論基於 findings_index.md 和 findings/ 詳細頁，而非原始碼直接推斷
2. **時間範圍**：本次掃描（日期 [X]），或只有部分批次？
3. **樣本 vs 全量**：已掃描 [N] 個檔案 / 目標目錄共 [M] 個檔案
4. **其他可能性**：高嚴重度發現是否可能有假陽性（測試環境、版本差異、已知技術債）？

若掃描未完成（N < M），summary.md 開頭**必須加上**：
```
⚠️ 基於部分資料（掃描進度：N/M 個檔案）
```

**禁用詞**：「確定」「一定是」「根本原因是」。  
**改用**：「初步證據指向…，待確認 [具體確認方法]」。

### 步驟 1–5 `[D/S]`：清理發現

1. `[D]` 讀取 `findings_index.md`（全部條目）
2. `[D]` 讀取所有 `findings/[filename].md`（詳細頁）
3. `[S]` 合併重複發現（同一問題被不同批次各報告一次）
4. `[S]` 移除 confidence 在 75–79 之間的邊界案例（提升整體精確度）
5. `[D]` 重新計算統計：高嚴重度 N 個、中嚴重度 N 個、跳過 N 個

### 步驟 6 `[D]`：產出 summary.md

儲存到 `progress/YYYY-MM-DD-<skill>/summary.md`：

```markdown
# 掃描摘要
> Skill: [skill名稱] | 日期: [YYYY-MM-DD] | 總計: [M] 個檔案

<!-- 若掃描未完成，加上此行 -->
⚠️ 基於部分資料（掃描進度：[N]/[M] 個檔案）

## 統計
- 🔴 高嚴重度：[N] 個（[N] 個檔案）
- 🟡 中嚴重度：[N] 個（[N] 個檔案）
- ✅ 無問題：[N] 個檔案
- ⏭️ 已跳過：[N] 個（原因分佈：編碼問題 [N] 個、非純文字 [N] 個）

## 優先修復（高嚴重度摘要）
#[N] [file:line] — [問題描述]（confidence:[分數]）
#[N] [file:line] — [問題描述]（confidence:[分數]）

## 已跳過檔案清單
| 檔案 | 跳過原因 |
|------|---------|
| [路徑] | [具體原因] |
```

### 步驟 7 `[D]`：寫入完成信號

在 `scan_plan.md` 末尾追加（surgical append，不覆蓋）：
```
OMNIHEAL_SCAN_COMPLETE | [YYYY-MM-DD HH:MM] | [M] 個檔案 | 高嚴重度 [N] 個
```

此信號讓使用者和外部監控無歧義判斷掃描是否完成（區別於「中途停止待恢復」）。

---

## Phase 1.5 完成後：更新跨掃描學習

在 `progress/findings.md` 末尾追加本次掃描的結構性學習（surgical append）：

```markdown
## [YYYY-MM-DD] [目標目錄]（[skill名稱]）
- [學習 1：例如「src/legacy/ 佔總 high findings 的 60%；下次可針對此目錄用 deep 深度」]
- [學習 2：例如「命名風格混用（camelCase/snake_case）；constitution.md 已更新規則」]
```

只記錄對**下次掃描有用**的結構性洞見，不重複 summary.md 的統計數字。
```

- [ ] **Step 2: Verify**

```bash
python -c "
content = open('phases/phase1_scanner.md').read()
checks = ['3-Strike Protocol', 'Level-2 方向自檢', 'Claim Verification', 'Conclusion Integrity', 'OMNIHEAL_SCAN_COMPLETE', '? INFERRED']
missing = [c for c in checks if c not in content]
print('MISSING:', missing) if missing else print('phase1_scanner.md OK')
"
```

Expected: `phase1_scanner.md OK`

- [ ] **Step 3: Commit**

```bash
git add phases/phase1_scanner.md
git commit -m "feat: add phase1_scanner.md — scan loop, 3-Strike, Claim Verification, Phase 1.5"
```

---

## Task 5: skill_code_lint.md

**Files:**
- Create: `skills/skill_code_lint.md`

- [ ] **Step 1: Write skills/skill_code_lint.md**

Write the following content to `skills/skill_code_lint.md`:

```markdown
# Skill：code_lint — 程式碼健檢

**用途**：識別程式碼中的命名不一致、過時寫法、潛在錯誤、安全風險。  
**適用對象**：任何純文字程式碼檔案（Python、JavaScript、TypeScript、Go、Java 等）。

---

## Skill 邊界

**負責（scope.in）：**
- 命名不一致（不符語言慣例的識別符命名）
- 函式過長（超過 50 行的函式）
- 潛在安全風險（SQL 注入、硬編碼密碼/API Key、不安全的反序列化）
- 未處理的異常（catch/except 區塊為空或只有 pass）
- 過時寫法（Python 2 print 語句、已棄用 API）
- 硬編碼設定值（IP、端口、路徑、憑證）

**不負責（scope.out）：**
- ❌ 效能最佳化建議（除非有可量化的 O(n^2) 循環等具體問題）
- ❌ 架構建議（「這個模組應該拆開」）
- ❌ 業務邏輯正確性（無法從程式碼判斷邏輯是否符合需求）
- ❌ 不報告「這個設計可以更好」（沒有客觀標準）
- ❌ 不報告「這段邏輯感覺有問題」（感覺不是證據）
- ❌ confidence < 80 的推測
- ❌ `? INFERRED`（grep 推斷，未讀原始碼）的發現

**誤報優先原則（False-Positive Avoidance）：**
> 寧可漏掉一個真正的問題，也不要輸出一個沒有證據的推測。
> 每個發現必須能回答：「我讀了哪行原始碼，看到什麼，根據什麼標準判斷這是問題。」
> grep 找到模式 != 問題存在；必須讀原始檔案確認（✓ VERIFIED）。

---

## 分析標準（原子化規則）

每條規則通過 Atomic Finding 5-question 自檢（只有一個主體、一個對象、一個動作、一個條件、一個結果）。

`fast` 深度只執行前 3 條（優先順序由高到低排列）：

### 規則 1：硬編碼密碼或 API Key（優先順序：最高）
- **標準**：非測試、非示例檔案中，字串賦值包含疑似密碼/金鑰的模式
  - `password = "xxx"` / `api_key = "sk-..."` / `secret = "..."` / `token = "..."` 等
- **排除**：
  - 測試檔案中明確標注的假資料（`test_password = "test123"` 在 `test_*.py` 中）
  - 空字串賦值（`password = ""`）
  - 從環境變數讀取（`password = os.getenv("DB_PASSWORD")`）
- **severity**：high | **confidence 閾值**：85

### 規則 2：SQL 字串拼接（注入風險）（優先順序：最高）
- **標準**：SQL 查詢字串使用字串格式化或拼接（`%s %` format、f-string 插入、`+` 拼接）而非參數化查詢
- **排除**：
  - 字串本身不包含任何變數（純靜態查詢字串）
  - 已使用 ORM 的 filter/query 方法（不直接拼 SQL）
- **severity**：high | **confidence 閾值**：85

### 規則 3：未處理的異常（空 catch/except）（優先順序：高）
- **標準**：`except:` 或 `catch` 區塊中只有 `pass`、`continue`，或完全空白
- **排除**：
  - 有明確 `log()`/`logger.`/`raise`/`return` 的 catch 區塊
  - 有 `# intentionally ignored` 類的明確說明注釋
- **severity**：high | **confidence 閾值**：80

### 規則 4：Python 函式命名不符 snake_case（優先順序：中）
- **標準**：Python 函式定義（`def`）使用 camelCase 或 PascalCase
  - `def doLogin(...)` / `def DoLogin(...)` → 不符合
- **排除**：
  - 類別定義（class 允許 PascalCase）
  - 從外部 library 繼承 override 的方法（如 Django 的 `setUp`）
  - 有 `# noqa` 或 `# type: ignore` 的行
- **severity**：medium | **confidence 閾值**：80

### 規則 5：函式超過 50 行（優先順序：中）
- **標準**：從 `def`/`function`/`func` 到函式結尾的行數超過 50
- **排除**：
  - 測試函式（`test_`、`spec_`、`it_` 開頭）
  - 有 `# generated` / `# auto-generated` 注釋的函式
- **severity**：medium | **confidence 閾值**：90（行數是確定性指標，信心度高）

### 規則 6：硬編碼的 IP 位址（優先順序：中）
- **標準**：非設定檔、非測試檔中出現 IPv4 位址字串（如 `"192.168.1.1"`）
- **排除**：
  - 本機位址（`127.0.0.1`、`0.0.0.0`、`localhost`）在開發設定中
  - 位址在文件字串（docstring）或注釋中
- **severity**：medium | **confidence 閾值**：80

### 規則 7：Python 2 print 語句（優先順序：低）
- **標準**：在 `.py` 檔案中出現 `print "..."` 形式（不帶括號的 Python 2 語法）
- **排除**：
  - 位於字串中的 print 說明（如 docstring 中引用 Python 2 語法的說明文字）
  - 已有 `from __future__ import print_function` 的檔案
- **severity**：medium | **confidence 閾值**：90（語法明確）

---

## 輸出格式

分析完一個檔案後，針對每個符合條件的原子化發現輸出一條：

```
#N file/path.py:行號 — 問題描述（severity:level, confidence:分數）[✓ VERIFIED]
   問題：[具體描述，引用原始碼片段，包含行號]
   建議：[一個具體的修正方向]
   ⚠️ Pattern Alert：[可選] 此問題類型通常為系統性問題，建議掃描 [具體目錄/檔案類型]
```

**規則：**
- `#N`：從 `scan_plan.md` 的 `last_finding_number:` 讀取，每個新發現後 +1 並更新
- `[✓ VERIFIED]`：必填標記，代表已讀原始檔案確認（非 grep 推斷）
- confidence < 80：**不輸出此條**，直接略過
- `? INFERRED`（未讀原始碼）：**不輸出為 finding**；記入 session_log 的 `inferred:` 條目
- `⚠️ Pattern Alert`：僅限 severity:high + confidence >= 85；必須具體指出目錄或類型

**若整個檔案無任何 confidence >= 80 的發現**：在 `findings_index.md` 標記為 `✅ clean`，**不建立詳細頁**。
```

- [ ] **Step 2: Commit**

```bash
git add skills/skill_code_lint.md
git commit -m "feat: add skill_code_lint.md — 7 atomic rules with confidence thresholds"
```

---

## Task 6: skill_log_parse.md

**Files:**
- Create: `skills/skill_log_parse.md`

- [ ] **Step 1: Write skills/skill_log_parse.md**

Write the following content to `skills/skill_log_parse.md`:

```markdown
# Skill：log_parse — 日誌解析健檢

**用途**：從雜亂的日誌檔中萃取有用情報，識別格式不一致、高頻錯誤、安全異常。  
**適用對象**：任何純文字日誌檔（.log、.txt、stdout 重導向等）。

---

## Skill 邊界

**負責（scope.in）：**
- 認證失敗高頻出現（可能的暴力破解或設定錯誤）
- 時間戳格式不一致（同一日誌中混用多種時間格式）
- 日誌行缺少時間戳（無法確定發生時間）
- 高頻重複錯誤（同一錯誤訊息出現超過 5 次）
- 異常時間空白（兩條日誌間隔超過 30 分鐘）

**不負責（scope.out）：**
- ❌ 業務邏輯正確性（無法從日誌推斷業務邏輯是否正確）
- ❌ 效能最佳化建議（日誌健檢不負責推斷系統效能）
- ❌ 不報告「日誌量太多」（沒有客觀標準）
- ❌ confidence < 80 的推測
- ❌ `? INFERRED`（未引用具體日誌行號）的發現

**誤報優先原則（False-Positive Avoidance）：**
> 日誌分析特別容易誤報：測試日誌、開發環境日誌、已知的暫時性錯誤都可能造成假陽性。
> 每個發現必須引用具體的日誌行號和原始日誌文字。

---

## 分析標準（原子化規則）

`fast` 深度只執行前 3 條：

### 規則 1：認證失敗高頻出現（優先順序：最高）
- **標準**：30 分鐘內出現超過 10 次包含以下關鍵字的日誌行：
  `authentication failed`、`login failed`、`unauthorized`、`401`、`403`
- **排除**：
  - 有明確「test suite」或「testing」標記的日誌段落
  - 單次系統重啟後的短暫重試（需要有後續成功的認證記錄）
- **severity**：high | **confidence 閾值**：85

### 規則 2：時間戳格式不一致（優先順序：高）
- **標準**：同一日誌檔中出現兩種或以上不同的時間戳格式
  - 例：`2026-05-18 22:01:00` 和 `18/May/2026:22:01:00` 混用
- **排除**：
  - multiline stack trace 的續行（沒有時間戳是正常的）
- **severity**：medium | **confidence 閾值**：80

### 規則 3：日誌行缺少時間戳（優先順序：高）
- **標準**：超過 5 行資料行（非空白、非明顯注釋）缺少時間戳格式
- **排除**：
  - 已知的 multiline 日誌格式（stack trace 續行、JSON 展開）
  - 檔案開頭的 header 行
- **severity**：medium | **confidence 閾值**：80

### 規則 4：高頻重複錯誤（優先順序：中）
- **標準**：去除時間戳後，同一錯誤訊息（或高度相似的訊息）在日誌中出現超過 5 次
- **排除**：
  - 已知的定期任務輸出（如 cron job 的心跳訊息）
- **severity**：medium | **confidence 閾值**：85

### 規則 5：異常時間空白（優先順序：中）
- **標準**：兩條有時間戳的日誌行之間間隔超過 30 分鐘（可能代表服務中斷）
- **排除**：
  - 日誌的開頭或結尾的空白期（夜間靜默是正常的）
- **severity**：medium | **confidence 閾值**：75
  - 注意：此規則 confidence 閾值為 75，低於 80 輸出條件。若無其他佐證，以 `? INFERRED` 記入 session_log，**不輸出為 finding**

---

## 輸出格式

```
#N logs/app.log:行號範圍 — 問題描述（severity:level, confidence:分數）[✓ VERIFIED]
   問題：[具體描述，引用相關日誌行內容和行號]
   建議：[一個具體的修正或調查方向]
   ⚠️ Pattern Alert：[可選，僅限 severity:high + confidence >= 85]
```

**注意**：日誌分析的「行號」通常是範圍（如 `logs/app.log:145-172`），因為問題往往涉及多行。
```

- [ ] **Step 2: Commit**

```bash
git add skills/skill_log_parse.md
git commit -m "feat: add skill_log_parse.md — 5 atomic rules for log health-check"
```

---

## Task 7: skill_text_align.md

**Files:**
- Create: `skills/skill_text_align.md`

- [ ] **Step 1: Write skills/skill_text_align.md**

Write the following content to `skills/skill_text_align.md`:

```markdown
# Skill：text_align — 文字稿對齊健檢

**用途**：識別 AI 語音轉錄產生的荒謬錯字、術語替換錯誤、上下文語義不合理的替換。  
**適用對象**：純文字逐字稿檔案（.txt、.md 格式）。

---

## Skill 邊界

**負責（scope.in）：**
- 技術術語被同音字替換（如：「Docker」→「多可」、「API」→「阿 PI」）
- 品牌名稱/產品名稱被轉錄錯誤（如：「GitHub」→「機 Hub」）
- 上下文語義明顯不合理的替換（前後文語境明確說明應為另一個詞）
- 人名因同音錯誤被轉錄為意義不符的字（需有前後文佐證）

**不負責（scope.out）：**
- ❌ 文法改進建議（語法正確但不優雅的表達）
- ❌ 風格改進（用詞選擇偏好）
- ❌ 內容的事實正確性（無法判斷說話者的陳述是否正確）
- ❌ 口頭禪或習慣性贅詞（如「就是說」「然後」）
- ❌ confidence < 80 的推測（文字稿判斷高度依賴上下文）
- ❌ `? INFERRED`（未引用具體行號和原始文字）的發現

**誤報優先原則（False-Positive Avoidance）：**
> 文字稿健檢特別容易誤報：行話、縮寫、創新用詞都可能看起來像錯誤。
> 只報告有充分上下文支撐、有明確「應為何詞」的案例。
> 若不確定「應為何詞」，不報告。

---

## 分析標準（原子化規則）

`fast` 深度只執行前 3 條：

### 規則 1：技術術語同音字替換（優先順序：最高）
- **標準**：在技術討論語境中，技術術語被轉錄為同音的非技術詞，且替換後的詞在技術語境中無意義
  - 判斷依據：前後文有技術討論（程式、系統、工具等語境）
- **排除**：
  - 說話者本人就是用非技術詞描述技術概念（創新用詞）
  - 縮寫或簡稱（如「CI」說成「CI」是正常的）
- **severity**：high | **confidence 閾值**：85

### 規則 2：品牌名稱/產品名稱轉錄錯誤（優先順序：最高）
- **標準**：廣為人知的品牌名（GitHub、PostgreSQL、Python、Claude、Anthropic、Docker）被替換為音似但錯誤的字
  - 判斷依據：前後文有提及該品牌/產品的語境
- **排除**：
  - 說話者明確說「一個叫 XXX 的工具」（不確定品牌名時）
- **severity**：high | **confidence 閾值**：80

### 規則 3：上下文語義明顯不合理（優先順序：高）
- **標準**：替換後的詞在當前句子的語境中語義荒謬，且有明確的「應為何詞」
  - 例：「我們需要在 server 上**部屬**一個新的容器」→「部屬」應為「部署」
- **排除**：
  - 語義雖奇怪但無法確定「應為何詞」的情況（confidence 不足，不報告）
- **severity**：medium | **confidence 閾值**：85

### 規則 4：人名因同音被轉錄錯誤（優先順序：中）
- **標準**：文字稿中出現疑似人名被轉錄為意義不符的字，且有前後文佐證
- **排除**：
  - 只出現一次、無前後文佐證的情況（confidence 不足）
- **severity**：medium | **confidence 閾值**：80

---

## 輸出格式

```
#N transcript.txt:行號 — [錯誤類型]（severity:level, confidence:分數）[✓ VERIFIED]
   問題：原文「[錯誤原文]」疑似應為「[正確版本]」—— 依據：[上下文語境說明，引用前後文]
   建議：將第 [N] 行「[錯誤原文]」更改為「[正確版本]」
```

**注意**：「建議」欄位必須給出確定的替換詞。若無法確定應為何詞，整條發現不輸出（confidence 不足）。
```

- [ ] **Step 2: Commit**

```bash
git add skills/skill_text_align.md
git commit -m "feat: add skill_text_align.md — 4 atomic rules for AI transcription error detection"
```

---

## Task 8: templates/constitution_base.md

**Files:**
- Create: `templates/constitution_base.md`

- [ ] **Step 1: Write templates/constitution_base.md**

Write the following content to `templates/constitution_base.md`:

```markdown
# 治理規則文件（Constitution）

> 本文件由 OmniHeal Phase 0 自動生成，記錄掃描前使用者確認的治理規則。
> 這些規則作為 Phase 1 掃描的「底線」：所有發現以此為基礎判斷問題的嚴重程度。
> 如需更新治理規則，直接編輯 `progress/constitution.md` 後重新執行 Phase 0。

## 基本資訊

- **目標目錄**：[Phase 0 填入]
- **主要語言**：[Phase 0 填入]
- **掃描日期**：[Phase 0 填入]
- **上次更新**：[Phase 0 填入]

---

## 治理規則

### 命名慣例
[Phase 0 根據使用者回答填入。若未回答，填入：「未指定，依語言標準慣例（Python: snake_case 函式/變數，PascalCase 類別）」]

範例：
```
- Python 函式和變數使用 snake_case
- 類別使用 PascalCase
- 常數使用 UPPER_SNAKE_CASE
```

### 錯誤處理規範
[Phase 0 根據使用者回答填入。若未回答，填入：「未指定，依 skill scope.in 的嚴格標準（空 catch/except 視為問題）」]

範例：
```
- 所有外部 IO 操作必須有 try/except
- 捕獲的異常必須記錄到 logger，不允許靜默 pass
```

### 安全邊界
[Phase 0 根據使用者回答填入。若未回答，填入：「未指定，所有處理外部輸入的函式均需重點審查」]

範例：
```
- src/auth/ 模組處理使用者認證，使用 deep 深度掃描
- src/api/ 模組處理外部請求，SQL 查詢必須使用參數化查詢
```

### 掃描排除清單
[Phase 0 根據專案結構填入，預設排除：]

```
- vendor/（第三方程式碼）
- node_modules/（Node.js 依賴）
- .git/（版本控制內部）
- __pycache__/（Python 快取）
- *.min.js（壓縮 JavaScript）
- *.pyc（Python 編譯快取）
```

### 備註
[Phase 0 根據步驟 3 的抽樣推斷填入重要背景資訊]

範例：
```
- src/legacy/ 目錄為計畫廢棄的模組（README 中有說明），findings 嚴重程度可降一級
```

若無特殊背景，填入：「無特殊備註」。
```

- [ ] **Step 2: Commit**

```bash
git add templates/constitution_base.md
git commit -m "feat: add constitution_base.md — governance rules template for Phase 0"
```

---

## Task 9: progress/scan_plan.md Starter Template

**Files:**
- Create: `progress/scan_plan.md`

- [ ] **Step 1: Write progress/scan_plan.md**

Write the following content to `progress/scan_plan.md`:

```markdown
# OmniHeal 掃描狀態

> 此檔案由 OmniHeal Phase 0 自動建立，Phase 1 持續更新。
> Agent 恢復掃描時，**只讀 `next:` 欄位**，直接繼續，不需詢問使用者。
> `last_updated:` 欄位讓使用者判斷掃描是否卡住（超過 30 分鐘沒更新 = 可能中斷）。

## 當前掃描任務
- 目標目錄：（Phase 0 填入）
- 使用技能：（Phase 0 填入）
- 開始時間：（Phase 0 填入）
- last_updated：（Phase 0 填入）
- 輸出目錄：（Phase 0 填入）

## Phase 狀態
- Phase 0（環境探測）：pending
- Phase 1（全域掃描）：pending
- Phase 1.5（發現清理）：pending

## Phase 1 批次計畫
（Phase 1 開始後由 Agent 填入）

## 跳過統計
（Phase 1 完成後由 Agent 填入）

## next
執行 Phase 0：閱讀 OmniHeal/phases/phase0_bootstrap.md，開始環境探測

## 追蹤欄位
- last_finding_number：0
```

- [ ] **Step 2: Commit**

```bash
git add progress/scan_plan.md
git commit -m "feat: add progress/scan_plan.md starter template with next: and tracking fields"
```

---

## Task 10: src/probe.py (TDD)

**Files:**
- Create: `tests/test_probe.py`
- Create: `src/probe.py`

probe.py purpose: deterministically scan a target directory and output text file listings and stats. No third-party dependencies (stdlib only).

- [ ] **Step 1: Write tests/test_probe.py**

Write the following content to `tests/test_probe.py`:

```python
"""Tests for src/probe.py — run from OmniHeal root: python -m pytest tests/"""
import subprocess
import sys
import tempfile
from pathlib import Path


def run_probe(target_dir: str, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "src/probe.py", target_dir, *extra_args],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,  # OmniHeal root
    )


def test_list_files_excludes_known_binary_extensions():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "script.py").write_text("print('hello')")
        Path(tmpdir, "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        Path(tmpdir, "archive.zip").write_bytes(b"PK\x03\x04")

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        assert "script.py" in result.stdout
        assert "image.png" not in result.stdout
        assert "archive.zip" not in result.stdout


def test_list_files_output_has_five_pipe_separated_fields():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "small.py").write_text("x = 1\n")

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        lines = [ln for ln in result.stdout.strip().split("\n") if ln]
        assert len(lines) == 1
        fields = lines[0].split(" | ")
        assert len(fields) == 5, f"Expected 5 fields, got: {lines[0]!r}"
        _path, file_type, size, complexity, depth = fields
        assert "small.py" in _path
        assert file_type == "py"
        assert "KB" in size
        assert complexity in ("low", "medium", "high")
        assert depth in ("fast", "standard", "deep")


def test_complexity_low_maps_to_fast_depth():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "tiny.py").write_text("x = 1\n")  # tiny → low complexity

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        line = result.stdout.strip().split("\n")[0]
        assert line.endswith("fast")


def test_summary_mode_counts_text_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "a.py").write_text("x = 1")
        Path(tmpdir, "b.md").write_text("# doc")
        Path(tmpdir, "c.png").write_bytes(b"\x89PNG\r\n")

        result = run_probe(tmpdir)

        assert result.returncode == 0
        assert "純文字檔" in result.stdout
        assert "2" in result.stdout  # 2 text files


def test_hidden_directories_excluded():
    with tempfile.TemporaryDirectory() as tmpdir:
        hidden_dir = Path(tmpdir, ".git")
        hidden_dir.mkdir()
        (hidden_dir / "config").write_text("repositoryformatversion = 0")
        Path(tmpdir, "visible.py").write_text("x = 1")

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        assert "config" not in result.stdout
        assert "visible.py" in result.stdout


def test_error_on_nonexistent_directory():
    result = run_probe("/nonexistent/path/that/does/not/exist/xyz123")

    assert result.returncode != 0
    assert result.stderr


def test_list_files_excludes_files_larger_than_1mb():
    with tempfile.TemporaryDirectory() as tmpdir:
        big_file = Path(tmpdir, "huge.txt")
        big_file.write_bytes(b"x" * (1024 * 1024 + 1))  # 1MB + 1 byte
        small_file = Path(tmpdir, "small.txt")
        small_file.write_text("hello")

        result = run_probe(tmpdir, "--list-files")

        assert result.returncode == 0
        assert "small.txt" in result.stdout
        assert "huge.txt" not in result.stdout
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_probe.py -v
```

Expected: All tests FAIL (src/probe.py does not exist yet).

- [ ] **Step 3: Write src/probe.py**

Write the following content to `src/probe.py`:

```python
#!/usr/bin/env python3
"""
probe.py — OmniHeal deterministic directory scanner

Usage:
    python probe.py <target_dir>              # Summary stats to stdout
    python probe.py <target_dir> --list-files # One line per text file

Output (--list-files): 5 pipe-separated fields per line:
    path | type | size | complexity | depth

Complexity thresholds:
    > 50KB  → high   → deep
    > 5KB   → medium → standard
    <= 5KB  → low    → fast
"""
import sys
from pathlib import Path

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp",
    ".mp4", ".mp3", ".wav", ".avi", ".mov", ".mkv",
    ".zip", ".gz", ".tar", ".rar", ".7z", ".bz2",
    ".pdf", ".docx", ".xlsx", ".pptx", ".odt",
    ".exe", ".dll", ".so", ".dylib", ".bin",
    ".pyc", ".class", ".jar", ".wasm",
    ".db", ".sqlite", ".sqlite3",
    ".svg",
}

MAX_FILE_SIZE = 1024 * 1024  # 1MB


def _is_text_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return False
    except OSError:
        return False
    try:
        path.read_text(encoding="utf-8", errors="strict")
        return True
    except (UnicodeDecodeError, PermissionError, OSError):
        return False


def _estimate_complexity(path: Path) -> str:
    try:
        size = path.stat().st_size
    except OSError:
        return "low"
    if size > 50_000:
        return "high"
    if size > 5_000:
        return "medium"
    return "low"


_DEPTH = {"high": "deep", "medium": "standard", "low": "fast"}


def _is_hidden(rel: Path) -> bool:
    return any(
        part.startswith(".") or part == "__pycache__"
        for part in rel.parts
    )


def _iter_files(target: Path):
    for p in sorted(target.rglob("*")):
        if p.is_dir():
            continue
        if _is_hidden(p.relative_to(target)):
            continue
        yield p


def _list_files(target: Path) -> None:
    for p in _iter_files(target):
        if not _is_text_file(p):
            continue
        rel = p.relative_to(target)
        size_kb = p.stat().st_size / 1024
        file_type = p.suffix.lstrip(".") or "text"
        complexity = _estimate_complexity(p)
        print(f"{rel} | {file_type} | {size_kb:.1f}KB | {complexity} | {_DEPTH[complexity]}")


def _summary(target: Path) -> None:
    text_count = 0
    binary_count = 0
    skip_count = 0

    for p in sorted(target.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(target)
        if _is_hidden(rel):
            skip_count += 1
            continue
        if _is_text_file(p):
            text_count += 1
        else:
            binary_count += 1

    print(f"目標目錄：{target}")
    print(f"純文字檔：{text_count} 個")
    print(f"二進位/過大：{binary_count} 個")
    print(f"跳過（隱藏/快取）：{skip_count} 個")
    print(f"總計：{text_count + binary_count + skip_count} 個")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python probe.py <target_dir> [--list-files]", file=sys.stderr)
        sys.exit(1)
    target = Path(sys.argv[1])
    if not target.exists():
        print(f"Error: does not exist: {target}", file=sys.stderr)
        sys.exit(1)
    if not target.is_dir():
        print(f"Error: not a directory: {target}", file=sys.stderr)
        sys.exit(1)
    if "--list-files" in sys.argv:
        _list_files(target)
    else:
        _summary(target)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_probe.py -v
```

Expected:
```
tests/test_probe.py::test_list_files_excludes_known_binary_extensions PASSED
tests/test_probe.py::test_list_files_output_has_five_pipe_separated_fields PASSED
tests/test_probe.py::test_complexity_low_maps_to_fast_depth PASSED
tests/test_probe.py::test_summary_mode_counts_text_files PASSED
tests/test_probe.py::test_hidden_directories_excluded PASSED
tests/test_probe.py::test_error_on_nonexistent_directory PASSED
tests/test_probe.py::test_list_files_excludes_files_larger_than_1mb PASSED

7 passed
```

If a test fails:
- `test_list_files_output_has_five_pipe_separated_fields`: verify the print format in `_list_files()` is exactly `f"{rel} | {file_type} | {size_kb:.1f}KB | {complexity} | {_DEPTH[complexity]}"`
- `test_hidden_directories_excluded`: verify `_is_hidden()` checks all parts, not just the last
- `test_list_files_excludes_files_larger_than_1mb`: verify `_is_text_file()` checks `stat().st_size > MAX_FILE_SIZE` **before** reading

- [ ] **Step 5: Manual smoke test**

```bash
python src/probe.py . --list-files
python src/probe.py .
```

Verify: `--list-files` shows `.md` and `.py` files with 5 fields each; no `.git/` entries appear; `pure文字檔` count is nonzero.

- [ ] **Step 6: Commit**

```bash
git add src/probe.py tests/test_probe.py
git commit -m "feat: add probe.py with 7 passing tests — stdlib-only directory scanner"
```

---

## Task 11: Milestone 1 Verification

Verifies the Milestone 1 acceptance criterion: **"Agent 讀 @OmniHeal/LAUNCH.md 後能理解完整工作流程，並知道如何恢復中斷的掃描"**

- [ ] **Step 1: Check all required files exist**

```bash
python -c "
import os
required = [
    'LAUNCH.md', 'README.md',
    'phases/phase0_bootstrap.md', 'phases/phase1_scanner.md',
    'skills/skill_code_lint.md', 'skills/skill_log_parse.md', 'skills/skill_text_align.md',
    'templates/constitution_base.md',
    'progress/scan_plan.md', 'progress/findings.md',
    'src/probe.py', 'tests/test_probe.py',
]
missing = [f for f in required if not os.path.exists(f)]
print('MISSING:', missing) if missing else print('All files present.')
"
```

Expected: `All files present.`

- [ ] **Step 2: Run full test suite**

```bash
python -m pytest tests/ -v
```

Expected: 7 passed.

- [ ] **Step 3: Verify key sections across instruction files**

```bash
python -c "
checks = {
    'LAUNCH.md': ['第零步', '5-Question Reboot Test', '絕對不能做的事'],
    'phases/phase0_bootstrap.md': ['MECE 要求', '步驟 5', 'Phase 0 完成檢查'],
    'phases/phase1_scanner.md': ['3-Strike Protocol', 'Claim Verification', 'OMNIHEAL_SCAN_COMPLETE'],
    'skills/skill_code_lint.md': ['scope.in', 'scope.out', 'VERIFIED', 'confidence 閾值'],
}
for f, terms in checks.items():
    content = open(f).read()
    missing = [t for t in terms if t not in content]
    print(f'{f}: MISSING {missing}') if missing else print(f'{f}: OK')
"
```

Expected: All lines end with `OK`.

- [ ] **Step 4: Verify probe.py output format matches spec**

```bash
python src/probe.py . --list-files | python -c "
import sys
lines = [l for l in sys.stdin.read().strip().split('\n') if l]
errors = []
for l in lines:
    parts = l.split(' | ')
    if len(parts) != 5:
        errors.append(f'Wrong field count ({len(parts)}): {l!r}')
    elif parts[4] not in ('fast', 'standard', 'deep'):
        errors.append(f'Bad depth {parts[4]!r}: {l!r}')
print('probe.py format: OK') if not errors else print('ERRORS:', errors[:3])
"
```

Expected: `probe.py format: OK`

- [ ] **Step 5: Final commit**

```bash
git status  # confirm nothing unexpected
git add docs/superpowers/plans/2026-05-18-omniheal-implementation.md
git commit -m "docs: add OmniHeal implementation plan"
```

---

## Self-Review

### Spec Coverage

| Spec Requirement | Covered by Task |
|-----------------|----------------|
| §4 Directory structure | Task 1 scaffold |
| §5 LAUNCH.md with 5-Question Reboot Test | Task 2 |
| §6 Phase 0 (MECE governance, file_index, constitution) | Task 3 |
| §6 Phase 1 (Context Budget, 3-Strike, Claim Verification, batch loop) | Task 4 |
| §6 Phase 1.5 (Conclusion Integrity Gate, OMNIHEAL_SCAN_COMPLETE) | Task 4 |
| §7 scan_plan.md format (next:, last_updated:, last_finding_number:) | Task 9 |
| §7 findings_index.md format | Task 3 (created) + Task 4 (filled) |
| §7 findings/[filename].md frontmatter format | Task 4 (output format) |
| §7 session_log.md format (scan/retry/skip/inferred entries) | Task 4 |
| §7 progress/findings.md cross-scan accumulator | Tasks 1 + 4 |
| §8 Skill boundary (scope.in/scope.out) | Tasks 5, 6, 7 |
| §8 Atomic Finding with 5-question self-check | Tasks 5, 6, 7 |
| §8 Output format (#N file:line [✓ VERIFIED] confidence) | Tasks 5, 6, 7 |
| §8 Pattern Alert (severity:high + confidence >= 85) | Tasks 5, 6, 7 |
| §9 probe.py (--list-files, summary, binary filter, 1MB limit) | Task 10 |
| §12 Milestone 1 acceptance | Task 11 |
| §12 Milestone 2 acceptance (probe.py tests) | Task 10 |

**Gaps (out of scope for this plan):** Milestone 3 (Phase 0 end-to-end on a real target project) and Milestone 4 (Phase 1 single-file + 3-Strike simulation) require a real target project and are integration tests to run after deployment.

### Placeholder Check

No TBD, TODO, or "similar to Task N" references. All code blocks are complete and runnable. All file paths are exact.

### Type/Naming Consistency

- `probe.py` output: `"{rel} | {file_type} | {size_kb:.1f}KB | {complexity} | {_DEPTH[complexity]}"` — 5 fields
- `test_probe.py`: `fields = lines[0].split(" | ")` → `assert len(fields) == 5` — matches
- `phase1_scanner.md` depth values: `fast/standard/deep` — matches probe.py `_DEPTH` map
- `scan_plan.md` field `last_finding_number:` — referenced consistently in Task 9 (init to 0), Task 4 step 4d (read and increment), and `skill_code_lint.md` output format
- All three skills use identical output format header — no divergence
