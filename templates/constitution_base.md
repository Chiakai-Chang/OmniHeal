# 治理規則文件（Constitution）

> 本文件由 OmniHeal Phase Preflight + Phase 0 共同生成，記錄掃描前確認的治理規則。
> 這些規則作為 Phase 1 掃描的「底線」：所有發現以此為基礎判斷問題的嚴重程度。
> 如需更新治理規則，直接編輯 `progress/constitution.md` 後重新執行相關 Phase。

## 基本資訊

- **目標目錄**：[Phase 0 填入]
- **主要語言**：[Pre-flight 偵測 / Phase 0 確認]
- **主要 Framework**：[Pre-flight 偵測 / 若無填入「未偵測到」]
- **掃描日期**：[Phase 0 填入]
- **上次更新**：[Phase 0 填入]

---

## Pre-flight 偵測結果（由 phase_preflight.md 生成）

### Framework 慣例排除
[Phase Preflight 填入。Phase 1 掃描時，這些 pattern 不視為違規。]

範例：
```
- Django migrations/ 目錄的 PascalCase class：框架要求，非違規
- React 元件函式使用 PascalCase，hooks 使用 useXxx：框架要求，非違規
- Go init() 函式：語言保留，非命名違規
```

若未偵測到 framework，填入：「無 framework 特定排除規則」。

### 現有 CI Toolchain
[Phase Preflight 填入。Phase 1 發現與此重疊的問題時，標注 `[ci-covered]`。]

範例：
```
- ESLint (strict)：涵蓋命名、未用變數、型別基本檢查
- mypy：涵蓋 Python 型別標注一致性
```

若未偵測到 CI toolchain，填入：「未偵測到現有 toolchain」。

### 業務領域與合規
[Phase Preflight 步驟 5 Q1 使用者回答填入。]

- **業務領域**：[例：金融交易 / 醫療健康 / 電商支付 / 企業 SaaS / 其他]
- **合規要求**：[例：PCI-DSS / HIPAA / SOC 2 / GDPR / 無]
- **領域對 severity 的影響**：
  - [例：金融領域 → float/double 做財務計算升為 severity:high]
  - [例：醫療領域 → 未加密的個資識別欄位升為 severity:high]

### 豁免 Pattern 清單
[Phase Preflight 步驟 5 Q2 使用者回答填入。Phase 1 遇到這些 pattern 時標注 `[by design]`，confidence 設為 60，不輸出為需修復的 finding。]

範例：
```
- except: pass 在 middleware.py：設計上由 Flask error handler 統一攔截
- DB_HOST = "192.168.1.100"：開發環境固定位址，已有 .env.example 說明
```

若無豁免 pattern，填入：「無豁免 pattern」。

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
