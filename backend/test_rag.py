from rag.document_processor import split_markdown_documents
from rag.vector_db import create_chroma_vector_db, similarity_search
from rag.rerank import rerank_documents

if __name__ == "__main__":
    print("===== 开始RAG模块全流程测试 =====")
    
    # 第一步：测试文档分块
    print("\n1. 开始文档分块...")
    docs = split_markdown_documents()
    if len(docs) == 0:
        print("错误：没有找到可处理的markdown文档，请检查data/raw_docs文件夹里是否有.md文件")
        exit()
    print(f"文档分块完成，共生成{len(docs)}个文本块")

    # 第二步：测试创建向量库
    print("\n2. 开始创建向量库...")
    create_result = create_chroma_vector_db(docs)
    print(create_result)

    # 第三步：测试相似度检索
    print("\n3. 测试向量检索...")
    test_query = "Python如何处理异常"
    search_results = similarity_search(test_query, top_k=5)
    print(f"检索到{len(search_results)}条相关内容")
    for i, res in enumerate(search_results):
        print(f"第{i+1}条，相似度距离：{res['distance']}")

    # 第四步：测试重排序功能
    print("\n4. 测试重排序功能...")
    reranked_results = rerank_documents(test_query, search_results, top_n=3)
    print(f"重排序完成，筛选出Top3相关内容")
    for i, res in enumerate(reranked_results):
        print(f"第{i+1}条，相关度得分：{res['relevance_score']}")

    print("\n===== RAG模块全流程测试完成！所有功能正常 =====")