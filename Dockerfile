# 固定和你本地一致的Python基础镜像
FROM python:3.10-slim

# 关闭Python缓冲，让日志正常输出到Railway控制台
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 第一步：先复制依赖文件，利用Docker缓存，依赖不变就不会重复安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 第二步：复制项目代码（自动忽略上面配置的大文件）
COPY . .

# 暴露后端服务端口
EXPOSE 8000

# 容器启动命令
CMD ["python", "backend/main.py"]