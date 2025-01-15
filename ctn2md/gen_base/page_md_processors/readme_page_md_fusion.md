# 页面融合处理模块

## 快速导航

### 关键文件索引
- 基础组件: `base.py` - 处理器基类和工作空间管理
- 总入口: `doc_processor.py` - 文档处理流程协调
- 页眉页脚: `header_footer.py` - 页眉页脚清理处理
- 表格处理: `table_processor.py` - 跨页表格合并处理
- LLM分析: `llm/document_analyzer.py` - 文档结构智能分析
- 动作解释: `llm/action_explainer.py` - 处理动作详细说明
- 数据模型: `llm/da_schemas.py` - 核心数据结构定义
- 提示词管理: `llm/da_prompts.py` - LLM提示词模板
- LLM客户端: `llm/da_client.py` - LLM服务调用封装

### 按功能查找
- 想了解整体流程? → 看 `doc_processor.py`
- 需要修改基础功能? → 看 `base.py`
- 调整页眉页脚处理? → 看 `header_footer.py`
- 优化表格合并? → 看 `table_processor.py`
- 修改LLM分析? → 看 `llm/document_analyzer.py` 和 `da_prompts.py`
- 调整数据结构? → 看 `llm/da_schemas.py`

## 1. 系统设计思路

### 1.1 核心原则
- 模块化：每个处理器专注于单一职责
- 可扩展：基于BaseProcessor易于添加新处理器
- 健壮性：完整的错误处理和日志记录
- 可测试性：每个模块都有独立的测试入口

### 1.2 关键特性
1. **统一的处理器接口**：
   ```python
   class BaseProcessor:
       def __init__(self, md_info: MdInfo):
           self.md_info = md_info
           
       def process(self, pages: List[List[str]], actions: Dict) -> List[List[str]]:
           raise NotImplementedError
   ```

2. **工作空间管理**：
   ```python
   def prepare_md_fusion_workspace(md_info: MdInfo) -> List[str]:
       workspace_dir = md_info.get_aux_md_fusion_dir()
       os.makedirs(workspace_dir, exist_ok=True)
       # 复制文件到工作空间...
       return workspace_files
   ```

3. **智能的表格处理**：
   ```python
   class TableProcessor(BaseProcessor):
       def process(self, pages: List[List[str]], actions: Dict) -> List[List[str]]:
           # 处理跨页表格
           for action in actions["merge_actions"]:
               if action["type"] == "table" and self._is_cross_page_table(action):
                   processed_pages = self._merge_table(processed_pages, action)
   ```

## 2. 核心组件

### 2.1 处理器基类 (base.py)
- 提供统一的处理器接口
- 工作空间管理功能
- 文件读写工具函数

### 2.2 文档处理协调器 (doc_processor.py)
- 初始化和协调各个处理器
- 按顺序执行处理流程
- 维护处理状态

### 2.3 页眉页脚处理器 (header_footer.py)
- 基于LLM分析结果执行清理
- 支持多种页眉页脚模式
- 保持文档结构完整性

### 2.4 表格处理器 (table_processor.py)
- 智能识别跨页表格
- 验证表格连续性
- 合并保持结构完整

## 3. LLM分析组件

### 3.1 文档分析器 (document_analyzer.py)
- 调用LLM分析文档结构
- 生成处理动作指令
- 提供分析结果解释

### 3.2 动作解释器 (action_explainer.py)
- 详细解释处理动作
- 提供处理建议
- 辅助调试分析

### 3.3 数据模型 (da_schemas.py)
```python
class TableRange(BaseModel):
    start: int
    end: int
    is_header: bool = False
    has_separator: bool = False
```

## 4. 使用示例

### 4.1 基本使用
```python
from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_processors.doc_processor import DocProcessor

# 初始化
md_info = MdInfo(json_path)
processor = DocProcessor(md_info)

# 处理文档
processed_pages = processor.process_document(pages)
```

### 4.2 自定义处理器
```python
from ctn2md.gen_base.page_md_processors.base import BaseProcessor

class CustomProcessor(BaseProcessor):
    def process(self, pages: List[List[str]], actions: Dict) -> List[List[str]]:
        # 实现自定义处理逻辑
        return processed_pages
```

## 5. 最佳实践

### 5.1 开发建议
- 使用 `load_env()` 确保环境初始化
- 保持处理器的单一职责
- 完整的错误处理和日志记录
- 添加独立的测试入口

### 5.2 调试技巧
- 使用 `__main__` 块测试
- 检查处理日志输出
- 验证中间处理结果
- 使用 rich 打印调试信息
