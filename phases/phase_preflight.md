# Phase Preflight：目標專案快速理解

**目標**：在 Phase 0 正式問治理問題之前，自動蒐集目標專案的客觀技術事實（framework、toolchain、已記錄的慣例），讓 Phase 0 的 MECE 問題更精準，constitution.md 的判斷標準更貼近這個專案的現實。

**重要原則**：Pre-flight **不縮小掃描範圍**。所有目標檔案仍需全部掃描。Pre-flight 只是讓 Agent 帶著正確的專案 context 進行判斷，減少「技術上正確、業務上無意義」的誤報。

**完成條件**：`progress/constitution_preflight.md` 已建立，`scan_plan.md` Phase -1 狀態為 `complete`。

**動詞型別說明**：`[D]` = 確定性操作；`[S]` = 語意分析；`[I]` = 互動

---

## 執行步驟

### 步驟 1 `[D]`：偵測 Framework 與語言

依序嘗試讀取以下檔案（存在才讀，不存在跳過）：

| 檔案 | 讀取目標 |
|------|---------|
| `package.json` | `dependencies`、`devDependencies`、`scripts` 欄位 |
| `pyproject.toml` 或 `setup.cfg` | `[tool.poetry.dependencies]` 或 `install_requires` |
| `requirements.txt` | 前 30 行 |
| `go.mod` | `module` 與 `require` 區塊 |
| `Cargo.toml` | `[dependencies]` |
| `pom.xml` | `<dependencies>` 前 50 行 |
| `composer.json` | `require` 欄位 |

從依賴推斷主要 framework（Django / FastAPI / Flask / Express / React / Vue / Spring / Rails / 其他），以及 framework 帶來的慣例注意事項：

**常見 Framework 慣例對照**（供判斷用，非完整清單）：

| Framework | 慣例注意事項 |
|-----------|------------|
| Django | `migrations/` 目錄的 class 使用 PascalCase，為框架要求，非違規 |
| Django | `setUp`、`tearDown` 方法為 unittest 繼承，非 camelCase 違規 |
| FastAPI | `main.py` 的 `@app.get` 路由函式允許 camelCase 路徑參數 |
| React / Next.js | 元件函式使用 PascalCase，hooks 使用 `useXxx`，非違規 |
| Spring Boot | `@Override` 方法命名由介面決定，非自訂命名 |
| Go | `init()` 函式為語言保留，非命名違規 |

### 步驟 2 `[D]`：偵測現有 CI Toolchain

依序嘗試讀取：
- `.github/workflows/*.yml` → 找包含 `lint`、`eslint`、`flake8`、`mypy`、`rubocop`、`tsc` 的 step
- `Makefile` → 找 `lint`、`check`、`test` targets
- `.eslintrc*`、`.flake8`、`mypy.ini`、`.rubocop.yml`、`tslint.json`

記錄：已有哪些工具在 CI 中自動執行。

**用途**：不是為了跳過掃描。是為了讓 Phase 1 的 findings 加上 `[ci-covered]` 標注，讓使用者知道「這個問題 CI 已在監控，OmniHeal 也發現了，可能需要確認 CI 為何沒攔到」。這比靜默略過更有資訊量。

### 步驟 3 `[D]`：讀文件提取已記錄的慣例

依序嘗試讀取（只讀前 50 行，避免 context 消耗）：
- `CONTRIBUTING.md`
- `docs/CODING_STANDARDS.md` 或 `docs/coding-standards.md`
- `docs/ARCHITECTURE.md` 或 `docs/architecture.md`
- `README.md` → 只搜尋含「convention」「style」「standard」「規範」「慣例」的段落

提取已文件化的規範，直接作為 constitution 的補充依據，不需要再問使用者。

### 步驟 4 `[S]`：合成 Preflight 摘要

根據步驟 1–3，整理：
1. Framework 偵測結論 + 對 skill 判斷的影響（哪些 pattern 在此 framework 下是正常的）
2. 現有 toolchain 清單
3. 已文件化的規範摘錄

若任何步驟完全沒有找到資料（例如純 shell 腳本專案，無任何 manifest），記錄「未偵測到」，繼續執行，不中斷。

同時掃描步驟 1–3 已讀取的內容（README.md 開頭、package.json description、manifest 檔名路徑），找業務關鍵詞推斷領域：

| 關鍵詞（任一匹配即推斷） | 推斷領域 |
|----------------------|---------|
| `payment`, `billing`, `invoice`, `stripe`, `tax`, `finance`, `bank`, `trading`, `fintech` | 金融/支付 |
| `patient`, `medical`, `health`, `doctor`, `clinical`, `hospital`, `pharma`, `hipaa` | 醫療健康 |
| `cart`, `checkout`, `order`, `product`, `shop`, `ecommerce`, `catalog` | 電商 |
| `tenant`, `saas`, `subscription`, `dashboard`, `enterprise`, `workspace`, `b2b` | 企業 SaaS |
| 其他或無匹配 | 一般開發工具/其他 |

記錄推斷結果，例如：`偵測到業務關鍵詞：[stripe, billing]，推斷領域：金融/支付`。若無匹配，記錄「無業務關鍵詞，推斷：一般開發工具/其他」。

### 步驟 5 `[I]`：前置確認（整個流程唯一互動點）

> **⚠️ 這是整個掃描流程唯一需要使用者在場的互動步驟。回答後，Agent 自動執行 Phase 0 → Phase 1 → Phase 1.5，無需再值守。**

呈現偵測結果摘要，詢問以下兩個問題：

---

**Q1（業務領域確認，必填）**：

「Pre-flight 偵測完成。偵測到這是一個 [Framework] 專案，主要語言 [Language]。

根據關鍵詞分析，推斷業務領域為：**[步驟 4 推斷結果]**

請確認：
- 若推斷正確 → 直接按 Enter 繼續
- 若不對 → 輸入正確領域（金融交易 / 醫療健康 / 電商支付 / 企業 SaaS / 開發工具 / 其他）

有特殊合規要求嗎？（PCI-DSS / HIPAA / SOC 2 / GDPR / 無，若無直接按 Enter）」

等待使用者確認 Q1 後再繼續（Q1 必須等待，不設 timeout，因為此答案影響整個掃描的 severity 判斷）。

---

**Q2（刻意使用的 Pattern，選填）**：

「有沒有看起來像問題、但其實是刻意設計的程式碼模式？

例如：
- `except: pass` → 因為 middleware 統一處理所有例外
- 特定命名風格 → 因為外部 API 或舊資料庫 schema 約束
- 硬編碼 IP → 因為是本地開發測試用的固定位址

這些在 findings 中會標注 `[by design]`，confidence 自動降為 60，不作為需修復的發現。

**若 60 秒內無回應，自動設「無豁免 pattern」並繼續。若要整夜跑，回答 Q1 後直接離開即可。**」

收到回答後，或 60 秒無回應後，記錄結果並繼續步驟 6。

### 步驟 6 `[D]`：建立 `progress/constitution_preflight.md`

這份文件是 Phase 0 的「底層 context」，Phase 0 步驟 0 讀取後納入 MECE 分解的前提假設。

```markdown
# Preflight Context
> 由 Phase Preflight 自動生成。Phase 0 讀取後合併入 constitution.md。

## 自動偵測結果

### Framework 與語言
- 主要語言：[language]
- 主要 Framework：[framework 或 "未偵測到"]
- Framework 慣例注意（Phase 1 掃描時應排除）：
  - [例：Django migrations/ 目錄的 PascalCase class 為框架要求，非違規]
  - [例：React 元件函式使用 PascalCase，hooks 使用 useXxx，非違規]

### 現有 CI Toolchain
- [工具名稱]：[涵蓋範圍說明]
- 若 Phase 1 發現與上述工具重疊的問題，標注 [ci-covered]

### 已文件化的規範
- [摘錄自 CONTRIBUTING.md 或 docs/ 的規範條文]
- 若無文件：「無文件化規範」

## 使用者確認

### 業務領域與合規
- 業務領域：[user answer]
- 合規要求：[user answer]
- 領域對 severity 的影響：
  - [例：金融領域 → float 做財務計算升為 severity:high]
  - [例：醫療領域 → 未加密的個資欄位升為 severity:high]

### 豁免 Pattern 清單
- [pattern 描述]：[原因] → Phase 1 遇到時標注 [by design]，不輸出為 finding
- 若無：「無豁免 pattern」
```

### 步驟 7 `[D]`：更新 `progress/scan_plan.md`

```markdown
## Phase 狀態
- Phase -1（Pre-flight）：complete
- Phase 0（環境探測）：pending
...

## next
執行 Phase 0：閱讀 OmniHeal/phases/phase0_bootstrap.md，開始環境探測
```

---

## Preflight 完成檢查

在繼續 Phase 0 前，確認：
- [ ] `progress/constitution_preflight.md` 存在且包含「使用者確認」段落（非空白）
- [ ] Framework 慣例欄位已填寫（或明確標注「未偵測到」）
- [ ] 豁免 Pattern 清單已填寫（或明確標注「無」）
- [ ] `scan_plan.md` Phase -1 狀態為 `complete`

---

## 補充：Domain Severity 調整規則

根據業務領域，以下 pattern 的 severity 自動升級（寫入 constitution.md，Phase 1 遵守）：

| 領域 | Pattern | 原始 severity | 升級後 severity |
|------|---------|-------------|---------------|
| 金融交易 | float/double 做財務計算 | low | high |
| 金融交易 | 缺少交易 audit log | medium | high |
| 醫療健康 | 未加密的個資識別欄位 | medium | high |
| 醫療健康 | 硬編碼的病患 ID | high | high（維持） |
| 電商支付 | 信用卡號碼 pattern 出現在 log | low | high |
| 電商支付 | SQL 查詢未參數化（支付模組） | high | high（加 Pattern Alert） |
| 任何 | 硬編碼 API Key / Secret | high | high（維持） |
