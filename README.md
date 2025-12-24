# Hashcat Password Structure Analysis

> 密碼結構安全性分析實驗專案 - 使用 Hashcat 進行系統性密碼破解測試

## 🎯 專案簡介

本專案透過 Hashcat 工具對不同密碼特徵（長度、複雜度、特殊字符、位置等）進行系統性破解測試，並透過資料分析與視覺化儀表板呈現實驗結果，為密碼政策制定提供實證依據。

## 📊 主要功能

### 🔬 實驗測試
- **長度影響分析**: 8-12 字符密碼破解時間測試
- **字符複雜度測試**: Level 1-3 複雜度分類
- **特殊字符影響**: +1 至 +4 特殊字符數量測試
- **位置影響分析**: Prefix、Suffix、Mixed 位置比較

### 📈 數據分析
- Python 統計分析腳本
- 箱型圖、長條圖、折線圖視覺化
- 完整統計指標 (Min, Q1, Median, Q3, Max, Mean, IQR)

### 💻 互動式儀表板
- React + Recharts 開發
- 黑色主題專業設計
- 即時數據篩選與互動
- 響應式佈局設計

## 🚀 快速開始

### 在線查看 Dashboard

訪問已部署的線上版本：

**🌐 (https://hashcat-password-structure-analysis-five.vercel.app/)**

### 本地啟動 Dashboard

\`\`\`bash
cd dashboard
npm install
npm run dev
\`\`\`

訪問 http://localhost:3002

### 執行數據分析

\`\`\`bash
# 特殊字符分析
cd graph/mask
python get_special_stats.py

# 複雜度分析
cd graph/other
python complexity_time.py
\`\`\`

## 📁 目錄結構

\`\`\`
exam/
├── dashboard/          # React 儀表板
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ExperimentDesign.jsx
│   │   │   └── Results.jsx
│   │   └── App.jsx
│   └── package.json
│
├── graph/             # Python 分析腳本
│   ├── mask/          # Mask Attack 分析
│   ├── dict/          # Dictionary Attack 分析
│   └── other/         # 其他分析
│
├── round1/            # 第一輪實驗數據
├── round2/            # 第二輪實驗數據
└── dictionary/        # 字典檔案（大型文件已移除）
\`\`\`

## 📦 字典文件說明

由於 GitHub 對單個文件大小有限制（100MB），以下大型字典文件已從倉庫中移除：

- `dictionary_prew.txt` (217.50 MB)
- `hashmob.net.user.found.txt` (716.30 MB)
- `hashmob.net.medium.found.txt` (114.73 MB)
- `dictionary-100mb.txt` (85.99 MB)
- `dictionary1.txt` (72.50 MB)
- `dictionary2.txt` (72.49 MB)
- `dictionary3.txt` (72.50 MB)

### 如何獲取字典文件

如需使用字典攻擊功能，請自行下載常用密碼字典：

1. **RockYou 字典**：最常用的密碼字典
   - 下載：https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
   - 放置位置：`dictionary/rockyou.txt`

2. **SecLists 密碼集合**：多種密碼列表
   - GitHub：https://github.com/danielmiessler/SecLists
   - 子目錄：`Passwords/`

3. **其他來源**：
   - Weakpass：https://weakpass.com/
   - Hashes.org：https://hashes.org/leaks.php

### 字典使用範例

\`\`\`bash
# Dictionary Attack
hashcat -m 100 -a 0 hash.txt dictionary/rockyou.txt

# Hybrid Attack (字典 + 遮罩)
hashcat -m 100 -a 6 hash.txt dictionary/rockyou.txt ?d?d
\`\`\`

## 🔑 主要發現

### 密碼長度影響
- **8→12 字符**: 破解時間從 14.07s 增長到 19936.46s（1418 倍）
- **最佳建議**: 至少使用 12 字符密碼

### 字符複雜度影響
- **Level 1→3**: 破解時間增長 428 倍
- **最佳建議**: 使用多種字符類型（大小寫、數字、特殊字符）

### 特殊字符效果
- **+1 特殊字符**: 破解時間增加 16%
- **+4 特殊字符**: 破解時間增加 190%

### 位置影響
- **Mixed 位置**: 平均破解時間最長（267.50s）
- **最佳建議**: 將特殊字符分散放置

## 🛠️ 技術棧

- **Hashcat 7.1.2** - 密碼破解引擎
- **Python 3.x** - 數據分析 (matplotlib, numpy)
- **React 18.2** - 前端框架
- **Recharts 2.10** - 圖表庫
- **Vite 5.0** - 構建工具

## 📚 文件說明

- [Hashcat攻擊模式指令說明.md](Hashcat攻擊模式指令說明.md) - 詳細指令文件
- [Hashcat狀態輸出解析.md](Hashcat狀態輸出解析.md) - 輸出格式說明
- [dashboard/README.md](dashboard/README.md) - Dashboard 使用說明

## ⚠️ 免責聲明

本專案僅供學術研究和教育目的使用。使用者應遵守當地法律法規，不得將本工具用於未經授權的密碼破解活動。

## 📝 授權

MIT License

## 👥 貢獻者

**第二組 - 密碼破解軟體研究小組**

---

**最後更新**: 2025-12-24
