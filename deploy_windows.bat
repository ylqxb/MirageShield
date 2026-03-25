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

REM 检查 docker-compose 是否安装
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: docker-compose 未安装，请先安装 Docker Compose
    echo 提示: Docker Desktop 通常已包含 docker-compose
    pause
    exit /b 1
)

REM 检查 5000 端口是否被占用
netstat -ano | findstr :5000 >nul 2>&1
if %errorlevel% equ 0 (
    echo 警告: 5000 端口已被占用，尝试停止占用进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

REM 停止并删除已存在的容器
docker ps -a | findstr mirageshield >nul 2>&1
if %errorlevel% equ 0 (
    echo 正在清理旧容器...
    docker-compose down >nul 2>&1
)

REM 清理未使用的镜像
echo 正在清理未使用的镜像...
docker image prune -f >nul 2>&1

echo 正在构建 Docker 镜像...
docker build -t mirageshield . --no-cache
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

echo 正在检查服务状态...
set /a attempts=0
:check_service
set /a attempts+=1
if %attempts% gtr 12 (
    echo 错误: 服务启动超时
    docker logs mirageshield
    pause
    exit /b 1
)

timeout /t 5 /nobreak >nul
curl -s http://localhost:5000/api/system/status >nul 2>&1
if %errorlevel% neq 0 (
    echo 等待服务启动... (%attempts%/12)
    goto check_service
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
echo 2. 服务默认运行在 5000 端口
echo 3. 数据存储在本地 data 目录
echo 4. 日志存储在本地 logs 目录
echo 5. 查看日志: docker logs -f mirageshield
echo ============================================

REM 如果以自动化模式运行（通过参数），则不等待用户输入
if "%1"=="--auto" exit /b 0
pause
