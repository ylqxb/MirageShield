@echo off

REM MirageShield 一键部署脚本 (Windows)
REM © 2026 MirageShield 团队 版权所有，侵权必究

echo ============================================
echo MirageShield 一键部署脚本
echo ============================================

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python 未安装，请先安装 Python 3.8-3.11
    pause
    exit /b 1
)

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

REM 检查 Docker 是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker 未运行，请启动 Docker Desktop
    pause
    exit /b 1
)

echo 正在构建 Docker 镜像...
docker build -t mirageshield .
if %errorlevel% neq 0 (
    echo 错误: 构建 Docker 镜像失败
    pause
    exit /b 1
)

echo 正在启动容器...
docker-compose up -d
if %errorlevel% neq 0 (
    echo 错误: 启动容器失败
    pause
    exit /b 1
)

echo 等待服务启动...
timeout /t 5 /nobreak >nul

echo 正在检查服务状态...
docker ps | findstr mirageshield
if %errorlevel% neq 0 (
    echo 错误: 服务启动失败
    pause
    exit /b 1
)

echo ============================================
echo 部署成功！
echo ============================================
echo 服务地址: http://localhost:5000
echo 前端地址: http://localhost:5000/ui
echo 在线 Demo: https://ylqxb.github.io/MirageShield
echo ============================================
echo 提示：
echo 1. 首次访问需要注册账号
2. 服务默认运行在 5000 端口
3. 数据存储在本地 data 目录
4. 日志存储在本地 logs 目录
echo ============================================
pause
