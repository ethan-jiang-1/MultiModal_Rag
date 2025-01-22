"""
LLM重试机制测试 - 测试API调用重试功能
"""

import unittest
from unittest.mock import patch, Mock
import httpx
import openai

from mmbase.utils_llm.llm_base import (
    chat_gpt_json,
    DEFAULT_RETRY_NUM
)

class TestLLMRetry(unittest.TestCase):
    """测试LLM重试机制"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_client = Mock()
        self.mock_response = Mock()
        self.mock_response.choices = [Mock(message=Mock(content='{"result": "success"}'))]
        
    def test_retry_on_request_error(self):
        """测试网络请求错误时的重试"""
        self.mock_client.chat.completions.create.side_effect = [
            httpx.RequestError("Connection failed"),  # 第1次失败
            httpx.RequestError("Connection failed"),  # 第2次失败
            self.mock_response  # 第3次成功
        ]
        
        with patch('time.sleep') as mock_sleep:  # 避免实际等待
            result = chat_gpt_json(
                messages=[{"role": "user", "content": "test"}],
                client=self.mock_client
            )
            
        self.assertEqual(result, {"result": "success"})
        self.assertEqual(self.mock_client.chat.completions.create.call_count, 3)
        
        # 验证重试间隔
        sleep_calls = [args[0] for args, _ in mock_sleep.call_args_list]
        self.assertEqual(len(sleep_calls), 2)  # 两次重试，两次sleep
        self.assertTrue(all(4 <= t <= 60 for t in sleep_calls))  # 检查等待时间范围
        
    def test_retry_on_rate_limit(self):
        """测试限流错误时的重试"""
        self.mock_client.chat.completions.create.side_effect = [
            openai.RateLimitError("Rate limit exceeded"),  # 第1次失败
            self.mock_response  # 第2次成功
        ]
        
        with patch('time.sleep') as mock_sleep:
            result = chat_gpt_json(
                messages=[{"role": "user", "content": "test"}],
                client=self.mock_client
            )
            
        self.assertEqual(result, {"result": "success"})
        self.assertEqual(self.mock_client.chat.completions.create.call_count, 2)
        
        # 验证限流错误的特殊等待时间
        sleep_time = mock_sleep.call_args[0][0]
        self.assertTrue(sleep_time > 4)  # 限流错误应该有更长的等待时间
        
    def test_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        self.mock_client.chat.completions.create.side_effect = httpx.RequestError("Connection failed")
        
        with patch('time.sleep'), self.assertRaises(httpx.RequestError):
            chat_gpt_json(
                messages=[{"role": "user", "content": "test"}],
                client=self.mock_client
            )
            
        self.assertEqual(
            self.mock_client.chat.completions.create.call_count,
            DEFAULT_RETRY_NUM
        )
        
    def test_non_retryable_error(self):
        """测试不需要重试的错误"""
        self.mock_client.chat.completions.create.side_effect = ValueError("Invalid input")
        
        with patch('time.sleep'), self.assertRaises(ValueError):
            chat_gpt_json(
                messages=[{"role": "user", "content": "test"}],
                client=self.mock_client
            )
            
        # 不应该重试
        self.assertEqual(self.mock_client.chat.completions.create.call_count, 1)
        
    def test_retry_with_different_errors(self):
        """测试不同类型错误混合的情况"""
        self.mock_client.chat.completions.create.side_effect = [
            httpx.RequestError("Connection failed"),  # 网络错误
            openai.RateLimitError("Rate limit"),      # 限流错误
            ValueError("Invalid format"),             # 格式错误
            self.mock_response                        # 最后成功
        ]
        
        with patch('time.sleep'):
            result = chat_gpt_json(
                messages=[{"role": "user", "content": "test"}],
                client=self.mock_client
            )
            
        self.assertEqual(result, {"result": "success"})
        self.assertEqual(self.mock_client.chat.completions.create.call_count, 4)

if __name__ == '__main__':
    unittest.main() 