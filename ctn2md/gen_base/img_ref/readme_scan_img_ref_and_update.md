# 图片引用扫描与更新模块

## 快速导航

### 关键文件索引
- 总入口: `scan_img_ref_and_update.py` - 图片引用扫描和更新的主入口
- 扫描器: `img_ref/scanner.py` - 图片引用扫描器
- 更新器: `img_ref/img_ref_updater.py` - 图片引用更新器
- 描述生成: `img_ref/description_generator.py` - 图片描述生成器
- 数据模型: `img_ref/models.py` - 图片引用相关的数据模型

### 按功能查找
- 想了解整体流程? → 看 `scan_img_ref_and_update.py`
- 需要修改扫描逻辑? → 看 `img_ref/scanner.py`
- 调整更新规则? → 看 `img_ref/img_ref_updater.py`
- 优化描述生成? → 看 `img_ref/description_generator.py`
- 修改数据结构? → 看 `img_ref/models.py`

## 1. 设计思路

### 1.1 核心原则
- 完整性：扫描文档中所有的图片引用
- 上下文感知：考虑图片引用的上下文内容
- 智能描述：使用LLM生成准确的图片描述
- 原子性：每个图片引用的更新是独立的

### 1.2 处理流程
1. **扫描阶段**：
   - 扫描markdown文件中的图片引用
   - 提取上下文信息(前后200字符)
   - 记录行号和引用格式

2. **描述生成**：
   - 分析文档标题和上下文
   - 使用LLM生成figure_name
   - 生成图片描述
   - 计算相关性得分

3. **更新阶段**：
   - 更新图片引用格式
   - 更新md_info中的图片列表
   - 保存修改后的文件

## 2. 目录结构

```
gen_base/
├── scan_img_ref_and_update.py    # 功能总入口
├── readme_scan_img_ref_and_update.md  # 本文档
└── img_ref/                      # 图片引用处理包
    ├── __init__.py              # 包初始化
    ├── scanner.py               # 图片引用扫描器
    ├── img_ref_updater.py       # 引用更新器
    ├── description_generator.py  # 描述生成器
    └── models.py                # 数据模型定义
```

## 3. 模块说明

### 3.1 入口模块

#### scan_img_ref_and_update.py
- 功能：图片引用处理的总入口
- 职责：协调扫描、描述生成和更新流程
- 特点：提供简单的调用接口

### 3.2 核心模块

#### ImageReferenceScanner
- 功能：扫描markdown中的图片引用
- 输入：markdown文件路径
- 输出：ImageReference对象列表
- 特点：支持上下文提取

#### ImageDescriptionGenerator
- 功能：生成图片描述
- 输入：文档标题、上下文、图片路径等
- 输出：figure_name和description
- 特点：使用LLM生成智能描述

### 3.3 支持模块

#### ImageReference
- 功能：图片引用数据模型
- 字段：ref_name, line_number, context等
- 方法：needs_update, to_markdown等

#### ImageReferenceUpdater
- 功能：更新图片引用
- 输入：ImageReference列表和文件路径
- 输出：更新后的markdown内容

## 4. 数据流

1. **输入阶段**
   - 读取markdown文件
   - 获取md_info配置

2. **扫描阶段**
   - 扫描图片引用
   - 提取上下文信息

3. **生成阶段**
   - 生成figure_name
   - 生成图片描述
   - 计算相关性得分

4. **更新阶段**
   - 更新引用格式
   - 更新md_info
   - 保存结果

## 5. 开发规范

### 5.1 代码组织
- 模块化设计
- 清晰的职责划分
- 完善的类型注解

### 5.2 错误处理
- 文件操作异常处理
- LLM调用异常处理
- 格式解析异常处理

### 5.3 测试策略
- 单元测试各个组件
- 集成测试完整流程
- 使用`__main__`进行快速测试

### 5.4 性能考虑
- 批量处理图片引用
- 缓存LLM结果
- 优化文件读写操作 