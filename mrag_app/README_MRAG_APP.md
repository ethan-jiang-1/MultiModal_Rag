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

## 快速开始

### 安装

1. 确保已安装 Python 3.12+
2. 安装依赖：
```bash
# 安装基础依赖
pip install -r requirements.txt

# 如果需要开发和测试功能，还需要安装
pip install -r requirements-dev.txt
```

### 配置

1. 在项目根目录创建 `.env` 文件
2. 添加必要的配置（参考 [环境配置说明](../README_MRAG_ENV.md)）：
```bash
# 必选：Python路径配置
PYTHONPATH=.

# 必选：至少配置一个LLM服务
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_VERSION=2023-05-15
```

### 启动应用

根据需要选择不同的启动方式：

1. **标准模式**（使用 GPT 模型）：
```bash
python app_gradio.py
```

2. **使用通义千问**：
```bash
python app_gradio_local_qwen.py
```

3. **使用火山方舟**：
```bash
python app_gradio_local_ark.py
```

4. **使用本地 GPT 模型**：
```bash
python app_gradio_local_gpt.py
```

启动后，应用将在本地运行（默认地址：http://localhost:7860）。

## 使用指南

### 界面布局

```
+------------------------+
|     模型选择下拉框     |
+------------------------+
|     知识库选择下拉框   |
+------------------------+
|     检索参数设置       |
+------------------------+
|     对话历史区域       |
+------------------------+
|     输入框            |
+------------------------+
|     发送按钮          |
+------------------------+
|     状态显示区域       |
+------------------------+
```

### 基本操作流程

1. **选择模型和知识库**
   - 从下拉框选择要使用的模型
   - 选择合适的知识库（如 MRAG 或 Papers）

2. **调整检索参数**
   - 设置检索文档数量（默认为 3）
   - 调整相似度阈值（可选）
   - 配置上下文窗口大小（可选）

3. **提问和交互**
   - 在输入框中输入问题
   - 点击发送按钮或按回车
   - 等待回答生成，查看实时进度

4. **查看结果**
   - 检查生成的回答
   - 查看相关的参考文档
   - 根据需要调整参数重试

### 高级功能

#### 1. 自定义提示词

可以使用特殊格式的提示词来控制回答的生成：

```
/format json  # 以JSON格式输出
/length short  # 生成简短回答
/style technical  # 使用技术性语言
```

#### 2. 知识库管理

- 切换不同知识库：
  ```python
  from mrag_app.app_qa_core import switch_knowledge_base
  switch_knowledge_base("papers")  # 切换到论文知识库
  ```

- 刷新知识库缓存：
  ```python
  from mrag_app.app_qa_core import refresh_kb_cache
  refresh_kb_cache()
  ```

#### 3. 进度监控

可以通过日志查看详细的处理进度：

```python
from mrag_app.app_log_monitor import ProgressLogger
logger = ProgressLogger()
logger.get_progress_history()  # 获取进度历史
```

## 自定义开发

### 1. 添加新的模型支持

创建新的模型适配器：

```python
from mrag_app.app_qa_core import BaseModelAdapter

class NewModelAdapter(BaseModelAdapter):
    def __init__(self):
        super().__init__()
        
    async def generate_response(self, prompt, **kwargs):
        # 实现模型调用逻辑
        pass
```

### 2. 自定义界面主题

在 `custom_theme.py` 中定义新主题：

```python
custom_theme = {
    "primary_color": "#2B7C85",
    "secondary_color": "#3C9D9B",
    "background_color": "#FFFFFF",
    # 更多样式配置...
}
```

### 3. 添加新的检索策略

实现自定义的检索策略：

```python
from mrag_app.app_qa_core import BaseRetriever

class CustomRetriever(BaseRetriever):
    def retrieve(self, query, **kwargs):
        # 实现检索逻辑
        pass
```

## 性能优化

### 1. 内存管理

- 定期清理缓存：
  ```python
  from mrag_app.app_qa_core import clear_cache
  clear_cache()
  ```

- 控制并发请求：
  ```python
  # 在配置中设置最大并发数
  MAX_CONCURRENT_REQUESTS = 5
  ```

### 2. 响应速度优化

- 使用异步处理：
  ```python
  async def process_query(query):
      # 异步处理逻辑
      pass
  ```

- 实现结果缓存：
  ```python
  from functools import lru_cache
  
  @lru_cache(maxsize=100)
  def cached_query(query_string):
      # 查询处理逻辑
      pass
  ```

## 故障排除

### 常见问题

1. **应用启动失败**
   - 检查端口是否被占用
   - 验证环境变量配置
   - 确认依赖安装完整

2. **模型调用失败**
   - 检查API密钥配置
   - 验证网络连接
   - 查看错误日志

3. **知识库加载错误**
   - 确认知识库文件存在
   - 检查文件权限
   - 验证向量数据库连接

4. **界面显示异常**
   - 清除浏览器缓存
   - 检查CSS加载
   - 更新Gradio版本

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看性能日志
tail -f logs/performance.log
```

## 系统要求

- **硬件要求**
  - CPU: 2核心以上
  - 内存: 8GB以上（推荐16GB）
  - 磁盘空间: 10GB以上

- **软件要求**
  - Python 3.12+
  - pip 21.0+
  - Node.js 18+（用于开发）

- **网络要求**
  - 稳定的互联网连接
  - 支持HTTPS协议
  - 端口7860可用

## 参考资料

- [Gradio 官方文档](https://gradio.app/docs/)
- [项目API文档](../docs/api/) 