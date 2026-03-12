# 第一阶段：构建阶段，只负责安装依赖
FROM python:3.10-slim AS builder

# 关闭pip缓存，减少体积
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置构建目录
WORKDIR /build

# 复制依赖文件，安装依赖到虚拟环境
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -r requirements.txt

# 第二阶段：运行阶段，只保留运行必须的文件，极致精简
FROM python:3.10-slim

# 运行时环境配置
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 从构建阶段复制已经装好的依赖，不用重复安装
COPY --from=builder /opt/venv /opt/venv

# 只复制后端核心代码，完全不碰数据文件
COPY backend/ ./backend/

# 暴露服务端口
EXPOSE 8000

# 启动服务
CMD ["python", "backend/main.py"]