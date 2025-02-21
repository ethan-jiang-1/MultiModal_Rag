# 项目文档目录

本目录包含项目的补充文档和资源。

## 目录结构

- `images/` - 文档使用的图片资源
  - `architecture/` - 系统架构相关图片
  - `examples/` - 使用示例和截图
  - `guides/` - 使用指南相关图片

## 图片命名规范

- 架构图: `arch_[module]_[description].png`
- 示例图: `example_[feature]_[description].png`
- 指南图: `guide_[topic]_[step].png`

## 项目可视化

### 项目结构
```mermaid
graph TD
    A[MultiModal_Rag] --> B[mrag_app]
    A --> C[docs]
    
    B --> D[core]
    B --> E[ui]
    B --> F[utils]
    B --> G[resources]
    B --> H[responses]
    
    C --> I[images]
    C --> J[diagrams]
    
    I --> K[architecture]
    I --> L[examples]
    I --> M[guides]
```

### 模块依赖关系
```mermaid
flowchart LR
    UI[ui/_app_gradio_base.py] --> Core[core/_qa_core.py]
    UI --> Utils[utils/_app_log_monitor.py]
    Core --> Responses[responses/_rag_response.py]
    Core --> Resources[resources/_app_qa_examples.py]
    Utils --> Responses
```

### 重构流程
```mermaid
graph TD
    A[准备阶段] --> B[分析阶段]
    B --> C[优化阶段]
    C --> D[验证阶段]
    D --> E[监控阶段]
    
    A --> A1[配置工具]
    A --> A2[建立基准]
    A --> A3[设定目标]
    
    B --> B1[生成依赖图]
    B --> B2[识别问题]
    B --> B3[评估依赖]
    
    C --> C1[处理循环依赖]
    C --> C2[提取共用功能]
    C --> C3[重构高耦合组件]
    
    D --> D1[运行测试]
    D --> D2[验证改进]
    D --> D3[准备回滚]
    
    E --> E1[设置监控]
    E --> E2[更新文档]
    E --> E3[持续优化]
```

### 数据流程
```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Core
    participant RAG
    participant Response
    
    User->>UI: 输入查询
    UI->>Core: 处理请求
    Core->>RAG: 检索相关内容
    RAG->>Response: 生成响应
    Response->>Core: 返回结果
    Core->>UI: 格式化输出
    UI->>User: 显示结果
```

## 说明
以上图表使用 Mermaid 语法生成，可在支持 Mermaid 的 Markdown 查看器中直接预览（如 GitHub、VS Code 等）。图表展示了项目的整体结构、模块依赖关系、重构流程以及系统数据流向，帮助开发者更好地理解项目架构。 