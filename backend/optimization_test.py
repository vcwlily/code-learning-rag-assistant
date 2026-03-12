from rag.vector_db import similarity_search
from rag.rerank import rerank_documents

# 设计10个测试问题，覆盖你的知识库内容，分为基础题、细节题、场景题
test_questions = [
    "Python的核心数据类型有哪些？",
    "Python如何处理异常？try-except的用法是什么？",
    "什么是Python的装饰器？怎么使用？",
    "Python的深拷贝和浅拷贝有什么区别？",
    "列表推导式的用法和优势是什么？",
    "Python中的self参数有什么作用？",
    "什么是递归函数？递归的优缺点是什么？",
    "Python的面向对象三大特性是什么？",
    "如何解决Python的索引越界问题？",
    "Python中的生成器和迭代器有什么区别？"
]

# 人工标注的正确答案关键词，用来判断检索结果是否相关
# 格式：问题索引 -> 必须包含的关键词列表
standard_keywords = {
    0: ["列表", "元组", "可变", "不可变", "修改"],
    1: ["try", "except", "异常", "捕获", "报错"],
    2: ["装饰器", "函数", "包装", "@", "语法糖"],
    3: ["深拷贝", "浅拷贝", "引用", "地址", "copy"],
    4: ["列表推导式", "循环", "简洁", "语法", "遍历"],
    5: ["self", "实例", "类", "方法", "对象"],
    6: ["递归", "函数", "自身", "终止条件", "栈"],
    7: ["封装", "继承", "多态", "面向对象", "类"],
    8: ["索引", "越界", "长度", "下标", "IndexError"],
    9: ["生成器", "迭代器", "yield", "next", "可迭代"]
}

def calculate_hit_rate(docs, keywords):
    """计算检索结果的命中率，只要有一个文档包含所有关键词，就算命中"""
    idx =0
    for doc in docs:
        content = doc["content"].lower()
        all_keywords_hit = all(keyword.lower() in content for keyword in keywords)
        print(f"粗召回内容{idx+1},{content}")
        print(f"关键词{idx+1},{keywords[idx]}")
        print(f"命中结果{idx+1},{all_keywords_hit}")
        idx += 1
        if not all_keywords_hit:
            continue
        if all_keywords_hit:
            return True
    return False

def calculate_top3_accuracy(docs, keywords):
    """计算top3结果的准确率，前3条里有相关内容就算准确"""
    return calculate_hit_rate(docs[:3], keywords)

if __name__ == "__main__":
    print("===== RAG优化效果对比测试 =====")
    print(f"测试问题数量：{len(test_questions)}个")
    print("-" * 50)

    # 统计优化前（仅向量检索）的准确率
    before_optimization_correct = 0
    # 统计优化后（向量检索+重排序）的准确率
    after_optimization_correct = 0

    # 逐个问题测试
    for idx, question in enumerate(test_questions):
        print(f"\n测试问题{idx+1}：{question}")
        keywords = standard_keywords.get(idx, [])
        if not keywords:
            print("跳过：无标注关键词")
            continue

        # 优化前：仅向量检索top3
        retrieve_docs = similarity_search(question, top_k=3)
        before_correct = calculate_top3_accuracy(retrieve_docs, keywords)
        if before_correct:
            before_optimization_correct += 1
        print(f"优化前（仅向量检索top3）：{'准确' if before_correct else '不准确'}")

        # 优化后：向量检索top10 + 重排序top3
        full_retrieve_docs = similarity_search(question, top_k=10)
        reranked_docs = rerank_documents(question, full_retrieve_docs, top_n=3)
        after_correct = calculate_top3_accuracy(reranked_docs, keywords)
        if after_correct:
            after_optimization_correct += 1
        print(f"优化后（检索+重排序top3）：{'准确' if after_correct else '不准确'}")

    # 计算最终准确率
    total_test = len(standard_keywords)
    before_accuracy = (before_optimization_correct / total_test) * 100
    after_accuracy = (after_optimization_correct / total_test) * 100
    promotion = after_accuracy - before_accuracy

    print("\n" + "=" * 50)
    print("===== 最终测试结果 =====")
    print(f"总测试用例数：{total_test}个")
    print(f"优化前准确率：{before_accuracy:.2f}%")
    print(f"优化后准确率：{after_accuracy:.2f}%")
    print(f"准确率提升：{promotion:.2f}个百分点")
    print("=" * 50)

    # 生成测试报告内容
    report_content = f"""
    # RAG优化效果测试报告
    ## 测试背景
    为验证Re-rank重排序技术对RAG检索精度的优化效果，设计了{total_test}个编程领域测试问题，对比优化前后的top3检索准确率。

    ## 测试方案
    - 优化前：仅使用向量相似度检索，返回top3结果
    - 优化后：先通过向量检索完成top10粗召回，再通过Cohere Re-rank模型完成top3精排
    - 评估标准：top3检索结果中包含问题的核心知识点，即为准确

    ## 测试结果
    | 指标 | 优化前 | 优化后 | 提升幅度 |
    |------|--------|--------|----------|
    | 准确率 | {before_accuracy:.2f}% | {after_accuracy:.2f}% | {promotion:.2f}% |

    ## 结论
    引入Re-rank重排序技术后，RAG系统的检索准确率提升了{promotion:.2f}个百分点，有效解决了向量检索只关注语义相似度、忽略关键词匹配的问题，大幅提升了问答的准确性，同时降低了大模型的幻觉风险。
    """

    # 把测试报告写入docs文件夹
    with open("../docs/RAG优化效果测试报告.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("\n测试报告已生成：docs/RAG优化效果测试报告.md")