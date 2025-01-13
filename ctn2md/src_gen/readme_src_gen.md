# Source Generator Module

生成器适配层，负责连接核心功能和各种生成引擎，提供统一的生成接口和适配逻辑。

## 功能特点

- 统一生成接口
- 引擎适配层
- 生成流程控制
- 结果标准化

## 模块组成

```
src_gen/
├── _ctn2md_gen_md_base.py         # 生成器基类
├── ctn2md_gen_md_lvlm.py          # LVLM生成器适配
├── ctn2md_gen_md_textin.py        # TextIn生成器适配
├── ctn2md_gen_md_llamaparse.py    # LlamaParse生成器适配
├── ctn2md_gen_md_markitdown.py    # Markitdown生成器适配
├── ctn2md_gen_md_plain.py         # Plain生成器适配
└── ctn2md_gen_md_pptx2md.py      # PPTX生成器适配
```

## 核心功能

### 1. 基础框架
- 统一接口定义
- 生命周期管理
- 错误处理机制

### 2. 引擎适配
- 参数转换
- 结果适配
- 状态同步

### 3. 流程控制
- 生成过程管理
- 资源控制
- 结果验证

## 使用方法

```python
# 1. 使用基类创建新生成器
from ctn2md.src_gen._ctn2md_gen_md_base import GenMd_Base

class MyGenerator(GenMd_Base):
    def generate_markdown(self, doc_pathname, out_dir=None):
        # 实现生成逻辑
        pass

# 2. 使用LVLM生成器
from ctn2md.src_gen.ctn2md_gen_md_lvlm import GenMd_Lvlm
generator = GenMd_Lvlm()
result = generator.generate_markdown("doc.pdf", "output_dir")

# 3. 使用TextIn生成器
from ctn2md.src_gen.ctn2md_gen_md_textin import GenMd_TextIn
generator = GenMd_TextIn()
result = generator.generate_markdown("doc.pdf", "output_dir")

# 4. 使用LlamaParse生成器
from ctn2md.src_gen.ctn2md_gen_md_llamaparse import GenMd_LlamaParse
generator = GenMd_LlamaParse()
result = generator.generate_markdown("doc.*", "output_dir")
```

## 最佳实践

1. 生成器开发：
   - 继承基类实现
   - 遵循接口规范
   - 处理异常情况

2. 引擎适配：
   - 参数正确映射
   - 结果格式转换
   - 保持状态同步

3. 性能优化：
   - 资源合理分配
   - 缓存中间结果
   - 并发处理控制 