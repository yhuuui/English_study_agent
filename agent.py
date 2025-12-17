# agent.py  —— 英语学习 AI 助手（CET-6 / 金融 / 学术阅读）

import os
import hashlib
import sqlite3
from datetime import datetime
from plyer import notification
from docx import Document
from llm import generate_code

# =========================
# 配置
# =========================
# 定义保存文件的文件夹路径
SAVE_FOLDER = r"E:\English_text"
# 确保保存文件夹存在，如果不存在则创建
os.makedirs(SAVE_FOLDER, exist_ok=True)

# 定义数据库文件的路径
DB_PATH = os.path.join(SAVE_FOLDER, "english_learning.db")

# =========================
# 数据库
# =========================
# 初始化数据库
def init_db():
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(DB_PATH)
    # 创建一个游标对象
    c = conn.cursor()

    # 创建 learning_state 表，如果它不存在的话
    # 这个表用于存储学习状态，包括主题、步骤和内容
    c.execute("""
    CREATE TABLE IF NOT EXISTS learning_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        step INTEGER,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 创建 sent_hash 表，如果它不存在的话
    # 这个表用于存储已发送内容的哈希值，以避免重复发送
    c.execute("""
    CREATE TABLE IF NOT EXISTS sent_hash (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE
    )
    """)

    # 提交事务
    conn.commit()
    # 关闭数据库连接
    conn.close()

# 获取当前的学习状态
def get_state():
    # 连接到数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 从 learning_state 表中查询最新的主题和步骤
    c.execute("SELECT topic, step FROM learning_state ORDER BY id DESC LIMIT 1")
    # 获取查询结果
    row = c.fetchone()
    # 关闭数据库连接
    conn.close()
    # 如果查询到结果，则返回结果，否则返回默认值
    return row if row else ("English Reading", 0)

# 保存学习状态
def save_state(topic, step, content):
    # 连接到数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 向 learning_state 表中插入新的状态记录
    c.execute(
        "INSERT INTO learning_state (topic, step, content) VALUES (?, ?, ?)",
        (topic, step, content)
    )
    # 提交事务
    conn.commit()
    # 关闭数据库连接
    conn.close()

# 检查一个哈希值是否存在于数据库中
def is_sent(h):
    # 连接到数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 在 sent_hash 表中查询指定的哈希值
    c.execute("SELECT 1 FROM sent_hash WHERE hash=?", (h,))
    # 获取查询结果
    res = c.fetchone()
    # 关闭数据库连接
    conn.close()
    # 如果查询到结果，则返回 True，否则返回 False
    return res is not None

# 将一个哈希值标记为已发送
def mark_sent(h):
    # 连接到数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 向 sent_hash 表中插入新的哈希值，如果已存在则忽略
    c.execute("INSERT OR IGNORE INTO sent_hash (hash) VALUES (?)", (h,))
    # 提交事务
    conn.commit()
    # 关闭数据库连接
    conn.close()

# =========================
# 工具
# =========================
# 计算文本的 SHA256 哈希值
def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# 发送桌面通知
def notify(msg):
    notification.notify(
        title="📘 Daily English Reading",
        message=msg,
        timeout=15
    )

# 将文本保存到 Word 文档
def save_to_word(text):
    # 生成文件名，包含当前日期
    filename = f"English_Reading_{datetime.today().strftime('%Y%m%d')}.docx"
    # 拼接文件的完整路径
    path = os.path.join(SAVE_FOLDER, filename)

    # 创建一个新的 Word 文档
    doc = Document()
    # 将文本按行分割，并逐行添加到文档中
    for line in text.split("\n"):
        doc.add_paragraph(line)

    # 保存 Word 文档
    doc.save(path)
    # 返回文件路径
    return path

# =========================
# 核心：生成每日英语阅读
# =========================
# 生成每日英语阅读内容
def generate_daily_reading():
    # 获取当前的学习状态
    topic, step = get_state()

    # 定义生成内容的提示（prompt）
    prompt = f"""
You are an advanced English learning assistant.

Task:
Generate a high-quality English reading passage suitable for CET-6 level learners.

Requirements:
1. Topic should be ONE of the following:
   - Finance & Economics
   - Academic Research
   - Science & Technology
   - Famous Speeches or Intellectual Essays
2. Length: 600–900 words
3. Style: formal, logical, well-structured
4. After the passage, provide 5–8 English comprehension questions
5. DO NOT provide answers
6. Content must be original and not repeated

Output format:
Title
---
Reading Passage
---
Questions
"""

    # 尝试最多 5 次来生成内容
    for _ in range(5):
        # 调用 llm 模块的 generate_code 函数生成内容
        result = generate_code(prompt)
        # 如果生成失败，则继续下一次尝试
        if not result:
            continue

        # 计算生成内容的哈希值
        h = sha(result)
        # 如果内容已经发送过，则继续下一次尝试
        if is_sent(h):
            continue

        # 将新内容的哈希值标记为已发送
        mark_sent(h)
        # 保存新的学习状态
        save_state(topic, step + 1, result)

        # 将生成的内容保存到 Word 文档
        file_path = save_to_word(result)
        # 返回生成的内容和文件路径
        return result, file_path

    # 如果 5 次尝试都失败，则返回 None
    return None, None

# =========================
# 交互
# =========================
# 聊天交互函数
def chat():
    print("=== English Learning Assistant ===")
    print("输入 task 生成今日阅读 | 输入 exit 退出")

    # 无限循环，等待用户输入
    while True:
        # 获取用户输入，并去除首尾空格，转换为小写
        cmd = input("\n你: ").strip().lower()

        # 如果用户输入 "exit"，则退出循环
        if cmd == "exit":
            print("Goodbye")
            break

        # 如果用户输入 "task"，则生成每日阅读
        if cmd == "task":
            # 调用 generate_daily_reading 函数生成内容
            content, file_path = generate_daily_reading()
            # 如果生成失败，则打印提示信息
            if not content:
                print("生成失败，请稍后再试")
                continue

            # 打印生成的阅读内容节选
            print("\n今日英文阅读已生成（节选）：\n")
            print(content[:600] + "...\n")

            # 发送桌面通知，告知用户文件已保存
            notify(
                f"Today's English reading is ready!\nSaved to:\n{file_path}"
            )
            continue

        # 如果用户输入其他内容，则提示用户输入 "task" 或 "exit"
        print("请输入 task 或 exit")

# =========================
# 主入口
# =========================
# 如果该脚本是作为主程序运行
if __name__ == "__main__":
    # 初始化数据库
    init_db()
    # 启动聊天交互
    chat()
