繁體中文 | [English](README.en.md)

# OmniHeal

**零安裝 AI 專案健檢工具箱。**

將 OmniHeal git clone 進任何專案，然後告訴任何 AI coding agent：
> "請閱讀 @OmniHeal 開始進行"

Agent 讀取 `LAUNCH.md` 後，自動完成整個專案的掃描與改善建議。

---

## 為什麼需要 OmniHeal？

現有的 linting / 靜態分析工具存在三個根本問題：

| 問題 | 現有工具 | OmniHeal |
|------|---------|---------|
| **安裝依賴** | 需要 `npm install`、`pip install`、設定 CI | `git clone` 即用，零依賴 |
| **掃描中斷** | 中斷後重頭來，或不支援恢復 | Task Queue 架構，中斷後從第一個未完成任務繼續 |
| **只找問題** | 輸出 47 個 findings，開發者不知道修哪個 | SWOT+TOWS 分析，輸出「今日修復 / 本週 PR / 下季規劃」行動路線圖 |

**最關鍵的差異：** OmniHeal 不只告訴你「有什麼問題」，而是告訴你「這週花 2 個人日，應該修哪 3 件事，不修會怎樣」。

---

## 使用方式

**步驟 1：將 OmniHeal clone 進目標專案**

```bash
cd your-project/
```

```bash
git clone https://github.com/Chiakai-Chang/OmniHeal.git
```

**步驟 2：告訴任何 AI Agent（Claude、Copilot 等）**

```
請閱讀 @OmniHeal/ 開始進行
```

或更具體地：

```
請閱讀 @OmniHeal/，對 ./src 目錄執行程式碼健檢，使用 code_lint 技能
```

Agent 從這裡接手一切。

---

## 啟動須知：2 分鐘確認 + 全程自動

啟動後，Agent 先執行**一次前置確認**（Pre-flight 步驟 5），之後整個掃描全程自動。

| 階段 | 需要你在場？ | 時間估計 |
|------|-----------|---------|
| Pre-flight 前置確認（業務領域確認，唯一互動點） | ✅ 一次，約 2 分鐘 | 回答後即可離開 |
| Phase 0 → Phase 1 → Phase 1.5（完整掃描） | ✗ 全自動 | 數分鐘到數小時（依專案大小） |

> **建議：** 啟動 Agent 後，先完成前置確認問卷（~2 分鐘），確認後再離開讓它整夜跑完。
> 若直接離開，Agent 會在前置確認處等待，早上回來才能繼續。

---

## 你會得到什麼？

掃描完成後，OmniHeal 產出兩份文件：

### `summary.md`（審計快照）
```
掃描時間：2026-05-18 | 共 157 個檔案 | 高風險發現 8 個
跳過統計：3 個（編碼問題 2、超大二進位 1）
⚠️ AI 限制聲明：本報告基於靜態分析，不保證窮盡所有問題
```

### `action_plan.md`（行動路線圖）
```
⚡ 今日修復（高威脅 × 低工時）
- [ ] config.py:12 — 硬編碼 API Key（~30 分鐘）
  不修後果：憑證洩漏即可存取第三方服務

📅 本週 PR（弱點聚類 × 機會）
- [ ] src/db/ SQL 注入系統性修復（解決 #1, #4, #7，同一根因）
  參考範本：src/auth/ 已正確實作

💪 強項維持
- src/auth/：zero high findings → 作為其他模組的修復範本
```

---

## 適用情境

| 使用者 | 情境 | 關鍵效益 |
|--------|------|---------|
| **技術顧問 / 架構師** | 接手老舊專案，摸清技術債全貌 | 一夜掃完 → action_plan.md 給出改善優先順序，不靠憑感覺 |
| **政府 / 企業採購承辦人** | 廠商系統驗收 code review | 不需要懂程式：clone → Agent 掃 → 拿 severity 分級報告要求廠商改善 |
| **AI / ML 工程師** | 本地 LLM 訓練腳本技術債 | Hardcoded 路徑、magic number、無 seed、無 OOM 處理 — 一次全抓 |
| **外包發包方** | 廠商交付物驗收談判 | findings 列表直接作為合約附件，改完再付尾款 |
| **開源維護者** | 外部 PR 合併前品質閘 | 自動對齊專案自身理念（CONTRIBUTING.md / ADR），不符合即升 severity |
| **資安合規團隊** | 正式稽核前低成本自查 | 先抓明顯問題，避免花大錢請稽核顧問被抓到低級漏洞 |

### 技能 × 情境

| 技能 | 適用情境 |
|------|---------|
| `skill_code_lint` | 程式碼品質、命名、安全漏洞、技術債掃描 |
| `skill_log_parse` | 系統日誌異常排查、格式不一致、高頻錯誤聚類分析 |
| `skill_text_align` | 政府公文 AI 轉錄品質、會議記錄同音字錯誤（台灣常見：「系統」→「西統」）、法規文件校對 |

### 誠實邊界

不適合：**Runtime bug 追蹤**（靜態分析，不執行程式）、**即時 CI/CD 閘**（設計定位是深度一次性健檢）、**SQL DDL 審查**（目前技能未覆蓋）。

---

## 運作流程

| 階段 | 做什麼 |
|------|--------|
| Pre-flight | 偵測 framework 慣例、CI toolchain、業務領域風險等級 |
| Phase 0 | 掃描目錄、MECE 治理問題（1–3 個）、產生 Task Queue |
| Phase 1 | 消耗 queue，逐一掃描，3-Strike Protocol 確保不中斷 |
| Phase 1.5 | SWOT 分析 → 產出 summary.md + action_plan.md |

---

## 可用技能

| 技能名稱 | 適用對象 |
|---------|---------|
| `skill_code_lint` | 程式碼：命名、安全風險、過時寫法 |
| `skill_log_parse` | 日誌：格式不一致、高頻錯誤、異常 |
| `skill_text_align` | 文字稿：AI 轉錄錯誤、同音字替換 |

---

## 設計基礎：14 個 repo 的蒸餾

OmniHeal 的每一個設計決策都有來源。以下是關鍵採用點：

| 來源 | 採用設計 | 解決的問題 |
|------|---------|----------|
| [Manus AI / planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 3-file 進度結構、3-Strike Protocol、Reboot Test | Agent 重啟後無縫恢復 |
| [Anthropic / claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 信心度門檻（≥80）、誤報優先設計 | 避免「報了 47 個問題有 30 個是假陽性」 |
| [ECC（黑客松冠軍）](https://github.com/affaan-m/everything-claude-code) | 分析深度等級（fast/standard/deep）、Context Budget 安全閘、Phase 1.5 De-Sloppify | 大型專案全程掃描品質一致 |
| [Continuous-Claude-v3](https://github.com/parcadei/Continuous-Claude-v3) | Claim Verification（✓ VERIFIED / ? INFERRED）| 研究發現 80% 的 AI 程式碼聲明未讀原始碼即輸出 |
| [PageIndex](https://github.com/VectifyAI/PageIndex) + [llm-wiki-plugin](https://github.com/VectifyAI/PageIndex) | 先建索引再深潛、findings 雙層結構、surgical append | 大型專案不盲目逐行掃描 |
| [Understand-Anything](https://github.com/Lum1104/Understand-Anything) | 確定性優先（probe.py 做結構提取，LLM 做語義判斷）| 不浪費 LLM token 在可用規則計算的事 |
| [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | Task Queue 恢復點設計、last_updated 時間戳 | 夜間無人值守長程掃描穩健性 |
| [PUA + YES.md](https://github.com/tanweai/pua) | Pattern Alert（冰山法則）、Level-2 方向自檢 | 發現一個問題時主動檢查同類型檔案 |
| [AIBDD](https://github.com/Waterball-Software-Academy/aixbdd) | D/S/I 動詞模型、Atomic Finding 原則 | 每條發現一個問題、一個位置、一個建議 |
| [MECE-ECS](https://github.com/Chiakai-Chang/mece-ecs) | MECE 治理問題設計 | Phase 0 治理問題不重疊、不遺漏 |
| [Andrej Karpathy Principles](https://github.com/multica-ai/andrej-karpathy-skills) | Think Before Coding / Simplicity First / Surgical Changes | 外部驗證 OmniHeal 設計哲學 |

> 完整研究決策紀錄：[`reference/RATIONALE.md`](reference/RATIONALE.md)（14 repos，每個都有採用項目與放棄原因）

---

## 核心設計原則

- **零安裝**：唯一依賴是 Python 3（僅標準函式庫）
- **永不中斷**：3-Strike Protocol 確保單一檔案失敗不停止整個掃描
- **高精度優先**：只輸出 `✓ VERIFIED`（已讀原始碼）且信心度 ≥ 80 的發現
- **可中斷恢復**：Task Queue 架構，恢復點 = queue 第一個未完成任務，不依賴 Agent 記憶力
- **Consulting 而非 Audit**：SWOT+TOWS 分析讓輸出從「47 個問題清單」升級為「這週修哪 3 個」
