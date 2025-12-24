# GitHub 推送指南

## 📋 當前狀態

✅ Git 倉庫已初始化
✅ 所有文件已提交（467 個文件）
✅ .gitignore 已配置
✅ README.md 已創建

## 🚀 下一步：推送到 GitHub

### 步驟 1: 在 GitHub 創建新倉庫

1. 訪問 https://github.com/new
2. 填寫以下資訊：
   - **Repository name**: `hashcat_password_structure_analysis`
   - **Description**: `Hashcat Password Structure Analysis - 密碼結構安全性分析實驗專案`
   - **Visibility**: 選擇 Public 或 Private
   - **⚠️ 重要**: 不要勾選 "Initialize this repository with a README"（因為我們已經有了）

3. 點擊 "Create repository"

### 步驟 2: 添加遠程倉庫並推送

創建倉庫後，GitHub 會顯示推送指令。在 PowerShell 中執行以下命令：

\`\`\`powershell
# 進入專案目錄
cd C:\Users\USER\Documents\hashcat-7.1.2\exam

# 添加遠程倉庫（請替換 YOUR_USERNAME 為你的 GitHub 用戶名）
git remote add origin https://github.com/YOUR_USERNAME/hashcat_password_structure_analysis.git

# 推送代碼到 GitHub
git branch -M main
git push -u origin main
\`\`\`

### 步驟 3: 驗證推送成功

訪問你的 GitHub 倉庫頁面，應該可以看到所有文件已成功上傳。

## 🔐 認證方式

### 方式 1: Personal Access Token (推薦)

1. 訪問 https://github.com/settings/tokens
2. 點擊 "Generate new token (classic)"
3. 選擇權限：勾選 `repo` (完整倉庫訪問權限)
4. 點擊 "Generate token"
5. **複製 Token**（只會顯示一次！）
6. 在推送時，使用 Token 作為密碼

### 方式 2: SSH Key

如果你已經設置了 SSH Key，可以使用 SSH URL：

\`\`\`powershell
git remote add origin git@github.com:YOUR_USERNAME/hashcat_password_structure_analysis.git
git push -u origin main
\`\`\`

## 📦 倉庫資訊

- **總文件數**: 467 個文件
- **總代碼行數**: 68,998,792 行插入
- **主要內容**:
  - ✅ Dashboard (React + Vite)
  - ✅ Python 分析腳本
  - ✅ 實驗數據 (Round 1-2)
  - ✅ 字典文件
  - ✅ 文檔說明

## 🔄 後續更新

當需要更新代碼時，使用以下命令：

\`\`\`powershell
# 查看修改
git status

# 添加所有修改
git add .

# 提交修改
git commit -m "描述你的修改"

# 推送到 GitHub
git push
\`\`\`

## ❓ 常見問題

### Q: 推送時出現 "failed to push some refs"
**A**: 先拉取遠程更新：
\`\`\`powershell
git pull origin main --rebase
git push
\`\`\`

### Q: 推送時要求輸入用戶名和密碼
**A**: 使用 Personal Access Token 作為密碼，不是你的 GitHub 登入密碼。

### Q: 文件太大無法推送
**A**: 已在 .gitignore 中排除 node_modules 等大型文件夾，應該沒問題。

---

**準備好了嗎？** 按照步驟 1-3 完成推送吧！ 🚀
