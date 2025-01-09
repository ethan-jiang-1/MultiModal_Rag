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
def test_progress_logging_main_flow():
    """测试进度日志记录的主要流程"""
    # 记录一个完整的进度流程
    ProgressLogger.log_progress("step1: 10%: 选择知识库:mrag")
    ProgressLogger.log_progress("step2: 50%: 处理中#正在检索")
    ProgressLogger.log_progress("step3: 100%: 完成回答")
    
    # 获取进度历史
    history = ProgressLogger.get_progress_history()
    
    # 验证进度记录
    assert len(history) == 3, "应该有3条进度记录"
    # 验证第一步
    assert history[0]["step"] == 1.0
    assert history[0]["percentage"] == 10
    assert history[0]["task_name"] == "选择知识库:mrag"
    # 验证中间步骤
    assert history[1]["percentage"] == 50
    assert history[1]["extra_info"] == "正在检索"
    # 验证最后一步
    assert history[2]["percentage"] == 100
    assert history[2]["task_name"] == "完成回答"

@pytest.mark.unit
def test_progress_status_main_flow():
    """测试进度状态管理的主要流程"""
    # 记录一个典型的状态信息
    ProgressLogger.log_progress('status```json\n{"model": "gpt-4", "kb": "mrag"}\n```')
    
    # 获取状态信息
    status = ProgressLogger.get_progress_status()
    
    # 验证状态信息
    status_key = next(key for key in status.keys() if key.strip() == "status")
    status_data = status[status_key]
    assert "model" in status_data
    assert "kb" in status_data
    assert status_data["model"] == "gpt-4"
    assert status_data["kb"] == "mrag"
    
    # 清除状态并验证
    ProgressLogger.clear_progress_history()
    assert len(ProgressLogger.get_progress_status()) == 0 