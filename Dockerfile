# 使用Python 3.8作为基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p data logs backups

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=start_server.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 启动应用
CMD ["python", "start_server.py"]
