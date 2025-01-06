import pytest
from unittest.mock import patch
from mrag_app._app_log_monitor import ProgressLogger

@pytest.fixture(autouse=True)
def clear_progress_history():
    """每个测试前清空进度历史"""
    ProgressLogger.clear_progress_history()
    yield

def test_progress_logger_initialization():
    """测试ProgressLogger的初始化状态"""
    assert isinstance(ProgressLogger._progress_history, list)
    assert isinstance(ProgressLogger._progress_status, dict)
    assert len(ProgressLogger._progress_history) == 0
    assert len(ProgressLogger._progress_status) == 0

def test_log_progress_basic():
    """测试基本的进度日志记录"""
    # 记录一条基本的进度信息
    ProgressLogger.log_progress("step1: 10%: 选择知识库:mrag")
    
    # 验证进度历史
    history = ProgressLogger.get_progress_history()
    assert len(history) == 1
    entry = history[0]
    assert entry["step"] == 1.0
    assert entry["percentage"] == 10
    assert entry["task_name"] == "选择知识库"
    assert entry["extra_info"] == "mrag"

def test_log_progress_decimal_step():
    """测试带小数点的步骤号"""
    ProgressLogger.log_progress("step1.5：10%：查询进入")
    
    history = ProgressLogger.get_progress_history()
    assert len(history) == 1
    entry = history[0]
    assert entry["step"] == 1.5
    assert entry["percentage"] == 10
    assert entry["task_name"] == "查询进入"
    assert entry["extra_info"] is None

def test_log_progress_multiple_steps():
    """测试多个进度步骤的记录"""
    steps = [
        "step1: 10%: 任务1#信息1",
        "step2: 20%: 任务2",
        "step3: 30%: 任务3#信息3"
    ]
    
    for step in steps:
        ProgressLogger.log_progress(step)
    
    history = ProgressLogger.get_progress_history()
    assert len(history) == 3
    
    # 验证每个步骤的信息
    assert history[0]["step"] == 1.0
    assert history[0]["extra_info"] == "信息1"
    assert history[1]["percentage"] == 20
    assert history[1]["extra_info"] is None
    assert history[2]["task_name"] == "任务3"
    assert history[2]["extra_info"] == "信息3"

def test_log_progress_invalid_format():
    """测试无效格式的进度信息"""
    with patch('logging.warning') as mock_warning:
        ProgressLogger.log_progress("invalid format")
        mock_warning.assert_called_once()
    
    history = ProgressLogger.get_progress_history()
    assert len(history) == 0

def test_progress_status_json():
    """测试JSON状态信息的记录"""
    # 记录一个JSON状态
    status_log = 'status1```json{"key": "value", "number": 123}```'
    ProgressLogger.log_progress(status_log)
    
    # 验证状态存储
    status = ProgressLogger.get_progress_status()
    assert "status1" in status
    assert status["status1"]["key"] == "value"
    assert status["status1"]["number"] == 123

def test_progress_status_invalid_json():
    """测试无效JSON状态信息的处理"""
    # 记录一个无效的JSON
    ProgressLogger.log_progress('status2```json{"key": invalid}```')
    
    # 验证状态存储（json_repair应该能修复简单的JSON错误）
    status = ProgressLogger.get_progress_status()
    assert "status2" in status
    assert status["status2"]["key"] == "invalid"

def test_clear_progress_history():
    """测试清除进度历史"""
    # 添加一些进度信息
    ProgressLogger.log_progress("step1: 10%: 任务1")
    ProgressLogger.log_progress('status```json{"key": "value"}```')
    
    # 验证信息已添加
    assert len(ProgressLogger.get_progress_history()) > 0
    assert len(ProgressLogger.get_progress_status()) > 0
    
    # 清除历史
    ProgressLogger.clear_progress_history()
    
    # 验证已清除
    assert len(ProgressLogger.get_progress_history()) == 0
    assert len(ProgressLogger.get_progress_status()) == 0

def test_progress_history_copy():
    """测试进度历史的复制行为"""
    ProgressLogger.log_progress("step1: 10%: 任务1")
    
    # 获取历史副本
    history1 = ProgressLogger.get_progress_history()
    history2 = ProgressLogger.get_progress_history()
    
    # 验证是不同的对象
    assert history1 is not history2
    # 但内容相同
    assert history1 == history2

def test_chinese_colon_support():
    """测试中文冒号的支持"""
    ProgressLogger.log_progress("step1：50%：测试任务#测试信息")
    
    history = ProgressLogger.get_progress_history()
    assert len(history) == 1
    entry = history[0]
    assert entry["step"] == 1.0
    assert entry["percentage"] == 50
    assert entry["task_name"] == "测试任务"
    assert entry["extra_info"] == "测试信息"

def test_multiple_json_status():
    """测试多个JSON状态的处理"""
    status_logs = [
        'status1```json{"key1": "value1"}```',
        'status2```json{"key2": "value2"}```'
    ]
    
    for log in status_logs:
        ProgressLogger.log_progress(log)
    
    status = ProgressLogger.get_progress_status()
    assert len(status) == 2
    assert status["status1"]["key1"] == "value1"
    assert status["status2"]["key2"] == "value2" 