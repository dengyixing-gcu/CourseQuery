#!/bin/bash

echo "========================================"
echo "  课表智能助手 - GitHub + Render 部署"
echo "========================================"
echo ""

# 检查 Git
if ! command -v git &> /dev/null; then
    echo "[错误] 未安装 Git!"
    echo "请先安装：sudo apt-get install git"
    exit 1
fi

# 获取 GitHub 用户名
echo "请输入您的 GitHub 用户名:"
read -r GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "[错误] GitHub 用户名不能为空"
    exit 1
fi

REPO_NAME="teacher-schedule-assistant"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo ""
echo "仓库地址：${REPO_URL}"
echo ""

# 初始化 Git
if [ ! -d ".git" ]; then
    echo "[1/5] 初始化 Git 仓库..."
    git init
    git checkout -b main 2>/dev/null || git checkout main
fi

# 添加文件
echo "[2/5] 添加文件..."
git add .

# 提交
echo "[3/5] 提交更改..."
git commit -m "feat: 课表智能助手初始版本"

# 添加远程仓库
echo "[4/5] 配置远程仓库..."
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"

echo ""
echo "========================================"
echo "  [5/5] 推送到 GitHub"
echo "========================================"
echo ""
echo "请输入您的 GitHub Token 或使用 HTTPS 密码:"
echo "(获取 Token: https://github.com/settings/tokens)"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "  ✅ 推送成功!"
    echo "========================================"
    echo ""
    echo "下一步操作:"
    echo "1. 访问 https://render.com"
    echo "2. 登录/注册 Render 账号"
    echo "3. 点击 'New +' → 'Web Service'"
    echo "4. 连接仓库：${REPO_NAME}"
    echo "5. 使用以下配置:"
    echo ""
    echo "   Build Command: pip install -r requirements.txt"
    echo "   Start Command: gunicorn app:app --bind 0.0.0.0:\$PORT"
    echo ""
    echo "6. 点击 'Create Web Service'"
    echo ""
    echo "部署完成后，您将获得一个 https:// 开头的访问地址!"
    echo ""
else
    echo ""
    echo "========================================"
    echo "  ❌ 推送失败"
    echo "========================================"
    echo ""
    echo "请检查:"
    echo "1. GitHub 用户名是否正确"
    echo "2. 是否已在 GitHub 创建同名仓库"
    echo "3. 认证信息是否正确"
    echo ""
fi
