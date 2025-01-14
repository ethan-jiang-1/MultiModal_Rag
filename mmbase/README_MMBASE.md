# MultiModal Base Framework

## 快速导航

### 关键文件索引
- LLM基础: `utils_llm/llm_base.py` - 多模型统一接口(Azure/DashScope/Ark)
- Markdown处理: `utils_llm/llm_markdown.py` - LLM输出格式规范化
- 诊断工具: `utils_llm/llm_diag.py` - 性能和错误诊断
- 调试支持: `utils_llm/llm_debug.py` - 开发调试工具
- 监控系统: `utils_llm/llm_base_monitor.py` - 性能指标CSV记录
- 存储服务: `utils_llm/llm_base_oss.py` - 阿里云OSS集成
- TOS服务: `utils_llm/llm_base_tos.py` - 火山引擎TOS集成
- 日志工具: `utils/util_logging.py` - 统一日志处理

### 按功能查找
- LLM调用失败? → 看 `llm_base.py` 的 retry 机制
- 输出格式混乱? → 看 `llm_markdown.py` 的 strip_llm_format_markers
- 性能分析? → 看 `llm_base_monitor.py` 的 CSV 记录
- 图片上传? → 看 `llm_base.py` 的 upload_image_to_cloud
- 多模态调用? → 看 `llm_base.py` 的 get_gpt_messages_multimodal

## 1. 系统设计思路

### 1.1 核心特性
- 统一接口设计
  ```python
  # 支持多种模型后端，通过环境变量切换
  client = get_azure_gpt_client()  # Azure OpenAI
  client = get_dashscope_client()  # 阿里云 DashScope
  client = get_ark_client()        # 火山引擎 Ark
  ```

- 健壮的重试机制
  ```python
  @retry(
      stop=stop_after_attempt(DEFAULT_RETRY_NUM),
      wait=wait_random_exponential_with_rate_limit(),
      retry=retry_if_exception_type((httpx.RequestError, ValueError, openai.RateLimitError))
  )
  ```

- 性能监控追踪
  ```python
  with MonitorContextLLM(messages, model, track_id, 0) as mc:
      response = client.chat.completions.create(...)
      mc.response = response  # 自动记录性能指标
  ```

### 1.2 关键配置
- 模型参数推荐
  ```python
  # SQL生成: 高精度低创造力
  temperature=0.1, top_p=0.9
  
  # 分析任务: 平衡逻辑和创造力
  temperature=0.3, top_p=0.85
  
  # 报告生成: 重视表达的多样性
  temperature=0.5, top_p=0.9
  ```

- 环境变量
  ```bash
  # Azure OpenAI
  OPENAI_API_KEY=
  OPENAI_BASE_URL=
  AZURE_OPENAI_VERSION=
  
  # 阿里云 DashScope
  DASHSCOPE_API_KEY=
  
  # 火山引擎 Ark
  ARK_API_KEY=
  ```

## 2. 核心功能

### 2.1 多模态支持
```python
# 支持本地图片和远程URL
messages = get_gpt_messages_multimodal(
    system_prompt="Analyze this image",
    user_prompt="What do you see?",
    image_path_or_url="local.jpg"  # 自动上传到云存储
)
```

### 2.2 格式处理
```python
# JSON响应
resp = chat_gpt_json(
    messages,
    model="gpt-4o-mini",
    temperature=0.1
)  # 自动修复损坏的JSON

# Markdown清理
clean_text = strip_llm_format_markers(
    "```markdown\nHello World\n```"
)  # 移除格式标记
```

### 2.3 性能监控
- CSV格式记录
  - timestamp: 调用时间戳
  - finish_reason: 完成原因
  - model_requested/actual: 请求/实际模型
  - sec_span: 耗时(秒)
  - total/prompt/completion_tokens: Token统计
  - token_per_ms: 生成速度
  - track_id: 追踪标识
  - attempt: 重试次数

## 3. 最佳实践

### 3.1 错误处理
- 使用 track_id 关联日志
- 检查 CSV 监控文件分析性能
- 查看重试次数和原因

### 3.2 性能优化
- 合理设置 temperature 和 top_p
- 监控 token_per_ms 指标
- 分析模型实际延迟

### 3.3 开发建议
- 使用 load_env() 确保环境变量
- 复用 MonitorContextLLM 跟踪性能
- 处理 JSON 时用 jsons_load_repair


