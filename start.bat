@echo off
chcp 65001 > nul
title LLM质量分析系统启动器

echo.
echo ============================================================
echo 🔍 LLM质量分析系统 - Windows启动脚本
echo ============================================================
echo.

echo 📋 正在检查Python环境...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH中
    echo 请安装Python 3.8及以上版本
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

echo 🚀 启动LLM质量分析系统...
python start.py

echo.
echo 👋 应用已停止
pause 