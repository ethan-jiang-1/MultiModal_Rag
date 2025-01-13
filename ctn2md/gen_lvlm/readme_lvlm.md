# LVLM Engine

基于大规模视觉语言模型的文档转换引擎，专门用于处理复杂排版和图文混排的PDF文档。

## 功能特点

- 智能区域检测 (gs0/gs1/gs2)
- 图文关系理解
- 布局结构重建
- 高质量图片说明生成

## 模块组成

```
gen_lvlm/
├── lvlm_base.py           # 基础类和接口定义
├── lvlm_pdf_pages_to_images.py  # PDF页面转图片
├── lvlm_gen_pages.py      # 页面生成逻辑
├── gen_markdown_lvml.py   # Markdown生成器
├── non_text_detector_gs*/ # 非文本区域检测器(gs0/gs1/gs2)
└── image2mds/            # 图片到Markdown转换
```

## 核心功能

### 1. 页面预处理
- PDF页面转换为高质量图片
- 智能页面分割
- 区域类型识别

### 2. 内容理解
- 非文本区域智能检测
- 图片内容理解
- 布局结构分析

### 3. Markdown生成
- 智能布局重建
- 图文关系保持
- 格式优化

## 使用方法

```python
from ctn2md.converters.converter_pdf_lvlm import do_content2md_convert

# 基本使用
result = do_content2md_convert("your_doc.pdf")

```

## 最佳实践

1. 区域检测模型选择：
   - gs0: 基础检测，适合简单布局
   - gs1: 标准检测，适合一般文档 
   - gs2: 高级检测，适合复杂排版

2. 性能优化：
   - 合理设置区域比例参数
   - 使用异步处理提高效率
   - 启用缓存减少重复处理

3. 质量控制：
   - 定期更新模型
   - 监控转换质量
   - 保持图文一致性 