# 页面融合处理模块

## 快速导航

### 关键文件索引
- 主控制器: `page_md_fusion.py` - 页面融合的主控制器
- 处理器组件:
  - `md_processor/base.py` - 处理器基类和工作空间管理
  - `md_processor/doc_structure_processor.py` - 文档结构处理协调器
  - `md_processor/heading_processor.py` - 标题处理器
  - `md_processor/header_footer.py` - 页眉页脚处理器
  - `md_processor/md_processor_explainer.py` - 处理结果说明生成器
- LLM组件:
  - `llm_heading/document_heading_analyzer.py` - 文档结构智能分析
  - `llm_heading/heading_action_explainer.py` - 处理动作详细说明
  - `llm_heading/da_schemas_heading.py` - 核心数据结构定义
  - `llm_heading/da_prompts_heading.py` - LLM提示词模板
  - `llm_heading/da_client_heading.py` - LLM服务调用封装
  - `llm_heading/full_marked_content_maker.py` - 内容标记生成

### 按功能查找
- 想了解整体流程? → 看 `page_md_fusion.py`
- 需要修改基础功能? → 看 `md_processor/base.py`
- 调整处理流程? → 看 `md_processor/doc_structure_processor.py`
- 优化标题处理? → 看 `md_processor/heading_processor.py`
- 优化页眉页脚? → 看 `md_processor/header_footer.py`
- 修改LLM分析? → 看 `llm_heading/document_heading_analyzer.py` 和 `da_prompts_heading.py`
- 调整数据结构? → 看 `llm_heading/da_schemas_heading.py`
- 查看处理结果? → 看 `md_processor/md_processor_explainer.py`

## 1. 系统设计思路

### 1.1 核心原则
- 模块化：每个处理器专注于单一职责
- 可扩展：基于BaseProcessor易于添加新处理器
- 健壮性：完整的错误处理和日志记录
- 可测试性：每个模块都有独立的测试入口
- 可解释性：提供处理结果的详细说明

### 1.2 关键特性
1. **主控制器设计**：
   ```python
   class PageMdFusion:
       def __init__(self, md_info: MdInfo, debug: bool = False):
           self.md_info = md_info
           self.debug = debug
           self.document_analyzer = DocumentHeadingAnalyzer(md_info, debug)
           self.processor = DocStructureProcessor(md_info, debug)
           
       def process(self) -> bool:
           try:
               # 1. 分析文档结构
               doc_analysis = self.document_analyzer.analyze()
               
               # 2. 处理文档
               processed_pages = self.processor.process_document(doc_analysis)
               
               # 3. 保存更新
               self.md_info.save()
               return True
           except Exception as e:
               logger.error(f"Error during fusion process: {e}")
               return False
   ```

2. **文档分析器设计**：
   ```python
   class DocumentHeadingAnalyzer:
       def analyze(self, fnames: Optional[List[str]] = None) -> DocumentAnalysisHeading:
           # 1. 准备带标记的文档内容
           marked_content, doc_pages = self.mcm.make_marked_content_from_md_info(self.md_info, fnames)
           
           # 2. 调用LLM分析
           das = self.llm_client.analyze_document(system_prompt, user_prompt)
           
           # 3. 修复heading_id格式
           self._fix_heading_ids(das)
           
           # 4. 生成分析报告
           if self.debug:
               self._generate_report(das)
           
           return das
   ```

3. **处理结果说明**：
   ```python
   class MdProcessorExplainer:
       def explain(self) -> str:
           parts = []
           
           # 1. 添加文档基本信息
           parts.append(self._format_doc_info())
           
           # 2. 格式化目录
           parts.append(self._format_toc())
           
           # 3. 总结移除的内容
           parts.append(self._summarize_removals())
           
           return "\n".join(parts)
   ```

## 2. 目录结构

```
page_md_fusion/
├── page_md_fusion.py      # 主控制器
├── md_processor/          # 处理器组件
│   ├── base.py           # 处理器基类
│   ├── doc_structure_processor.py  # 处理协调器
│   ├── heading_processor.py        # 标题处理器
│   ├── header_footer.py           # 页眉页脚处理器
│   └── md_processor_explainer.py  # 结果说明生成器
└── llm_heading/          # LLM分析组件
    ├── document_heading_analyzer.py
    ├── heading_action_explainer.py
    ├── da_schemas_heading.py
    ├── da_prompts_heading.py
    ├── da_client_heading.py
    └── full_marked_content_maker.py
```

## 3. 核心组件

### 3.1 主控制器 (page_md_fusion.py)
- 协调整体处理流程
- 初始化文档分析器和处理器
- 错误处理和日志记录
- 调试模式支持

### 3.2 处理器组件
- **文档结构处理器** (`doc_structure_processor.py`):
  - 协调各个处理器的执行
  - 维护处理状态
  - 生成处理结果说明

- **标题处理器** (`heading_processor.py`):
  - 标题格式规范化
  - 标题层级调整
  - 跨页问题处理

- **页眉页脚处理器** (`header_footer.py`):
  - 页眉页脚识别和清理
  - 分隔符处理
  - 保持文档结构完整性

- **结果说明生成器** (`md_processor_explainer.py`):
  - 生成文档结构说明
  - 展示处理前后的变化
  - 提供处理统计信息

### 3.3 LLM分析组件
- **文档分析器** (`document_heading_analyzer.py`):
  - 分析文档结构
  - 生成处理指令
  - 提供调试信息

- **内容标记生成器** (`full_marked_content_maker.py`):
  - 生成带标记的文档内容
  - 保持页面和行号信息
  - 支持跨页分析

- **LLM客户端** (`da_client_heading.py`):
  - 处理LLM调用
  - 缓存管理
  - 错误处理

## 4. 使用示例

### 4.1 基本使用
```python
from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.page_md_fusion.page_md_fusion import PageMdFusion

# 初始化
md_info = MdInfo.from_json(json_path)
fusion = PageMdFusion(md_info, debug=True)

# 执行处理
success = fusion.process()
```

### 4.2 调试模式
```python
# 启用调试模式
fusion = PageMdFusion(md_info, debug=True)
success = fusion.process()

# 查看处理结果说明
from ctn2md.gen_base.page_md_fusion.md_processor.md_processor_explainer import MdProcessorExplainer
explainer = MdProcessorExplainer(pages_content, doc_analysis)
print(explainer.explain())
```

## 5. 最佳实践

### 5.1 开发建议
- 使用 `load_dotenv()` 确保环境初始化
- 保持处理器的单一职责
- 完整的错误处理和日志记录
- 添加独立的测试入口
- 使用调试模式进行开发

### 5.2 调试技巧
- 使用 `__main__` 块测试
- 检查处理日志输出
- 验证中间处理结果
- 使用 `MdProcessorExplainer` 查看结果
- 利用 `rich` 打印调试信息
