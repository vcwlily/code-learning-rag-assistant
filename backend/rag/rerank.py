import cohere
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
# 初始化Cohere客户端
cohere_client = cohere.Client(api_key=COHERE_API_KEY)

def rerank_documents(query: str, docs: list, top_n: int = 3):
    """
    对向量检索的结果做重排序，筛选出和用户问题最相关的内容
    解决向量检索只看语义相似度、忽略关键词匹配的问题，大幅提升准确率
    """
    if not docs:
        return []
    # 提取文档内容
    document_contents = [doc["content"] for doc in docs]
    # 调用重排序接口
    rerank_response = cohere_client.rerank(
        model="rerank-multilingual-v3.0",
        query=query,
        documents=document_contents,
        top_n=top_n
    )
    # 格式化重排序后的结果，保留原有的元数据
    reranked_results = []
    for res in rerank_response.results:
        original_doc = docs[res.index]
        reranked_results.append({
            "content": original_doc["content"],
            "metadata": original_doc["metadata"],
            "relevance_score": res.relevance_score,
            "original_distance": original_doc["distance"]
        })
    return reranked_results