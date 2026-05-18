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
- **適用語言**：所有語言
- **標準**：非測試、非示例檔案中，字串賦值包含疑似密碼/金鑰的模式
  - `password = "xxx"` / `api_key = "sk-..."` / `secret = "..."` / `token = "..."` 等
- **排除**：
  - 測試檔案中明確標注的假資料（`test_password = "test123"` 在 `test_*.py` 中）
  - 空字串賦值（`password = ""`）
  - 從環境變數讀取（`password = os.getenv("DB_PASSWORD")`）
- **severity**：high | **confidence 閾值**：85

### 規則 2：SQL 字串拼接（注入風險）（優先順序：最高）
- **適用語言**：所有語言
- **標準**：SQL 查詢字串使用字串格式化或拼接（`%s %` format、f-string 插入、`+` 拼接）而非參數化查詢
- **排除**：
  - 字串本身不包含任何變數（純靜態查詢字串）
  - 已使用 ORM 的 filter/query 方法（不直接拼 SQL）
- **severity**：high | **confidence 閾值**：85

### 規則 3：未處理的異常（空 catch/except）（優先順序：高）
- **適用語言**：所有語言
- **標準**：`except:` 或 `catch` 區塊中只有 `pass`、`continue`，或完全空白
- **排除**：
  - 有明確 `log()`/`logger.`/`raise`/`return` 的 catch 區塊
  - 有 `# intentionally ignored` 類的明確說明注釋
- **severity**：high | **confidence 閾值**：80

### 規則 4：Python 函式命名不符 snake_case（優先順序：中）
- **適用語言**：**僅 `.py` 檔案**（JavaScript/TypeScript/Go 等語言有各自的命名慣例，不適用本規則）
- **標準**：Python 函式定義（`def`）使用 camelCase 或 PascalCase
  - `def doLogin(...)` / `def DoLogin(...)` → 不符合
- **排除**：
  - 類別定義（class 允許 PascalCase）
  - 從外部 library 繼承 override 的方法（如 Django 的 `setUp`）
  - 有 `# noqa` 或 `# type: ignore` 的行
- **severity**：medium | **confidence 閾值**：80

### 規則 5：函式超過 50 行（優先順序：中）
- **適用語言**：所有語言（`def` / `function` / `func` 關鍵字）
- **標準**：從 `def`/`function`/`func` 到函式結尾的行數超過 50
- **排除**：
  - 測試函式（`test_`、`spec_`、`it_` 開頭）
  - 有 `# generated` / `# auto-generated` 注釋的函式
- **severity**：medium | **confidence 閾值**：90（行數是確定性指標，信心度高）

### 規則 6：硬編碼的 IP 位址（優先順序：中）
- **適用語言**：所有語言
- **標準**：非設定檔、非測試檔中出現 IPv4 位址字串（如 `"192.168.1.1"`）
- **排除**：
  - 本機位址（`127.0.0.1`、`0.0.0.0`、`localhost`）在開發設定中
  - 位址在文件字串（docstring）或注釋中
- **severity**：medium | **confidence 閾值**：80

### 規則 7：Python 2 print 語句（優先順序：低）
- **適用語言**：**僅 `.py` 檔案**
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
