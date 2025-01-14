# LVLM Engine

基于大规模视觉语言模型的文档转换引擎，专门用于处理复杂排版和图文混排的PDF文档。

## 快速导航

### 核心文件
- `lvlm_base.py` - 基础类型定义和图像内容分类
- `lvlm_pdf_pages_to_images.py` - PDF页面转换和区域检测核心实现
- `lvlm_gen_pages.py` - 页面生成和处理流程控制
- `gen_markdown_lvml.py` - Markdown生成和格式化

### 功能模块
- 非文本检测器: `non_text_detector_gs[0-2]/`
- 图像处理: `image2mds/`

## 系统设计

### 核心特性
1. **智能区域检测**
   ```python
   # 支持三种检测模式
   mctl_lvlm_region_detect = "gs0"  # 基础模式
   mctl_lvlm_region_detect = "gs1"  # 标准模式
   mctl_lvlm_region_detect = "gs2"  # 高级模式
   ```

2. **内容类型识别**
   ```python
   # 支持的内容类型
   LVLM_IMG_CNT_TYPE = {
       "GRAPH",   # 图表
       "IMAGE",   # 图片
       "TABLE",   # 表格
       "LIST",    # 列表
       "TEXT",    # 文本
       "IGNORE",  # 忽略
       "UNKNOWN"  # 未知
   }
   ```

3. **图像质量控制**
   ```python
   # 图像输出配置
   IMG_EXT = "jpg"      # 输出格式
   JPG_QUALITY = 90     # JPEG质量
   ```

### 关键配置
```python
# 环境变量
load_dotenv()  # 加载.env配置

# 区域检测控制
md_info.get_md_control("mctl_lvlm_region_detect", "gs0")  # 检测模式
md_info.get_md_control("mctl_lvlm_images_ignore", "")     # 忽略图片列表
```

## 核心功能

### 1. PDF预处理
```python
from ctn2md.gen_lvlm.lvlm_pdf_pages_to_images import parse_pdf_to_images

# 转换指定页面
image_infos = parse_pdf_to_images(
    md_info,
    sel_page_indexes=[1,2],  # 可选，指定页面
    mctl_lvlm_region_detect="gs2"  # 可选，检测模式
)
```

### 2. 区域检测
- 支持多级检测策略(gs0/gs1/gs2)
- 自动识别文档类型(PDF/PPT)
- 智能区域分割和标注

### 3. 内容生成
- 保持原始布局结构
- 智能图文关系重建
- 格式化输出控制

## 最佳实践

### 1. 检测模式选择
- gs0: 适用于简单文档，速度快
- gs1: 适用于一般文档，平衡性能
- gs2: 适用于复杂排版，精度高

### 2. 性能优化
- 使用JPG格式，质量90
- 按需选择页面处理
- 支持增量更新模式

### 3. 错误处理
```python
try:
    image_infos = parse_pdf_to_images(md_info)
except Exception as e:
    logging.error(f"处理失败: {str(e)}")
```

### 4. 开发建议
- 遵循类型注解规范
- 使用异步处理提高效率
- 保持错误日志完整性 