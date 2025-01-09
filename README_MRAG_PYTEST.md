# 测试说明文档

本文档详细说明了项目的测试配置、运行方法和编写规范。

## VSCode 配置

### Test Explorer 配置

在 `.vscode/settings.json` 中添加以下配置，使 VSCode 的 Test Explorer 能够识别并运行测试：

```json
{
    "python.testing.pytestArgs": [
        "ctn2md_tests",
        "mmbase_tests",
        "mrag_app_tests",
        "mrag_vdb_tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true
}
```

### 推荐的 VSCode 扩展

- Python Test Explorer for Visual Studio Code
- Coverage Gutters（用于显示测试覆盖率）
- Python Test Explorer

## 测试结构

项目的测试按模块分布在不同目录：

```
.
├── ctn2md_tests/      # 文档转换模块测试
├── mmbase_tests/      # 基础设施模块测试
├── mrag_app_tests/    # 应用界面模块测试
└── mrag_vdb_tests/    # 向量数据库模块测试
```

## 运行测试

### 命令行运行

```bash
# 运行所有测试
pytest

# 运行特定模块的测试
pytest mrag_app_tests/

# 运行特定测试文件
pytest mrag_app_tests/test_rag_models.py

# 运行特定测试函数
pytest mrag_app_tests/test_rag_models.py::test_progress_step_creation

# 显示详细输出
pytest -v

# 生成测试覆盖率报告
pytest --cov=mrag_app mrag_app_tests/
```

### 使用 VSCode Test Explorer

1. 打开 VSCode 的测试视图（Test Explorer）
2. 可以选择运行：
   - 所有测试（Run All Tests）
   - 特定文件的测试（点击文件旁的运行按钮）
   - 单个测试（点击测试函数旁的运行按钮）

## 编写测试规范

### 测试文件命名

- 测试文件应以 `test_` 开头
- 文件名应清晰表明被测试的模块
- 示例：`test_rag_models.py`, `test_app_log_monitor.py`

### 测试函数编写

```python
def test_function_name():
    """测试函数的文档字符串，说明测试的目的和验证的内容"""
    # 准备测试数据
    test_data = ...
    
    # 执行被测试的功能
    result = function_under_test(test_data)
    
    # 验证结果
    assert result == expected_result
```

### Mock 的使用

```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    """使用 Mock 示例"""
    with patch('module.external_function') as mock_func:
        mock_func.return_value = 'mocked_result'
        result = function_using_external()
        assert result == 'expected_result'
        mock_func.assert_called_once()
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# 生成覆盖率报告
pytest --cov=mrag_app --cov-report=html mrag_app_tests/

# 在浏览器中查看报告
open htmlcov/index.html
```

### 覆盖率要求

- 核心业务逻辑的测试覆盖率应达到 80% 以上
- 工具函数的测试覆盖率应达到 70% 以上
- UI 相关代码可以适当降低覆盖率要求

## 持续集成

项目使用 GitHub Actions 进行持续集成测试：

- 每次提交都会自动运行测试
- 测试失败会阻止合并
- 可以在 GitHub Actions 页面查看测试结果和覆盖率报告

## 常见问题

1. **测试无法发现**
   - 检查文件名是否以 `test_` 开头
   - 确认测试函数名是否以 `test_` 开头
   - 验证 VSCode 配置是否正确

2. **测试运行失败**
   - 确保已安装所有依赖：`pip install -r requirements-dev.txt`
   - 检查 PYTHONPATH 是否正确设置
   - 查看是否所有必要的环境变量都已配置

3. **Mock 相关问题**
   - 确保 Mock 的路径正确
   - 检查 Mock 的返回值是否符合预期
   - 验证 Mock 的调用次数和参数

4. **测试覆盖率问题**
   - 使用 `pytest --cov-report=term-missing` 查看未覆盖的代码行
   - 确保测试包含了所有主要的代码路径
   - 适当使用参数化测试增加覆盖率