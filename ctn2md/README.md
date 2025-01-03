# CTN2MD (Content To Markdown)

智能文档转换工具，支持多种文档格式到 Markdown 的高质量转换。

## 核心功能

### 1. 多引擎支持
- LVLM (Large Vision Language Model) 模式
- TextIn OCR 模式
- LlamaParse 模式
- 纯文本模式

### 2. 智能处理能力
- 自动标题层级优化
- 内容智能分段
- 图文关联分析
- 文档结构重组
- 内容智能总结

### 3. 批量处理
- 支持批量文档转换
- 多种文档格式支持
- 可配置的转换参数
- 转换进度监控

### 4. 元信息管理
- 文档唯一标识
- 版本控制 (当前版本: 0.10.0)
- 转换流程追踪
- 文档结构分析

## 项目结构

```
ctn2md/
├── src/            # 核心功能实现
├── gen_ti/         # TextIn 引擎相关
├── gen_lvlm/       # LVLM 引擎相关
├── gen_lp/         # LlamaParse 引擎相关
├── utils_llm/      # LLM 工具
├── utils_vllm/     # Vision LLM 工具
├── utils_gen/      # 通用生成工具
└── utils/          # 通用工具函数
```

## 快速开始

### 安装
```bash
pip install -r requirements.txt
```

### 基本使用

1. 单文档转换
```python
# TextIn 模式
from ctn2md.ctn2md_converter_ti import do_content2md_convert
do_content2md_convert("your_doc.pdf")

# LVLM 模式
from ctn2md.ctn2md_converter_lvlm import do_content2md_convert
do_content2md_convert("your_doc.pdf")

# LlamaParse 模式
from ctn2md.ctn2md_converter_lp import do_content2md_convert
do_content2md_convert("your_doc.pdf")
```

2. 批量转换
```python
from ctn2md.batch_cvt_papers import batch_convert
batch_convert(["doc1.pdf", "doc2.pdf"])
```

## 配置说明

### 环境变量
项目使用 `.env` 文件管理配置：
- `ENV_MODEL_FLOW`: 流程控制模型 (gpt/qwen/ark)
- `ENV_MODEL_GEN_LP`: LlamaParse 生成模型
- `ENV_MODEL_GEN_LVLM`: LVLM 生成模型
- `ENV_MODEL_GEN_TI`: TextIn 生成模型

### 转换控制
可以通过 `mdcontrols` 参数控制转换行为：
- 标题处理策略
- 内容分段规则
- 图文关联策略
- 输出格式控制

## 输出目录结构

```
_output/
├── ctn2md_{kb_name}__{doc_title}/    # 文档输出目录
    ├── _aux/                         # 辅助文件目录
    ├── _info.json                    # 文档信息
    ├── _info_ctrl.json              # 控制信息
    ├── _final_info.json             # 最终结果信息
    └── {doc_title}___md.md          # 最终 Markdown 文件
```

## 开发指南

### 添加新的转换引擎
1. 在 `gen_*` 目录下创建新的引擎实现
2. 实现相应的转换器类
3. 在 `ctn2md_converter_*.py` 中添加接口

### 自定义处理流程
可以通过修改以下组件来自定义处理：
1. 标题处理器
2. 内容分段器
3. 图文关联分析器
4. 内容总结器

## 系统要求

- Python 3.12+
- 足够的系统内存（建议 8GB+）
- 支持的模型服务
  - GPT/Qwen/Ark 等 LLM
  - TextIn API（可选）
  - LlamaParse（可选）

