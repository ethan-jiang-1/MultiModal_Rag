# 页面融合处理模块

## 快速导航

### 关键文件索引
- 总入口: `page_md_fusion.py` - 页面融合功能的主入口
- 文档分析: `page_md_processors/llm/document_analyzer.py` - LLM文档结构分析
- 处理协调: `page_md_processors/doc_processor.py` - 处理流程协调
- 页眉页脚: `page_md_processors/header_footer.py` - 页眉页脚处理
- 表格处理: `page_md_processors/table_processor.py` - 跨页表格处理
- 数据模型: `page_md_processors/llm/schemas.py` - 核心数据结构定义

### 按功能查找
- 想了解整体流程? → 看 `page_md_fusion.py`
- 需要修改LLM分析? → 看 `llm/document_analyzer.py` 和 `llm/prompts.py`
- 调整处理逻辑? → 看 `doc_processor.py`
- 页眉页脚处理? → 看 `header_footer.py`
- 表格合并处理? → 看 `table_processor.py`
- 修改数据结构? → 看 `llm/schemas.py`

## 1. 系统设计思路

### 1.1 核心原则
- 健壮性：不依赖精确行号，使用特征模式识别
- 可靠性：完整的验证和错误处理机制
- 可维护性：清晰的模块划分和状态管理
- 可扩展性：支持新的处理器和验证规则
- 可调试性：每个模块尤其是有 __main__ 的模块，必须：
  - 需要 load_env() 
  - 所有其他模块引用都是全路径，从项目根目录开始， 在load_env() 之后， 因为load_env() 会设置环境变量， 这些环境变量会影响其他模块的初始化 
  - 所有的调整都是从根目录开始，不用进入子目录。

### 1.2 关键创新
1. **特征识别替代位置依赖**：
   - 使用内容特征和上下文定位
   - 支持模糊匹配和相似度计算
   - 降低对LLM精确输出的依赖

2. **完整的文档结构分析**：
   - 维护文档的逻辑结构
   - 处理复杂的跨页关系
   - 保持层级和格式的一致性

3. **健壮的处理流程**：
   - 预检和后处理机制
   - 细粒度的错误处理
   - 支持处理回滚

## 2. 核心数据结构

### 2.1 内容定位与识别
```python
class ContentIdentifier(BaseModel):
    """内容标识器 - 替代简单的行号定位"""
    content_pattern: str      # 内容特征模式
    surrounding_text: str     # 周围文本
    relative_position: str    # 相对位置描述
    confidence_rules: Dict    # 置信度规则
```

### 2.2 文档结构表示
```python
class DocumentStructure(BaseModel):
    """文档结构 - 维护整体逻辑关系"""
    logical_blocks: List[Block]    # 逻辑块
    block_relations: Dict          # 块间关系
    continuity_markers: List       # 连续性标记
    format_standards: Dict         # 格式标准
```

### 2.3 处理流水线
```python
class ProcessingPipeline(BaseModel):
    """处理流水线 - 确保处理可靠性"""
    pre_checks: List[Check]        # 预检
    processing_steps: List[Step]   # 处理步骤
    recovery_points: List[Point]   # 恢复点
    validation_rules: Dict         # 验证规则
```

### 2.4 错误处理
```python
class ErrorHandling(BaseModel):
    """错误处理 - 保证系统稳定性"""
    error_types: Dict[str, Handler]  # 错误处理器
    recovery_strategies: Dict        # 恢复策略
    error_reporting: Reporter        # 错误报告
```

## 3. 处理流程详解

### 3.1 预处理阶段
1. **文档分析**：
   - 识别文档类型和结构
   - 建立逻辑块索引
   - 确定处理策略

2. **特征提取**：
   - 提取内容特征
   - 建立上下文关系
   - 生成特征索引

### 3.2 处理阶段
1. **页眉页脚处理**：
   - 基于特征识别而非位置
   - 使用相似度确认
   - 保留处理历史

2. **表格处理**：
   - 识别表格结构
   - 处理跨页关系
   - 维护表格完整性

3. **格式处理**：
   - 统一格式标准
   - 保持层级关系
   - 验证格式一致性

### 3.3 后处理阶段
1. **完整性检查**：
   - 验证结构完整性
   - 检查跨页关系
   - 确认格式一致性

2. **错误修正**：
   - 自动修正常见错误
   - 提供修正建议
   - 记录修正历史

## 4. 验证机制

### 4.1 预检验证
```python
class PreCheck(BaseModel):
    """预检验证"""
    structure_checks: List[Check]  # 结构检查
    content_checks: List[Check]    # 内容检查
    format_checks: List[Check]     # 格式检查
```

### 4.2 处理验证
```python
class ProcessingValidation(BaseModel):
    """处理验证"""
    step_validation: Dict[str, Validator]  # 步骤验证器
    state_validation: StateValidator       # 状态验证
    consistency_checks: List[Check]        # 一致性检查
```

### 4.3 结果验证
```python
class ResultValidation(BaseModel):
    """结果验证"""
    completeness_check: Check      # 完整性检查
    consistency_check: Check       # 一致性检查
    quality_metrics: Dict          # 质量指标
```

## 5. 错误处理机制

### 5.1 错误分类
1. **结构错误**：
   - 不完整的表格
   - 断开的段落
   - 错误的层级关系

2. **内容错误**：
   - 误删内容
   - 重复内容
   - 格式混乱

3. **处理错误**：
   - 处理超时
   - 资源不足
   - 状态不一致

### 5.2 恢复策略
1. **自动恢复**：
   - 使用恢复点
   - 重试处理
   - 降级处理

2. **手动干预**：
   - 提供错误报告
   - 建议修正方案
   - 记录处理历史

## 6. 扩展性设计

### 6.1 处理器扩展
```python
class ProcessorExtension(BaseModel):
    """处理器扩展"""
    processor_type: str           # 处理器类型
    validation_rules: Dict        # 验证规则
    error_handlers: Dict          # 错误处理器
```

### 6.2 规则扩展
```python
class RuleExtension(BaseModel):
    """规则扩展"""
    rule_type: str               # 规则类型
    rule_definition: Dict        # 规则定义
    validation_method: Callable  # 验证方法
```

## 7. 监控和反馈

### 7.1 处理监控
```python
class ProcessingMonitor(BaseModel):
    """处理监控"""
    performance_metrics: Dict    # 性能指标
    resource_usage: Dict        # 资源使用
    error_statistics: Dict      # 错误统计
```

### 7.2 质量反馈
```python
class QualityFeedback(BaseModel):
    """质量反馈"""
    quality_metrics: Dict       # 质量指标
    improvement_suggestions: List # 改进建议
    historical_comparison: Dict  # 历史对比
```

## 8. 最佳实践

### 8.1 开发建议
1. **特征定义**：
   - 使用明确的特征模式
   - 包含足够的上下文
   - 考虑边界情况

2. **错误处理**：
   - 实现细粒度的错误捕获
   - 提供清晰的错误信息
   - 保持处理的可回滚性

3. **验证规则**：
   - 定义完整的验证链
   - 实现多层次的检查
   - 保持验证的独立性

### 8.2 调试技巧
1. **日志记录**：
   - 记录关键处理步骤
   - 保存中间状态
   - 追踪错误链

2. **状态检查**：
   - 验证状态一致性
   - 检查资源使用
   - 监控处理性能

这种设计确保了：
1. 系统的健壮性和可靠性
2. 处理结果的可预测性
3. 错误的可控性和可恢复性
4. 系统的可维护性和可扩展性
