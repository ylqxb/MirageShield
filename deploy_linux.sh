#!/bin/bash
# ###########################################################
# ⚠️ 此脚本仅为预览版提供，未在任何 Linux 环境测试
# 可能无法运行、存在错误，仅供学习参考
# ###########################################################

# MirageShield 一键部署脚本 (Linux)
# © 2026 MirageShield 团队 版权所有，侵权必究

echo "============================================"
echo "MirageShield 一键部署脚本"
echo "============================================"

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python 3 未安装，请先安装 Python 3.8-3.11"
    exit 1
fi

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo "错误: Docker 未运行，请启动 Docker 服务"
    exit 1
fi

# 检查 docker-compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

echo "正在构建 Docker 镜像..."
docker build -t mirageshield .
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

echo "等待服务启动..."
sleep 5

echo "正在检查服务状态..."
docker ps | grep mirageshield
if [ $? -ne 0 ]; then
    echo "错误: 服务启动失败"
    exit 1
fi

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
echo "============================================"
