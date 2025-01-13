# CTN2MD (Content To Markdown)

智能文档转换工具，支持多种文档格式到Markdown的高质量转换。

## 项目特点

- 多引擎支持 (LVLM/TextIn/LlamaParse/Markitdown/Pptx2Md)
- 智能布局分析
- 高质量转换
- 批量处理能力

## 系统架构

```
ctn2md/
├── gen_lvlm/          # LVLM引擎 [文档](gen_lvlm/readme_lvlm.md)
├── gen_textin/        # TextIn引擎 [文档](gen_textin/readme_textin.md)
├── gen_llamaparse/    # LlamaParse引擎 [文档](gen_llamaparse/readme_llamaparse.md)
├── converters/        # 转换器层 [文档](converters/readme_converters.md)
├── src/              # 核心功能层 [文档](src/readme_src.md)
├── src_gen/          # 生成器适配层 [文档](src_gen/readme_src_gen.md)
├── utils/            # 基础工具 [文档](utils/readme_utils.md)
├── utils_llm/        # LLM工具 [文档](utils_llm/readme_utils_llm.md)
├── utils_vllm/       # VLLM工具 [文档](utils_vllm/readme_utils_vllm.md)
└── utils_gen/        # 生成工具 [文档](utils_gen/readme_utils_gen.md)
```

## 快速开始

### 1. 环境配置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 基本使用

```python
# 1. PDF文档转换 (LVLM引擎，适合复杂排版)
from ctn2md.converters.converter_pdf_lvlm import do_content2md_convert
result = do_content2md_convert("doc.pdf")

# 2. PDF文档转换 (TextIn引擎，适合文本为主)
from ctn2md.converters.converter_pdf_textin import do_content2md_convert
result = do_content2md_convert("doc.pdf")

# 3. 通用格式转换 (支持多种格式)
from ctn2md.converters.converter_all_llamaparse import do_content2md_convert
result = do_content2md_convert("doc.*")

# 4. 批量转换
from ctn2md.batch_cvt_papers import batch_convert
batch_convert(["doc1.pdf", "doc2.pdf"])
```

### 3. 配置说明

```python
# 转换控制参数
mdcontrols = {
    # 通用配置
    "mctl_move_aux_files": True,        # 是否移动辅助文件
    "mctl_treat_doc_as_ctntype": "auto", # 文档类型处理方式
    "mctl_ge_md_async": False,          # 异步生成开关
    "mctl_fix_heading_model": "qwen",   # 标题修复模型
    "mctl_summarize_model": "qwen",     # 摘要生成模型
    "mctl_cache_dir": "_cache",         # 缓存目录

    # LVLM引擎配置
    "mctl_lvlm_region_detect": "gs2",   # 区域检测模型
    "mctl_lvlm_img2md_model": "qwen",   # 图片转MD模型

    # TextIn引擎配置
    "mctl_ti_img_relevance_model": "qwen", # 图片相关性判断
    "mctl_ti_img_caption_model": "qwen",   # 图片说明生成

    # LlamaParse引擎配置
    "mctl_lp_min_img_relevance_score": 0.2, # 图片相关性阈值
    "mctl_lp_img_caption_model": "qwen",    # 图片说明生成
}
```

## 转换示例

### 1. PDF文档转换 (LVLM引擎)

适用于复杂排版的PDF文档，如技术合同、研究报告等。

输入：`业绩案例、比亚迪车架总成技术服务合同.pdf`
输出目录结构：
```
_output/ctn2md_mrag__业绩案例_比亚迪车架总成技术服务合同_lvlm/
├── _aux/                    # 辅助文件目录
│   ├── images/             # 提取的图片
│   └── temp/              # 临时文件
├── _info.json             # 文档信息
├── _info_ctrl.json        # 控制信息
├── _final_info.json       # 最终结果信息
└── 业绩案例、比亚迪车架总成技术服务合同___pdf.md  # 转换后的Markdown文件
```

### 2. Office文档转换

支持各类Office文档（DOCX、PPTX、XLSX）的转换。

输入：`高效沟通之黄金三角模型课程大纲.docx`
输出示例：
```markdown
# 高效沟通之黄金三角模型课程大纲

## 课程目标
1. 理解沟通的本质和重要性
2. 掌握黄金三角模型的核心要素
3. 提升实际沟通效果

## 课程内容
### 1. 沟通基础
- 沟通的定义
- 沟通的要素
- 常见沟通障碍
...
```

### 3. 批量转换

支持多文件批量转换，适合处理大量文档。

```python
# 批量转换示例
doc_pathnames = [
    "datasrc/papers/paper1.pdf",
    "datasrc/papers/paper2.pdf",
    "datasrc/docs/doc1.docx",
    "datasrc/slides/slide1.pptx"
]
batch_convert(doc_pathnames)
```

输出目录结构：
```
_output/
├── ctn2md_papers__paper1_lvlm/
├── ctn2md_papers__paper2_lvlm/
├── ctn2md_docs__doc1_mid/
└── ctn2md_slides__slide1_px2m/
```

## 日志系统

系统提供三种日志文件：
```
logs/
├── ctn2md_error.log  # 错误日志
├── ctn2md_prg.log    # 进度日志
└── ctn2md_llm.log    # LLM调用日志
```

## 详细文档

- [LVLM引擎](gen_lvlm/readme_lvlm.md)
- [TextIn引擎](gen_textin/readme_textin.md)
- [LlamaParse引擎](gen_llamaparse/readme_llamaparse.md)
- [转换器层](converters/readme_converters.md)
- [核心功能层](src/readme_src.md)
- [生成器适配层](src_gen/readme_src_gen.md)
- [基础工具](utils/readme_utils.md)
- [LLM工具](utils_llm/readme_utils_llm.md)
- [VLLM工具](utils_vllm/readme_utils_vllm.md)
- [生成工具](utils_gen/readme_utils_gen.md)

## 最佳实践

### 1. 引擎选择
- 复杂排版PDF使用LVLM引擎
- 文本为主PDF使用TextIn引擎
- 其他格式使用LlamaParse引擎

### 2. 性能优化
- 使用异步处理大文件
- 启用缓存机制
- 合理设置并发数

### 3. 质量控制
- 选择合适的模型
- 定期更新模型
- 监控转换质量

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件 