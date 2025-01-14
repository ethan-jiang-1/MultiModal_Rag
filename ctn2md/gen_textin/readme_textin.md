# TextIn Engine

基于OCR技术的文档转换引擎，专门用于处理以文本为主的PDF文档，提供可靠的文本提取和结构化能力。

## 快速导航

### 核心文件
- `_ti_img_description.py` - 图片描述生成核心
- `_ti_update_img_ref.py` - 图片引用更新和处理
- `_ti_get_image.py` - 图片下载和缓存
- `ti_pdf_pages_to_images.py` - PDF页面转换
- `gen_markdown_textin.py` - Markdown生成器

### 功能模块
- 图片处理: `_ti_*`
- PDF处理: `ti_pdf_*`
- Markdown生成: `gen_markdown_*.py`

## 系统设计

### 核心特性
1. **智能图片描述**
   ```python
   class ImageDescription(BaseModel):
       FigureName: str | None      # 图像名称
       RelevanceScore: float       # 相关性分数(0-10)
       Explanation: str            # 相关性判断依据
       PictureDescription: str     # 详细内容描述
   ```

2. **多模型支持**
   ```python
   # 支持多种模型
   mctl_ti_img_relevance_model = "qwen"  # qwen/gpt/ark
   mctl_ti_img_caption_model = "qwen"    # qwen/gpt/ark
   ```

3. **缓存优化**
   ```python
   # 智能缓存策略
   - instruction_cache  # 指令缓存
   - description_cache # 描述缓存
   - image_features    # 图像特征缓存
   ```

### 关键配置
```python
# 环境变量
load_dotenv()  # 加载.env配置

# 图片处理控制
md_info.get_md_control("mctl_ti_img_relevance_model", "qwen")  # 相关性模型
md_info.get_md_control("mctl_ti_img_caption_model", "qwen")    # 描述生成模型
```

## 核心功能

### 1. 图片描述生成
```python
from ctn2md.gen_textin._ti_img_description import get_img_alt_text_and_description

# 同步生成
alt_text, description = get_img_alt_text_and_description(
    md_info, img_url, local_path, content
)

# 异步生成
alt_text, description = await get_img_alt_text_and_description_async(
    md_info, img_url, local_path, content
)
```

### 2. 图片引用处理
- 支持Markdown和HTML格式图片
- 自动下载远程图片
- 智能重试机制
- 异步并行处理

### 3. 内容优化
- 智能图片命名
- 上下文相关描述
- 格式自动规范化

## 最佳实践

### 1. 模型选择
- qwen: 通用场景，性能均衡
- gpt: 高精度需求
- ark: 特定领域优化

### 2. 性能优化
- 使用异步API提高并发
- 启用多级缓存机制
- 智能重试和超时控制

### 3. 错误处理
```python
try:
    updater = ImageReferenceUpdater(md_info, page_index, page_md)
    image_paths = await updater.update_refs_async()
except Exception as e:
    logging.error(f"处理失败: {str(e)}")
```

### 4. 开发建议
- 使用类型注解和Pydantic模型
- 实现同步和异步接口
- 保持完整的错误日志
- 合理使用重试机制 