# llm.py
import os
import json
import requests
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（可选）
load_dotenv()

# DeepSeek API 的 URL
API_URL = "https://api.deepseek.com/v1/chat/completions"

def generate_code(prompt: str) -> str | None:
    """
    调用 DeepSeek API 生成 Python 代码
    :param prompt: 用户提示
    :return: 生成的代码或文本
    """
    # 从环境变量中获取 API 密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    # 调试信息：打印获取到的 API 密钥
    print("DEBUG inside function: DEEPSEEK_API_KEY =", api_key)

    # 严格判断 key 是否存在且不为空
    if api_key is None or api_key.strip() == "":
        # 如果 API 密钥不存在，则抛出运行时错误
        raise RuntimeError("EEPSEEK_API_KEY 为空，请检查环境变量或 .env 文件")

    # 设置请求头，包括授权信息和内容类型
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 构建请求体（payload）
    payload = {
        "model": "deepseek-chat",  # 使用的模型
        "messages": [
            {"role": "system", "content": "You are a professional English learning assistant specializing in advanced reading and academic English."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,  # 控制生成文本的创造性
        "max_tokens": 800    # 生成文本的最大长度
    }

    # 调试用：打印将要发送的 JSON 数据
    print("=== Payload ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    try:
        # 发送 POST 请求到 API，并将超时时间设置为 120 秒以处理长时间的生成任务
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    except requests.exceptions.RequestException as e:
        # 如果请求失败，则打印错误信息并返回 None
        print("请求 API 失败:", e)
        return None

    # 检查响应状态码是否为 200 (成功)
    if resp.status_code != 200:
        # 如果状态码不为 200，则打印错误信息和响应内容
        print(f"Error: {resp.status_code}")
        print(resp.text)
        return None

    try:
        # 解析 JSON 响应并返回生成的内容
        return resp.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        # 如果解析失败，则打印错误信息并返回 None
        print("解析返回结果失败:", e)
        return None

