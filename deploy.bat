@echo off

REM MirageShield Enhanced Deployment Script (Windows)
REM © 2026 MirageShield Team

set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%"

:menu
echo ============================================
echo MirageShield 增强部署工具
echo ============================================
echo 1. Docker 部署（推荐）
echo 2. 本地直接部署（无Docker）
echo 3. 仅更新 Demo 页面
echo 4. 退出
echo ============================================
set /p choice="请选择部署方式 (1-4): "

if "%choice%"=="1" goto docker_deploy
if "%choice%"=="2" goto local_deploy
if "%choice%"=="3" goto update_demo
if "%choice%"=="4" goto end

echo 无效选择，请重新输入
goto menu

:docker_deploy
echo ============================================
echo Docker 部署模式
echo ============================================

REM Check if Python is installed
echo 检查 Python 安装情况...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未安装 Python。正在尝试自动安装...
    echo 请稍候，正在下载 Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
    if errorlevel 1 (
        echo 下载 Python 失败，请手动下载并安装: https://www.python.org/downloads/
        pause
        goto menu
    )
    echo 正在安装 Python...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo Python 安装完成，请重新运行本脚本
    pause
    goto end
)

REM Check if Docker is installed
echo 检查 Docker 安装情况...
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未安装 Docker。正在尝试自动安装...
    echo 请稍候，正在下载 Docker Desktop...
    powershell -Command "Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe' -OutFile 'docker-installer.exe'"
    if errorlevel 1 (
        echo 下载 Docker 失败，请手动下载并安装: https://www.docker.com/products/docker-desktop
        pause
        goto menu
    )
    echo 正在安装 Docker...
    start /wait docker-installer.exe install --quiet
    del docker-installer.exe
    echo Docker 安装完成，请重启计算机后重新运行本脚本
    pause
    goto end
)

REM Check if Docker is running
echo 检查 Docker 是否运行...
docker info >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker 未运行。正在启动 Docker Desktop...
    start "Docker Desktop" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo 请等待 Docker 启动完成（约30秒）...
    timeout /t 30 /nobreak >nul
    docker info >nul 2>&1
    if errorlevel 1 (
        echo Docker 启动失败，请手动启动 Docker Desktop
        pause
        goto menu
    )
)

REM Check if docker-compose is available
echo 检查 docker-compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: docker-compose 不可用。
    echo 注意: Docker Desktop 通常包含 docker-compose。
    echo 请确保 Docker Desktop 已正确安装。
    pause
    goto menu
)

REM Build Docker image
echo 正在构建 Docker 镜像...
docker build -t mirageshield .
if errorlevel 1 (
    echo 错误: 构建 Docker 镜像失败。
    echo 请检查 Docker 安装并重试。
    pause
    goto menu
)

REM Start container
echo 正在启动容器...
docker-compose up -d
if errorlevel 1 (
    echo 错误: 启动容器失败。
    echo 请检查 Docker 安装并重试。
    pause
    goto menu
)

echo ============================================
echo 部署成功！
echo ============================================
echo 服务地址: http://localhost:8080
echo 前端地址: http://localhost:8080/ui
echo ============================================
echo 提示:
echo 1. 首次访问需要账户注册
echo 2. 服务默认运行在 8080 端口
echo 3. 数据存储在本地 data 目录
echo 4. 日志存储在本地 logs 目录
echo 5. 查看日志: docker logs -f mirageshield
echo ============================================

REM 自动打开浏览器
echo 正在打开浏览器...
start http://localhost:8080

pause
goto menu

:local_deploy
echo ============================================
echo 本地直接部署模式
echo ============================================

REM Check if Python is installed
echo 检查 Python 安装情况...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未安装 Python。正在尝试自动安装...
    echo 请稍候，正在下载 Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
    if errorlevel 1 (
        echo 下载 Python 失败，请手动下载并安装: https://www.python.org/downloads/
        pause
        goto menu
    )
    echo 正在安装 Python...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo Python 安装完成，请重新运行本脚本
    pause
    goto end
)

REM Install dependencies
echo 正在安装依赖项...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 安装依赖项失败。
    echo 请检查网络连接并重试。
    pause
    goto menu
)

REM Create data and logs directories
echo 正在创建数据目录...
mkdir data >nul 2>&1
mkdir logs >nul 2>&1

REM Start server
echo 正在启动服务器...
start "MirageShield Server" python start_server.py

REM Wait for server to start
echo 请等待服务器启动（约10秒）...
timeout /t 10 /nobreak >nul

echo ============================================
echo 部署成功！
echo ============================================
echo 服务地址: http://localhost:8080
echo 前端地址: http://localhost:8080/ui
echo ============================================
echo 提示:
echo 1. 首次访问需要账户注册
echo 2. 服务默认运行在 8080 端口
echo 3. 数据存储在本地 data 目录
echo 4. 日志存储在本地 logs 目录
echo ============================================

REM 自动打开浏览器
echo 正在打开浏览器...
start http://localhost:8080

pause
goto menu

:update_demo
echo ============================================
echo 更新 Demo 页面
echo ============================================

REM Update demo.html from ui/index.html
echo 正在更新 demo.html...
powershell -Command "Get-Content 'ui\index.html' | Set-Content 'demo.html'"
if errorlevel 1 (
    echo 错误: 更新 demo.html 失败。
    pause
    goto menu
)

REM Add demo mode flag
echo 正在添加演示模式标记...
powershell -Command "$content = Get-Content 'demo.html'; $content = $content -replace '<script>', '<script>const isDemoMode = true;'; Set-Content 'demo.html' $content"
if errorlevel 1 (
    echo 错误: 添加演示模式标记失败。
    pause
    goto menu
)

REM Update GitHub Pages demo
echo 正在更新 GitHub Pages demo...
powershell -Command "Copy-Item 'demo.html' 'ui\demo.html' -Force"
if errorlevel 1 (
    echo 错误: 更新 GitHub Pages demo 失败。
    pause
    goto menu
)

echo ============================================
echo Demo 页面更新成功！
echo ============================================
echo 本地 Demo: http://localhost:8080/demo.html
echo GitHub Pages Demo: https://ylqxb.github.io/MirageShield
echo ============================================

pause
goto menu

:end
echo 退出部署工具...
pause
exit