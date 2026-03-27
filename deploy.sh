#!/bin/bash

# MirageShield Enhanced Deployment Script (Linux)
# © 2026 MirageShield Team

SCRIPT_DIR=$(dirname "$0")
PROJECT_DIR="$SCRIPT_DIR"

menu() {
    echo "============================================"
    echo "MirageShield 增强部署工具"
    echo "============================================"
    echo "1. Docker 部署（推荐）"
    echo "2. 本地直接部署（无Docker）"
    echo "3. 仅更新 Demo 页面"
    echo "4. 退出"
    echo "============================================"
    read -p "请选择部署方式 (1-4): " choice
    
    case $choice in
        1)
            docker_deploy
            ;;
        2)
            local_deploy
            ;;
        3)
            update_demo
            ;;
        4)
            echo "退出部署工具..."
            exit 0
            ;;
        *)
            echo "无效选择，请重新输入"
            menu
            ;;
    esac
}

docker_deploy() {
    echo "============================================"
    echo "Docker 部署模式"
    echo "============================================"
    
    # Check if Python is installed
    echo "检查 Python 安装情况..."
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未安装 Python。正在尝试自动安装..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip
        else
            echo "错误: 无法自动安装 Python，请手动安装 Python 3.8+"
            read -p "按 Enter 键返回菜单..."
            menu
        fi
    fi
    
    # Check if Docker is installed
    echo "检查 Docker 安装情况..."
    if ! command -v docker &> /dev/null; then
        echo "错误: 未安装 Docker。正在尝试自动安装..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y docker.io
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
            echo "Docker 安装完成，请重新登录后运行本脚本"
            read -p "按 Enter 键返回菜单..."
            menu
        elif command -v yum &> /dev/null; then
            sudo yum install -y docker
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
            echo "Docker 安装完成，请重新登录后运行本脚本"
            read -p "按 Enter 键返回菜单..."
            menu
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y docker
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
            echo "Docker 安装完成，请重新登录后运行本脚本"
            read -p "按 Enter 键返回菜单..."
            menu
        else
            echo "错误: 无法自动安装 Docker，请手动安装 Docker"
            read -p "按 Enter 键返回菜单..."
            menu
        fi
    fi
    
    # Check if Docker is running
    echo "检查 Docker 是否运行..."
    if ! docker info &> /dev/null; then
        echo "错误: Docker 未运行。正在启动 Docker..."
        if command -v systemctl &> /dev/null; then
            sudo systemctl start docker
            sleep 10
            if ! docker info &> /dev/null; then
                echo "Docker 启动失败，请手动启动 Docker"
                read -p "按 Enter 键返回菜单..."
                menu
            fi
        else
            echo "请手动启动 Docker 服务"
            read -p "按 Enter 键返回菜单..."
            menu
        fi
    fi
    
    # Check if docker-compose is available
    echo "检查 docker-compose..."
    if ! command -v docker-compose &> /dev/null; then
        echo "错误: docker-compose 不可用。正在安装..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y docker-compose
        elif command -v yum &> /dev/null; then
            sudo yum install -y docker-compose
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y docker-compose
        else
            echo "错误: 无法安装 docker-compose，请手动安装"
            read -p "按 Enter 键返回菜单..."
            menu
        fi
    fi
    
    # Build Docker image
    echo "正在构建 Docker 镜像..."
    docker build -t mirageshield .
    if [ $? -ne 0 ]; then
        echo "错误: 构建 Docker 镜像失败。"
        echo "请检查 Docker 安装并重试。"
        read -p "按 Enter 键返回菜单..."
        menu
    fi
    
    # Start container
    echo "正在启动容器..."
    docker-compose up -d
    if [ $? -ne 0 ]; then
        echo "错误: 启动容器失败。"
        echo "请检查 Docker 安装并重试。"
        read -p "按 Enter 键返回菜单..."
        menu
    fi
    
    echo "============================================"
    echo "部署成功！"
    echo "============================================"
    echo "服务地址: http://localhost:8080"
    echo "前端地址: http://localhost:8080/ui"
    echo "============================================"
    echo "提示:"
    echo "1. 首次访问需要账户注册"
    echo "2. 服务默认运行在 8080 端口"
    echo "3. 数据存储在本地 data 目录"
    echo "4. 日志存储在本地 logs 目录"
    echo "5. 查看日志: docker logs -f mirageshield"
    echo "============================================"
    
    # 自动打开浏览器
    echo "正在打开浏览器..."
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8080
    elif command -v open &> /dev/null; then
        open http://localhost:8080
    fi
    
    read -p "按 Enter 键返回菜单..."
    menu
}

local_deploy() {
    echo "============================================"
    echo "本地直接部署模式"
    echo "============================================"
    
    # Check if Python is installed
    echo "检查 Python 安装情况..."
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未安装 Python。正在尝试自动安装..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip
        else
            echo "错误: 无法自动安装 Python，请手动安装 Python 3.8+"
            read -p "按 Enter 键返回菜单..."
            menu
        fi
    fi
    
    # Install dependencies
    echo "正在安装依赖项..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 安装依赖项失败。"
        echo "请检查网络连接并重试。"
        read -p "按 Enter 键返回菜单..."
        menu
    fi
    
    # Create data and logs directories
    echo "正在创建数据目录..."
    mkdir -p data logs
    
    # Start server
    echo "正在启动服务器..."
    python3 start_server.py &
    
    # Wait for server to start
    echo "请等待服务器启动（约10秒）..."
    sleep 10
    
    echo "============================================"
    echo "部署成功！"
    echo "============================================"
    echo "服务地址: http://localhost:8080"
    echo "前端地址: http://localhost:8080/ui"
    echo "============================================"
    echo "提示:"
    echo "1. 首次访问需要账户注册"
    echo "2. 服务默认运行在 8080 端口"
    echo "3. 数据存储在本地 data 目录"
    echo "4. 日志存储在本地 logs 目录"
    echo "============================================"
    
    # 自动打开浏览器
    echo "正在打开浏览器..."
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8080
    elif command -v open &> /dev/null; then
        open http://localhost:8080
    fi
    
    read -p "按 Enter 键返回菜单..."
    menu
}

update_demo() {
    echo "============================================"
    echo "更新 Demo 页面"
    echo "============================================"
    
    # Update demo.html from ui/index.html
    echo "正在更新 demo.html..."
    cp "ui/index.html" "demo.html"
    if [ $? -ne 0 ]; then
        echo "错误: 更新 demo.html 失败。"
        read -p "按 Enter 键返回菜单..."
        menu
    fi
    
    # Add demo mode flag
    echo "正在添加演示模式标记..."
    sed -i 's/<script>/<script>const isDemoMode = true;/' "demo.html"
    if [ $? -ne 0 ]; then
        echo "错误: 添加演示模式标记失败。"
        read -p "按 Enter 键返回菜单..."
        menu
    fi
    
    # Update GitHub Pages demo
    echo "正在更新 GitHub Pages demo..."
    cp "demo.html" "ui/demo.html"
    if [ $? -ne 0 ]; then
        echo "错误: 更新 GitHub Pages demo 失败。"
        read -p "按 Enter 键返回菜单..."
        menu
    fi
    
    echo "============================================"
    echo "Demo 页面更新成功！"
    echo "============================================"
    echo "本地 Demo: http://localhost:8080/demo.html"
    echo "GitHub Pages Demo: https://ylqxb.github.io/MirageShield"
    echo "============================================"
    
    read -p "按 Enter 键返回菜单..."
    menu
}

# 主菜单
menu