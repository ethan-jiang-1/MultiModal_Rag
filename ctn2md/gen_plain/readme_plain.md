# Plain Engine

基于简单复制的文档转换引擎，专门用于处理已经是 Markdown 格式的文档，提供可靠的文件复制和图片资源管理能力。

## 快速导航

### 核心文件
- `gen_markdown_plain.py` - 转换引擎实现
  - 文件复制
  - 图片处理
  - 元信息维护

### 功能模块
- 文件处理
  - 原始文件复制
  - 图片资源管理
  - JSON信息保存

## 系统设计

### 核心特性
1. **智能复制**
   ```python
   def _copy_orginal_files(md_info: MdInfo, doc_pathname: str) -> str:
       # 复制主文档
       pathname_s0_md = md_info.name_step_pathname(0)
       shutil.copy(doc_pathname, pathname_s0_md)
       
       # 复制相关JSON
       fname_final_json = MdInfo.get_fname_final_json()
       # ...
   ```

2. **图片资源管理**
   ```python
   def _copy_img_files_in_markdown(doc_pathname: str, out_dir: str) -> list:
       # 扫描图片引用
       image_refs = find_all_image_refs(doc_pathname)
       
       # 复制图片文件
       for ref_url in image_refs:
           src_path = os.path.join(src_dir, ref_url)
           dest_path = os.path.join(out_dir, ref_url)
           # ...
   ```

3. **元信息保持**
   ```python
   # 保存原始文档信息
   md_info[PUBLIC_MIFN.PATHNAME_SRC_DOC] = org_final_org_doc
   md_info[MIFN.FNAMES_IMGS] = img_refs
   ```

### 关键配置
```python
# 环境变量
load_dotenv()  # 加载.env配置

# 文件路径控制
md_info.get_doc_pathname()  # 源文档路径
md_info.get_out_dir()      # 输出目录
md_info.name_step_pathname(0)  # 步骤文件命名
```

## 核心功能

### 1. 文档复制
```python
from ctn2md.gen_plain.gen_markdown_plain import gen_markdown_plain

# 基本使用
result = gen_markdown_plain(md_info)
```

### 2. 图片处理
- 自动扫描图片引用
- 保持目录结构
- 智能路径处理

### 3. 信息维护
- 保存处理步骤
- 记录图片引用
- 维护源文件信息

## 最佳实践

### 1. 文档组织
- 使用相对路径
- 保持目录结构
- 规范图片命名

### 2. 性能优化
- 避免重复复制
- 使用高效IO
- 合理组织文件

### 3. 错误处理
```python
try:
    pathname_s0_md = _copy_orginal_files(md_info, doc_pathname)
    img_refs = _copy_img_files_in_markdown(doc_pathname, out_dir)
except Exception as e:
    logging.error(f"处理失败: {str(e)}")
```

### 4. 开发建议
- 使用类型注解
- 完整错误日志
- 保持代码简洁
- 遵循单一职责 