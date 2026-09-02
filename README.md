# Git Panel

磁吸在 Claude Code 終端機右側的 Git 圖形面板。按鈕觸發 Git 指令、執行前有白話說明與確認、隨終端機移動縮放、隨 Claude Code 自動開關。

## 需求

- Windows（面板定位依賴 Win32 API）
- Python 3.11 以上
- 已安裝 `git` 並可在 PATH 中執行

## 安裝

```
pip install -r requirements.txt
python hook_setup.py install
```

`install` 會在 `~/.claude/settings.json` 加入一條 SessionStart hook。之後每次在任何資料夾開啟 Claude Code（輸入 `claude`），面板就會自動出現在終端機右側。

## 手動啟動（不經 hook）

在專案資料夾的終端機執行：

```
python main.py
```

## 移除自動啟動

```
python hook_setup.py uninstall
```

只會移除自己那一條 hook，`settings.json` 內其他設定不受影響。

## 測試

```
python -m pytest tests/ -v
```
