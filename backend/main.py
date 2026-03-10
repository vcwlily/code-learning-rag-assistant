from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 导入我们开发的核心模块
from llm.code_analyzer import analyze_code
from rag.vector_db import similarity_search

# 加载环境变量
load_dotenv()

# 初始化FastAPI应用
app = FastAPI(
    title="代码学习智能审查助手",
    description="基于RAG与大模型的编程答疑系统后端接口",
    version="1.0.0"
)

# 配置CORS跨域中间件，解决前后端联调的跨域问题，部署后也能正常访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，开发和部署都方便，复试项目足够用
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 定义请求体的数据模型，规范接口入参格式
class CodeAnalyzeRequest(BaseModel):
    code: str
    language: str = "Python"

class RagRetrieveRequest(BaseModel):
    question: str
    top_k: int = 10

# 健康检查接口：用来测试后端服务是否正常启动
@app.get("/", tags=["健康检查"])
async def health_check():
    return {
        "status": "ok",
        "service": "代码学习智能审查助手后端服务",
        "version": "1.0.0"
    }

# 代码分析接口：核心接口1，实现代码的全维度分析
@app.post("/api/code-analysis", tags=["核心功能接口"])
async def code_analysis(request: CodeAnalyzeRequest):
    # 入参校验
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="代码内容不能为空")
    # 调用核心分析能力
    try:
        result = analyze_code(request.code, request.language)
        return {
            "code": 200,
            "message": "代码分析成功",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"代码分析失败：{str(e)}")

# RAG检索接口：核心接口2，实现知识库内容检索
@app.post("/api/rag-retrieve", tags=["核心功能接口"])
async def rag_retrieve(request: RagRetrieveRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="查询问题不能为空")
    try:
        results = similarity_search(request.question, request.top_k)
        return {
            "code": 200,
            "message": "检索成功",
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败：{str(e)}")

# 启动后端服务
if __name__ == "__main__":
    import uvicorn
    # 从环境变量读取配置，默认0.0.0.0:8000
    import os
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)