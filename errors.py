from __future__ import annotations

from git_service import GitResult

_PATTERNS: list[tuple[str, str]] = [
    ("[rejected]", "推送被拒：遠端有你還沒拉下來的新提交。請先按「拉取」或「同步」，再重新推送。"),
    ("non-fast-forward", "推送被拒：遠端有你還沒拉下來的新提交。請先按「拉取」或「同步」，再重新推送。"),
    ("CONFLICT", "發生合併衝突：兩邊改了同一個地方。衝突檔案已列在輸出區，可交給 Claude Code 或手動解決後再提交；也可按「中止合併」放棄這次合併。"),
    ("Authentication failed", "認證失敗：無法登入 GitHub。請確認你已安裝並登入 Git Credential Manager，或檢查帳號權限。"),
    ("could not read Username", "認證失敗：無法登入 GitHub。請確認你已安裝並登入 Git Credential Manager，或檢查帳號權限。"),
    ("No configured push destination", "尚未設定遠端倉庫：這個專案還沒連到 GitHub。可用進階區的「Clone」拉取現有專案，或先在 GitHub 建立倉庫後設定遠端。"),
    ("does not appear to be a git repository", "找不到遠端倉庫：請確認網址正確、倉庫存在且你有權限存取。"),
    ("not something we can merge", "找不到要合併的分支：請確認分支名稱正確。"),
    ("Please commit your changes or stash", "有未提交的變更擋住了這個操作：請先「提交」，或用進階區的「暫存」把變更收起來再試。"),
    ("couldn't find remote ref", "遠端沒有這個分支：遠端倉庫上還沒有對應的分支可以拉取。"),
    ("Name already exists", "GitHub 上已有同名倉庫：請換一個倉庫名稱，或改用「貼現有倉庫網址」連到既有的倉庫。"),
    ("gh auth login", "尚未登入 GitHub CLI：請在終端機執行 gh auth login，用瀏覽器完成登入後再試一次。"),
    ("Could not resolve hostname", "連不上 GitHub：請檢查網路連線後再試。"),
]


def explain_error(result: GitResult) -> str | None:
    text = result.text
    for pattern, message in _PATTERNS:
        if pattern.lower() in text.lower():
            return message
    return None
