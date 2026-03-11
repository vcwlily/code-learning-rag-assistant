from rag.vector_db import similarity_search
from rag.rerank import rerank_documents
from llm.deepseek_client import call_deepseek_chat
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 【复试核心亮点】RAG问答系统prompt，核心解决幻觉问题
RAG_QA_SYSTEM_PROMPT = """
你是一名专业、严谨的编程教学导师，只擅长解答编程相关的问题，非编程问题直接拒绝回答。
核心规则（必须100%严格遵守，违反规则会造成严重后果）：
1.  你的回答必须**完全基于下方提供的【参考知识库内容】**，禁止编造知识库中没有的知识点、代码示例、概念解释。
2.  如果【参考知识库内容】为空，或者没有和用户问题相关的内容，必须直接回答：「抱歉，我的知识库中没有相关内容，无法为你解答该问题」，绝对禁止编造答案。
3.  回答要通俗易懂，适配编程初学者，代码示例要完整可运行，步骤清晰，不要堆砌专业术语。
4.  回答的结尾必须标注引用的知识库来源，格式统一为：【引用来源：{对应的文档标题信息}】。
5.  只回答和编程、代码相关的问题，无关问题直接拒绝回答，不要输出无关内容。
"""

def rag_qa_chain(user_question: str, code_context: str = "", top_k_retrieve: int = 10, top_k_rerank: int = 3):
    """
    RAG智能问答全链路主函数
    :param user_question: 用户的编程问题
    :param code_context: 用户提供的代码上下文，可选
    :param top_k_retrieve: 向量粗召回的数量
    :param top_k_rerank: 重排序精排的数量
    :return: 结构化的问答结果，包含答案、引用内容、检索结果
    """
    # 1. 拼接查询语句，把问题和代码上下文结合，提升检索相关性
    full_query = f"用户问题：{user_question}\n相关代码上下文：{code_context}"

    # 2. 第一阶段：粗召回 - 向量相似度检索，先召回top10相关文档
    try:
        retrieve_docs = similarity_search(full_query, top_k=top_k_retrieve)
    except Exception as e:
        return {
            "answer": f"检索知识库失败：{str(e)}",
            "reference": "",
            "retrieve_docs": [],
            "reranked_docs": []
        }

    # 3. 第二阶段：精排 - Re-rank重排序，筛选出top3最相关的文档（复试核心亮点）
    try:
        reranked_docs = rerank_documents(user_question, retrieve_docs, top_n=top_k_rerank)
    except Exception as e:
        # 重排序失败时，降级使用粗召回的前3条，保证功能可用
        reranked_docs = retrieve_docs[:3]
        print(f"重排序失败，降级使用粗召回结果：{str(e)}")

    # 4. 格式化参考内容，拼接成prompt需要的格式
    if reranked_docs:
        reference_content = "\n\n".join([
            f"【参考文档{i+1}】：\n内容：{doc['content']}\n来源信息：{doc.get('metadata', '无')}"
            for i, doc in enumerate(reranked_docs)
        ])
    else:
        reference_content = "无相关参考内容"

    # 5. 拼接用户prompt，送入大模型
    user_prompt = f"""
    用户的编程问题：{user_question}
    用户提供的代码上下文：{code_context if code_context else '无'}
    【参考知识库内容】：
    {reference_content}

    请严格遵守系统prompt的规则，基于参考内容回答用户的问题。
    """

    # 6. 调用大模型生成答案，temperature调低，保证输出严谨，减少幻觉
    try:
        answer = call_deepseek_chat(
            system_prompt=RAG_QA_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3
        )
    except Exception as e:
        answer = f"大模型生成答案失败：{str(e)}"

    # 7. 返回结构化结果，方便接口封装和前端展示
    return {
        "answer": answer,
        "reference": reference_content,
        "retrieve_docs": retrieve_docs,
        "reranked_docs": reranked_docs
    }

# 本地测试用
if __name__ == "__main__":
    # 测试问答功能
    test_question = "Python的列表和元组有什么区别？"
    result = rag_qa_chain(test_question)
    print("生成的答案：")
    print(result["answer"])
    print("\n引用的内容：")
    print(result["reference"])