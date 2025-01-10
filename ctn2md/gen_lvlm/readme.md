# LVLM 转换器

基于大规模视觉语言模型的文档转换引擎，专注于复杂版面理解和图文关联分析。

## 特点

### 1. 视觉理解能力
- **版面智能分析**
  - 复杂布局理解
  - 多栏文档处理
  - 图表位置识别
  - 页面结构分析

- **图文关联处理**
  - 图文配对分析
  - 图片描述生成
  - 表格语义理解
  - 图表数据提取

### 2. 内容理解
- **语义分析**
  - 上下文关联理解
  - 章节结构识别
  - 引用关系分析
  - 内容主题提取

- **格式优化**
  - 智能分段处理
  - 标题层级优化
  - 列表结构重建
  - 引用格式标准化

## 技术实现

### 主要组件
```
gen_lvlm/
├── lvlm_gen_pages.py        # 页面生成核心
├── lvlm_vision_process.py   # 视觉处理模块
└── lvlm_content_analyze.py  # 内容分析模块
```

### 处理流程
1. 文档预处理
2. 视觉特征提取
3. 版面结构分析
4. 内容语义理解
5. Markdown生成
6. 后处理优化

## 使用指南

### 基本用法
```python
from ctn2md.ctn2md_converter_lvlm import do_content2md_convert

# 基本转换
result = do_content2md_convert("document.pdf")

# 使用高级配置
controls = None # 用默认设置
result = do_content2md_convert("document.pdf", mdcontrols=controls)
```

### 配置选项
- 通用配置：
  - `mctl_ge_md_async`: 异步处理开关
  - `mctl_move_aux_files`: 是否移动辅助文件
  - `mctl_treat_doc_as_ctntype`: 文档类型处理方式
  - `mctl_fix_heading_model`: 标题修复模型 (gpt/qwen/ark)
  - `mctl_summarize_model`: 摘要生成模型 (gpt/qwen/ark)

- LVLM专用配置：
  - `mctl_lvlm_images_ignore`: 忽略的图片列表（逗号分隔）
  - `mctl_lvlm_img2md_model`: 图片转MD模型 (gpt/qwen/ark)
  - `mctl_lvlm_region_detect`: 区域检测模型 (gs0/gs1/gs2)
  
  - 布局参数：
    - `mctl_lvlm_paint_page_content_area_ratios`: 页面内容区域比例 (0.15, 0.15, 0.1, 0.1)
    - `mctl_lvlm_paint_max_area_ratio`: 最大区域比例 (0.7)
    - `mctl_lvlm_paint_max_outside_ratio`: 最大外部比例 (0.1)
    - `mctl_lvlm_paint_min_coverage_ratio`: 最小覆盖比例 (0.7)
    - `mctl_lvlm_paint_content_area_buffer_ratio`: 内容区域缓冲比例 (0.05)
  
  - 距离参数：
    - `mctl_lvlm_paint_text_distance_ratio`: 文本距离比例 (0.015, 0.015, 0.015, 0.028)
    - `mctl_lvlm_table_line_distance_ratio`: 表格线距离比例 (0.03)
    - `mctl_lvlm_table_short_line_ratio`: 表格短线比例 (0.03)
    - `mctl_lvlm_table_text_distance_ratio`: 表格文本距离比例 (0.02, 0.02, 0.02, 0.02)

### 环境变量
- `ENV_MODEL_FLOW`: 流程控制模型 (gpt/qwen/ark)
- `ENV_MODEL_GEN_LVLM`: LVLM生成模型图文关联模型 (gpt/qwen/ark)
- `ENV_MODEL_GEN_LVLM_REGION`: LVLM区域检测模型 (gs0/gs1/gs2)

## 最佳实践

### 1. 性能优化
- 合理设置视觉质量参数
- 优化图片处理配置
- 使用适当的语义分析深度

### 2. 质量提升
- 对复杂版面文档使用高质量设置
- 启用深度语义分析
- 开启版面增强功能

### 3. 常见问题
- 复杂图表处理
- 多语言混排文档
- 特殊字体支持

## 系统要求
- 支持的文件格式：
  - PDF（主要支持）
  - 图文混排文档
  - 学术论文
