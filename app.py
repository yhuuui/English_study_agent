# 导入必要的库
from flask import Flask, render_template, request, jsonify, session  # Flask web框架相关模块
import re  # 正则表达式模块，用于文本处理
import os  # 操作系统接口模块
import uuid  # UUID生成模块，用于生成会话ID
from datetime import datetime  # 日期时间处理模块
from docx import Document  # python-docx库，用于创建Word文档
from docx.shared import Pt  # Word文档字体大小设置
from docx.oxml.ns import qn  # Word文档XML命名空间处理
from agent import generate_daily_reading, get_state, save_state, is_sent, mark_sent, sha, init_db  # 代理模块相关函数
from llm import generate_code  # 大语言模型生成代码的函数
import db  # 导入数据库模块

# 创建Flask应用实例
app = Flask(__name__)
app.secret_key = 'english_learning_assistant_secret_key_2024'  # 设置会话密钥

# 字体配置
FONT_PATH = r"D:\downLoad\Fast-Font-main\Fast-Font-main\Fast_Sans.ttf"  # 字体文件路径
FONT_NAME = "Fast_Sans"  # 字体名称
SAVE_FOLDER = r"E:\English_text"  # 保存文件的目录
os.makedirs(SAVE_FOLDER, exist_ok=True)  # 创建保存目录，如果不存在的话

def get_session_id():
    """
    获取或创建会话ID
    
    Returns:
        str: 会话ID
    """
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


def build_context_prompt(session_id, current_message):
    """
    构建包含历史上下文的提示词
    
    Args:
        session_id (str): 会话ID
        current_message (str): 当前用户消息
        
    Returns:
        str: 包含上下文的完整提示词
    """
    # 获取聊天历史
    history = db.get_chat_history(session_id, limit=5)  # 获取最近5条记录
    
    # 获取最新的任务内容（如果存在）
    latest_task = db.get_latest_task_content(session_id)
    
    # 构建上下文
    context_parts = []
    
    if latest_task:
        context_parts.append(f"最近生成的英语阅读材料：\n{latest_task[:500]}...")
    
    if history:
        context_parts.append("最近的对话历史：")
        for user_msg, ai_resp, msg_type, timestamp in history[-3:]:  # 只取最近3条
            context_parts.append(f"用户: {user_msg}")
            context_parts.append(f"AI: {ai_resp[:200]}...")
    
    # 构建完整提示词
    if context_parts:
        context_str = "\n".join(context_parts)
        prompt = f"""你是一个英语学习助手。以下是我们之前的对话上下文：

{context_str}

现在用户的新问题是：{current_message}

请基于上下文回答用户的问题。如果用户询问之前生成的文章内容，请参考上面的阅读材料进行回答。"""
    else:
        prompt = f"你是一个英语学习助手。用户的问题是：{current_message}"
    
    return prompt


def clean_markdown(text):
    """
    清理Markdown格式文本
    
    Args:
        text (str): 输入的文本
        
    Returns:
        str: 清理后的文本，移除了#和*符号
    """
    if not text:
        return ""
    # 移除 # 和 * 符号
    cleaned = re.sub(r'[#*]', '', text)
    return cleaned

def save_to_word_custom(text):
    """
    将文本保存为自定义格式的Word文档
    
    Args:
        text (str): 要保存的文本内容
        
    Returns:
        str: 保存的文件路径
    """
    # 生成文件名，格式为：English_Reading_YYYYMMDD.docx
    filename = f"English_Reading_{datetime.today().strftime('%Y%m%d')}.docx"
    path = os.path.join(SAVE_FOLDER, filename)

    # 创建新的Word文档
    doc = Document()
    
    # 设置默认样式字体
    style = doc.styles['Normal']
    font = style.font
    font.name = FONT_NAME
    # 为兼容性设置东亚字体（如果有混合内容）
    font.element.rPr.rFonts.set(qn('w:eastAsia'), FONT_NAME)
    
    # 添加内容
    # 在保存前清理markdown格式
    clean_text = clean_markdown(text)
    
    # 按行添加段落
    for line in clean_text.split("\n"):
        p = doc.add_paragraph(line)
        p.style = doc.styles['Normal']

    try:
        # 尝试保存文档
        doc.save(path)
        return path
    except PermissionError:
        # 如果文件被占用，生成带时间戳的备用文件名
        alt_name = f"English_Reading_{datetime.today().strftime('%Y%m%d_%H%M%S')}.docx"
        alt_path = os.path.join(SAVE_FOLDER, alt_name)
        doc.save(alt_path)
        return alt_path

@app.route('/')
def index():
    """
    主页路由处理函数
    
    Returns:
        str: 渲染的HTML模板
    """
    return render_template('index.html')


@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """
    清除当前会话的聊天历史
    
    Returns:
        json: 操作结果
    """
    try:
        session_id = get_session_id()
        # 清除当前会话的历史记录
        import sqlite3
        conn = sqlite3.connect(db.DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Chat history cleared successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    聊天API路由处理函数
    处理用户的聊天请求，包括生成英语阅读任务和普通对话
    
    Returns:
        json: 包含响应内容的JSON对象
    """
    # 获取请求数据
    data = request.json
    message = data.get('message', '').strip()
    
    # 获取会话ID
    session_id = get_session_id()
    
    # 如果消息为空，返回空响应
    if not message:
        return jsonify({'response': ''})

    # 如果用户输入'task'，生成英语阅读任务
    if message.lower() == 'task':
        # 生成阅读任务
        # 复用agent.py的逻辑但需要捕获输出
        # agent.py的generate_daily_reading返回(content, file_path)
        # 但它使用agent.py的save_to_word保存文件
        # 我们想要使用自定义的save_to_word逻辑
        
        # 所以我们应该调用LLM生成部分，但自己处理保存
        # 但agent.py中的generate_daily_reading包含了所有内容包括保存
        # 为了使用自定义字体，我们复制逻辑而不是修改agent.py
        
        # 获取当前状态
        topic, step = get_state()
        
        # 构建提示词
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
        # 重试逻辑，最多尝试5次
        content = None
        for _ in range(5):
            try:
                # 调用LLM生成内容
                result = generate_code(prompt)
            except Exception as e:
                return jsonify({'response': f'Service error: {str(e)}'})
            if not result:
                continue
            # 计算内容哈希值
            h = sha(result)
            # 检查是否已经发送过相同内容
            if is_sent(h):
                continue
            # 标记为已发送
            mark_sent(h)
            # 保存状态
            save_state(topic, step + 1, result)
            content = result
            break
        
        # 如果成功生成内容
        if content:
            # 清理markdown格式
            cleaned_content = clean_markdown(content)
            # 保存为Word文档
            file_path = save_to_word_custom(cleaned_content)
            
            # 构建响应消息
            response_msg = f"Today's English reading is ready!\nSaved to: {file_path}\n\n" + cleaned_content[:600] + "..."
            
            # 保存聊天历史（包含完整内容）
            db.save_chat_history(session_id, message, cleaned_content, 'task')
            
            # 返回响应
            return jsonify({
                'response': response_msg,
                'full_content': cleaned_content,
                'file_path': file_path
            })
        else:
            error_msg = "Failed to generate content. Please try again."
            db.save_chat_history(session_id, message, error_msg, 'task')
            return jsonify({'response': error_msg})

    else:
        # 处理普通聊天消息
        try:
            # 构建包含上下文的提示词
            context_prompt = build_context_prompt(session_id, message)
            
            # 调用LLM生成响应
            response = generate_code(context_prompt)
        except Exception as e:
            error_msg = f'Service error: {str(e)}'
            db.save_chat_history(session_id, message, error_msg, 'chat')
            return jsonify({'response': error_msg})
        
        if response:
            # 清理响应中的markdown格式
            cleaned_response = clean_markdown(response)
            
            # 保存聊天历史
            db.save_chat_history(session_id, message, cleaned_response, 'chat')
            
            return jsonify({'response': cleaned_response})
        else:
            error_msg = "Sorry, I couldn't generate a response."
            db.save_chat_history(session_id, message, error_msg, 'chat')
            return jsonify({'response': error_msg})

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    db.init_db()  # 确保新的聊天历史表也被创建
    
    # 清理7天前的旧聊天记录
    db.clear_old_chat_history(7)
    
    # 启动Flask应用
    # host='0.0.0.0' 允许外部访问
    # port=80 使用80端口
    # debug=True 开启调试模式
    app.run(host='0.0.0.0', port=80, debug=True)
