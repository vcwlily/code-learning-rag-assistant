import requests
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def call_deepseek_chat(system_prompt: str, user_prompt: str, temperature: float = 0.3):
    """
    统一封装DeepSeek聊天模型的API调用
    :param system_prompt: 系统提示词，定义模型的角色和规则
    :param user_prompt: 用户输入的内容
    :param temperature: 模型温度，越低输出越稳定，越高创造性越强
    :return: 模型生成的内容，调用失败返回错误信息
    """
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    # 请求体
    request_data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature,
        "stream": False,
        "max_tokens": 4000
    }

    # 发送请求，做异常捕获
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=request_data, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"API调用失败：{str(e)}"
    except KeyError as e:
        return f"API返回格式异常：{str(e)}"