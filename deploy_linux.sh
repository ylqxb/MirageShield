#!/bin/bash
###############################################################################
# ⚠️ 此脚本仅为预览版提供，未在任何 Linux 环境测试
# 可能无法运行、存在错误，仅供学习参考
###############################################################################

# MirageShield 一键部署脚本 (Linux)
# © 2026 MirageShield 团队 版权所有，侵权必究

set -e  # 遇到错误立即退出
set -u  # 使用未定义变量时报错

echo "============================================"
echo "MirageShield 一键部署脚本"
echo "============================================"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python 3 未安装，请先安装 Python 3.8-3.11"
    echo "提示: sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    echo "提示: 请参考 Docker 官方文档安装"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "错误: Docker 未运行，请启动 Docker 服务"
    echo "提示: sudo systemctl start docker"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: docker-compose 未安装，请先安装 docker-compose"
    echo "提示: Docker Desktop 通常已包含 docker-compose"
    exit 1
fi

# 检查 5000 端口是否被占用
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "警告: 5000 端口已被占用，尝试停止占用进程..."
    PORT_PID=$(lsof -Pi :5000 -sTCP:LISTEN -t)
    if [ ! -z "$PORT_PID" ]; then
        kill -9 $PORT_PID 2>/dev/null || true
        sleep 2
    fi
fi

# 停止并删除已存在的容器
if docker ps -a | grep -q mirageshield; then
    echo "正在清理旧容器..."
    docker-compose down >/dev/null 2>&1 || true
fi

# 清理未使用的镜像
echo "正在清理未使用的镜像..."
docker image prune -f >/dev/null 2>&1 || true

# 创建必要的目录
echo "正在创建目录..."
mkdir -p data logs backups

# 设置目录权限
chmod 755 data logs backups

echo "正在构建 Docker 镜像..."
docker build -t mirageshield . --no-cache
if [ $? -ne 0 ]; then
    echo "错误: 构建 Docker 镜像失败"
    exit 1
fi

echo "正在启动容器..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "错误: 启动容器失败"
    exit 1
fi

echo "正在检查服务状态..."
MAX_ATTEMPTS=12
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    sleep 5

    if curl -sf http://localhost:5000/api/system/status >/dev/null 2>&1; then
        echo "============================================"
        echo "部署成功！"
        echo "============================================"
        echo "服务地址: http://localhost:5000"
        echo "前端地址: http://localhost:5000/ui"
        echo "在线 Demo: https://ylqxb.github.io/MirageShield"
        echo "============================================"
        echo "提示："
        echo "1. 首次访问需要注册账号"
        echo "2. 服务默认运行在 5000 端口"
        echo "3. 数据存储在本地 data 目录"
        echo "4. 日志存储在本地 logs 目录"
        echo "5. 查看日志: docker logs -f mirageshield"
        echo "============================================"
        exit 0
    fi

    echo "等待服务启动... ($ATTEMPT/$MAX_ATTEMPTS)"
done

echo "错误: 服务启动超时"
docker logs mirageshield
exit 1
