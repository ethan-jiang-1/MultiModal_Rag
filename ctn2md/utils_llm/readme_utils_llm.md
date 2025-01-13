# LLM Utils Module

语言模型工具模块，提供与各种LLM（Language Model）交互的通用功能和工具。

## 功能特点

- 多模型支持
- 统一接口
- 缓存机制
- 错误处理

## 模块组成

```
utils_llm/
├── llm_base.py        # LLM基础功能
├── llm_gpt.py         # GPT模型适配
├── llm_qwen.py        # Qwen模型适配
├── llm_ark.py         # Ark模型适配
├── llm_cache.py       # 缓存管理
└── llm_error.py       # 错误处理
```

## 核心功能

### 1. 模型管理
- 模型初始化
- 参数配置
- 状态管理

### 2. 请求处理
- 提示词处理
- 响应解析
- 结果验证

### 3. 性能优化
- 响应缓存
- 并发控制
- 错误重试

## 使用方法

```python
# 1. 基础使用
from ctn2md.utils_llm.llm_base import LLMBase

# 创建LLM实例
llm = LLMBase(model_name="gpt-3.5-turbo")
response = llm.generate("Your prompt here")

# 2. 特定模型使用
from ctn2md.utils_llm.llm_qwen import QwenLLM

# 使用Qwen模型
qwen = QwenLLM()
response = qwen.generate("Your prompt here")

# 3. 带缓存的使用
from ctn2md.utils_llm.llm_cache import LLMCache

# 启用缓存
cache = LLMCache()
response = cache.get_or_generate("prompt", llm_func)
```

## 最佳实践

1. 模型选择：
   - 根据任务选择合适模型
   - 考虑性能和成本
   - 处理模型限制

2. 错误处理：
   - 实现重试机制
   - 处理超时情况
   - 记录错误信息

3. 性能优化：
   - 合理使用缓存
   - 控制请求频率
   - 优化提示词 