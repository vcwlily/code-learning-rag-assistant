# 固定和本地一致的轻量Python镜像
FROM python:3.10-slim

# 基础配置：关闭缓冲、禁用pip版本检查、关闭缓存，减少耗时
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# 设置容器工作目录
WORKDIR /app

# 【核心缓存优化】先复制依赖文件，只要requirements.txt不变，这一步永远用缓存，不用重复安装
COPY requirements.txt .
# 直接安装依赖，砍掉多余的升级操作
RUN pip install -r requirements.txt

# 【极致精简】只复制后端核心代码，完全不碰其他无关文件
COPY backend/ ./backend/

# 暴露后端服务端口
EXPOSE 8000

# 启动服务
CMD ["python", "backend/main.py"]