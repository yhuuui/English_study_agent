# db.py - 数据库操作模块
# 提供英语学习助手的数据库相关功能

import sqlite3  # SQLite数据库操作模块
import os  # 操作系统接口模块

# 数据库文件路径
DB_PATH = r"E:\English_text\english_learning.db"


def init_db():
    """
    初始化数据库
    创建必要的数据库表结构
    """
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 创建学习记录表
    # 用于存储学习状态、主题、步骤和内容
    c.execute("""
    CREATE TABLE IF NOT EXISTS learning_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自增ID
        topic TEXT,                            -- 学习主题
        step INTEGER,                          -- 学习步骤
        content TEXT,                          -- 学习内容
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP  -- 时间戳
    )
    """)

    # 创建去重表
    # 用于存储已发送内容的哈希值，防止重复生成相同内容
    c.execute("""
    CREATE TABLE IF NOT EXISTS sent_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自增ID
        content_hash TEXT UNIQUE               -- 内容哈希值，唯一约束
    )
    """)

    # 创建会话历史表
    # 用于存储用户与AI的对话历史，提供上下文记忆
    c.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自增ID
        session_id TEXT,                       -- 会话ID，用于区分不同会话
        user_message TEXT,                     -- 用户消息
        ai_response TEXT,                      -- AI响应
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 时间戳
        message_type TEXT DEFAULT 'chat'       -- 消息类型：chat/task
    )
    """)

    # 提交事务并关闭连接
    conn.commit()
    conn.close()


def save_learning_state(topic, step, content):
    """
    保存学习状态到数据库
    
    Args:
        topic (str): 学习主题
        step (int): 学习步骤
        content (str): 学习内容
    """
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 插入学习状态记录
    c.execute(
        "INSERT INTO learning_state (topic, step, content) VALUES (?, ?, ?)",
        (topic, step, content)
    )
    # 提交事务并关闭连接
    conn.commit()
    conn.close()


def get_latest_state():
    """
    获取最新的学习状态
    
    Returns:
        tuple: (主题, 步骤) 如果没有记录则返回默认值 ("English Reading", 0)
    """
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 查询最新的学习状态记录
    c.execute(
        "SELECT topic, step FROM learning_state ORDER BY id DESC LIMIT 1"
    )
    row = c.fetchone()
    conn.close()
    # 如果有记录则返回，否则返回默认值
    return row if row else ("English Reading", 0)


def is_content_sent(content_hash):
    """
    检查内容是否已经发送过（通过哈希值判断）
    
    Args:
        content_hash (str): 内容的哈希值
        
    Returns:
        bool: 如果内容已发送过返回True，否则返回False
    """
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 查询是否存在相同哈希值的记录
    c.execute(
        "SELECT 1 FROM sent_content WHERE content_hash = ?",
        (content_hash,)
    )
    result = c.fetchone()
    conn.close()
    # 如果查询到记录则表示已发送过
    return result is not None


def mark_content_sent(content_hash):
    """
    标记内容为已发送（将哈希值存入数据库）
    
    Args:
        content_hash (str): 内容的哈希值
    """
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 插入哈希值记录，如果已存在则忽略（INSERT OR IGNORE）
    c.execute(
        "INSERT OR IGNORE INTO sent_content (content_hash) VALUES (?)",
        (content_hash,)
    )
    # 提交事务并关闭连接
    conn.commit()
    conn.close()

def save_chat_history(session_id, user_message, ai_response, message_type='chat'):
    """
    保存聊天历史记录
    
    Args:
        session_id (str): 会话ID
        user_message (str): 用户消息
        ai_response (str): AI响应
        message_type (str): 消息类型，默认为'chat'
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat_history (session_id, user_message, ai_response, message_type) VALUES (?, ?, ?, ?)",
        (session_id, user_message, ai_response, message_type)
    )
    conn.commit()
    conn.close()


def get_chat_history(session_id, limit=10):
    """
    获取指定会话的聊天历史记录
    
    Args:
        session_id (str): 会话ID
        limit (int): 返回的最大记录数，默认为10
        
    Returns:
        list: 聊天历史记录列表，每个元素为(user_message, ai_response, message_type, timestamp)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT user_message, ai_response, message_type, timestamp FROM chat_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    rows = c.fetchall()
    conn.close()
    # 返回时按时间正序排列（最早的在前面）
    return list(reversed(rows))


def get_latest_task_content(session_id):
    """
    获取指定会话中最新的任务内容
    
    Args:
        session_id (str): 会话ID
        
    Returns:
        str: 最新的任务内容，如果没有则返回None
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT ai_response FROM chat_history WHERE session_id = ? AND message_type = 'task' ORDER BY id DESC LIMIT 1",
        (session_id,)
    )
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def clear_old_chat_history(days=7):
    """
    清理指定天数之前的聊天历史记录
    
    Args:
        days (int): 保留天数，默认为7天
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "DELETE FROM chat_history WHERE timestamp < datetime('now', '-{} days')".format(days)
    )
    conn.commit()
    conn.close()