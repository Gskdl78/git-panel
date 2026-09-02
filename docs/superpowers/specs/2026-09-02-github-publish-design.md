# 發佈到 GitHub（gh CLI 整合）設計規格

日期：2026-09-02　狀態：已由使用者核准（對話中逐項確認）

## 一句話描述

按「推送」（或「同步」）時若偵測到專案尚未設定遠端，不硬推，改彈「發佈到 GitHub」精靈：可「貼現有倉庫網址」（純 git）或「新建 GitHub 倉庫」（gh repo create 一次完成建庫＋設遠端＋推送）。

## 使用者決策

- 呈現方式：推送時智慧引導，不加新按鈕（同步比照辦理 — 同樣會推送）。
- 新建倉庫：每次都問公開/私人，預設私人；倉庫名預設＝專案資料夾名，可改。
- gh CLI：由 controller 以 winget 代裝；精靈内仍需防呆（未安裝 → 新建選項停用＋中文安裝指引；未登入 → 提示 `gh auth login`）。

## 行為

1. `_push` / `_sync` 先查 `GitService.has_remote()`；無遠端 → `publish_wizard(panel)`，有 → 原行為不變。
2. 精靈第一步：兩個 radio（貼網址／新建）。gh 未安裝時「新建」停用並顯示指引（winget install GitHub.cli → gh auth login）。
3. 貼網址路徑：輸入網址 → 確認框（`git remote add origin <url>` ＋ `git push -u origin HEAD` 預覽）→ 依序執行、記錄輸出、refresh。
4. 新建路徑：先查 `gh auth status`（未登入 → 中文提示，不進精靈）→ 輸入名稱＋公開/私人 → 確認框（gh 指令預覽）→ `gh repo create <name> --private|--public --source=. --remote=origin --push` → 記錄、refresh。
5. 錯誤白話翻譯擴充（errors.py）：同名倉庫已存在、未登入 gh、連不上 GitHub。

## 模組

- `gh_service.py`（新）：`find_gh`/`gh_available`/`gh_authed`/`repo_create_args`（純函式）/`repo_create`。gh 呼叫比照 GitService.run 慣例（CREATE_NO_WINDOW、utf-8、errors=replace、stdin=DEVNULL）。
- `git_service.py`：新增 `has_remote() -> bool`。
- `ui/publish_wizard.py`（新）：`publish_wizard(panel)` 與內部對話框。
- `ui/commit_box.py`：`_push`/`_sync` 前置攔截。

## 測試約束

- 測試絕不呼叫真實 gh、不連網、不在 GitHub 建立任何東西：gh 相關一律 monkeypatch；貼網址路徑用本地 bare repo 當「網址」驗證真實 git 行為。

## 範圍外

- 多遠端管理、更換遠端 UI（進階區「發佈」鈕）、gh 自動安裝/自動登入。
