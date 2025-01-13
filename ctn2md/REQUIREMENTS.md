# 环境要求和依赖说明

## 系统要求

- Python 3.10+
- 操作系统：
  - Linux (推荐 Ubuntu 20.04+)
  - macOS (10.15+)
  - Windows 10/11

## 基础依赖

```
# 核心依赖
python-dotenv>=0.19.0    # 环境变量管理
rich>=10.0.0            # 终端输出美化
pydantic>=2.0.0        # 数据验证
loguru>=0.6.0          # 日志管理
aiofiles>=23.1.0       # 异步文件操作
httpx>=0.24.0          # HTTP客户端

# 文档处理
python-docx>=0.8.11    # Word文档处理
python-pptx>=0.6.21    # PPT文档处理
openpyxl>=3.1.0        # Excel文档处理
PyMuPDF>=1.21.0        # PDF文档处理
markdown>=3.4.0        # Markdown处理
```

## AI模型依赖

```
# LLM模型
openai>=1.0.0          # GPT模型支持
dashscope>=1.10.0      # Qwen模型支持
zhipuai>=1.0.0         # Ark模型支持

# VLLM模型
qwen-vl>=1.0.0         # Qwen-VL模型
gpt4v>=1.0.0           # GPT4-Vision模型
```

## 可选依赖

```
# 性能优化
uvicorn>=0.20.0        # ASGI服务器
gunicorn>=20.1.0       # WSGI服务器
redis>=4.5.0           # 缓存支持

# 开发工具
pytest>=7.3.0          # 单元测试
black>=22.3.0          # 代码格式化
isort>=5.10.0          # Import排序
flake8>=4.0.0          # 代码检查
```

## 安装说明

### 1. 基础安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装基础依赖
pip install -r requirements.txt
```

### 2. 开发环境安装

```bash
# 安装开发依赖
pip install -r requirements-dev.txt
```

### 3. 模型配置

1. 配置环境变量
```bash
# .env文件
OPENAI_API_KEY=your_openai_key
QWEN_API_KEY=your_qwen_key
ARK_API_KEY=your_ark_key
```

2. 模型选择
```python
# 配置默认模型
os.environ["ENV_MODEL_FLOW"] = "qwen"      # 流程控制模型
os.environ["ENV_MODEL_GEN_LP"] = "qwen"    # LlamaParse生成模型
os.environ["ENV_MODEL_GEN_LVLM"] = "qwen"  # LVLM生成模型
os.environ["ENV_MODEL_GEN_TI"] = "qwen"    # TextIn生成模型
```

## 常见问题

### 1. 依赖冲突

如果遇到依赖冲突，可以尝试：
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-deps
pip install -r requirements.txt
```

### 2. 模型访问

- 确保网络可以访问相应的模型API
- 检查API密钥是否正确配置
- 确认模型服务是否可用

### 3. 性能优化

- 使用SSD存储缓存文件
- 配置足够的内存（推荐8GB+）
- 启用异步处理大文件 