from fastembed import TextEmbedding
from chromadb import PersistentClient
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownTextSplitter
import os

# ========== 1. 路径配置（动态计算，适配本地和线上所有场景） ==========
# 获取当前文件（vector_db.py）所在的目录：backend/rag/
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# 往上两级，定位到项目根目录
project_root = os.path.dirname(os.path.dirname(current_file_dir))

# 优先加载项目根目录的.env文件
load_dotenv(os.path.join(project_root, ".env"))

# 向量库路径：本地用项目目录，线上Hugging Face用持久化目录/data
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", os.path.join(project_root, "data", "chroma_db"))
# 如果是Hugging Face线上环境，强制用持久化目录
if os.getenv("SPACE_ID"):
    CHROMA_DB_PATH = "/data/chroma_db"

COLLECTION_NAME = "code_learning_knowledge_base"
# 知识库目录：项目根目录/data/raw_docs
KNOWLEDGE_BASE_DIR = os.path.join(project_root, "data", "raw_docs")

# ========== 2. 原有功能保持不变 ==========
def get_embedding_model():
    return TextEmbedding(model_name="BAAI/bge-small-zh-v1.5")

def create_chroma_vector_db(documents):
    """
    创建持久化的向量数据库，把文档批量存入（保留原有API，供外部调用）
    """
    embedding_model = get_embedding_model()
    # 确保向量库目录存在
    os.makedirs(os.path.dirname(CHROMA_DB_PATH), exist_ok=True)
    chroma_client = PersistentClient(path=CHROMA_DB_PATH)

    # 如果集合已存在，先删除，避免重复插入
    if COLLECTION_NAME in [collection.name for collection in chroma_client.list_collections()]:
        chroma_client.delete_collection(COLLECTION_NAME)
    
    # 创建集合
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "编程学习知识库向量库"},
        embedding_function=None
    )

    # 准备要插入的数据
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
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

# ========== 3. 【新增核心】自动初始化向量库 ==========
def _auto_init_vector_db():
    """
    内部函数：自动检查向量库，不存在/为空则自动读取知识库文件并初始化
    """
    embedding_model = get_embedding_model()
    # 确保向量库目录存在
    os.makedirs(os.path.dirname(CHROMA_DB_PATH), exist_ok=True)
    chroma_client = PersistentClient(path=CHROMA_DB_PATH)

    try:
        # 尝试获取已有集合
        collection = chroma_client.get_collection(COLLECTION_NAME)
        # 集合存在且不为空，直接返回
        if collection.count() > 0:
            print(f"✅ [向量库] 已存在，文档数量：{collection.count()}")
            return
        print(f"⚠️ [向量库] 集合存在但为空，开始初始化...")
    except Exception:
        print(f"🔧 [向量库] 集合不存在，开始自动初始化...")

    # 创建集合
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "编程学习知识库向量库"}
    )

    # 检查知识库目录是否存在
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        print(f"❌ [向量库] 知识库目录不存在：{KNOWLEDGE_BASE_DIR}，跳过初始化")
        return

    # 初始化Markdown文本分块器
    text_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = []
    metadatas = []
    ids = []

    # 遍历所有markdown知识库文件
    print(f"📖 [向量库] 正在读取知识库文件：{KNOWLEDGE_BASE_DIR}")
    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if filename.endswith(".md"):
            file_path = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # 文本分块
                chunks = text_splitter.split_text(content)
                # 整理入库数据
                for i, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadatas.append({"source": filename, "chunk_id": i})
                    ids.append(f"{filename}_{i}")
                print(f"  - 已处理：{filename}，分块数：{len(chunks)}")
            except Exception as e:
                print(f"  ⚠️ 读取文件失败 {filename}：{str(e)}")

    if not documents:
        print(f"❌ [向量库] 未找到任何有效的知识库文档，初始化失败")
        return

    # 批量向量化
    print(f"⚡ [向量库] 正在生成向量，文档块总数：{len(documents)}...")
    embeddings = list(embedding_model.embed(documents))

    # 存入向量库
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"✅ [向量库] 初始化完成，共入库 {len(documents)} 个文本块")

# ========== 4. 【新增】模块加载时自动执行初始化 ==========
# 项目启动时（import这个文件时），自动检查并初始化向量库
_auto_init_vector_db()

# ========== 5. 检索功能（增加自动兜底，API保持不变） ==========
def similarity_search(query: str, top_k: int = 10):
    """
    向量相似度检索，根据用户查询，返回相关的文档内容（API完全兼容原有代码）
    """
    embedding_model = get_embedding_model()
    chroma_client = PersistentClient(path=CHROMA_DB_PATH)
    
    # 获取已存在的集合（如果初始化成功，这里一定能拿到）
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
    print(f"\n检索到{len(results)}条相关内容")
    for res in results:
        print(f"\n相关内容：{res['content'][:200]}\n相似度距离：{res['distance']}\n")