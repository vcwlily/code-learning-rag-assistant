# 固定精简版Python基础镜像，减小镜像体积
FROM python:3.10-slim

# 关闭Python缓冲，优化日志输出
ENV PYTHONUNBUFFERED=1
# 配置清华镜像源，加快依赖安装速度
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# 设置工作目录
WORKDIR /app

# 分层构建：先复制依赖，最大化利用Docker缓存（依赖不变就不会重复安装）
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 只复制后端核心代码，完全不碰其他无关文件
COPY backend/ ./backend/

# 暴露后端服务端口
EXPOSE 8000

# 直接启动服务，不用cd切换目录，更高效稳定
CMD ["python", "backend/main.py"]