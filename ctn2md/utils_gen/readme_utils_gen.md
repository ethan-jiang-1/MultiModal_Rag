# Generator Utils Module

生成器工具模块，提供通用的生成功能支持，包括模板处理、格式转换和生成控制等。

## 功能特点

- 模板管理
- 格式转换
- 生成控制
- 结果验证

## 模块组成

```
utils_gen/
├── gen_base.py        # 生成器基础功能
├── gen_template.py    # 模板处理工具
├── gen_format.py      # 格式转换工具
├── gen_control.py     # 生成控制工具
└── gen_validate.py    # 结果验证工具
```

## 核心功能

### 1. 模板处理
- 模板加载
- 变量替换
- 格式检查

### 2. 格式转换
- 数据格式化
- 类型转换
- 编码处理

### 3. 生成控制
- 流程管理
- 资源控制
- 错误处理

## 使用方法

```python
# 1. 模板处理
from ctn2md.utils_gen.gen_template import Template

# 加载和使用模板
template = Template.load("template.md")
result = template.render({"title": "Document", "content": "..."})

# 2. 格式转换
from ctn2md.utils_gen.gen_format import Format

# 转换格式
formatted = Format.convert(data, target_format="markdown")

# 3. 生成控制
from ctn2md.utils_gen.gen_control import Generator

# 控制生成过程
generator = Generator()
result = generator.generate(data, controls={"max_length": 1000})
```

## 最佳实践

1. 模板使用：
   - 维护模板版本
   - 验证模板有效性
   - 处理特殊字符

2. 格式处理：
   - 检查数据类型
   - 处理边界情况
   - 保持格式一致

3. 生成控制：
   - 设置合理限制
   - 监控资源使用
   - 记录生成日志 