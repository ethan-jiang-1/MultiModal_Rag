# LlamaParse 转换器

基于LlamaParse的通用文档转换引擎，支持多种文档格式，专注于格式兼容性和通用性。

## 账号配置

### 1. LlamaParse 账号获取
1. 访问 [LlamaIndex Cloud](https://cloud.llamaindex.ai/) 官网
2. 点击 "Sign Up" 注册账号（支持 GitHub 账号登录）
3. 登录后进入 Dashboard
4. 在 API Keys 部分获取你的 API Key

### 2. 环境配置
1. 在项目根目录创建 `.env` 文件
2. 添加以下配置：
```bash
LLAMAINDEX_API_KEY=your_api_key_here    # 替换为你的API Key
```

### 3. 使用限制
- 免费账户：
  - 每天 100 次调用 ？
  - 最大文件大小：10MB
  - 基础模型支持
- 付费账户：
  - 更多API调用次数
  - 更大文件大小限制
  - 高级模型支持
  - 优先处理队列

## 特点

### 1. 格式支持
- **多格式处理**
  - PDF文档
  - Office文档（DOCX, PPTX）
  - 网页文档（HTML）
  - 图片文件（PNG, JPG）
  - 文本文件（TXT, MD）

- **格式转换能力**
  - 统一输出标准
  - 格式保留转换
  - 样式映射处理
  - 特殊格式适配

### 2. 内容处理
- **文档结构化**
  - 自动格式识别
  - 结构重组优化
  - 内容规范化
  - 元数据提取

- **智能优化**
  - 格式一致性检查
  - 样式统一处理
  - 引用链接修复
  - 内容清理优化

## 技术实现

### 主要组件
```
gen_lp/
├── lp_gen_pages.py          # 页面生成核心
├── lp_format_process.py     # 格式处理模块
└── lp_content_optimize.py   # 内容优化模块
```

### 处理流程
1. 格式识别
2. 内容提取
3. 结构分析
4. 格式转换
5. Markdown生成
6. 格式优化

## 使用指南

### 基本用法
```python
from ctn2md.ctn2md_converter_lp import do_content2md_convert

# 基本转换
result = do_content2md_convert("document.docx")

# 使用高级配置
controls = None # 用默认设置
result = do_content2md_convert("document.pptx", mdcontrols=controls)
```

### 配置选项
- 通用配置：
  - `mctl_ge_md_async`: 异步处理开关
  - `mctl_move_aux_files`: 是否移动辅助文件
  - `mctl_treat_doc_as_ctntype`: 文档类型处理方式
  - `mctl_fix_heading_model`: 标题修复模型 (gpt/qwen/ark)
  - `mctl_summarize_model`: 摘要生成模型 (gpt/qwen/ark)

- LlamaParse专用配置：
  - 图像处理：
    - `mctl_lp_min_img_relevance_score`: 图片相关性最小分数 (0.2)
    - `mctl_lp_img_relevance_model`: 图片相关性判断模型 (gpt/qwen/ark)
    - `mctl_lp_img_caption_model`: 图片说明生成模型 (gpt/qwen/ark)
    - `mctl_lp_need_image_ref`: 是否需要图片引用 (true/false)
    - `mctl_lp_img_to_heading`: 图片到标题的映射
  
  - 文档处理：
    - `mctl_lp_langauge`: 文档语言 (zh_cn/en)
    - `mctl_lp_take_screenshot`: 是否截图 (true/false)
    - `mctl_lp_disable_ocr`: 是否禁用OCR (true/false)
    - `mctl_lp_premium_pages`: 高级模式页面列表 (页码从1开始)

### 环境变量
- `ENV_MODEL_FLOW`: 流程控制模型 (gpt/qwen/ark)
- `ENV_MODEL_GEN_LP`: LlamaParse生成模型 (gpt/qwen/ark)

## 最佳实践

### 1. 格式处理
- 根据源文档类型选择合适的配置
- 使用适当的样式保留设置
- 注意特殊格式的处理

### 2. 质量优化
- 启用高质量格式处理
- 保留必要的原始样式
- 使用输出清理功能

### 3. 常见问题
- 复杂格式转换
- 样式保留平衡
- 特殊字符处理

## 系统要求
- 支持的文件格式：
  - PDF
  - DOCX, PPTX
  - HTML
  - PNG, JPG
  - TXT, MD