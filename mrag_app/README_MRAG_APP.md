# MRAG App 模块

## 快速导航

### 核心文件
- `ui/app_gradio.py` - 主应用入口，基于 Gradio 的 Web UI 启动器
- `ui/_app_gradio_base.py` - Gradio UI 核心实现，包含界面布局和交互逻辑
- `core/_qa_core.py` - QA 核心处理逻辑
- `core/_rag_core_query.py` - RAG 检索查询实现
- `responses/_rag_response.py` - RAG 响应数据结构和处理

### 启动变体
- `app_gradio_local_qwen.py` - 通义千问模型本地部署版本
- `app_gradio_local_ark.py` - Ark 模型本地部署版本
- `app_gradio_local_gpt.py` - GPT 模型本地部署版本

## 系统设计

### 核心特性
1. **多模型支持**
```python
# 切换不同的模型实现
RagModelGptSel.set_gpt_model("gpt-4o")  # 或 "qwen", "ark" 等
```

2. **进度监控**
```python
# 实时进度更新
ProgressLogger.get_progress_status()
ProgressLogger.get_progress_history()
```

3. **响应处理**
```python
# 解析 RAG 响应
content, details, sources, images = parse_content_from_rag_response(rag_response)
```

### 关键配置
- `GRADIO_USE_LOCAL_FONTS`: 控制字体加载 (默认: True)
- `GRADIO_DISABLE_PRELOAD`: 禁用预加载 (默认: True)
- `GRADIO_OFFLINE_MODE`: 强制使用本地资源 (默认: True)

## 核心功能

### Web UI 功能
1. **问答交互**
   - 支持多轮对话
   - 实时进度显示
   - 源文档引用
   - 图片展示

2. **系统控制**
   - 模型切换
   - 知识库选择
   - 检索数量调整
   - 会话清理

### 进度监控
- 实时进度百分比
- 当前任务状态
- 详细进度日志
- 额外状态信息

## 最佳实践

### 部署建议
1. **环境准备**
   - 安装依赖: `pip install -r requirements.txt`
   - 配置 `.env` 文件设置必要的环境变量

2. **启动选项**
   - 开发环境: `python ui/app_gradio.py`
   - 生产环境: 使用对应的模型变体启动器

3. **性能优化**
   - 使用本地字体和资源
   - 禁用不必要的预加载
   - 合理设置检索数量

### 错误处理
- 使用 `try-except` 包装核心操作
- 详细的日志记录
- 友好的错误提示

### 开发建议
- 遵循模块化设计
- 使用类型注解
- 保持代码简洁
- 添加必要的注释 