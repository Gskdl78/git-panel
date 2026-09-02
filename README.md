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

## 已知限制

- 傳統主控台（conhost，非 Windows Terminal）啟動時找不到終端機視窗，面板會安靜不出現（Windows 11 預設為 Windows Terminal，一般不受影響）
- Win11 視窗陰影邊框可能造成面板與終端機之間約 7px 視覺縫隙
- 多螢幕且縮放比例不同時，面板位置換算可能偏移
- 終端機最大化或貼齊右緣時，面板會被推到螢幕外（規格為固定貼右側）
