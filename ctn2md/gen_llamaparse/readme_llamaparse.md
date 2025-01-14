# LlamaParse Engine

通用文档解析引擎，支持多种格式（PDF、DOCX、PPTX、TXT、MD、HTML等）的文档转换，提供统一的Markdown输出。

## 快速导航

### 核心文件
```
gen_llamaparse/
├── gen_markdown_llamaparse.py # 主入口，负责文档解析流程编排
├── lp_base.py               # 基础功能实现，包含图像分析和处理
├── lp_page2markdown.py      # 页面到Markdown转换实现
├── lp_gen_normal_pages.py   # 普通页面生成处理
├── lp_gen_premium_pages.py  # 高级页面生成处理
├── _download_images.py      # 图片下载和处理
├── _download_table.py       # 表格下载工具
├── _download_image_status.py # 图片状态跟踪
└── n2u_unique_job.py        # 任务唯一性管理
```

## 系统设计

### 核心特性
1. **多模型图像分析**
```python
# 支持多种模型进行图像分析
mctl_lp_img_caption_model = "qwen" | "gpt" | "ark"  # 图片描述模型
mctl_lp_img_relevance_model = "qwen" | "gpt" | "ark"  # 相关性分析模型
```

2. **智能图像处理**
```python
# 图像状态管理
class PAGE_IMG_STATUS:
    REMOVED = "removed"        # 已移除的图片
    POSITIONED = "positioned"  # 已定位的图片
    IRRELEVANCE = "irrelevance" # 不相关的图片
    REF_FILTERED = "ref_filtered" # 引用过滤的图片
```

3. **文档类型自动识别**
```python
# 根据页面特征自动识别文档类型
if page_width > page_height:
    md_info[MIFN.DOC_CTN_TYPE] = CTN_TYPE.PPT  # 自动识别PPT
```

### 关键配置
- `mctl_lp_img_to_heading` - 图片到标题的映射配置
- `mctl_lp_premium_pages` - 高级页面处理配置
- `mctl_lp_img_caption_model` - 图片描述模型选择
- `mctl_lp_img_relevance_model` - 图片相关性模型选择

## 核心功能

### 1. 文档解析流程
- **基础解析**
  - 文档预处理和格式识别
  - 页面分割和内容提取
  - 结构化数据转换
  - 格式标准化处理

- **资源处理**
  - 图片智能提取和分析
  - 表格结构识别和转换
  - 资源状态跟踪和管理
  - 引用关系建立

- **内容优化**
  - 格式美化和标准化
  - 图文关联优化
  - 引用完整性检查
  - 结构一致性维护

## 使用方法

```python
from ctn2md.converters.converter_all_llamaparse import do_content2md_convert

# 基本使用
result = do_content2md_convert("your_doc.pdf")  # 支持 .docx, .pptx 等

# 高级配置
md_info = MdInfo(...)
md_info.set_md_control("mctl_lp_img_caption_model", "gpt")  # 设置图片描述模型
result = generate_markdown_llamaparse(md_info)
```

## 最佳实践

### 1. 模型选择
- **通用场景**: 使用 Qwen (快速且稳定)
- **高精度要求**: 使用 GPT (更精确的描述)
- **性能优先**: 使用 Ark (处理速度快)

### 2. 性能优化
- **缓存策略**
  - 使用图片描述缓存
  - 复用解析结果
  - 优化内存使用

- **并发控制**
  - 合理设置下载并发
  - 控制处理批大小
  - 避免资源竞争

### 3. 质量控制
- **输入控制**
  - 优先使用原生格式
  - 避免使用扫描版PDF
  - 保持格式一致性

- **输出验证**
  - 检查格式转换结果
  - 验证资源完整性
  - 确保结构一致性

### 4. 错误处理
- 完整的异常捕获机制
- 详细的日志记录
- 优雅的降级处理策略 