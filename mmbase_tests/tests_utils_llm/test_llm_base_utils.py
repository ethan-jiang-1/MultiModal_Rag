from unittest.mock import MagicMock
from openai import RateLimitError
from mmbase.utils_llm.llm_base import (
    jsons_load_repair,
    wait_random_exponential_with_rate_limit
)

def test_json_repair_basic():
    """测试基本的JSON修复功能"""
    # 测试正常JSON
    assert jsons_load_repair('{"key": "value"}') == {"key": "value"}
    
    # 测试需要修复的JSON
    assert jsons_load_repair('{key: "value"}') == {"key": "value"}
    assert jsons_load_repair("{'key': 'value'}") == {"key": "value"}

def test_json_repair_complex():
    """测试复杂JSON的修复"""
    # 测试嵌套结构
    complex_json = '''{
        "array": [1, 2, 3],
        "nested": {"a": 1, "b": [4, 5, 6]},
        "null": null,
        "number": 42.5,
        "boolean": true
    }'''
    result = jsons_load_repair(complex_json)
    assert result["array"] == [1, 2, 3]
    assert result["nested"]["a"] == 1
    assert result["nested"]["b"] == [4, 5, 6]
    assert result["null"] is None
    assert result["number"] == 42.5
    assert result["boolean"] is True

def test_json_repair_invalid():
    """测试无效JSON的修复"""
    # 测试缺少引号的键
    assert jsons_load_repair('{key: value}') == {"key": "value"}
    
    # 测试单引号
    assert jsons_load_repair("{'key': 'value'}") == {"key": "value"}
    
    # 测试尾部多余的逗号
    assert jsons_load_repair('{"key": "value",}') == {"key": "value"}
    
    # 测试注释
    assert jsons_load_repair('''
    {
        // 这是注释
        "key": "value" # 这也是注释
    }
    ''') == {"key": "value"}

def test_wait_strategy_basic():
    """测试基本等待策略"""
    wait_func = wait_random_exponential_with_rate_limit(
        multiplier=1,
        min_seconds=4,
        max_seconds=60
    )
    
    # 创建一个模拟的retry_state
    retry_state = MagicMock()
    retry_state.attempt_number = 1
    retry_state.outcome.exception.return_value = Exception("Generic error")
    
    # 测试基本等待时间
    wait_time = wait_func(retry_state)
    assert 4 <= wait_time <= 60

def test_wait_strategy_rate_limit():
    """测试速率限制的等待策略"""
    wait_func = wait_random_exponential_with_rate_limit(
        multiplier=1,
        min_seconds=4,
        max_seconds=60
    )
    
    # 创建一个模拟的retry_state，模拟速率限制错误
    retry_state = MagicMock()
    retry_state.attempt_number = 1
    retry_state.outcome.exception.return_value = RateLimitError(
        message="Rate limit exceeded",
        response=MagicMock(status_code=429),
        body={"error": {"message": "Rate limit exceeded"}}
    )
    
    # 测试速率限制时的等待时间
    wait_time = wait_func(retry_state)
    assert wait_time >= 12  # 速率限制时应该至少是基础等待时间的3倍
    assert wait_time <= 300  # 但不应超过5分钟

def test_wait_strategy_consecutive_calls():
    """测试连续调用的等待策略"""
    wait_func = wait_random_exponential_with_rate_limit(
        multiplier=1,
        min_seconds=4,
        max_seconds=60
    )
    
    # 创建模拟的retry_state
    retry_state = MagicMock()
    retry_state.outcome.exception.return_value = Exception("Generic error")
    
    # 测试连续调用时的等待时间增长
    previous_wait = 0
    for attempt in range(1, 4):
        retry_state.attempt_number = attempt
        wait_time = wait_func(retry_state)
        assert wait_time >= previous_wait  # 等待时间应该递增
        previous_wait = wait_time 