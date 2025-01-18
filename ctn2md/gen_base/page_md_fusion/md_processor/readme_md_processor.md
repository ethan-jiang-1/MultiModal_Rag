# MD Processor 设计文档

## 1. 核心设计思路

### 1.1 目录结构

#### 代码目录
```
ctn2md/gen_base/page_md_fusion/md_processor/
├── base.py               # 基础处理器
├── doc_processor.py      # 文档处理协调器
├── heading_processor.py  # 标题处理器
└── header_footer.py      # 页眉页脚处理器
```

#### 数据目录（在 MdInfo 中能获取到相关的内容）
```
{output_dir}/
├── _aux/                    # 原始分页MD文件
│   ├── page_1.md           # 第1页，包含原始标题、正文、页眉页脚
│   ├── page_2.md           # 第2页
│   └── ...
│
└── _aux_md_fusion/          # 处理结果目录
    ├── page_1.md            # 处理后的第1页（标题和页眉页脚都已处理）
    ├── page_2.md            # 处理后的第2页
    └── ...
```

#### MdInfo 关键方法
```python
class MdInfo:
    def get_aux_md_fusion_dir(self) -> str:
        """获取MD融合的工作目录"""
        
    def get_aux_dir(self) -> str:
        """获取原始分页文件目录"""
        
    def get_fnames_pages(self) -> List[str]:
        """获取所有分页文件名"""
```

### 1.2 处理原则
1. **安全性**：
   - 所有处理在 `_aux_md_fusion` 目录进行
   - 原始文件（`_aux` 目录）保持不变
   - 每个处理步骤保存中间结果

2. **行号稳定性**：
   - 标题处理优先（不改变行号）
   - 页眉页脚处理后置（会删除行）
   - 保证 LLM 分析结果中的行号准确性

3. **可追溯性**：
   - 每个处理步骤生成独立文件
   - 方便比较和调试
   - 支持处理回滚


## 2. 处理流程

### 2.1 总体流程
```
输入分页MD文件 -> LLM分析 -> 标题处理 -> 页眉页脚处理 -> 输出处理后的分页文件
```

### 2.2 详细步骤

1. **文档分析（DocumentHeadingAnalyzer）**：
   - 输入：原始分页MD文件（_aux/page_n.md）
   - 处理：LLM分析文档结构
   - 输出：DocumentAnalysisHeading对象
     * 标题信息（位置、层级、内容）
     * 页眉页脚信息
     * 结构验证结果
     * 跨页问题标记

2. **内存中处理**：
   - 标题处理：
     * 标题格式规范化
     * 标题层级调整
     * 跨页问题处理
   - 页眉页脚处理：
     * 根据分析结果删除页眉页脚

3. **结果输出**：
   - 输出：处理后的分页文件（_aux_md_fusion/page_n.md）
   - 保存：分析结果和处理日志

### 2.3 跨页处理策略
1. **断开标题处理**：
   - 识别跨页的标题片段
   - 在起始页保留完整标题
   - 在后续页删除残余部分

2. **上下文丢失处理**：
   - 识别缺失上下文的标题
   - 根据文档结构补充必要信息
   - 保持章节层级一致性

## 3. 关键数据结构

### 3.1 数据结构来源
所有核心数据结构定义在 `da_schemas_heading.py` 中，包括：
- DocumentAnalysisHeading：文档分析结果
- HeadingInfo：标题信息
- RemoveInfo：需要移除的内容
- 各种枚举类型（HeadingErrorType, HeadingValidationScope 等）

### 3.2 数据流向
1. **LLM分析阶段**：
   - 输入：原始MD文件
   - 输出：DocumentAnalysisHeading对象
   - 关键字段：headings, remove_infos, structure_validation

2. **标题处理阶段**：
   - 主要使用：HeadingInfo（位置、层级、内容）
   - 验证信息：HeadingValidation
   - 错误处理：HeadingErrorType

3. **页眉页脚处理阶段**：
   - 主要使用：RemoveInfo（位置、原因）
   - 模式识别：HeadingHeaderPattern

### 3.3 错误处理和恢复
1. **错误类型**：
   - 文件访问错误
   - 格式解析错误
   - LLM分析错误
   - 处理逻辑错误

2. **恢复机制**：
   - 保存处理检查点
   - 回滚到上一状态
   - 错误日志记录
   - 手动干预接口

## 4. 调试和验证

### 4.1 调试方法
1. 在 `_aux_md_fusion` 目录比较处理前后文件
2. 检查每个处理步骤的日志输出
3. 验证标题层级和编号的正确性

### 4.2 常见问题处理
1. **行号不准确**：
   - 确保标题处理在页眉页脚处理之前
   - 验证 LLM 分析结果中的行号

2. **跨页问题**：
   - 检查标题是否完整保留
   - 验证上下文连贯性

3. **格式不一致**：
   - 统一标题格式化规则
   - 检查特殊字符处理
