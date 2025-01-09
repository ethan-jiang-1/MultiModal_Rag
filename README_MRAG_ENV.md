# 环境变量配置说明

本文档详细说明了项目中使用的环境变量及其配置方法。所有配置项都应该放在项目根目录的 `.env` 文件中。

## 必选配置

以下配置项是系统正常运行所必需的：

### Python环境配置
```bash
# Python模块搜索路径配置（必选）
PYTHONPATH=.
```

### 基础LLM服务（至少需要配置一个）
```bash
# Azure OpenAI配置
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_VERSION=2023-05-15

# 或者 通义千问配置
DASHSCOPE_API_KEY=your-api-key

# 或者 火山方舟配置
ARK_API_KEY=your-api-key
```

## 可选配置

以下配置项是可选的，根据您使用的功能来决定是否需要配置：

### 文档处理服务（选择一个配置）
```bash
# LlamaParse配置（推荐，支持更多文档格式）
LLAMAPARSE_API_KEY=your-api-key

# 或者 TEXTIN配置
X_TI_APP_ID=your-app-id
X_TI_SECRET_CODE=your-secret-code
```

### 存储服务配置（主要为了辅助多模态上传图片）
```bash
# 阿里云OSS配置
OSS_ACCESS_KEY_ID=your-access-key
OSS_ACCESS_KEY_SECRET=your-secret-key
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
OSS_BUCKET_NAME=your-bucket-name

# 或者 火山引擎TOS配置
VOLC_ACCESSKEY=your-access-key
VOLC_SECRETKEY=your-secret-key
VOLC_ENDPOINT=tos-cn-beijing.volces.com
VOLC_BUCKET_NAME=your-bucket-name
```

### 向量服务配置（用于高级检索功能）
```bash
# Jina AI配置
JINA_API_KEY=your-api-key

# 私有部署配置（如果使用本地服务）
JINA_RERANKER_ENDPOINT=http://localhost:8000
```

## 文档布局分析配置（用于辅助文档处理）

```bash
DOCLAYOUT_ENDPOINT=http://localhost:8001
```

## 配置验证

您可以使用以下命令验证配置是否正确：

```bash
# 验证环境变量是否正确加载
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('PYTHONPATH:', os.getenv('PYTHONPATH'))"

# 验证LLM服务配置
python tools/verify_llm_config.py

# 验证文档处理服务配置
python tools/verify_doc_service.py
```

## 常见问题

1. **环境变量未加载**
   - 确保 `.env` 文件在项目根目录
   - 确保使用了 `python-dotenv` 加载环境变量
   - 检查文件权限是否正确

2. **API密钥无效**
   - 确保复制的API密钥完整，没有多余的空格
   - 检查API密钥是否已过期
   - 验证服务是否在您的地区可用

3. **存储服务连接失败**
   - 检查网络连接
   - 验证Endpoint是否正确
   - 确认存储桶是否存在且有正确的访问权限

4. **PYTHONPATH配置问题**
   - 在项目根目录运行命令
   - 确保 `PYTHONPATH=.` 已正确设置
   - 如果使用IDE，确保IDE也正确加载了环境变量

## 配置模板

您可以使用以下模板创建 `.env` 文件，根据需要取消注释并填写相应的值：

```bash
# 必选配置
PYTHONPATH=.

# LLM服务配置（至少选择一个）
#AZURE_OPENAI_ENDPOINT=
#AZURE_OPENAI_API_KEY=
#AZURE_OPENAI_VERSION=

#DASHSCOPE_API_KEY=

#ARK_API_KEY=

# 文档处理服务配置（可选）
#LLAMAPARSE_API_KEY=

# 或者 #TEXTIN配置
#X_TI_APP_ID=tus
#X_TI_SECRET_CODE=

# 存储服务配置（可选）
#OSS_ACCESS_KEY_ID=
#OSS_ACCESS_KEY_SECRET=
#OSS_ENDPOINT=
#OSS_BUCKET_NAME=

# 向量服务配置（可选）
#JINA_API_KEY=
#JINA_RERANKER_ENDPOINT=

# 文档布局分析配置（可选）
#DOCLAYOUT_ENDPOINT=
```
