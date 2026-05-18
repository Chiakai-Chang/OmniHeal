# OmniHeal Task Queue 架構評估討論紀錄

> **版本**：v1.0  
> **日期**：2026-05-18  
> **觸發原因**：使用者提出 Task Queue 模式，以解決現有「掃描品質在長程過程中維持一致」的根本問題  
> **參與角色**：5 位虛擬專家（4 輪討論）  
> **結論**：採用 Queue 架構，v1.12 實作  
> **相關文件**：`docs/reviews/2026-05-18-mece-review.md`（前次 P1 改進復盤）

---

## 問題背景

使用者指出：現有設計中「如何保證全掃的質量在整個過程中維持一致」是核心問題。

具體癥結：
- `scan_plan.md` 的 `next:` 欄位是「描述性恢復點」，恢復品質取決於 Agent 的記憶力
- 「讀 session_log 最後 10 行」是硬切啟發式，不可靠
- 批次降級邏輯（context 50%/20% 兩段）複雜且主觀

使用者提案：改為 **Task Queue 模式** ——
- 每個工作單元是一個 task 文件，存於 `progress/queue/` 目錄
- 每個 task 文件包含：前提脈絡 + 目標 + 可選參考文件
- 恢復 = 找第一個 `status: pending` task，執行它
- 新工作可動態插入 queue（Pattern Alert、跟進任務）

---

## 參與角色

| 角色 | 代號 | 專業視角 |
|------|------|---------|
| AI 系統架構師 | ARCH | 端到端 Agent 流程、context 管理 |
| 實作工程師 | ENG | 可行性、edge case、Windows 相容 |
| 資安研究員 | SEC | 威脅建模、injection 防禦 |
| 產品設計師 | PD | 使用者體驗、可觀測性 |
| 終端使用者代表 | USER | 維護者視角、實際使用痛點 |

---

## 第一輪：整體方向正確嗎？

**ARCH**：完全正確。現有設計的根本問題是「恢復點 = 文字描述」，品質取決於描述準確性和記憶力。Queue 模型把「恢復點 = 工作項目本身」——Queue 裡剩幾個 pending 就是剩多少工作，不依賴記憶。這是分散式系統的成熟模式，移植到 Agent 場景完全成立。

**ENG**：實作層面可行。`ls progress/queue/*.md`、filter `status: pending`、執行、改為 `done`，純文件操作，Windows/Linux/Mac 均適用。唯一顧慮：大型專案若 1000+ 個檔案，一對一 task 文件太多。需要批次化策略。

**SEC**：安全態勢改善。每個 task 的 context 明確宣告在 task 文件裡，Prompt Injection 即使汙染某個 task，下一個 task 從乾淨 context 開始，汙染不跨 task 傳播。比現有 session_log 一路寫到底更隔離。

**PD**：使用者體驗改善。使用者隨時可以 `ls progress/queue/` 看剩多少工作，比讀 `scan_plan.md` 直觀。也可以手動刪除不想掃的 task 文件（明確控制權）。

**USER**：我只在意：能不能看到「已完成 45/120」？  
**PD**：task 文件加序號前綴（task_001_xxx.md），`ls | wc -l` = 總數，`grep "status: done" -l | wc -l` = 完成數，不需額外 UI。

**→ 第一輪共識**：Queue 方向正確，採用。

---

## 第二輪：設計細節辯論

### 辯題 A：Task 粒度

**ENG**：高複雜度 = 一檔一 task（deep 深度，獨立 context）；中低複雜度 = 一批 20 個（一個 task）。1000 個檔案 → 約 55 個 task，目錄乾淨。

**ARCH**：批次 task 文件要列出所有檔案路徑，Agent 不需要讀 file_index.md，所有資訊在 task 文件裡。

**SEC**：批次 task 文件的檔案清單由 Phase 0 產生、固定在文件裡，Agent 無法被操控增刪。比動態讀 file_index.md 更安全。

**→ 共識**：complexity-based 粒度。high = 一檔一 task；medium/low = 一批 20 個一 task。

---

### 辯題 B：Queue 由誰產生？

**ARCH**：Phase 0 負責全量產生，含最後一個 Phase 1.5 summary task（task_999_phase15_summary.md）。Phase 1 只消耗 Queue。

**ENG**：Phase 0 已知 file_index.md 和複雜度，task 生成完全確定性（[D] 操作），不需 LLM 判斷。

**USER**：Phase 0 產生後，我可以在 Phase 1 開始前審閱 task 清單，甚至刪掉不想掃的目錄。這比現在好多了。

**→ 共識**：Phase 0 全量產生 Queue，Phase 1 只消耗。

---

### 辯題 C：Pattern Alert 跟進任務

**ARCH**：發現系統性問題後，在 Queue 插入後綴 task（task_001b_followup_auth_dir.md），排在觸發 task 之後，讓跟進掃描優先於其他未掃目錄。

**ENG**：命名規則：主任務 task_001 → 跟進 task_001b、task_001c（若 task_001b 已存在則用 task_001c）。字母序確保排序正確。

**SEC**：跟進 task 文件需標注 `triggered_by: task_001（發現原因）`，讓審計軌跡可追溯。

**→ 共識**：Pattern Alert 觸發時，插入後綴命名跟進 task，帶 triggered_by 欄位。

---

### 辯題 D：Context Budget 安全閘

**ARCH**：Queue 模型下安全閘更簡單：每個 task **開始前**評估 context。若 < 20%，不啟動，直接停止。

**ENG**：不再有批次降級邏輯。high-complexity 檔案是獨立 task，不存在「批次中途降級」。

**PD**：更清晰。之前的降級邏輯讓使用者不確定「當前掃描到底做了完整分析還是 fast 分析」。現在每個 task 的深度在 task 文件裡固定，透明。

**→ 共識**：Context Budget 簡化為「task 啟動前評估；< 20% 停止，不啟動新 task」。

---

## 第三輪：現有機制映射

| 元件 | 現狀 | Queue 後 |
|------|------|---------|
| `scan_plan.md` 的 `next:` | 複雜描述性欄位 | 移除；恢復點 = queue 第一個 pending task |
| Reboot Test 第 5 題（讀 session_log）| 硬切啟發式 | 改為「找 queue 第一個 pending task 是什麼」 |
| Context Budget 批次降級邏輯 | 50%/20% 兩段複雜邏輯 | 簡化：< 20% 不啟動新 task |
| 3-Strike Protocol | 保留 | 不變 |
| Claim Verification | 保留 | 不變 |
| Prompt Injection 偵測（P1）| 已加 | 不變 |
| findings_index.md | 跨批次 surgical append | 跨 task surgical append，不變 |
| session_log.md | 連續記錄 | 每個 task 結束後 append 一行摘要 |
| Calibration Self-Check（P1）| 批次結束自問 | 改為 task 結束自問 |

---

## 第四輪：最終裁決

| 決定 | 細節 |
|------|------|
| Task 粒度 | high → 一檔一 task；medium/low → 一批 20 個一 task |
| Queue 產生 | Phase 0 全量，含 task_999_phase15_summary.md |
| 跟進任務命名 | task_NNNb、task_NNNc，帶 `triggered_by` |
| Context Budget | task 啟動前檢查，< 20% 停止 |
| Reboot Test | 第 5 題改為「找 queue 第一個 pending task」 |
| scan_plan.md | 移除 `next:` 欄位，記錄 queue 目錄路徑 |

---

## Task 文件格式規範

### 高複雜度檔案 task（一檔一 task）

```markdown
---
task_id: 001
status: pending
type: file_scan
file: src/auth/login.py
skill: skill_code_lint
depth: deep
---

## 前提脈絡
- 治理規則：見 progress/constitution.md（前 30 行）
- 本檔案複雜度：high，使用 deep 深度（分段讀取，每段 4000 字元）

## 目標
掃描 src/auth/login.py，輸出所有 confidence >= 80 的 findings

## 完成條件
- findings/login_py.md 已建立（若有發現），或 findings_index.md 追加 ✅ clean
- session_log.md 追加一行摘要
- 本文件 status 改為 done
```

### 批次 task（中低複雜度）

```markdown
---
task_id: 015
status: pending
type: batch_scan
skill: skill_code_lint
depth: standard
files:
  - src/utils/format.py
  - src/utils/helpers.py
  - src/models/user.py
---

## 前提脈絡
- 治理規則：見 progress/constitution.md（前 30 行）
- 本批次複雜度：medium/low，使用 standard 深度

## 目標
依序掃描以上檔案，每個檔案的發現記入 findings_index.md

## 完成條件
- 全部檔案已掃描（含跳過記錄）
- session_log.md 追加一行摘要
- 本文件 status 改為 done
```

### 跟進 task（Pattern Alert 觸發）

```markdown
---
task_id: 001b
status: pending
type: followup
triggered_by: task_001（src/auth/login.py 發現 SQL 注入）
skill: skill_code_lint
depth: standard
target_dir: src/auth/
exclude: src/auth/login.py
---

## 前提脈絡
- task_001 在 src/auth/login.py:23 發現 SQL 字串拼接（severity:high）
- Pattern Alert：此類問題通常系統性出現，建議掃描 src/auth/ 全目錄

## 目標
掃描 src/auth/ 下所有 .py 檔（排除已掃的 login.py），重點關注 SQL 查詢模式

## 完成條件
- 已掃描 src/auth/ 下所有未掃檔案
- session_log.md 追加一行摘要
- 本文件 status 改為 done
```

### Phase 1.5 summary task

```markdown
---
task_id: 999
status: pending
type: summary
---

## 前提脈絡
- Phase 1 全部 task 已完成（此 task 在 queue 末尾）
- 讀取 findings_index.md 和所有 findings/*.md 詳細頁

## 目標
執行 Phase 1.5：整合發現，產出 progress/YYYY-MM-DD-skill/summary.md

## 參考文件
- phases/phase1_scanner.md 的「Phase 1.5」章節

## 完成條件
- summary.md 已建立
- scan_plan.md 末尾追加 OMNIHEAL_SCAN_COMPLETE 信號
- 本文件 status 改為 done
```

---

## 版本控制說明

| 版本 | 日期 | 變更摘要 |
|------|------|---------|
| v1.0 | 2026-05-18 | 初始版本，Queue 架構設計定稿 |
