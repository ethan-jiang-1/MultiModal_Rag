# MRAG App (MultiModal RAG Application)

基于 Gradio 构建的多模态检索增强生成（MultiModal RAG）应用界面。

## 功能特性

- 提供友好的 Web 界面，支持与多种 LLM 模型交互
- 支持多种模型后端：
  - GPT-4/3.5 系列
  - Qwen (通义千问)
  - Ark
  - 本地模型
- 支持多个知识库切换
- 实时进度显示和日志监控
- 自定义 CSS 主题，优化界面展示
- 支持 Markdown 格式输出，包括图片显示
- 可配置的检索参数（如检索数量等）

## 安装

1. 确保已安装 Python 3.8+
2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 启动应用

可以通过以下几种方式启动应用：

1. 标准模式（使用 GPT 模型）：
```bash
python app_gradio.py
```

2. 使用 Qwen 模型：
```bash
python app_gradio_local_qwen.py
```

3. 使用 Ark 模型：
```bash
python app_gradio_local_ark.py
```

4. 使用本地 GPT 模型：
```bash
python app_gradio_local_gpt.py
```

启动后，应用将在本地运行，并提供一个 Web 界面地址。

### 主要功能

- 模型选择：可以在界面上切换不同的 LLM 模型
- 知识库选择：支持选择不同的知识库进行检索
- 检索数量调整：可以调整每次检索的文档数量
- 实时进度显示：查询过程中会显示实时进度和状态
- 历史记录：保存对话历史，方便回顾

## 环境变量

应用使用 `.env` 文件管理配置，主要包括：
- API 密钥配置
- 模型参数设置
- 系统路径配置

## 开发说明

- 使用 Gradio 框架构建界面
- 采用模块化设计，核心功能与界面分离
- 支持自定义主题和样式
- 包含完整的日志系统

## 系统要求

- Python 3.8+
- 足够的系统内存（建议 8GB+）
- 稳定的网络连接（使用在线模型时） 