# Git Panel 設計規格

日期：2026-09-02
狀態：已由使用者核准

## 一句話描述

一個磁吸在 Claude Code 終端機右側的 Git 圖形面板：按鈕觸發 Git 指令、點擊先顯示白話說明再確認執行、隨 Claude Code 自動開啟與關閉、隨終端機視窗移動縮放。

## 背景與目標

使用者的工作流程：在專案資料夾開啟終端機 → 輸入 `claude` 啟動 Claude Code。希望不用背 Git 指令，改用圖形按鈕操作 Git，且面板要「一直黏著終端機不分開」。

成功標準：

- 開啟 Claude Code 後面板自動出現並貼附在終端機右側。
- 拖動、縮放、最小化、還原終端機，面板即時跟隨；終端機或 Claude Code 關閉時面板自動消失。
- 日常 Git 操作（stage、commit、push、pull、分支、歷史、clone）都能透過按鈕與輸入框完成。
- 每個動作執行前都有白話說明與確認/取消，不會誤觸。

## 技術選型

- **Python 3.11+**
- **PySide6**（Qt for Python）— GUI
- **pywin32**（win32gui / win32process / win32con）— 視窗追蹤與磁吸
- **subprocess** 執行 git 指令（不依賴第三方 git 函式庫，輸出好解析、行為透明）
- 目標平台：Windows 11 的 Windows Terminal（傳統主控台 conhost 的視窗由旁系子進程持有、不在祖先鏈上，實作不支援 — 面板會安靜退出，詳見 README 已知限制）

## 架構

```
git-panel/
├── main.py                 # 進入點：解析參數、找終端機視窗、啟動面板
├── window_tracker.py       # Win32 視窗追蹤與磁吸邏輯
├── git_service.py          # 所有 git 指令的執行與輸出解析
├── ui/
│   ├── panel.py            # 主面板（直向堆疊各區塊）
│   ├── file_list.py        # 檔案變更清單（勾選 = stage）
│   ├── commit_box.py       # commit 訊息輸入 + 提交/推送/拉取/同步按鈕
│   ├── branch_bar.py       # 分支顯示與切換/新增/合併
│   ├── history_view.py     # commit 歷史 + diff 檢視
│   ├── advanced_bar.py     # 進階區（暫存/還原/重設/Clone）
│   ├── output_log.py       # 指令執行記錄與錯誤顯示
│   ├── confirm_dialog.py   # 共用確認框（說明 + 指令預覽 + 確認/取消）
│   └── wizards.py          # 多步驟精靈（合併、重設、Clone）
├── hook_setup.py           # 安裝/移除 Claude Code SessionStart hook
├── docs/superpowers/specs/ # 規格文件
└── tests/                  # git_service 與精靈邏輯的單元測試
```

各模組單一職責：UI 不直接跑 git（一律經過 `git_service`）；`window_tracker` 不認識 Git；`confirm_dialog` 是所有按鈕共用的閘門。

## 磁吸機制

1. **找到終端機視窗**：SessionStart hook 啟動面板時傳入 Claude Code 的進程資訊；面板沿進程樹（psutil / win32process）往上找到擁有視窗的終端機進程（WindowsTerminal.exe、conhost 等），取得 HWND。找不到時退回使用當時的前景視窗，並在輸出區提示。
2. **跟隨**：QTimer 每 30–60ms 輪詢 `GetWindowRect`，把面板設為：`x = 終端機右緣`、`y = 終端機頂緣`、`寬 = 320px（固定）`、`高 = 終端機高度`。
3. **狀態同步**：終端機最小化 → 面板隱藏；還原 → 面板重現；視窗代碼失效（終端機關閉）→ 面板結束。另外輪詢 Claude Code 進程，結束時面板自動關閉。
4. **視窗樣式**：無工作列圖示的工具視窗（Qt.Tool），不搶焦點。
5. **防重複**：以終端機 HWND 為鍵的鎖定檔（`%TEMP%` 下），同一終端機最多一個面板；多個終端機各有各的面板。

## 介面佈局（寬 320px，高度隨終端機）

由上到下：

1. **狀態列**：專案資料夾名、目前分支、ahead/behind（↑n ↓n）。
2. **檔案變更**：變更檔案清單，勾選 = stage、取消勾選 = unstage；點檔名開 diff 檢視。
3. **提交區**：commit 訊息多行輸入框；按鈕 `[提交] [推送] [拉取] [同步]`（同步 = pull --rebase 後 push，說明會寫清楚）。
4. **分支區**：分支下拉清單；按鈕 `[切換] [新增] [合併]`。
5. **歷史區**：最近 commit 清單（短 hash + 訊息）；點擊看該次 diff。
6. **進階區**（預設收合）：`[暫存] [還原] [重設] [標籤] [Clone]`。
7. **輸出區**：每次執行的實際指令與結果；錯誤以紅字顯示白話說明與建議。

介面全繁體中文；按鈕名稱 2–3 字。

## 確認流程（所有按鈕共通）

點擊任何動作按鈕 → 彈出確認框，內容包含：

- 白話說明這個動作會做什麼（含目前狀態，例如「將本地 main 的 2 個提交上傳」）。
- 實際將執行的 git 指令（等寬字型顯示）。
- `[確認] [取消]` 按鈕。
- 危險操作（reset --hard、強制推送等）以紅色警告樣式呈現，確認按鈕文字改為「我了解風險，執行」。

## 多步驟精靈

- **合併**：選來源分支 → 顯示說明與影響 → 確認執行。
- **重設**：從歷史選 commit → 選模式（保留變更 soft/mixed、完全丟棄 hard，各附白話說明）→ 危險確認。
- **Clone**：輸入 GitHub 網址 + 選擇目的資料夾 → 確認後執行，輸出區顯示進度。
- **非 git 資料夾（精簡模式）**：面板只顯示 `[初始化]` 與 `[Clone]` 兩鈕；完成後自動切換為完整面板。

## 自動啟動（Claude Code hooks）

- `hook_setup.py install`：把 SessionStart hook 寫入 `~/.claude/settings.json`（保留既有設定，僅附加）；hook 以背景方式（pythonw、detached）啟動面板並傳入進程資訊，不阻塞 Claude Code 啟動。
- 面板存活與否不依賴 SessionEnd hook（以進程/視窗輪詢為準），SessionEnd 僅作為輔助清理。
- `hook_setup.py uninstall`：移除 hook。

## 錯誤處理

- git 指令非零結束碼：輸出區紅字顯示「白話翻譯 + 建議」，常見情境（push 被拒、需要先 pull、合併衝突、無遠端、認證失敗）有對應訊息；未知錯誤顯示原始輸出。
- 合併衝突：不自動處理；列出衝突檔案，提示交給 Claude Code 或手動解決，並提供 `[中止合併]` 按鈕。
- 面板任何內部例外不得讓 Claude Code 受影響（完全獨立進程）。

## 測試策略

- `git_service`：pytest + 臨時 git repo（tmp_path），驗證狀態解析、stage/commit/push（本地 bare repo 模擬遠端）、錯誤分類。
- 精靈與確認邏輯：純邏輯層單元測試（指令組裝、危險等級判定）。
- 磁吸行為：手動驗收清單（拖動、縮放、最小化、關閉、多開、非 git 資料夾）。

## 範圍外（YAGNI）

- 左右側切換、寬度比例縮放（固定右側 320px，可日後再加）。
- rebase 互動模式、submodule、GPG 簽章、多遠端管理。
- macOS / Linux 支援。
