# Phase 0：環境探測與規則建立

**目標**：了解目標專案的性質，建立「治理規則文件」(`progress/constitution.md`) 與「全局檔案索引」(`progress/file_index.md`)。

**完成條件**：`progress/scan_plan.md` 中 Phase 0 狀態為 `complete`，且兩個輸出檔案都已建立。

**動詞型別說明**：`[D]` = 確定性操作（不需 LLM 判斷）；`[S]` = 語意分析（需 LLM）；`[I]` = 互動（暫停等使用者回應）

---

## 執行步驟

### 步驟 0 `[D]`：讀取 Pre-flight Context（若存在）

若 `progress/constitution_preflight.md` 存在，讀取全文，將以下資訊納入後續步驟的判斷前提：
- Framework 慣例排除清單（步驟 3 抽樣推斷時，不把 framework 慣例誤判為問題）
- 業務領域與合規要求（步驟 4 MECE 分解時，領域決定哪些維度更重要）
- 豁免 Pattern 清單（步驟 6 建立 constitution.md 時直接複製進來）

**若 `progress/constitution_preflight.md` 不存在**：跳過步驟 0，直接從步驟 1 開始。Phase 0 的 MECE 問題照常問，constitution 不會有 Pre-flight 欄位（可接受，只是 findings 品質可能較低）。

**步驟 4 MECE 問題的調整**：若已有 preflight context，下列維度可跳過（preflight 已回答）：
- framework 慣例問題 → preflight 步驟 1 已偵測
- 業務領域問題 → preflight 步驟 5 Q1 已問
- 豁免 pattern 問題 → preflight 步驟 5 Q2 已問

Phase 0 的 MECE 問題只需補充 preflight **未涵蓋**的維度（通常剩下：命名慣例細節、錯誤處理策略、安全邊界的具體模組）。

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

### 步驟 7.5 `[D]`：產生 Task Queue（`progress/queue/`）

建立 `progress/queue/` 目錄，根據 `progress/file_index.md` 的複雜度欄位產生 task 文件：

**粒度規則：**
- `high` 複雜度 → 一檔一 task（`type: file_scan`，`depth: deep`）
- `medium`/`low` 複雜度 → 每 20 個一批（`type: batch_scan`，`depth: standard`）

**命名規則：**`task_NNN_[簡短描述].md`（NNN 為三位數序號，從 001 開始）
- high 檔案：`task_001_src_auth_login_py.md`（路徑轉底線）
- 批次 task：`task_015_batch_016_035.md`（記錄批次範圍）
- 最後一個：`task_999_phase15_summary.md`（固定）

**task 文件格式（high 複雜度示例）：**
```markdown
---
task_id: 001
status: pending
type: file_scan
file: src/auth/login.py
skill: [選定技能]
depth: deep
---

## 前提脈絡
治理規則：見 progress/constitution.md（前 30 行）；複雜度 high，deep 深度

## 目標
掃描 src/auth/login.py，輸出所有 confidence >= 80 的 findings

## 完成條件
- findings_index.md 已追加（有發現建 findings/ 詳細頁；無發現標 ✅ clean）
- session_log.md 已追加摘要行
- 本文件 status 改為 done
```

**task 文件格式（批次 task 示例）：**
```markdown
---
task_id: 015
status: pending
type: batch_scan
skill: [選定技能]
depth: standard
files:
  - src/utils/format.py
  - src/utils/helpers.py
  - src/models/user.py
  - ...(共 20 個)
---

## 前提脈絡
治理規則：見 progress/constitution.md（前 30 行）；medium/low 複雜度，standard 深度

## 目標
依序掃描以上檔案，findings 記入 findings_index.md

## 完成條件
- 全部檔案已掃描（含跳過記錄）
- session_log.md 已追加摘要行
- 本文件 status 改為 done
```

**Phase 1.5 task（固定為最後一個）：**
```markdown
---
task_id: 999
status: pending
type: summary
---

## 前提脈絡
Phase 1 全部 task 已完成（此 task 在 queue 末尾）

## 目標
執行 Phase 1.5：整合發現，產出 progress/YYYY-MM-DD-skill/summary.md

## 參考
phases/phase1_scanner.md 的「Phase 1.5」章節

## 完成條件
- summary.md 已建立（含 Trust Declaration）
- scan_plan.md 末尾追加 OMNIHEAL_SCAN_COMPLETE
- 本文件 status 改為 done
```

### 步驟 8 `[D]`：更新 `progress/scan_plan.md`，標記 Phase 0 完成

更新 `progress/scan_plan.md`（若不存在則新建，使用 `OmniHeal/progress/scan_plan.md` 的格式）：

```markdown
## 當前掃描任務
- 目標目錄：[目標路徑]
- 使用技能：[skill名稱]
- 開始時間：[YYYY-MM-DD HH:MM]
- last_updated：[YYYY-MM-DD HH:MM]
- 輸出目錄：progress/[YYYY-MM-DD-skill]/
- queue 目錄：progress/queue/

## Phase 狀態
- Phase 0（環境探測）：complete
- Phase 1（全域掃描）：pending（queue 已就緒，共 [N] 個 task）
- Phase 1.5（發現清理）：pending

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
- [ ] `progress/queue/` 目錄存在且含 task_NNN_*.md 文件（至少 task_999_phase15_summary.md）
- [ ] `progress/YYYY-MM-DD-<skill>/findings_index.md` 已建立（含表頭）
- [ ] `progress/YYYY-MM-DD-<skill>/session_log.md` 已建立（含步驟 3 的紀錄）
