#!/usr/bin/env python3
# 使用 waitress 启动 API 服务
# © 2026 MirageShield 团队 版权所有，侵权必究
from waitress import serve
import api.app
import os

if __name__ == '__main__':
    print("Starting server with waitress...")
    # 优化 waitress 配置
    cpu_count = os.cpu_count() or 4
    thread_count = cpu_count * 4  # 增加线程数到CPU核心数的4倍
    connection_limit = 1000  # 进一步增加连接限制
    
    serve(
        api.app.app, 
        host='0.0.0.0', 
        port=5000, 
        threads=thread_count,  # 动态计算线程数
        connection_limit=connection_limit,  # 增加连接限制
        max_request_body_size=2097152,  # 2MB
        expose_tracebacks=False  # 生产环境不暴露错误堆栈
    )
    print(f"Server started with {thread_count} threads and {connection_limit} connection limit")
