# prompt.py - 提示词模块
# 提供生成英语阅读材料的提示词模板

def daily_english_reading_prompt(step: int) -> str:
    """
    生成每日英语阅读的提示词
    
    Args:
        step (int): 当前学习步骤数
        
    Returns:
        str: 格式化的提示词字符串，用于指导AI生成英语阅读材料
    """
    return f"""
Your task:
Generate ONE high-quality English reading passage suitable for CET-6 or early postgraduate level learners.

Requirements:
1. Topic must be ONE of the following:
   - Finance & Economics                    # 金融与经济
   - Academic Research                      # 学术研究
   - Science & Technology                   # 科学与技术
   - Famous Speeches or Intellectual Essays # 著名演讲或知识性文章
2. Word count: 600–900 words               # 字数要求：600-900词
3. Style: formal, logical, academic or speech-like  # 风格：正式、逻辑性强、学术性或演讲风格
4. Vocabulary: rich but appropriate for advanced learners  # 词汇：丰富但适合高级学习者
5. Content must be ORIGINAL and not repeated  # 内容必须原创且不重复

After the reading passage, provide:
- 5 to 8 English comprehension questions    # 5-8个英语理解题
- Questions should include:                 # 题目应包括：
  • main idea                              # 主旨大意
  • inference                              # 推理判断
  • vocabulary in context                  # 词汇理解
  • author's attitude                      # 作者态度
- DO NOT provide answers                   # 不要提供答案

Output format strictly as:                 # 严格按照以下格式输出：

Title
---
Reading Passage
---
Questions

This is reading number {step + 1}.        # 这是第{step + 1}篇阅读材料
"""