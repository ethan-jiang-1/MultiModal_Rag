# 图片引用扫描与更新模块

## 快速导航

### 关键文件索引
- 总入口: `scan_img_ref_and_update.py` - 图片引用扫描和更新的主入口
- 扫描器: `ir_scanner.py` - 图片引用扫描和上下文提取
- 更新器: `ir_img_ref_updater.py` - 图片引用格式更新
- 描述生成: `ir_description_generator.py` - 智能图片描述生成
- 数据模型: `ir_models.py` - 图片引用数据结构定义

### 按功能查找
- 想了解整体流程? → 看 `scan_img_ref_and_update.py`
- 需要修改扫描逻辑? → 看 `ir_scanner.py`
- 调整更新规则? → 看 `ir_img_ref_updater.py`
- 优化描述生成? → 看 `ir_description_generator.py`
- 修改数据结构? → 看 `ir_models.py`

## 1. 设计思路

### 1.1 核心原则
- 完整性：扫描文档中所有的图片引用
- 上下文感知：提取图片前后200字符作为上下文
- 智能描述：使用LLM生成准确的figure_name和description
- 相关性评分：计算描述与上下文的相关性得分

### 1.2 关键特性
1. **统一的图片引用模型**：
   ```python
   @dataclass
   class ImageReference:
       ref_name: str            # 图片引用名称
       position: int            # 在文档中的位置
       context_before: str      # 图片前的上下文
       context_after: str       # 图片后的上下文
       line_number: int         # 所在行号
       figure_name: str = ""    # 图片标题
       image_description: str = ""  # 图片描述
       relevance_score: float = 0.0  # 相关性分数
   ```

2. **智能描述生成**：
   ```python
   class ImageDescriptionGenerator:
       def generate_description(self,
           doc_title: str,
           context_before: str,
           context_after: str,
           image_path: str,
           ref_name: str,
           index: int
       ) -> Tuple[str, str, float]:
           # 返回 figure_name, description, relevance_score
   ```

3. **灵活的更新机制**：
   ```python
   def update_img_ref(md_info: MdInfo, 
                     references: List[ImageReference], 
                     markdown_file: str) -> None:
       # 更新markdown文件中的图片引用格式
   ```

## 2. 处理流程

### 2.1 扫描阶段
- 使用正则表达式匹配图片引用
- 提取上下文信息(前后200字符)
- 记录位置和行号信息

### 2.2 描述生成阶段
- 分析文档标题和上下文
- 使用LLM生成figure_name
- 生成图片描述
- 计算相关性得分

### 2.3 更新阶段
- 更新图片引用格式
- 更新md_info中的图片列表
- 保存修改后的文件

## 3. 使用示例

### 3.1 基本使用
```python
from ctn2md.md_info.md_info_base import MdInfo
from ctn2md.gen_base.img_ref.scan_img_ref_and_update import scan_img_ref_and_update

# 初始化
md_info = MdInfo(pname_info)
test_file = md_info.name_step_pathname(0)

# 扫描和更新
references = scan_img_ref_and_update(md_info, test_file)
```

### 3.2 自定义扫描器
```python
from ctn2md.gen_base.img_ref.ir_scanner import ImageReferenceScanner

# 创建扫描器
scanner = ImageReferenceScanner(context_chars=200)

# 扫描文件
references = scanner.scan_file(markdown_file)
```

## 4. 最佳实践

### 4.1 开发建议
- 使用 `load_env()` 确保环境初始化
- 合理设置上下文长度
- 完整的错误处理和日志记录
- 添加独立的测试入口

### 4.2 调试技巧
- 使用 `__main__` 块测试
- 检查生成的描述质量
- 验证相关性得分
- 使用 rich 打印调试信息 