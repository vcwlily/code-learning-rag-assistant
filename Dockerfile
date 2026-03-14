# ===============================前后端在huggingface 上同一个空间中部署所需要的配置=============================================
# 用Python 3.10作为基础镜像，和你本地环境保持一致
# FROM python:3.10-slim

# 设置工作目录
# WORKDIR /app

# 安装系统依赖（如果需要）
# RUN apt-get update && apt-get install -y \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制所有代码
# COPY . .

# 暴露端口（Streamlit用8501，FastAPI用7860，Hugging Face默认会路由7860）
# EXPOSE 7860
# EXPOSE 8501

# 分步启动FastAPI后端和Streamlit前端
# CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 7860 & cd frontend && streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]

# ================================end============================================

# =================================前后端分别部署在huggingface 上的不同空间位置配置之后端配置=============================================
# 官方Python镜像，和你本地开发版本保持一致，推荐3.10/3.11
FROM python:3.10-slim

# 设置容器工作目录
WORKDIR /code

# 先复制依赖文件，安装依赖（优化镜像构建缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目代码到容器
COPY . .

# 暴露端口（Hugging Face强制要求7860端口，必须和main.py里的端口一致）
EXPOSE 7860

# 启动命令：运行FastAPI服务，路径和你的项目结构完全匹配
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]