# PPTX2MD Engine

基于 pptx2md 的演示文稿转换引擎，专门用于处理 PowerPoint 文档到 Markdown 的转换，提供可靠的幻灯片内容提取和格式转换能力。

## 快速导航

### 核心文件
- `gen_markdown_pptx2md.py` - 转换引擎实现
  - PowerPoint处理
  - 图片资源管理
  - 格式转换控制

### 功能模块
- 文档处理
  - 幻灯片转换
  - 图片提取
  - 格式优化

## 系统设计

### 核心特性
1. **配置管理**
   ```python
   from pptx2md import convert, ConversionConfig
   
   cfg = ConversionConfig(
       pptx_path=pptx_path,      # PPT文件路径
       output_path=out_path,     # 输出路径
       image_dir=img_dir,        # 图片目录
       disable_notes=True,       # 禁用备注
       disable_color=True,       # 禁用颜色
   )
   ```

2. **文件处理**
   ```python
   def _get_unique_doc_pathname(md_info: MdInfo) -> str:
       unique_id = md_info.get_unique_job_id()
       src_pathname = md_info.get_doc_pathname()
       src_suffix = os.path.splitext(src_pathname)[1]
       # 生成唯一文件名
       unique_doc_pathname = os.path.join(
           md_info.get_out_dir(), 
           f"{unique_id}{src_suffix}"
       )
       return unique_doc_pathname
   ```

3. **质量控制**
   ```python
   # 设置转换质量
   md_info.set_gen_engine("pptx2md")
   md_info[MIFN.FHL_QUALITY] = FHL_QUALITY_TYPE.MEDIUM
   ```

### 关键配置
```python
# 环境变量
load_dotenv()  # 加载.env配置

# 转换控制
md_info.get_doc_pathname()  # 源文档路径
md_info.get_out_dir()      # 输出目录
md_info.name_step_pathname(0)  # 步骤文件命名
```

## 核心功能

### 1. PowerPoint转换
```python
from ctn2md.gen_pptx2md.gen_markdown_pptx2md import generate_markdown_pptx2md

# 基本使用
result = generate_markdown_pptx2md(md_info)
```

### 2. 图片处理
- 自动提取幻灯片图片
- 维护图片引用关系
- 智能路径管理

### 3. 格式优化
- 保持幻灯片结构
- 优化文本格式
- 处理特殊元素

## 最佳实践

### 1. 文档准备
- 使用标准PPT格式
- 避免复杂动画
- 保持图片清晰度

### 2. 性能优化
- 合理设置图片质量
- 禁用不必要功能
- 优化文件大小

### 3. 错误处理
```python
try:
    success = gen_pages_pptx2md(md_info)
    if not success:
        logging.error("转换失败")
except Exception as e:
    logging.error(f"处理异常: {str(e)}")
```

### 4. 开发建议
- 使用类型注解
- 保持日志完整
- 遵循配置规范
- 处理所有异常 