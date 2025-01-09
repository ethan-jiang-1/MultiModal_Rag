import pytest
import logging
from mrag_app._app_log_monitor import ProgressLogger

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """每个测试前后自动清理进度历史"""
    ProgressLogger.clear_progress_history()
    yield
    ProgressLogger.clear_progress_history()

@pytest.mark.unit
def test_progress_logger_setup():
    """测试进度日志记录器的初始化"""
    # 确保处理器已经设置
    ProgressLogger._setup_handler()
    
    # 验证logger已经被正确配置
    logger = logging.getLogger(ProgressLogger._logger.name)
    assert logger.handlers, "Logger应该有至少一个处理器"
    
    # 验证处理器类型
    handler = logger.handlers[-1]
    assert handler.__class__.__name__ == "ProgressHandler", "最后一个处理器应该是ProgressHandler"

@pytest.mark.unit
def test_progress_logging_basic():
    """测试基本的进度日志记录功能"""
    # 记录一些进度信息
    ProgressLogger.log_progress("step1: 10%: 开始任务")
    ProgressLogger.log_progress("step2: 50%: 处理中")
    ProgressLogger.log_progress("step3: 100%: 完成")
    
    # 获取进度历史
    history = ProgressLogger.get_progress_history()
    
    # 验证进度记录
    assert len(history) == 3, "应该有3条进度记录"
    assert history[0]["step"] == 1.0
    assert history[0]["percentage"] == 10
    assert history[0]["task_name"] == "开始任务"
    assert history[2]["percentage"] == 100

@pytest.mark.unit
def test_progress_logging_with_extra_info():
    """测试带有额外信息的进度日志记录"""
    # 记录带有额外信息的进度
    ProgressLogger.log_progress("step1: 25%: 处理数据#正在加载")
    ProgressLogger.log_progress("step2: 75%: 分析结果#发现异常")
    
    history = ProgressLogger.get_progress_history()
    
    assert len(history) == 2
    assert history[0]["extra_info"] == "正在加载"
    assert history[1]["extra_info"] == "发现异常"

@pytest.mark.unit
def test_progress_logging_decimal_steps():
    """测试带小数步骤的进度日志记录"""
    # 记录带小数的步骤
    ProgressLogger.log_progress("step1.5: 30%: 中间步骤")
    
    history = ProgressLogger.get_progress_history()
    
    assert len(history) == 1
    assert history[0]["step"] == 1.5
    assert history[0]["percentage"] == 30

@pytest.mark.unit
def test_progress_history_management():
    """测试进度历史记录的管理功能"""
    # 添加一些进度记录
    ProgressLogger.log_progress("step1: 0%: 开始")
    ProgressLogger.log_progress("step2: 50%: 中间")
    
    # 验证历史记录
    history1 = ProgressLogger.get_progress_history()
    assert len(history1) == 2
    
    # 清除历史记录
    ProgressLogger.clear_progress_history()
    
    # 验证清除后的状态
    history2 = ProgressLogger.get_progress_history()
    assert len(history2) == 0

@pytest.mark.unit
def test_invalid_progress_format():
    """测试无效格式的进度日志处理"""
    # 记录一些格式不正确的进度信息
    ProgressLogger.log_progress("invalid format")
    ProgressLogger.log_progress("step1: invalid%: task")
    ProgressLogger.log_progress("step1: 50: task")  # 缺少百分号
    
    history = ProgressLogger.get_progress_history()
    assert len(history) == 0, "格式无效的进度不应该被记录"

@pytest.mark.unit
def test_progress_status_management():
    """测试进度状态管理功能"""
    # 记录一些JSON格式的状态信息
    ProgressLogger.log_progress('status```json\n{"key": "value"}\n```')
    
    # 获取状态信息
    status = ProgressLogger.get_progress_status()
    
    # 验证状态信息
    status_key = next(key for key in status.keys() if key.strip() == "status")
    assert status[status_key] == {"key": "value"}
    
    # 清除状态
    ProgressLogger.clear_progress_history()
    assert len(ProgressLogger.get_progress_status()) == 0 