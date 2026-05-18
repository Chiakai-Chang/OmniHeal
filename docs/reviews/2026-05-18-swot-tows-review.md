# OmniHeal SWOT+TOWS 輸出層設計討論紀錄

> **版本**：v1.0  
> **日期**：2026-05-18  
> **觸發原因**：使用者提問：「健檢完以後是窮盡找麻煩，還是能像 SWOT+TOWS 一樣知道如何改善？」  
> **參與角色**：6 位虛擬專家（5 輪討論）  
> **結論**：Phase 1.5 加入 SWOT 分析步驟 + 輸出 action_plan.md，v1.13 實作  
> **相關文件**：`docs/reviews/2026-05-18-mece-review.md`、`docs/reviews/2026-05-18-queue-architecture-review.md`

---

## 核心問題

OmniHeal 現有輸出 = Audit（審計）模式：找到 47 個問題，列清單。  
使用者需要的 = Consulting（顧問）模式：「這週修哪 3 個，為什麼，不修會怎樣」。

這不是格式問題，是思維框架問題。SWOT+TOWS 提供了從診斷到策略的轉化框架。

---

## 參與角色

| 代號 | 角色 | 視角 |
|------|------|------|
| MGMT | 管理顧問（McKinsey 背景）| SWOT/TOWS 方法論、診斷→策略落差 |
| ENG | 資深工程師（Tech Lead）| 開發者實際需求、什麼報告真的有用 |
| PD | 產品設計師 | 輸出可讀性、認知負荷、行動轉化率 |
| SEC | 資安研究員 | 風險優先化、威脅情境 |
| EM | 工程主管（VP Eng）| 資源分配、商業 ROI、決策框架 |
| ARCH | AI 系統架構師 | LLM 可行性、資料來源、整合點 |

---

## 第一輪：「找麻煩」vs「有幫助」的缺口

**MGMT**：Audit 告訴你「有什麼問題」；Consulting 告訴你「做什麼決定」。47 個 findings 是診斷，不是交付物。真正的交付物是：「這季優先做這 3 件事，原因 X，預期效益 Y」。

**ENG**：我拿到 47 個 findings 會怎麼辦？花 10 分鐘看，然後關掉。不知道哪些今天修、哪些等下季、哪些其實不重要，就是 noise。

**PD**：選擇悖論——選項越多，行動意願越低。正確輸出是「3 件今天能做的事」，其他收納起來。

**SEC**：severity 不等於優先順序。同樣是 medium，暴露在外部請求路徑的 SQL 注入，風險比內網硬編碼 IP 高 10 倍。現有設計缺少「暴露程度」維度。

**EM**：「給工程師 2 個人日，應該修哪些 findings？」現在的報告無法回答。需要 ROI 視角。

**ARCH**：Phase 1.5 已有所有 findings 的 context。缺的是分析框架，不是資料。技術可行。

**→ 共識**：OmniHeal 需從 Audit 升級到 Consulting 模式。核心缺口：有診斷，無策略。

---

## 第二輪：SWOT 四象限如何建構？

### Strengths（最困難的部分）

**ENG**：「沒問題」在程式碼品質語境是 Strengths 的有效 proxy。`src/auth/` 30 個檔案全 clean = 開發紀律的體現，不是「剛好沒被發現」。

**SEC**：兩層 Strengths：安全強項（處理外部輸入的模組 + clean density > 90%）；品質強項（非安全邊界模組 clean → 開發紀律好）。

**PD**：Strengths 讓使用者有信心繼續，也提供修復範本：「用 auth 的寫法修復 api」是最容易理解的建議。

**ARCH**：Strengths 構建演算法（Phase 1.5 可實現，不需額外掃描）：
1. Clean 密度：每個目錄計算 `clean_files / total_files`
2. 安全強項：constitution.md 安全邊界模組 + clean density > 90%
3. 品質參考：clean density > 95% → 修復範本推薦

### Weaknesses、Opportunities、Threats

| SWOT | 資料來源 | 構建方式 |
|------|---------|---------|
| Weaknesses | findings 聚類 | 按目錄+類型分組；標記系統性/習慣/局部 |
| Opportunities | findings 聚類 + 目錄結構 | ≥3 同類型 findings 同一目錄 → 一 PR 解決；有 Strengths 模組作範本 → 轉化機會 |
| Threats | findings + constitution.md 安全邊界 + domain context | 安全邊界模組 findings + domain severity 升級 findings |

**ENG**：Opportunities 聚類邏輯：同目錄+同類型 → 系統性（一根因）；共用函式有 bug → 修一處所有呼叫者受益（高槓桿）。

---

## 第三輪：TOWS 轉化為具體行動

### TOWS 矩陣對應程式碼健檢

| | Opportunities（O）| Threats（T）|
|--|-----------------|------------|
| **Strengths（S）**| SO：將強項 pattern 推廣修復弱點 | ST：在強項模組加監控防威脅擴散 |
| **Weaknesses（W）**| WO：一 PR 修多個聚類 findings | WT：今天就修（高威脅 × 快修）|

### 時間表格式（TOWS 的輸出形式）

**PD**：不展示 SWOT 矩陣（中間過程），直接展示 TOWS 結果：
```
⚡ 今日修復（WT：高威脅 × 低工時）
📅 本週 PR（WO：弱點聚類 × 機會）
🗓️ 下季規劃（SO：長期提升）
💪 強項維持（S：作為修復範本）
⚠️ 高風險未修警告（WT 高工時項目的補償建議）
```

**SEC**：「⚠️ 高風險未修警告」必要——有些 WT 使用者可能選擇暫不修，但需明確知道補償措施（如 WAF 規則）。讓風險顯性化，但不強迫修復。

**EM**：每個 action item 必包含：修復對象、影響 finding 數、預估工時（Low/Medium/High）、不修後果（Threat 項目必填）。

---

## 第四輪：設計決策辯論

### A：輸出放在哪裡？

**→ 共識**：`summary.md`（審計快照）+ `action_plan.md`（活文件，可 check off）分開。受眾不同、更新頻率不同、格式不同。

### B：工時估算可靠嗎？

**ENG**：LLM 精確估工時不可靠（不知道 codebase 規模、dev 熟悉度）。

**MGMT**：不需精確，需相對量級：Low/Medium/High + 依據說明。

**→ 共識**：三級工時（Low < 1hr / Medium < 1day / High > 1day）+ 依據 + 「不修後果」（比正向工時更有說服力）。

### C：局部掃描的 action_plan？

**PD**：局部掃描只輸出 WT 類行動（已確認緊急），其餘標注「待完整掃描後產出」。

**→ 共識**：掃描未完成時 action_plan.md 降級，只有今日修復和高風險未修警告有效，其餘加 `⚠️ 基於部分資料` 標注。

---

## 第五輪：最終裁決

### Phase 1.5 新增步驟規格

在現有「步驟 1–5 清理發現」之後、「步驟 6 產出 summary.md」之前，插入：

**步驟 5.5 `[S]`：SWOT 分析**
1. S：計算每目錄 clean density；constitution.md 安全邊界 + clean > 90% → 安全強項
2. W：findings 按目錄+類型聚類；標記系統性/習慣/局部
3. O：同目錄 ≥3 個相同類型 findings → 系統性機會；有 Strengths 模組可作範本 → 轉化機會
4. T：安全邊界模組的 findings + domain severity 升級 findings + high confidence high severity

**步驟 5.6 `[D/S]`：產出 action_plan.md**
1. WT（高 Threat × Low Effort）→ 今日修復
2. WO（弱點聚類 × Opportunity）→ 本週 PR
3. WT（高 Threat × High Effort）→ 高風險未修警告
4. SO/ST → 下季規劃 + 強項維持
5. 每 action item：finding 編號、工時、不修後果

### 優先矩陣

| 改進 | 優先級 |
|------|--------|
| Phase 1.5 加 SWOT 分析步驟（5.5）| **P1** |
| 產出 action_plan.md（5.6）取代原 P2 action_items.md | **P1** |
| action_plan.md 含強項維持 + 高風險未修警告 | **P1** |
| 局部掃描降級輸出 | **P1** |
| 跨掃描 SWOT 變化追蹤 | **P2** |
| 工時精確估算 | **P3（LLM 風險，暫不做）** |

---

## action_plan.md 完整格式規格

```markdown
# 健檢改善路線圖
> 基於 [date] 掃描 | Skill: [skill] | [M] 個檔案 | [N] 個 findings

⚠️ 基於部分資料（[N]/[M] 個檔案）— 僅局部掃描時顯示，以下標 * 的區塊為完整掃描後才有效

---

## ⚡ 今日修復（高威脅 × 低工時）
預估工時：Low（< 1 小時）

- [ ] #3 `config.py:12` — 硬編碼 API Key 改為環境變數（Low，~30 分鐘）
  - 不修後果：憑證若洩漏，攻擊者可直接存取第三方服務
- [ ] #1 `src/api/handlers.py:45` — SQL 字串拼接改參數化查詢（Low，~20 分鐘）
  - 不修後果：外部 API 端點可被 SQL 注入攻擊

## 📅 本週 PR（弱點聚類 × 機會）*
預估工時：Medium（< 1 天）｜一個 PR 解決多個 findings

- [ ] `src/db/` SQL 注入系統性修復（解決 #1, #4, #7，同一根因）
  - 建議：修改 `db_helper.py` query builder，所有呼叫者自動受益
  - 參考範本：`src/auth/db_access.py` 已正確實作參數化查詢
- [ ] `src/api/` exception 處理補齊（解決 #2, #5, #9，同一 pattern）
  - 建議：仿照 `src/models/` 的 error handling pattern

## 🗓️ 下季規劃（架構決策 / 低風險技術債）*

- [ ] `src/legacy/` 命名一致性整理（12 個 medium findings）
  - 工時：High（> 1 天，建議在重構週處理）
  - 不緊急：不影響安全，影響可維護性

## 💪 強項維持（建議作為修復範本）*
- `src/auth/`：zero high findings，安全邊界處理正確 → **作為 src/api/ 修復範本**
- `src/models/`：命名規範一致 → **命名相關修復請仿照此模組**

## ⚠️ 高風險未修警告
若以下 findings 暫不修復，建議採取補償措施：

- #1 SQL 注入（`src/api/handlers.py:45`）暴露於外部請求路徑
  → 補償建議：API gateway 加 WAF 規則；監控異常查詢 pattern

---
*本文件由 OmniHeal 自動產生。修復完成後請勾選對應項目追蹤進度。*
```

---

## 版本控制說明

| 版本 | 日期 | 變更摘要 |
|------|------|---------|
| v1.0 | 2026-05-18 | 初始版本，SWOT+TOWS 輸出層設計定稿 |
