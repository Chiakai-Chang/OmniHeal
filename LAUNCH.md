# OmniHeal 啟動手冊

## 你是誰、你要做什麼

你是一個 AI 代理（Agent），被要求對某個專案執行「健康檢查」（Health Check）。

OmniHeal 是放進目標專案裡的「AI 代理指令手冊 + 輔助工具箱」。你的任務：
1. 快速理解目標專案的技術特性（Pre-flight）
2. 探測目標目錄的結構與性質（Phase 0）
3. 逐一掃描所有文字檔，依照選定技能進行分析（Phase 1）
4. 整合發現，產出結構化報告（Phase 1.5）

**你使用的工具都是標準工具**：讀檔、寫檔、執行 Bash 指令。你不需要呼叫任何外部 API 或第二個模型。你本身就是分析引擎。

**最關鍵的原則**：**掃描永遠不能因為單一檔案失敗而中斷。** 遇到任何錯誤，記錄下來，繼續處理下一個檔案。

---

> **⚠️ 互動說明（啟動前閱讀）**
>
> Pre-flight 步驟 5 是整個流程**唯一**需要使用者在場的互動點：
> - **Q1（業務領域）**：必須等待確認，約 1–2 分鐘。若推斷正確，按 Enter 即可。
> - **Q2（豁免 Pattern）**：選填，60 秒無回應自動設「無」並繼續。
>
> **完成 Pre-flight 步驟 5 後，全程自動執行至 Phase 1.5 產出報告，無需值守。**
> 建議回答確認後再離開，避免 Agent 停在等待狀態過夜。

---

## ★ 第零步：先確認是否有未完成的工作（必做）

在做任何事之前，**先讀 `progress/scan_plan.md`**。

```
如果 Phase 1 狀態是 in_progress → 恢復上次掃描（見「重啟自我檢查」章節）
如果 Phase -1 狀態是 in_progress → 恢復 Pre-flight（重新讀 phases/phase_preflight.md）
如果沒有 scan_plan.md，或所有 Phase 都是 complete → 開始新任務（繼續往下讀）
```

---

## 本次任務（若為新任務）

- **目標目錄**：使用者指定的目錄（例如 `../src`）；若未指定，預設為 OmniHeal 父目錄
- **使用技能**：使用者指定（`skill_code_lint` / `skill_log_parse` / `skill_text_align`）；若未指定，預設為 `skill_code_lint`
- **輸出目錄**：`progress/YYYY-MM-DD-<skill>/`（用今天日期和技能名稱命名）

可用技能：

| 技能名稱 | 適用對象 |
|---------|---------|
| `skill_code_lint` | 程式碼檔案（命名、安全、過時寫法） |
| `skill_log_parse` | 日誌檔案（格式不一致、高頻錯誤、異常） |
| `skill_text_align` | 文字稿（AI 轉錄錯誤、同音字替換） |

---

## 里程碑（依序執行）

1. 閱讀 `phases/phase_preflight.md`，快速理解目標專案（framework、toolchain、domain），建立 `progress/constitution_preflight.md`
2. 閱讀 `phases/phase0_bootstrap.md`，執行環境探測，建立 `progress/constitution.md` 和 `progress/file_index.md`
3. 確認 `progress/scan_plan.md` 的 Phase 0 狀態已標記為 `complete`
4. 閱讀 `phases/phase1_scanner.md`，開始逐批掃描
5. 每完成一個批次，更新 `progress/scan_plan.md` 的 `next:` 與 `last_updated:` 欄位
6. 掃描完成後，執行 Phase 1.5（見 `phases/phase1_scanner.md` 末段），產出 `summary.md`

---

## 重啟自我檢查（中斷後必做）

若掃描中斷後重新啟動，**依序**讀以下最小必要 context（不多讀）：

1. `progress/scan_plan.md` → 看 `next:` 欄位（定向，30 秒）
2. `progress/YYYY-MM-DD-<skill>/findings_index.md` **最後 20 行**（確認最近掃描狀態）
3. `progress/YYYY-MM-DD-<skill>/session_log.md` **最後 10 行**（確認上次做到哪裡）
4. **直接按 `next:` 欄位的指示繼續，無需詢問使用者**

**嚴禁**：恢復時重新讀取所有 `findings/[filename].md` 詳細頁（context pollution，讓你沒有足夠 context 繼續掃描）。

### 6-Question Reboot Test（恢復前自問）

恢復掃描時，依序讀以下最小必要 context：
1. `progress/scan_plan.md`（目標、Phase 狀態）
2. `progress/queue/` 目錄清單（找第一個 pending task）
3. `progress/YYYY-MM-DD-<skill>/findings_index.md` **最後 20 行**（確認最近狀態）

然後確認你能回答這 6 個問題：
1. 我在掃描哪個目錄？（`scan_plan.md` 的目標目錄）
2. 現在跑到哪個 Phase？（`scan_plan.md` 的 Phase 狀態）
3. 這次的任務目標是什麼？（`scan_plan.md` 的目標目錄與使用技能）
4. 我已經發現了什麼？（`findings_index.md` 的最後 20 行）
5. **下一個任務是什麼？**（`progress/queue/` 第一個 `status: pending` 的 task 文件）
6. **Calibration Check**：截至目前最嚴重發現的 file:line 和 severity 是什麼？
   - 能清楚說出 → 繼續，保持 task 文件指定深度
   - 記憶模糊 → 繼續，但**將下個 task 降級至 `fast` 深度**
   - 完全想不起來（且有發現記錄）→ 停止，下次 session 用乾淨 context 重啟

若能回答全部 6 題，直接執行第 5 題的 pending task，**不需詢問使用者**。

---

## 絕對不能做的事

- ❌ 遇到任何錯誤中斷整個掃描（記錄後繼續，見 Phase 1 的 3-Strike Protocol）
- ❌ 跳過更新 `scan_plan.md` 的 `next:` 與 `last_updated:` 欄位
- ❌ 恢復後詢問使用者「我應該繼續嗎？」（讀 `scan_plan.md` 的 `next:` 即可）
- ❌ 把設定值（目標目錄、技能名稱）寫死在任何地方
- ❌ 恢復時重新讀取所有歷史 findings 詳細頁
- ❌ 輸出 `? INFERRED`（只靠 grep 推斷，未讀原始碼）的發現到 findings
