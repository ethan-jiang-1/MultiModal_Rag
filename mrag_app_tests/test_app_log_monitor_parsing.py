import pytest
from mrag_app._app_log_monitor import ProgressLogger

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """每个测试前清理历史记录，测试后恢复初始状态"""
    ProgressLogger.clear_progress_history()
    initial_handlers = ProgressLogger._logger.handlers.copy()
    yield
    ProgressLogger.clear_progress_history()
    # 恢复原始处理器状态
    ProgressLogger._logger.handlers = initial_handlers
    ProgressLogger._logger_hooked = False

@pytest.mark.unit
class TestProgressLoggerParsing:
    """测试进度日志解析功能"""
    
    def test_parse_json_status(self):
        """测试JSON状态解析功能"""
        # 测试基本JSON解析
        test_log = "test_status```json{\"key\": \"value\"}```"
        ProgressLogger._parse_and_store_status(test_log)
        status = ProgressLogger.get_progress_status()
        assert "test_status" in status
        assert status["test_status"]["key"] == "value"

        # 测试复杂JSON解析
        complex_log = "complex_status```json{\"array\": [1, 2, 3], \"nested\": {\"a\": 1}}```"
        ProgressLogger._parse_and_store_status(complex_log)
        status = ProgressLogger.get_progress_status()
        assert "complex_status" in status
        assert status["complex_status"]["array"] == [1, 2, 3]
        assert status["complex_status"]["nested"]["a"] == 1

    def test_parse_progress_formats(self):
        """测试不同格式的进度日志解析"""
        test_logs = [
            "step1: 10%: 选择知识库:mrag",
            "step1.5：10%：查询进入",
            "step2: 20%: 处理结果#附加信息",
            "step10：100%：查询完成#成功"
        ]
        for log in test_logs:
            ProgressLogger._parse_and_store_progress(log)
        
        history = ProgressLogger.get_progress_history()
        assert len(history) == 4
        
        # 验证第一条记录
        assert history[0]["step"] == 1.0
        assert history[0]["percentage"] == 10
        assert history[0]["task_name"] == "选择知识库:mrag"
        assert history[0]["extra_info"] is None

        # 验证小数步骤号
        assert history[1]["step"] == 1.5
        assert history[1]["task_name"] == "查询进入"

        # 验证带额外信息的记录
        assert history[2]["step"] == 2.0
        assert history[2]["extra_info"] == "附加信息"

        # 验证最后一条记录
        assert history[3]["step"] == 10.0
        assert history[3]["percentage"] == 100
        assert history[3]["extra_info"] == "成功"

    def test_invalid_progress_format(self):
        """测试无效的进度日志格式"""
        invalid_logs = [
            "invalid format",
            "step: 10%",
            "stepA: 10%: task",
            "step1: 200%: task"  # 这个格式实际上是有效的，只是百分比超出范围
        ]
        for log in invalid_logs:
            ProgressLogger._parse_and_store_progress(log)
        
        history = ProgressLogger.get_progress_history()
        # 只有最后一个格式是有效的，所以应该只有一条记录
        assert len(history) == 1
        assert history[0]["percentage"] == 200
        assert history[0]["task_name"] == "task"

    def test_handler_setup_and_logging(self):
        """测试日志处理器的设置和日志记录功能"""
        # 确保初始状态
        ProgressLogger._logger_hooked = False
        initial_handlers = len(ProgressLogger._logger.handlers)

        # 设置处理器
        ProgressLogger._setup_handler()
        assert len(ProgressLogger._logger.handlers) == initial_handlers + 1

        # 测试重复设置
        ProgressLogger._setup_handler()
        assert len(ProgressLogger._logger.handlers) == initial_handlers + 1  # 不应该重复添加

        # 测试通过log_progress记录日志
        ProgressLogger.log_progress("step1: 10%: 测试任务")
        history = ProgressLogger.get_progress_history()
        assert len(history) == 1
        assert history[0]["task_name"] == "测试任务"

    def test_clear_functionality(self):
        """测试清理功能"""
        # 添加一些测试数据
        ProgressLogger._parse_and_store_progress("step1: 10%: 测试任务")
        ProgressLogger._parse_and_store_status("test_status```json{\"key\": \"value\"}```")
        
        # 验证数据已添加
        assert len(ProgressLogger.get_progress_history()) == 1
        assert len(ProgressLogger.get_progress_status()) == 1

        # 清理数据
        ProgressLogger.clear_progress_history()
        
        # 验证数据已清理
        assert len(ProgressLogger.get_progress_history()) == 0
        assert len(ProgressLogger.get_progress_status()) == 0 