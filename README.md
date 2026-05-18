# OmniHeal

**零安裝 AI 專案健檢工具箱。**

將 OmniHeal git clone 進任何專案，然後告訴任何 AI coding agent：
> "請閱讀 @OmniHeal 開始進行"

Agent 讀取 `LAUNCH.md` 後，自動在夜間完成整個專案的掃描。

## 使用方式

```bash
# 步驟 1：將 OmniHeal clone 進目標專案
cd your-project/
git clone <omniheal-repo-url> OmniHeal/

# 步驟 2：告訴任何 AI Agent（Claude、Copilot 等）
"請閱讀 @OmniHeal 開始進行"
# 或更具體地：
"請閱讀 @OmniHeal，對 ./src 目錄執行程式碼健檢，使用 code_lint 技能"
```

Agent 從這裡接手一切。

## 運作流程

| 階段 | 做什麼 |
|------|--------|
| Phase 0 | 掃描目錄結構，詢問 1–3 個治理問題，建立 `progress/constitution.md` |
| Phase 1 | 每批 20–30 個檔案逐一掃描，結果寫入 `progress/YYYY-MM-DD-<skill>/` |
| Phase 1.5 | 整合發現，產出 `progress/YYYY-MM-DD-<skill>/summary.md` |

## 可用技能

| 技能名稱 | 適用對象 |
|---------|---------|
| `skill_code_lint` | 程式碼：命名、安全風險、過時寫法 |
| `skill_log_parse` | 日誌：格式不一致、高頻錯誤、異常 |
| `skill_text_align` | 文字稿：AI 轉錄錯誤、同音字替換 |

## 核心設計原則

- **零安裝**：唯一依賴是 Python 3（僅標準函式庫）
- **永不中斷**：3-Strike Protocol 確保單一檔案失敗不會停止整個掃描
- **誤報優先**：只輸出 `✓ VERIFIED`（已讀原始碼）且信心度 ≥ 80 的發現
- **可中斷恢復**：中斷的掃描從 `progress/scan_plan.md` 的 `next:` 欄位自動恢復
