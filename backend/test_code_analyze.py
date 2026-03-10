from llm.code_analyzer import analyze_code, solve_code_error

if __name__ == "__main__":
    print("===== 开始代码分析模块测试 =====")
    
    # 测试代码分析功能
    print("\n1. 测试代码分析功能...")
    test_code = """
def calculate_sum(n):
    sum = 0
    for i in range(n):
        sum += i
    return sum

print(calculate_sum(10))
    """.strip()  # 用strip()去掉首尾多余的空行
    
    analyze_result = analyze_code(test_code, "Python")
    print("代码分析结果：")
    print("-" * 50)
    print(analyze_result)
    print("-" * 50)

    print("\n===== 代码分析模块测试完成 =====")