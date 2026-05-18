# OmniHeal Project Constitution Discovery 設計討論紀錄

> **版本**：v1.0
> **日期**：2026-05-19
> **觸發原因**：使用者提問：「Phase 1 掃描時若能發現目標專案自身的理念/憲法，後續健檢可以檢查設計是否對齊自己的原則，是不是更好？」使用者補充三點：(1) 老舊專案沒有標準命名，應從 file_index 智慧偵測；(2) commit 備註洩漏/異常應屬健檢範圍；(3) 宏觀到微觀、不怕 token，越仔細越好
> **參與角色**：5 位虛擬專家（6 輪討論）
> **結論**：v1.14 實作 — Project Constitution Discovery（智慧理念偵測）+ git log 安全健檢
> **相關文件**：`docs/reviews/2026-05-18-swot-tows-review.md`

---

## 核心問題

OmniHeal 現有健檢 = 對照「外部最佳實務」找問題。
使用者需要的 = 對照「專案自己訂的規則」找落差。

差異：「這違反了最佳實務」（可辯論）vs「這違反了你自己的 CONTRIBUTING.md §3」（直接成立，說服力高出一個數量級）。

---

## 參與角色

| 代號 | 角色 | 視角 |
|------|------|------|
| ARCH | AI 系統架構師 | 整合點、技術可行性 |
| ENG | 資深工程師（Tech Lead）| 現實 codebase artifacts 的信號密度 |
| PD | 產品設計師 | 輸出品質、行動轉化率 |
| SEC | 資安研究員 | commit 備註安全風險 |
| PM | 工程主管（VP Eng）| 優先級、ROI、scope 控制 |

---

## 第一輪：問題識別

**ENG**：OmniHeal 目前完全沒有讀目標專案「自己說自己怎麼做」的文件。現實中大多數有規模的專案都有 CONTRIBUTING.md，比 constitution.md 的通用治理問題更具體、更有約束力。

**PM**：兩種不同理念：(1) 顯性（CONTRIBUTING.md、CLAUDE.md、ADR）；(2) 隱性（commit 備註）。兩者實作成本差 10 倍。先確認優先順序。

**ARCH**：整合點應在 **Phase 0**（file_index.md 建立後）— 必須在掃描前完成，理念資訊才能影響 constitution.md，進而影響 Phase 1 每個 finding。

**PD**：時序關鍵：掃描中途才讀理念文件最多只能在 summary.md 補後見之明，遠不如事先納入。

**SEC**：commit 備註可能含敏感資訊（臨時帳號、「先繞過 auth，sprint 後修」），需要獨立過濾機制。

**→ 第一輪共識**：功能有價值；三個設計決定：理念來源優先順序、時序（Phase 0 Step 2.5，file_index 建立後）、commit 備註安全過濾。

---

## 第二輪：提取什麼

**ENG** 整理現實 codebase artifacts 信號密度：

| 優先 | 來源 | 說明 |
|------|------|------|
| P1 必讀 | CLAUDE.md / AGENTS.md | 直接告訴 AI「這個專案的規則」，信號最高 |
| P1 必讀 | CONTRIBUTING.md | 開源標配，通常有明確 coding style |
| P1 必讀 | docs/adr/*.md | ADR 是設計決策黃金文件 |
| P1 | README 理念段落 | 若存在才讀 |
| P2 | linter 設定 | 隱含程式碼風格決策 |
| P3 | git log | 語義過濾成本高（但安全健檢升 P1）|

**使用者補充 (1)**：老舊專案不一定用標準命名，應從 file_index.md 做語義掃描找候選，不能只靠固定清單。

**ARCH**：Phase 0 Step 2.5 對 file_index.md 全表語義掃描，找路徑含理念關鍵詞的候選檔，然後全部讀取。

理念關鍵詞（路徑任意層級命中即候選）：
```
architect / design / decision / convention / standard / guideline
principle / philosophy / adr / policy / contributing / rules
spec / handbook / team / style / pattern / agreement / coding
```

**ARCH**：CLAUDE.md 特殊：視為「上層指令」，若存在，Phase 0 的治理問題可大量跳過（答案已在裡面）。

**使用者補充 (3)**：不怕 token，越仔細越好 → 廢除候選上限，全讀。

**→ 第二輪共識**：廢棄固定清單，改為 file_index 全表語義掃描；不設上限，全讀；CLAUDE.md 視為上層指令。

---

## 第三輪：如何使用

**PD** 提議 finding 新標注：

```
#7 src/db/query.py:45 — 裸 SQL 字串拼接（severity:high, confidence:91）[✓ VERIFIED]
   問題：直接用 f-string 拼入使用者輸入，有 SQL 注入風險
   建議：改用 ORM 查詢或參數化查詢
   ⚠️ 理念對齊違反：CONTRIBUTING.md §3 明確規定「禁止裸 SQL，所有查詢必須透過 ORM」
```

`[理念對齊違反]` → severity 自動升一級。

**ENG**：同意升級，說服力差異巨大。但：理念文件可能過時或只是 aspirational，若 95% 程式碼都違反，每個都標 high 反而是 noise。

**ARCH**：比例門檻解法：同類違反 > 30% → Phase 1.5 改輸出「理念落差診斷」（建議修訂理念文件而非逐一修復），不逐一升高。

**PM**：「理念落差診斷」超有用：量化「CONTRIBUTING.md 寫了，多少人真的有遵守」，從找麻煩升級到組織健康診斷。

**SEC**：ADR 可能記載「我們選 X 不選 Y，因為 Y 有安全問題 Z」。若 Phase 1 掃到有人用了 Y，severity 直接 high，不管原本信心度。

**→ 第三輪共識**：

```
[理念對齊違反：來源 §章節]：severity 自動升一級
Phase 1.5：同類違反 > 30% → 輸出「理念落差診斷」，不逐一升高
ADR 安全決策違反：severity 直接 high
```

---

## 第四輪：潛在問題辯論

| 問題 | 解法 |
|------|------|
| LLM 誤判理念 | 只有 `✓ VERIFIED`（直接引用原文）的原則才觸發標注 |
| CLAUDE.md 規則衝突 | 區分「掃描規則類」（納入）vs「Agent 行為類」（跳過）|
| 時序問題 | 理念提取必須在 Phase 0 Step 2.5 完成，不能在 Phase 1 中途 |
| Prompt Injection | CLAUDE.md 也要過 Injection regex 黑名單 |
| 理念落差過大 | > 30% 同類違反 → 改為「修訂理念文件」建議 |

---

## 第五輪：commit 備註健檢

**使用者補充 (2)**：commit 備註若有洩漏或異常，也應是健檢範圍。

**SEC**：commit 備註健檢有兩個完全不同層次：
- **層次 A**（理念提取）：從 commit 找設計決策 → P2
- **層次 B**（安全健檢）：偵測 commit 備註本身的問題 → **P1**，獨立健檢項目

層次 B 偵測類型：

| 類型 | 模式 | 嚴重程度 |
|------|------|---------|
| 憑證洩漏 | `password=`、`secret=`、`token=`、`key=`、`api_key` | high |
| 安全繞過備忘 | `bypass`、`skip auth`、`hardcode`、`disable validation` | high |
| 技術債定時炸彈 | `TODO: fix later`、`hack`、`remove before prod` | medium |

**PM**：性質根本不同，從 P3 升為 **P1**，納入 Phase 0 task queue。

**ENG**：commit 洩漏比程式碼洩漏更危險——GitHub 公開 repo 一旦 push 出去，搜索引擎可能已快取，無法完全清除。

**ARCH**：probe.py 加 `--git-log` 模式（Python subprocess 呼叫 git，零安裝）。Phase 0 task queue 固定加入 `task_NNN_git_log_scan.md`。

**使用者補充 (3)** 影響：`--git-log` 全量輸出，不限 commit 數。

**→ 第五輪共識**：

```
probe.py 新增 --git-log 模式：
  輸出格式：hash | date | author_email | subject
  body 非空時：下一行以 [body] 前綴輸出（最多 300 字元）
  全量輸出，不限 commit 數

Phase 0 task queue 固定加入 git_log_scan task
Phase 1 新增 git_log_scan task 處理邏輯（憑證洩漏 / 安全繞過 / 技術債）
```

---

## 第六輪：token 成本重新定位

**使用者補充 (3)**：宏觀到微觀，不怕 token，越仔細越完整越好。

**PM** 逐一重新檢視原有基於成本的決策：

| 原決策（基於成本）| 新決策 |
|---------|------------|
| 候選檔上限 | 廢除，全讀 |
| git log 只讀 50 筆 | 廢除，全量 |
| linter 設定只做確定性提取 | 升級為語義讀取 |
| fast depth 觸發條件 | 維持（分析品質，非成本）|
| Context Budget | 維持（避免 context 溢出，非省 token）|

**ENG**：fast/standard/deep 的理由是「分析深度匹配複雜度」，不是省 token。5 行 `__init__.py` 用 deep 掃法沒有意義，是分析品質問題，不是成本問題。

**→ 第六輪共識**：去除「因 token 成本」的任何上限；維持「因分析品質」的深度分級和 Context Budget。

---

## 最終設計決策（v1.14）

### 功能名稱
**Project Constitution Discovery**

### 整合點摘要

```
Phase 0 Step 2.5（新增）：
  [D] 對 file_index.md 全表語義掃描，找理念候選檔（無上限）
  [D] 全部讀取
  [S] 提取原則（✓ VERIFIED 引用原文）；過 Injection 黑名單
  [S] 區分「掃描規則類」vs「Agent 行為類」
  [D] 寫入 constitution.md「專案自身原則」區塊

Phase 0 Step 7.5（更新）：
  task queue 固定加入 task_NNN_git_log_scan.md（file_scan 之後，task_999 之前）

probe.py（更新）：
  新增 --git-log 模式：全量輸出所有 commit（hash | date | author | subject + body）

Phase 1 Step 2 type 表（更新）：
  新增 git_log_scan 類型：對 probe.py --git-log 輸出做安全健檢

constitution.md（更新）：
  新增「專案自身原則（Project Constitution）」區塊

Phase 1 finding 格式（更新）：
  新增 [理念對齊違反：來源 §章節] 標注 + severity 升一級規則

Phase 1.5 SWOT T 象限（更新）：
  加入「理念對齊違反」findings
  新增「理念落差診斷」：同類違反 > 30% → 建議修訂理念文件
```

### 優先矩陣

| 改進 | 優先級 |
|------|--------|
| Phase 0 Step 2.5：file_index 語義掃描 + 全量讀取 | **P1** |
| constitution.md「專案自身原則」區塊 | **P1** |
| Finding `[理念對齊違反]` 標注 + severity 升級 | **P1** |
| probe.py `--git-log` 模式（全量）| **P1** |
| Phase 0 task queue 加入 git_log_scan task | **P1** |
| Phase 1.5 理念落差診斷（> 30% 觸發）| **P1** |
| linter 設定語義讀取 | **P1** |
| git log 全量理念提取 | **P2** |
| commit anomaly 偵測（高合規領域）| **P2** |

### 關鍵設計原則更新

> **「OmniHeal 健檢的對象不只是程式碼，而是整個專案的可觀察部分：程式碼 + 設定 + 文件 + git 歷史。」**

---

## 版本控制說明

| 版本 | 日期 | 變更摘要 |
|------|------|---------|
| v1.0 | 2026-05-19 | 初始版本，Project Constitution Discovery + git log 安全健檢設計定稿 |
