# Utils Module

通用工具模块，提供文件操作、Markdown处理和内容类型判断等基础功能支持。

## 功能特点

- 文件操作工具
- Markdown处理工具
- 内容类型判断
- 路径规范化

## 模块组成

```
utils/
├── util_file.py      # 文件操作工具
├── util_markdown.py  # Markdown处理工具
└── util_ctn_type.py # 内容类型工具
```

## 核心功能

### 1. 文件操作 (util_file.py)
- 路径规范化
- 目录创建和检查
- 文件移动和复制

### 2. Markdown处理 (util_markdown.py)
- 格式标准化
- 链接处理
- 图片引用处理

### 3. 内容类型 (util_ctn_type.py)
- 文件类型检测
- 类型验证
- 格式转换

## 使用方法

```python
# 1. 文件操作
from ctn2md.utils.util_file import normalize_path, ensure_dir_exists

# 路径规范化
path = normalize_path("path/to/file")

# 确保目录存在
ensure_dir_exists("path/to/dir")

# 2. Markdown处理
from ctn2md.utils.util_markdown import process_markdown

# 处理Markdown文本
processed_md = process_markdown(markdown_text)

# 3. 内容类型判断
from ctn2md.utils.util_ctn_type import CTN_TYPE

# 获取文件类型
doc_type = CTN_TYPE.get_ctn_type_by_doc_pathname("doc.pdf")

# 验证类型
is_valid = CTN_TYPE.is_valid_type(doc_type)
```

## 最佳实践

1. 文件操作：
   - 始终使用规范化路径
   - 检查目录权限
   - 处理路径异常

2. Markdown处理：
   - 保持格式一致性
   - 验证链接有效性
   - 处理特殊字符

3. 类型判断：
   - 验证文件扩展名
   - 处理未知类型
   - 使用类型常量 