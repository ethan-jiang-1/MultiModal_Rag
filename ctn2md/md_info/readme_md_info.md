# Markdown 信息管理模块

## 快速导航

### 关键文件索引
- `md_info_base.py` - Markdown 信息基础类，提供统一的信息管理接口
- `md_info_ctrl.py` - 控制参数管理，定义处理流程的配置项

### 按功能查找
- 需要创建/加载文档信息？ → `MdInfo` 类的 `__init__` 和 `load` 方法
- 想保存处理状态？ → `MdInfo` 类的 `save` 方法
- 要调整处理参数？ → `md_info_ctrl.py` 中的 `get_default_md_control`
- 需要版本迁移？ → `MdInfo` 类的 `_migrate` 方法

## 1. 核心功能

### 1.1 文档信息管理
```python
from ctn2md.md_info.md_info_base import MdInfo

# 创建文档信息管理器
md_info = MdInfo("output_dir")

# 加载已有信息
md_info.load()

# 保存当前状态
md_info.save()
```

### 1.2 控制参数管理
```python
from ctn2md.md_info.md_info_ctrl import get_default_md_control

# 获取默认控制参数
ctrl_params = get_default_md_control()

# 主要参数组
general_controls = {
    "version": "0.11.2",
    "mctl_move_aux_files": True,
    "mctl_treat_doc_as_ctntype": "auto",
    "mctl_ge_md_async": False
}
```

## 2. 关键数据结构

### 2.1 文档信息字段
```python
class PUBLIC_MIFN:
    VERSION = "version"                    # 版本信息
    GEN_ENGINE = "parse_engine"           # 解析引擎
    PATHNAME_ORG_DOC = "pathname_org_doc" # 原始文档路径
    DOC_UNIQUE_ID = "doc_unique_id"       # 文档唯一ID
    DOC_CTN_TYPE = "doc_content_type"     # 文档内容类型
    DOC_NAME_TITLE = "doc_title_name"     # 文档标题名称
```

### 2.2 控制参数结构
```python
class DefaultModelSource:
    @classmethod
    def get_flow_fix_heading_model(cls) -> str:
        return os.getenv(ENV_MODEL_FLOW, "qwen")
    
    @classmethod
    def get_flow_summarize_model(cls) -> str:
        return os.getenv(ENV_MODEL_FLOW, "qwen")
```

## 3. 使用指南

### 3.1 基本流程
1. **初始化**
   ```python
   md_info = MdInfo("output_dir")
   md_info.load()  # 如果存在则加载
   ```

2. **配置参数**
   ```python
   ctrl_params = get_default_md_control()
   md_info.update(ctrl_params)
   ```

3. **保存状态**
   ```python
   md_info.save()
   ```

### 3.2 环境变量
- `ENV_MODEL_FLOW`: 流程模式使用的模型
- `ENV_MODEL_GEN_LP`: LlamaParse模式使用的模型
- `ENV_MODEL_GEN_LVLM`: LVLM模式使用的模型
- `ENV_MODEL_GEN_TI`: TextIn模式使用的模型

## 4. 最佳实践

### 4.1 版本管理
- 使用 `_MIB_INFO_VER` 跟踪版本
- 通过 `_migrate` 方法处理版本迁移
- 保持向后兼容性

### 4.2 错误处理
```python
try:
    md_info = MdInfo(output_dir)
    md_info.load()
except ValueError as e:
    logging.error(f"初始化失败: {e}")
except FileNotFoundError:
    logging.error("文件不存在")
```

## 5. 开发建议

### 5.1 新功能开发
1. **遵循基本原则**
   - 所有修改必须向后兼容
   - 新功能需要添加迁移支持
   - 保持接口的一致性

2. **代码规范**
   - 使用类型注解
   - 添加详细注释
   - 遵循 PEP 8 规范

### 5.2 测试要求
1. **单元测试**
   - 测试所有公共方法
   - 验证错误处理
   - 检查版本迁移

2. **集成测试**
   - 测试与其他模块的交互
   - 验证配置参数的影响
   - 检查性能和资源使用 