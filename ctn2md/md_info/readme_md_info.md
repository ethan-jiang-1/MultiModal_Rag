# Markdown 信息管理模块

## 快速导航

### 关键文件索引
- 核心基类: `md_info_base.py` - 定义了 Markdown 信息的基础数据结构和操作
- 控制器: `md_info_ctrl.py` - 管理 Markdown 处理的控制参数
- 特殊页面: `md_page_spe.py` - 处理特殊页面的逻辑

### 按功能查找
- 需要管理文档信息? → 看 `md_info_base.py` 中的 `MdInfo` 类
- 处理页面位置控制? → 看 `md_process_plc.py` 中的注入函数
- 调整处理参数? → 看 `md_info_ctrl.py` 中的控制参数
- 处理特殊页面? → 看 `md_page_spe.py` 中的特殊页面逻辑

## 1. 系统设计思路

### 1.1 核心原则
- 统一管理：集中管理文档信息和处理状态
- 位置追踪：精确跟踪文档内容的位置信息
- 可扩展性：支持不同类型的文档处理器
- 错误处理：完整的错误处理和恢复机制

### 1.2 关键创新
1. **统一的信息管理**：
   - 使用 `MdInfo` 类统一管理文档信息
   - 支持信息的持久化和迁移
   - 提供版本控制和兼容性检查

2. **精确的位置控制**：
   - 使用 PLC (Position Location Control) 注释系统
   - 支持页面、行号、字符数统计
   - 维护文档的逻辑结构

## 2. 核心数据结构

### 2.1 文档信息结构
```python
class MdInfo(dict):
    """文档信息管理类"""
    def __init__(self, md_info_path_or_out_dir: str):
        # 初始化文档信息管理器
        self._md_info_path = self._get_suggested_md_info_path(md_info_path_or_out_dir)
        self._out_dir = os.path.dirname(self._md_info_path)
```


## 3. 核心功能

### 3.1 文档信息管理
1. **基础操作**：
   ```python
   md_info = MdInfo("output_dir")
   md_info.load()  # 加载信息
   md_info.save()  # 保存信息
   ```

2. **信息访问**：
   ```python
   doc_type = md_info.get_doc_type()
   ctn_type = md_info.get_ctn_type()
   doc_title = md_info.get_doc_title()
   ```
   ```

## 4. 最佳实践

### 4.1 文档处理建议
1. **初始化顺序**：
   - 先初始化 `MdInfo` 实例
   - 加载现有信息或创建新信息
   - 设置必要的控制参数

### 4.2 错误处理
1. **常见错误**：
   - 文件路径不存在
   - 版本不兼容
   - 信息格式错误

2. **处理策略**：
   - 使用 try-except 捕获异常
   - 记录详细的错误信息
   - 实现回滚机制

## 5. 开发指南

### 5.1 扩展建议
1. **添加新功能**：
   - 继承 `MdInfo` 类
   - 实现新的处理方法
   - 保持向后兼容

2. **修改现有功能**：
   - 遵循版本控制规范
   - 更新文档和测试
   - 保持接口稳定

### 5.2 测试要求
1. **单元测试**：
   - 测试基本功能
   - 测试边界条件
   - 测试错误处理

2. **集成测试**：
   - 测试与其他模块的交互
   - 测试完整的处理流程
   - 测试性能和资源使用 