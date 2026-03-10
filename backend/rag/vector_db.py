from fastembed import TextEmbedding
from chromadb import PersistentClient
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "../data/chroma_db")
COLLECTION_NAME = "code_learning_knowledge_base"

# 初始化Embedding模型，用和之前完全一样的bge-small-zh，效果完全一致
def get_embedding_model():
    return TextEmbedding(model_name="BAAI/bge-small-zh-v1.5")

def create_chroma_vector_db(documents):
    """
    创建持久化的向量数据库，把文档批量存入
    """
    # 初始化模型和客户端
    embedding_model = get_embedding_model()
    chroma_client = PersistentClient(path=CHROMA_DB_PATH)

    # 如果集合已存在，先删除，避免重复插入
    if COLLECTION_NAME in [collection.name for collection in chroma_client.list_collections()]:
        chroma_client.delete_collection(COLLECTION_NAME)
    
    # 创建集合，指定用fastembed的embedding函数
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "编程学习知识库向量库"},
        embedding_function=None  # 我们手动处理embedding，更可控
    )

    # 准备要插入的数据
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    # 生成向量
    embeddings = list(embedding_model.embed(texts))
    ids = [f"doc_{i}" for i in range(len(texts))]

    # 批量插入向量库
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    return f"向量库创建成功，共插入{len(texts)}条文档块"

def similarity_search(query: str, top_k: int = 10):
    """
    向量相似度检索，根据用户查询，返回相关的文档内容
    """
    embedding_model = get_embedding_model()
    chroma_client = PersistentClient(path=CHROMA_DB_PATH)
    
    # 获取已存在的集合
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
    except Exception as e:
        raise Exception(f"向量库不存在，请先创建向量库：{str(e)}")

    # 把用户查询转成向量，做相似度检索
    query_embedding = list(embedding_model.embed([query]))[0]
    search_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # 格式化返回结果，和之前的格式完全一致，不影响后续代码
    result_list = []
    for i in range(len(search_results["documents"][0])):
        result_list.append({
            "content": search_results["documents"][0][i],
            "metadata": search_results["metadatas"][0][i],
            "distance": search_results["distances"][0][i]
        })
    return result_list

# 本地测试用
if __name__ == "__main__":
    # 测试检索功能
    test_query = "Python的列表和元组有什么区别"
    results = similarity_search(test_query, top_k=3)
    print(f"检索到{len(results)}条相关内容")
    for res in results:
        print(f"相关内容：{res['content'][:200]}\n相似度距离：{res['distance']}\n")