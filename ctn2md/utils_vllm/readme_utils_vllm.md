# VLLM Utils Module

视觉语言模型工具模块，提供与各种VLLM（Vision Language Model）交互的通用功能和工具。

## 功能特点

- 多模型支持
- 图像处理
- 视觉分析
- 文本生成

## 模块组成

```
utils_vllm/
├── vllm_base.py       # VLLM基础功能
├── vllm_qwen.py       # Qwen-VL模型适配
├── vllm_gpt4v.py      # GPT4-Vision适配
├── vllm_cache.py      # 缓存管理
├── image_process.py   # 图像处理
└── vision_analyze.py  # 视觉分析
```

## 核心功能

### 1. 模型管理
- 模型初始化
- 参数配置
- 状态管理

### 2. 图像处理
- 图像预处理
- 格式转换
- 质量优化

### 3. 视觉分析
- 场景理解
- 对象检测
- 布局分析

## 使用方法

```python
# 1. 基础使用
from ctn2md.utils_vllm.vllm_base import VLLMBase

# 创建VLLM实例
vllm = VLLMBase(model_name="qwen-vl")
response = vllm.analyze_image("path/to/image.jpg", "Describe this image")

# 2. 特定模型使用
from ctn2md.utils_vllm.vllm_qwen import QwenVL

# 使用Qwen-VL模型
qwen_vl = QwenVL()
response = qwen_vl.analyze_image("path/to/image.jpg")

# 3. 图像处理
from ctn2md.utils_vllm.image_process import process_image

# 处理图像
processed_img = process_image("path/to/image.jpg", target_size=(800, 600))
```

## 最佳实践

1. 模型选择：
   - 根据任务选择合适模型
   - 考虑性能和成本
   - 处理模型限制

2. 图像处理：
   - 优化图像质量
   - 控制图像大小
   - 保持图像特征

3. 性能优化：
   - 使用批处理
   - 启用缓存
   - 并行处理 