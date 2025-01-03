# MultiModal_Rag

一个完整的多模态 RAG (Retrieval-Augmented Generation) 系统，包含文档转换、向量数据库存储和 Gradio 交互界面。

## 系统架构

该项目由三个主要模块组成：

1. **CTN2MD** (Content to Markdown)
   - 将各种格式文档（PDF、PPTX、DOCX等）转换为结构化的 Markdown
   - 自动识别和优化文档结构，生成合理的 TOC (Table of Contents)
   - 支持图片提取和智能描述生成
   - 多模态内容处理（文本、图片、表格等）

2. **MRAG_VDB** (MultiModal RAG Vector Database)
   - 处理和存储 Markdown 文档到向量数据库
   - 支持多模态内容的向量化和索引
   - 提供高效的相似度搜索接口
   - 集成重排序机制提升检索质量

3. **MRAG_APP** (MultiModal RAG Application)
   - 基于 Gradio 的交互式界面
   - 支持多模态问答
   - 可视化知识检索结果
   - 用户友好的文档管理界面

## 特性

- 多格式文档支持
- 智能文档结构化
- 多模态内容处理
- 高效向量检索
- 交互式界面
- 可扩展架构