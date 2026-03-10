from llm.deepseek_client import call_deepseek_chat

# 代码分析的系统提示词，严格定义输出格式和规则
CODE_ANALYSIS_SYSTEM_PROMPT = """
你是一名专业、耐心的编程教学导师，精通Python、Java、C++、JavaScript等主流编程语言。
用户会给你一段代码和对应的编程语言，你必须严格按照以下4个模块输出结果，禁止编造内容，禁止输出和代码分析无关的信息：
1. 语法纠错：检查代码是否有语法错误、拼写错误、缩进问题。如果有错误，明确指出错误位置和错误原因，给出修正后的完整代码；如果没有错误，直接输出「✅ 代码无语法错误」。
2. 逻辑解释：用通俗易懂的语言，逐行解释代码的执行逻辑，讲清楚代码的核心功能和实现思路，适合编程初学者理解。
3. 复杂度分析：分析代码的时间复杂度和空间复杂度，给出明确的复杂度等级（比如O(n)），并说明分析的理由。
4. 优化建议：给出至少2条可落地的代码优化建议，从可读性、性能、健壮性、规范度等维度出发，给出具体的优化方案，不要空泛的建议。
输出要求：用markdown格式排版，每个模块用二级标题区分，语言简洁易懂，不要用太专业的术语堆砌。
"""

# 代码报错解决的系统提示词
CODE_ERROR_SOLVE_SYSTEM_PROMPT = """
你是一名专业的编程调试专家，擅长解决各类代码报错问题。
用户会给你代码、报错信息和编程语言，你需要完成以下3件事：
1. 报错根因分析：精准定位报错的根本原因，用通俗易懂的语言解释清楚，不要只复制报错信息。
2. 修复后的完整代码：给出可直接运行的、修复后的完整代码，不要只给修改的片段。
3. 避坑建议：给出1-2条避坑建议，帮助用户避免后续再出现同类错误。
输出要求：用markdown格式排版，语言通俗易懂，适合编程初学者理解。
"""

def analyze_code(code: str, language: str = "Python"):
    """
    代码分析主函数
    :param code: 用户输入的代码内容
    :param language: 代码对应的编程语言
    :return: 模型返回的分析结果
    """
    user_prompt = f"编程语言：{language}\n代码内容：\n```\n{code}\n```"
    return call_deepseek_chat(CODE_ANALYSIS_SYSTEM_PROMPT, user_prompt, temperature=0.2)

def solve_code_error(code: str, error_info: str, language: str = "Python"):
    """
    代码报错解决函数
    :param code: 报错的代码
    :param error_info: 终端里的报错信息
    :param language: 代码对应的编程语言
    :return: 模型返回的解决方案
    """
    user_prompt = f"编程语言：{language}\n报错代码：\n```\n{code}\n```\n报错信息：\n```\n{error_info}\n```"
    return call_deepseek_chat(CODE_ERROR_SOLVE_SYSTEM_PROMPT, user_prompt, temperature=0.3)