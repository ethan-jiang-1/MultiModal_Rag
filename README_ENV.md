# 环境变量配置说明

本文档详细说明了项目中使用的环境变量及其配置方法。

## Azure OpenAI相关
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI服务的端点
- `AZURE_OPENAI_BASE_URL`: Azure OpenAI服务的基础URL
- `AZURE_OPENAI_API_KEY`: Azure OpenAI服务的API密钥
- `AZURE_OPENAI_VERSION`: Azure OpenAI API的版本号


## LlamaParse相关
- `LLAMAPARSE_API_KEY`: LlamaParse服务的主API密钥

## Jina AI相关
- `JINA_API_KEY`: Jina AI服务的API密钥

## 阿里云相关 模型/OSS存储相关
- `DASHSCOPE_API_KEY`: 智谱AI服务的API密钥
- `OSS_ACCESS_KEY_ID`: 阿里云OSS访问密钥ID
- `OSS_ACCESS_KEY_SECRET`: 阿里云OSS访问密钥密码
- `OSS_ENDPOINT`: 阿里云OSS服务端点
- `OSS_BUCKET_NAME`: 阿里云OSS存储桶名称

## 火山引擎相关 模型/TOS存储相关
- `ARK_API_KEY`: ARK服务的API密钥
- `VOLC_ACCESSKEY`: 火山引擎访问密钥
- `VOLC_SECRETKEY`: 火山引擎密钥
- `VOLC_ENDPOINT`: 火山引擎服务端点
- `VOLC_BUCKET_NAME`: 火山引擎存储桶名称

## TEXTIN相关 PDF->MD
- `X_TI_APP_ID`: TEXTIN APP
- `X_TI_SECRET_CODE`: TEXTIN SECRET

## 其他AI服务相关（私有部署） 
- `JINA_RERANKER_ENDPOINT`: Jina重排序服务的端点私有部署 RERANKER local
- `DOCLAYOUT_ENDPOINT`: 文档布局分析服务的端点私有部署 YOLO DOCLAYOUT local

## Python环境配置
- `PYTHONPATH`: Python模块搜索路径配置 **设置为当前目录**
