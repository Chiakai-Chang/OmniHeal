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
