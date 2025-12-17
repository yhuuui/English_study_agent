# dedup.py - 去重模块
# 提供内容去重功能，防止生成重复的学习内容

import hashlib  # 哈希算法模块
import sqlite3  # SQLite数据库操作模块


def calculate_hash(code):
    """
    计算代码/内容的SHA256哈希值
    
    Args:
        code (str): 要计算哈希值的代码或内容
        
    Returns:
        str: 十六进制格式的哈希值字符串
    """
    return hashlib.sha256(code.encode('utf-8')).hexdigest()


def is_code_duplicate(code_hash):
    """
    检查代码是否重复（通过哈希值判断）
    
    Args:
        code_hash (str): 代码的哈希值
        
    Returns:
        bool: 如果代码重复返回True，否则返回False
    """
    # 连接数据库
    conn = sqlite3.connect('learning_assistant.db')
    cursor = conn.cursor()

    # 查询是否存在相同哈希值的记录
    cursor.execute('SELECT * FROM pushed_code WHERE hash = ?', (code_hash,))
    result = cursor.fetchone()

    # 关闭数据库连接
    conn.close()

    # 如果查询到记录则表示代码重复
    return result is not None
