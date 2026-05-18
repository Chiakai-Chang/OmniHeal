# OmniHeal 掃描狀態

> 此檔案由 OmniHeal Phase Preflight 自動建立，Phase 0/1 持續更新。
> Agent 恢復掃描時，**只讀 `next:` 欄位**，直接繼續，不需詢問使用者。
> `last_updated:` 欄位讓使用者判斷掃描是否卡住（超過 30 分鐘沒更新 = 可能中斷）。

## 當前掃描任務
- 目標目錄：（Phase 0 填入）
- 使用技能：（Phase 0 填入）
- 開始時間：（Phase 0 填入）
- last_updated：（Phase 0 填入）
- 輸出目錄：（Phase 0 填入）

## Phase 狀態
- Phase -1（Pre-flight）：pending
- Phase 0（環境探測）：pending
- Phase 1（全域掃描）：pending
- Phase 1.5（發現清理）：pending

## Phase 1 批次計畫
（Phase 1 開始後由 Agent 填入）

## 跳過統計
（Phase 1 完成後由 Agent 填入）

## next
執行 Phase -1：閱讀 OmniHeal/phases/phase_preflight.md，開始目標專案快速理解

## 追蹤欄位
- last_finding_number：0
