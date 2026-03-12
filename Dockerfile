# 固定和本地一致的精简Python镜像
FROM python:3.10-slim

# 关闭Python缓冲，让日志正常输出到Railway控制台
ENV PYTHONUNBUFFERED=1
# 配置清华镜像源，大幅加快依赖安装速度
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# 设置容器内的工作目录
WORKDIR /app

# 明确复制根目录的依赖文件
COPY ./requirements.txt /app/requirements.txt

# 安装项目依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制后端核心代码
COPY ./backend /app/backend

# 暴露后端服务端口
EXPOSE 8000

# 容器启动命令
CMD ["python", "backend/main.py"]