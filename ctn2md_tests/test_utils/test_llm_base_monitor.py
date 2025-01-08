import pytest
from unittest.mock import MagicMock, patch
import time
import os
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from ctn2md.utils_llm.llm_base_monitor import MonitorContextLLM

@pytest.fixture
def mock_messages():
    """模拟消息列表"""
    return [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello!"}
    ]

@pytest.fixture
def mock_completion():
    """模拟ChatCompletion响应"""
    completion = MagicMock(spec=ChatCompletion)
    completion.model = "gpt-4"
    completion.usage = MagicMock(
        completion_tokens=20,
        prompt_tokens=30,
        total_tokens=50
    )
    message = MagicMock(spec=ChatCompletionMessage)
    message.content = "Hello! How can I help you?"
    choice = MagicMock()
    choice.message = message
    choice.finish_reason = "stop"
    completion.choices = [choice]
    return completion

def test_monitor_basic_flow(mock_messages, mock_completion):
    """测试基本监控流程"""
    with patch('csv.writer') as mock_writer:
        writer = MagicMock()
        mock_writer.return_value = writer
        
        monitor = MonitorContextLLM(mock_messages, "gpt-4", "test-123", 0)
        monitor.__enter__()
        time.sleep(0.1)  # 模拟处理时间
        monitor.response = mock_completion
        monitor.__exit__(None, None, None)
        
        # 验证基本属性
        assert monitor.track_id == "test-123"
        assert monitor.model == "gpt-4"
        assert monitor.messages == mock_messages
        assert monitor.response == mock_completion
        assert monitor.d0 is not None
        assert monitor.d1 is not None
        assert monitor.d1 > monitor.d0

def test_monitor_error_handling(mock_messages):
    """测试错误处理"""
    with patch('logging.exception') as mock_exception:
        with pytest.raises(ValueError):
            with MonitorContextLLM(mock_messages, "gpt-4", "test-123", 0):
                raise ValueError("Test error")
        
        # 验证记录了异常
        mock_exception.assert_called_with("test-123")

def test_monitor_with_retry_count(mock_messages, mock_completion):
    """测试带重试次数的监控"""
    monitor = MonitorContextLLM(mock_messages, "gpt-4", "test-123", 2)
    monitor.__enter__()
    monitor.response = mock_completion
    monitor.__exit__(None, None, None)
    
    # 验证重试次数
    assert monitor.attempt == 2

def test_monitor_no_response(mock_messages):
    """测试没有响应的情况"""
    monitor = MonitorContextLLM(mock_messages, "gpt-4", "test-123", 0)
    monitor.__enter__()
    time.sleep(0.1)  # 添加一个小延迟
    monitor.__exit__(None, None, None)
    
    # 验证基本属性
    assert monitor.response is None
    assert monitor.d0 is not None
    assert monitor.d1 is not None
    assert monitor.d1 > monitor.d0

def test_monitor_different_models():
    """测试不同模型的文件名生成"""
    models = {
        "gpt-4": "ctn_monitor_gpt.csv",
        "qwen-max": "ctn_monitor_qwen.csv",
        "ep-model": "ctn_monitor_ark.csv",
        "other-model": "ctn_monotor_ukn.csv"
    }
    
    for model, expected_file in models.items():
        filename = MonitorContextLLM._get_monitor_filename(model)
        assert os.path.basename(filename) == expected_file 