# 英语学习助手 (English Learning Assistant)

一个基于AI的英语学习助手，专门为CET-6和研究生水平的学习者生成高质量的英语阅读材料和理解题。

## 功能特点

### 核心功能
- **智能文章生成**：生成600-900词的高质量英语阅读文章
- **多领域覆盖**：金融经济、学术研究、科学技术、著名演讲等
- **理解题配套**：每篇文章配5-8道理解题（主旨、推理、词汇、态度等）
- **Word文档导出**：自动保存为格式化的Word文档

### 智能记忆功能
- **上下文记忆**：AI能记住之前的对话和生成的文章内容
- **连续对话**：可以基于之前生成的文章进行深入讨论
- **会话管理**：支持清除历史记录，重置AI记忆

### 数据管理
- **内容去重**：防止生成重复的学习材料
- **学习进度**：自动跟踪学习步骤和历史记录
- **自动清理**：定期清理过期的聊天记录

## 技术架构

- **后端**：Flask + SQLite
- **前端**：HTML + JavaScript
- **AI模型**：DeepSeek API
- **文档处理**：python-docx

## 安装和使用

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/yourusername/english-learning-assistant.git
cd english-learning-assistant

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥
创建 `.env` 文件并添加你的DeepSeek API密钥：
```
DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 启动应用
```bash
# Windows
run_web.bat

# 或者直接运行
python app.py
```

### 4. 访问应用
打开浏览器访问：`http://localhost:80`

## 使用方法

### 生成阅读材料
1. 在聊天框中输入 `task`
2. AI会生成一篇英语阅读文章和配套题目
3. 文章会自动保存为Word文档

### 讨论文章内容
1. 生成文章后，可以直接询问文章相关问题
2. 例如："这篇文章的主要观点是什么？"
3. AI会基于之前生成的文章内容回答

### 清除记忆
- 点击界面上的"Clear History"按钮
- 或者刷新页面开始新的会话

## 项目结构

```
english-learning-assistant/
├── app.py              # Flask主应用
├── db.py               # 数据库操作
├── llm.py              # AI模型接口
├── agent.py            # 代理逻辑
├── state.py            # 状态管理
├── dedup.py            # 去重功能
├── prompt.py           # 提示词模板
├── templates/
│   └── index.html      # 前端界面
├── requirements.txt    # 依赖列表
├── .gitignore         # Git忽略文件
├── run_web.bat        # Windows启动脚本
└── README.md          # 项目说明
```

## 配置说明

### 字体设置
在 `app.py` 中可以修改Word文档的字体设置：
```python
FONT_PATH = r"your_font_path"  # 字体文件路径
FONT_NAME = "Your_Font_Name"   # 字体名称
```

### 保存路径
修改文档保存路径：
```python
SAVE_FOLDER = r"your_save_path"  # 保存目录
```

### 数据库路径
在 `db.py` 中修改数据库路径：
```python
DB_PATH = r"your_database_path"
```

## 开发说明

### 数据库结构
- `learning_state`: 学习状态记录
- `sent_content`: 内容去重记录
- `chat_history`: 聊天历史记录

### API接口
- `POST /api/chat`: 聊天接口
- `POST /api/clear_history`: 清除历史记录

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 更新日志

### v2.0.0 (2024-12-17)
-  新增智能上下文记忆功能
-  新增会话管理和历史记录清除
-  修复AI记忆问题
-  完善中文注释和文档

### v1.0.0
-  初始版本发布
-  基础文章生成功能
-  Word文档导出功能
-  内容去重功能

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件到：2064780260@qq.com

---


**注意**：使用本项目需要有效的DeepSeek API密钥。请确保遵守相关服务条款。

