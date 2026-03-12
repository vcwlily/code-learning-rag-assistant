# 固定Python基础镜像
FROM python:3.10-slim

# 基础环境配置
ENV PYTHONUNBUFFERED=1
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# 设置工作目录
WORKDIR /app

# 先把当前目录所有文件复制到容器的/app里（.dockerignore会自动排除没用的）
COPY . .

# 安装依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["python", "backend/main.py"]