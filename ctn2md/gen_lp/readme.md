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
controls = {
    "mctl_format_quality": "high",   # 格式质量设置
    "mctl_style_preserve": True,     # 保留原始样式
    "mctl_clean_output": True        # 输出清理
}
result = do_content2md_convert("document.pptx", mdcontrols=controls)
```

### 配置选项
- `mctl_format_quality`: 格式处理质量
- `mctl_style_preserve`: 样式保留选项
- `mctl_clean_output`: 输出清理开关
- `mctl_meta_extract`: 元数据提取级别

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

- Python 3.12+
- 内存：4GB+
- 支持的文件格式：
  - PDF
  - DOCX, PPTX
  - HTML
  - PNG, JPG
  - TXT, MD