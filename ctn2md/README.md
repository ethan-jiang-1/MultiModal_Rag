## 系统架构

### 1. CTN2MD (Content to Markdown)

多引擎文档转换系统，支持多种转换策略：

#### 转换引擎

1. **LlamaParse 引擎** (ctn2md_converter_lp.py)
   - 通用文档处理能力，支持多种格式
   - 处理质量适中，但覆盖面广
   - 适合批量快速处理场景

2. **LVLM 引擎** (ctn2md_converter_lvlm.py)
   - 基于大规模视觉语言模型
   - 支持多种高质量模型：GPT-4V、Qwen-VL、Ark-VL
   - 处理质量优秀，特别适合复杂版面
   - 可配置不同模型以平衡效果和性能

3. **Markdown 优化引擎** (ctn2md_converter_md.py)
   - 专门处理 Markdown 文件
   - 优化文档结构和格式
   - 提升可读性和一致性

4. **Textin OCR 引擎** (ctn2md_converter_ti.py)
   - 专业 PDF 文档处理
   - OCR 识别质量优秀
   - 特别适合扫描版 PDF 处理

#### 配置与控制

核心配置位于 `ctn2md/src/md_info_base.py` 的 `_DEFAULT_MDCONTROL`，