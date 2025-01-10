# CTN2MD (Content To Markdown)

智能文档转换工具，支持多种文档格式到 Markdown 的高质量转换。

## 核心功能

### 1. 多引擎支持
- **LVLM (Large Vision Language Model) 模式**
  - 支持格式：PDF
  - 特点：基于视觉语言模型，可以准确理解文档布局和内容
  - 适用场景：复杂排版文档，图文混排文档
  - 转换质量：优秀

- **TextIn OCR 模式**
  - 支持格式：PDF, DOC
  - 特点：基于OCR技术，可靠的文本提取能力
  - 适用场景：文本为主的文档，扫描版PDF
  - 转换质量：优秀

- **LlamaParse 模式**
  - 支持格式：PDF, PPTX, DOCX, TXT, MD, HTML, PNG, JPG等
  - 特点：格式支持最全面，通用性强
  - 适用场景：多格式批量转换
  - 转换质量：良好

### 2. 智能处理能力
- **文档结构优化**
  - 自动标题层级优化
  - 智能段落划分
  - 列表格式标准化
  - 表格结构重建

- **内容增强**
  - 图文智能关联
  - 内容智能分段
  - 格式自动修正
  - 内容智能总结

- **质量保证**
  - 多级质量检查
  - 错误自动修复
  - 格式一致性验证
  - 增量更新支持

### 3. 系统特性
- **高性能处理**
  - 异步并行处理
  - 增量更新机制
  - 智能缓存系统
  - 批量处理优化

- **可靠性保证**
  - 完善的错误处理
  - 自动重试机制
  - 状态追踪
  - 日志记录

## 项目结构

```
ctn2md/
├── src/                # 核心功能实现
│   ├── md_info_base.py     # 基础信息处理
│   ├── md_page_spe.py      # 特殊页面处理
│   └── ...
├── gen_ti/            # TextIn引擎相关
├── gen_lvlm/          # LVLM引擎相关
├── gen_lp/            # LlamaParse引擎相关
├── utils_llm/         # LLM工具
├── utils_vllm/        # Vision LLM工具
├── utils_gen/         # 通用生成工具
└── utils/             # 通用工具函数
```

## 快速开始

### 1. 环境配置
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export ENV_MODEL_FLOW=qwen     # 流程控制模型
export ENV_MODEL_GEN_TI=qwen   # TextIn生成模型
export ENV_MODEL_GEN_LP=qwen   # LlamaParse生成模型
export ENV_MODEL_GEN_LVLM=qwen # LVLM生成模型
```

### 2. 基本使用

```python
# TextIn模式（适合文本文档）
from ctn2md.ctn2md_converter_ti import do_content2md_convert
do_content2md_convert("your_doc.pdf")

# LVLM模式（适合复杂排版）
from ctn2md.ctn2md_converter_lvlm import do_content2md_convert
do_content2md_convert("your_doc.pdf")

# LlamaParse模式（支持多种格式）
from ctn2md.ctn2md_converter_lp import do_content2md_convert
do_content2md_convert("your_doc.pdf")
```

### 3. 批量处理
```python
from ctn2md.batch_cvt_papers import batch_convert
batch_convert(["doc1.pdf", "doc2.pdf"])
```

## 配置说明

### 环境变量
- `ENV_MODEL_FLOW`: 流程控制模型 (gpt/qwen/ark)
- `ENV_MODEL_GEN_LP`: LlamaParse生成模型
- `ENV_MODEL_GEN_LVLM`: LVLM生成模型
- `ENV_MODEL_GEN_TI`: TextIn生成模型

### 转换控制参数
```python
mdcontrols = {
    "mctl_ge_md_async": True,     # 是否使用异步处理
    "mctl_heading_fix": True,     # 是否修复标题
    "mctl_quality_check": True,   # 是否进行质量检查
    # ... 更多参数
}
```

## 输出说明

```
_output/
├── ctn2md_{kb_name}__{doc_title}/    # 文档输出目录
    ├── _aux/                         # 辅助文件目录
    │   ├── images/                   # 图片资源
    │   └── temp/                     # 临时文件
    ├── _info.json                    # 文档信息
    ├── _info_ctrl.json              # 控制信息
    ├── _final_info.json             # 最终结果信息
    └── {doc_title}___md.md          # 最终Markdown文件
```

## 开发指南

### 添加新的转换引擎
1. 继承 `GenMd_Base` 类
2. 实现必要的接口方法
3. 添加新的转换器类
4. 注册到系统中

### 自定义处理流程
可以通过修改以下组件来自定义处理：
1. 内容提取器
2. 格式转换器
3. 后处理优化器
4. 质量检查器

## 系统要求

- Python 3.12+
- 内存要求：8GB+
- 支持的模型服务：
  - GPT/Qwen/Ark等LLM
  - TextIn API
  - LlamaParse
  - LVLM服务

## 第三方服务配置

### LlamaParse 配置
- 访问 [LlamaIndex Cloud](https://cloud.llamaindex.ai/) 获取 API Key
- 在 `.env` 文件中配置：
```bash
LLAMAINDEX_API_KEY=your_api_key_here
```
详细说明请参考 [LlamaParse转换器文档](gen_lp/README.md)

### TextIn 配置
- 访问 [TextIn](https://www.textin.com/) 获取服务账号
- 在 `.env` 文件中配置相关密钥

### LVLM 配置
- 支持多种视觉语言模型服务
- 在 `.env` 文件中配置相应的模型接口

## 版本历史

当前版本：0.10.0

## 许可证

MIT License


