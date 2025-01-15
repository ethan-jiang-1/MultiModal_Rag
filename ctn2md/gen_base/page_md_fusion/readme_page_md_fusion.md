# 页面融合处理模块

## 快速导航

### 关键文件索引
- 主控制器: `page_md_fusion.py` - 页面融合的主控制器
- 处理器组件:
  - `processor/base.py` - 处理器基类和工作空间管理
  - `processor/doc_processor.py` - 文档处理流程协调
  - `processor/header_footer.py` - 页眉页脚清理处理
  - `processor/table_processor.py` - 跨页表格合并处理
- LLM组件:
  - `llm/document_analyzer.py` - 文档结构智能分析
  - `llm/action_explainer.py` - 处理动作详细说明
  - `llm/da_schemas.py` - 核心数据结构定义
  - `llm/da_prompts.py` - LLM提示词模板
  - `llm/da_client.py` - LLM服务调用封装
  - `llm/marked_content_maker.py` - 内容标记生成

### 按功能查找
- 想了解整体流程? → 看 `page_md_fusion.py`
- 需要修改基础功能? → 看 `processor/base.py`
- 调整处理流程? → 看 `processor/doc_processor.py`
- 优化页眉页脚? → 看 `processor/header_footer.py`
- 优化表格合并? → 看 `processor/table_processor.py`
- 修改LLM分析? → 看 `llm/document_analyzer.py` 和 `da_prompts.py`
- 调整数据结构? → 看 `llm/da_schemas.py`

## 1. 系统设计思路

### 1.1 核心原则
- 模块化：每个处理器专注于单一职责
- 可扩展：基于BaseProcessor易于添加新处理器
- 健壮性：完整的错误处理和日志记录
- 可测试性：每个模块都有独立的测试入口

### 1.2 关键特性
1. **主控制器设计**：
   ```python
   class PageMdFusion:
       def __init__(self, md_info: MdInfo):
           self.md_info = md_info
           self.processor = DocProcessor(md_info)
           
       def process(self) -> bool:
           try:
               # 1. 准备工作空间
               pages = prepare_md_fusion_workspace(self.md_info)
               # 2. 处理文档
               _ = self.processor.process_document(pages)
               # 3. 保存更新
               self.md_info.save()
               return True
           except Exception as e:
               logger.error(f"Error during fusion process: {e}")
               return False
   ```

2. **统一的处理器接口**：
   ```python
   class BaseProcessor:
       def __init__(self, md_info: MdInfo):
           self.md_info = md_info
           
       def process(self, pages: List[List[str]], actions: Dict) -> List[List[str]]:
           raise NotImplementedError
   ```

3. **智能的表格处理**：
   ```python
   class TableProcessor(BaseProcessor):
       def process(self, pages: List[List[str]], actions: Dict) -> List[List[str]]:
           if not actions.get("merge_actions"):
               return pages
           
           for action in actions["merge_actions"]:
               if action["type"] == "table" and self._is_cross_page_table(action):
                   processed_pages = self._merge_table(processed_pages, action)
           return processed_pages
   ```

## 2. 目录结构

```
page_md_fusion/
├── page_md_fusion.py      # 主控制器
├── processor/             # 处理器组件
│   ├── base.py           # 处理器基类
│   ├── doc_processor.py  # 处理协调器
│   ├── header_footer.py  # 页眉页脚处理
│   └── table_processor.py # 表格处理
└── llm/                  # LLM分析组件
    ├── document_analyzer.py
    ├── action_explainer.py
    ├── da_schemas.py
    ├── da_prompts.py
    ├── da_client.py
    └── marked_content_maker.py
```

## 3. 核心组件

### 3.1 主控制器 (page_md_fusion.py)
- 协调整体处理流程
- 工作空间管理
- 结果保存和错误处理

### 3.2 处理器组件
- **基础处理器** (`processor/base.py`):
  - 提供统一的处理器接口
  - 工作空间管理功能
  - 文件读写工具函数

- **处理协调器** (`processor/doc_processor.py`):
  - 初始化和协调各个处理器
  - 按顺序执行处理流程
  - 维护处理状态

- **专用处理器**:
  - 页眉页脚处理器：清理页眉页脚
  - 表格处理器：处理跨页表格

### 3.3 LLM分析组件
- **文档分析器**：分析文档结构，生成处理指令
- **动作解释器**：解释处理动作，提供建议
- **内容标记生成器**：生成内容标记

## 4. 使用示例

### 4.1 基本使用
```python
from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.page_md_fusion import PageMdFusion

# 初始化
md_info = MdInfo.from_json(json_path)
fusion = PageMdFusion(md_info)

# 执行处理
success = fusion.process()
```

### 4.2 自定义处理器
```python
from ctn2md.gen_base.page_md_fusion.processor.base import BaseProcessor

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
