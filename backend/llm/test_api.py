import requests
from dotenv import load_dotenv
import os

# 加载.env文件里的环境变量
load_dotenv()
# 从环境变量获取API Key，绝对不要硬编码在这里！
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def test_deepseek_api():
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    # 请求体
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的编程导师，擅长用通俗易懂的语言讲解代码知识。"},
            {"role": "user", "content": "请简单解释一下Python的列表和元组的区别。"}
        ],
        "temperature": 0.3,
        "stream": False
    }
    # 发送请求
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        # 打印返回结果
        print("API调用成功！返回结果：")
        print(response.json()["choices"][0]["message"]["content"])
        return True
    except Exception as e:
        print(f"API调用失败！错误信息：{str(e)}")
        return False

if __name__ == "__main__":
    test_deepseek_api()