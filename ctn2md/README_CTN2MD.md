# CTN2MD (Content To Markdown)

智能文档转换工具，支持多种文档格式到 Markdown 的高质量转换。

## 核心功能

### 1. 多引擎支持
- **LVLM (Large Vision Language Model) 模式**
  - 支持格式：PDF
  - 特点：基于视觉语言模型，可以准确理解文档布局和内容
  - 核心能力：
    - 智能区域检测 (gs0/gs1/gs2)
    - 图文关系理解
    - 布局结构重建
  - 适用场景：复杂排版文档，图文混排文档
  - 转换质量：优秀

- **TextIn OCR 模式**
  - 支持格式：PDF
  - 特点：基于OCR技术，可靠的文本提取能力
  - 核心能力：
    - 精确OCR识别
    - 智能布局分析
    - 图片描述生成
  - 适用场景：文本为主的文档，扫描版PDF
  - 转换质量：优秀

- **LlamaParse 模式**
  - 支持格式：PDF, PPTX, DOCX, TXT, MD, HTML, PNG, JPG等
  - 特点：格式支持最全面，通用性强
  - 核心能力：
    - 多格式解析
    - 内容结构化
    - 智能图片处理
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
├── gen_lvlm/                # LVLM引擎相关
│   ├── image2mds/              # 图片到MD转换
│   ├── non_text_detector_*/    # 区域检测模型
│   └── lvlm_*.py              # LVLM核心功能
├── gen_ti/                 # TextIn引擎相关
│   ├── _ti_*.py               # 核心功能模块
│   └── ti_*.py                # 工具和接口
├── gen_lp/                 # LlamaParse引擎相关
│   ├── _download_*.py         # 资源下载模块
│   └── lp_*.py                # 核心功能模块
├── utils_llm/              # LLM工具
├── utils_vllm/             # Vision LLM工具
├── utils_gen/              # 通用生成工具
├── utils/                  # 通用工具函数
├── src_gen/                # 核心和gen的适配
└── src/                    # 核心功能实现
```

## 快速开始

### 1. 环境配置
```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 基本使用

```python
# TextIn模式（适合文本文档）
from ctn2md.ctn2md_converter_pdf_ti import do_content2md_convert
do_content2md_convert("your_doc.pdf")

# LVLM模式（适合复杂排版）
from ctn2md.ctn2md_converter_pdf_lvlm import do_content2md_convert
do_content2md_convert("your_doc.pdf")

# LlamaParse模式（支持多种格式）
from ctn2md.ctn2md_converter_all_lp import do_content2md_convert
do_content2md_convert("your_doc.*")  # 支持多种格式
```

### 3. 批量处理
```python
# 批量处理多个文档
from ctn2md.batch_cvt_papers import batch_convert
batch_convert(["doc1.pdf", "doc2.pdf"])

# 批量处理MRAG文档
from ctn2md.batch_cvt_mrag import batch_convert
batch_convert(["doc1.pdf", "doc2.pdf"])
```

## 配置说明

### 环境变量
- `ENV_MODEL_FLOW`: 流程控制模型 (gpt/qwen/ark)
- `ENV_MODEL_GEN_LP`: LlamaParse生成模型 (gpt/qwen/ark)
- `ENV_MODEL_GEN_LVLM`: LVLM生成模型 (gpt/qwen/ark)
- `ENV_MODEL_GEN_LVLM_REGION`: LVLM区域检测模型 (gs0/gs1/gs2)
- `ENV_MODEL_GEN_TI`: TextIn生成模型 (gpt/qwen/ark)

### 转换控制参数
```python
mdcontrols = {
    # 通用配置
    "mctl_move_aux_files": True,                    # 是否移动辅助文件
    "mctl_treat_doc_as_ctntype": "auto",           # 文档类型处理方式
    "mctl_ge_md_async": False,                     # 异步生成开关
    "mctl_fix_heading_model": "qwen",              # 标题修复模型
    "mctl_summarize_model": "qwen",                # 摘要生成模型
    "mctl_cache_dir": "_cache",                    # 缓存目录

    # LlamaParse专用配置
    "mctl_lp_min_img_relevance_score": 0.2,        # 图片相关性最小分数
    "mctl_lp_img_relevance_model": "qwen",         # 图片相关性判断模型
    "mctl_lp_img_caption_model": "qwen",           # 图片说明生成模型
    "mctl_lp_need_image_ref": True,                # 是否需要图片引用
    "mctl_lp_langauge": "zh_cn",                   # 文档语言
    "mctl_lp_take_screenshot": False,              # 是否截图
    "mctl_lp_disable_ocr": False,                  # 是否禁用OCR
    "mctl_lp_premium_pages": [],                   # 高级模式页面列表

    # LVLM专用配置
    "mctl_lvlm_images_ignore": "",                 # 忽略的图片列表
    "mctl_lvlm_img2md_model": "qwen",              # 图片转MD模型
    "mctl_lvlm_region_detect": "gs2",              # 区域检测模型
    "mctl_lvlm_paint_max_area_ratio": 0.7,         # 最大区域比例
    "mctl_lvlm_paint_max_outside_ratio": 0.1,      # 最大外部比例
    "mctl_lvlm_paint_min_coverage_ratio": 0.7,     # 最小覆盖比例

    # TextIn专用配置
    "mctl_ti_img_relevance_model": "qwen",         # 图片相关性判断模型
    "mctl_ti_img_caption_model": "qwen",           # 图片说明生成模型
    "mctl_ti_cache_instruct": True,                # 是否缓存指令
    "mctl_ti_cache_description": True,              # 是否缓存描述
}
```

## 输出说明

```
_output/
├── ctn2md_{kb_name}__{doc_title}/    # 文档输出目录
    ├── _aux/                         # 辅助文件目录
    │   ├── images/                   # 图片资源
    │   ├── temp/                     # 临时文件
    ├── _cache/                       # 缓存文件
    ├── _info.json                    # 文档信息
    ├── _info_ctrl.json              # 控制信息
    ├── _final_info.json             # 最终结果信息
    └── {doc_title}___md.md          # 最终Markdown文件
```

## 开发指南

### 1. 添加新的转换引擎
1. 在 `gen_*` 目录下创建新的引擎目录
2. 实现以下核心组件：
   - 文档解析器
   - 内容提取器
   - 格式转换器
   - 后处理优化器
3. 创建对应的转换器类
4. 在 `ctn2md_converter_*.py` 中注册新引擎

### 2. 自定义处理流程
可以通过修改以下组件来自定义处理：
1. 内容提取器：实现特定格式的内容提取
2. 格式转换器：定制化的格式转换规则
3. 后处理优化器：自定义的优化规则
4. 质量检查器：特定场景的质量检查

### 3. 缓存机制
系统提供了多层次的缓存支持：
1. 指令缓存：避免重复的指令生成
2. 描述缓存：缓存生成的描述结果
3. 图片缓存：缓存处理过的图片
4. 中间结果缓存：缓存转换过程的中间结果

## 系统要求
- Python 3.10+
- 支持的模型服务：
  - GPT/Qwen/Ark等LLM
  - TextIn API
  - LlamaParse
  - LVLM服务

## 版本历史

当前版本：0.11.0


