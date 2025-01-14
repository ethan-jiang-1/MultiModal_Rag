# MarkItDown Engine

基于 Mammoth 和 MarkItDown 的文档转换引擎，专门用于处理 Office 文档（Word、Excel）到 Markdown 的转换，提供高质量的格式保持和结构化输出。

## 快速导航

### 核心文件
- `gen_markdown_markitdown.py` - 转换引擎入口
- `doc2md/mammoth_transform.py` - Word文档转换核心
- `doc2md/mammoth_style_map.py` - 样式映射定义
- `xls2md/_gen_md_from_xls.py` - Excel转换实现

### 功能模块
- Word处理: `doc2md/`
  - 样式转换
  - 图片导出
  - 格式映射
- Excel处理: `xls2md/`
  - 表格转换
  - 格式保持

## 系统设计

### 核心特性
1. **多格式支持**
   ```python
   # 支持的文档类型
   CTN_TYPE = {
       "DOC",    # Word文档
       "XLS",    # Excel表格
   }
   ```

2. **智能样式映射**
   ```python
   # Word样式映射示例
   style_map = [
       "p[style-name='Heading 1'] => h1:fresh",
       "p[style-name='Heading 2'] => h2:fresh",
       "p[style-name='Quote'] => blockquote:fresh",
   ]
   ```

3. **图片处理**
   ```python
   # 图片导出配置
   ImageExporter.set_output_dir(
       output_dir,    # 输出目录
       unique_job_id  # 任务ID
   )
   ```

### 关键配置
```python
# 环境变量
load_dotenv()  # 加载.env配置

# 文档处理控制
md_info.set_gen_engine("markitdown")           # 设置引擎
md_info[MIFN.FHL_QUALITY] = FHL_QUALITY_TYPE.MEDIUM  # 设置质量
```

## 核心功能

### 1. Word文档转换
```python
from ctn2md.gen_markitdown.doc2md._gen_md_from_doc import gen_md_from_doc

# 转换Word文档
result = gen_md_from_doc(md_info)
```

### 2. Excel转换
```python
from ctn2md.gen_markitdown.xls2md._gen_md_from_xls import gen_md_from_xls

# 转换Excel文件
result = gen_md_from_xls(md_info)
```

### 3. 格式优化
- 保持原始样式
- 智能表格处理
- 图片引用维护

## 最佳实践

### 1. Word文档处理
- 使用标准样式
- 避免复杂嵌套
- 保持图片清晰度

### 2. Excel处理
- 使用规范表格
- 避免合并单元格
- 保持数据格式

### 3. 错误处理
```python
try:
    result = generate_markdown_markitdown(md_info)
except Exception as e:
    logging.error(f"转换失败: {str(e)}")
```

### 4. 开发建议
- 遵循类型注解规范
- 使用日志追踪
- 保持代码模块化
- 实现错误重试机制 