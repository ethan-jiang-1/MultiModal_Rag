# MRAG VDB (Vector Database)

MRAG 的向量数据库核心组件，提供文档向量化、存储和检索功能。

## 核心功能

### 1. 文档处理与向量化
- 支持将 Markdown 文档转换为向量数据
- 智能文档分块
- 文档元信息管理
- 支持图片等参考文件的同步管理

### 2. 向量数据库操作
- 文档 Upsert（插入/更新）操作
- 批量文档处理
- 多知识库（Collection）管理
- 向量数据持久化

### 3. 高级检索功能
- 混合检索策略
  - 向量相似度检索
  - BM25 文本匹配
  - 重排序（Rerank）支持
- 可配置的权重系统
  - 距离权重（WEIGHT_DISTANCE）
  - 重排序权重（WEIGHT_RERANK）
  - BM25权重（WEIGHT_BM25）
- 分段检索与重组

## 项目结构

```
mrag_vdb/
├── build/          # 文档构建和向量化
├── query/          # 检索相关功能
├── knowledge/      # 知识库管理
├── utils/          # 通用工具
├── utils_llm/      # LLM 相关工具
└── common/         # 共享组件
```

## 快速开始

### 安装
```bash
pip install -r requirements.txt
```

### 添加文档到向量数据库
```python
from mrag_vdb.add_doc_to_vdb import upsert_doc_to_vdb

# 添加单个文档
upsert_doc_to_vdb("path/to/your/document.md")

# 批量添加文档
from mrag_vdb.batch_docs_to_vdb_mrag import upsert_batch_kbname_to_vdb
upsert_batch_kbname_to_vdb("path/to/docs", "kb_name")
```

### 检索示例
```python
from mrag_vdb.query.query2section_reranked import query2sortedsections_reranked
from mrag_vdb.query.query2section_raw import query2section_raw_on_multiple_collection

# 执行检索
raw_results = query2section_raw_on_multiple_collection("your query")
reranked_results = query2sortedsections_reranked("your query", raw_results)
```

## 配置说明

### 环境变量
项目使用 `.env` 文件管理配置，主要包括：
- 向量数据库连接配置
- 模型参数设置
- 文件路径配置

### 核心参数
- 检索权重配置：
  - `WEIGHT_DISTANCE`: 向量距离权重
  - `WEIGHT_RERANK`: 重排序权重
  - `WEIGHT_BM25`: BM25 权重

## 开发指南

### 添加新知识库
1. 准备 Markdown 格式的文档
2. 使用 `batch_docs_to_vdb_*.py` 脚本进行批量导入
3. 文档命名规范：`ctn2md_{kb_name}__*`

### 自定义检索策略
可以通过调整以下组件来自定义检索：
1. 修改权重配置
2. 实现新的重排序器
3. 调整分块策略

## 系统要求

- Python 3.8+
- 足够的磁盘空间用于向量存储
- 建议使用 SSD 以获得更好的检索性能

## 注意事项

1. 文档处理
   - 确保文档格式规范
   - 注意图片等引用文件的路径处理
   
2. 向量数据库
   - 定期备份向量数据
   - 监控数据库大小

3. 性能优化
   - 合理设置分块大小
   - 优化检索参数
   - 适当使用批处理 