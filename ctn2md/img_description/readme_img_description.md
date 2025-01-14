# 图像描述生成模块

## 快速导航

### 关键文件索引
- `llm_gen_vllm_instruction.py` - 生成图像描述指令的主入口
- `vllm_img_description_qwen.py` - 千问模型的图像描述实现
- `vllm_img_description_gpt.py` - GPT模型的图像描述实现
- `vllm_img_description_ark.py` - Ark模型的图像描述实现

### 提示词文件
- `vllm_img_description_qwen_prompt.py` - 千问模型提示词
- `vllm_img_description_gpt_prompt.py` - GPT模型提示词
- `vllm_img_description_ark_prompt.py` - Ark模型提示词
- `llm_gen_vllm_instruction_*_prompt.py` - 各模型的指令生成提示词

## 核心功能

### 1. 生成图像描述指令
```python
from ctn2md.img_description.llm_gen_vllm_instruction import gen_vllm_instruction_llm

# 生成图像描述指令
instruction = gen_vllm_instruction_llm(
    doc_title="文档标题",
    page_content="页面内容",
    model="qwen-turbo-1101"  # 或 "gpt-4" 或 "ep-xxx"
)
```

### 2. 生成图像描述
```python
from ctn2md.img_description.vllm_img_description_qwen import generate_image_description_by_qwen

# 使用千问模型生成描述
description = generate_image_description_by_qwen(
    image_path_or_url="图片路径或URL",
    instruction="描述指令",
    model="qwen-vl-max-1119"
)
```

## 支持的模型

### 1. 千问系列
- `qwen-turbo-1101` - 指令生成
- `qwen-vl-max-1119` - 图像描述
- `qwen-plus` - 高级版本

### 2. GPT系列
- `gpt-4` - 指令生成
- `gpt-4-vision` - 图像描述

### 3. Ark系列
- `ep-xxx` - 指令生成和图像描述

## 处理流程

### 1. 指令生成流程
1. **上下文分析**
   - 提取文档标题
   - 分析页面内容
   - 确定内容语言

2. **指令生成**
   - 选择合适的模型
   - 应用模型特定提示词
   - 生成描述指令

### 2. 图像描述流程
1. **图像处理**
   - 支持本地文件和URL
   - 验证图像有效性
   - 准备多模态输入

2. **描述生成**
   - 应用描述指令
   - 调用视觉语言模型
   - 生成详细描述

## 最佳实践

### 开发建议
1. **模型选择**
   - 根据任务选择合适模型
   - 考虑性能和成本平衡
   - 注意模型版本兼容性

2. **错误处理**
   - 验证输入有效性
   - 处理模型调用异常
   - 保存诊断信息

### 性能优化
1. **参数调优**
   - temperature=0.1 (指令生成)
   - temperature=0.01 (图像描述)
   - top_p=0.9~0.95

2. **资源管理**
   - 复用模型客户端
   - 及时释放资源
   - 使用异步调用 