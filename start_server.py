#!/usr/bin/env python3
# 使用 waitress 启动 API 服务
# © 2026 MirageShield 团队 版权所有，侵权必究
import os
import sys
import socket
import subprocess

# 设置环境变量为生产模式，避免debug模式警告
os.environ['FLASK_ENV'] = 'production'

from waitress import serve
import api.app

def check_port(port):
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def kill_process_using_port(port):
    """尝试终止占用指定端口的进程"""
    try:
        if os.name == 'nt':  # Windows
            # 使用 netstat 命令查找占用端口的进程
            cmd = f'netstat -ano | findstr :{port}'
            output = subprocess.check_output(cmd, shell=True, text=True)
            lines = output.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[4]
                        print(f"发现占用端口 {port} 的进程 PID: {pid}")
                        # 尝试终止进程
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                        print(f"已终止进程 PID: {pid}")
                        return True
        else:  # Linux
            # 使用 lsof 命令查找占用端口的进程
            cmd = f'lsof -i :{port}'
            output = subprocess.check_output(cmd, shell=True, text=True)
            lines = output.strip().split('\n')
            for line in lines[1:]:  # 跳过表头
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        print(f"发现占用端口 {port} 的进程 PID: {pid}")
                        # 尝试终止进程
                        subprocess.run(f'kill -9 {pid}', shell=True)
                        print(f"已终止进程 PID: {pid}")
                        return True
    except Exception as e:
        print(f"终止进程时出错: {e}")
    return False

if __name__ == '__main__':
    port = 8080
    
    # 检查端口是否被占用
    if check_port(port):
        print(f"端口 {port} 已被占用，尝试终止占用进程...")
        if kill_process_using_port(port):
            print(f"成功释放端口 {port}")
        else:
            print(f"无法释放端口 {port}，请手动终止占用进程后重试")
            sys.exit(1)
    
    print("Starting server with waitress...")
    # 优化 waitress 配置
    cpu_count = os.cpu_count() or 4
    thread_count = cpu_count * 4  # 增加线程数到CPU核心数的4倍
    connection_limit = 1000  # 进一步增加连接限制
    
    serve(
        api.app.app, 
        host='0.0.0.0', 
        port=port, 
        threads=thread_count,  # 动态计算线程数
        connection_limit=connection_limit,  # 增加连接限制
        max_request_body_size=2097152,  # 2MB
        expose_tracebacks=False  # 生产环境不暴露错误堆栈
    )
    print(f"Server started with {thread_count} threads and {connection_limit} connection limit")
