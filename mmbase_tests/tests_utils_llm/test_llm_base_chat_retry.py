"""
LLM重试机制测试 - 测试各种错误情况下的重试行为
"""

import unittest
from unittest.mock import Mock, patch
import openai
import httpx

from mmbase.utils_llm.llm_base import (
    chat_gpt_json,
    DEFAULT_RETRY_NUM
)

class TestLLMChatRetry(unittest.TestCase):
    """专门测试LLM对话的重试机制"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_client = Mock()
        self.test_messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"}
        ]
        
    def _mock_chat_response(self, content: str) -> Mock:
        """创建模拟的API响应"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=content))]
        return mock_response
    
    def test_retry_on_network_error(self):
        """测试网络错误时的重试机制"""
        # 模拟连续失败直到最后一次成功
        failures = [httpx.RequestError("Connection failed")] * (DEFAULT_RETRY_NUM - 1)
        self.mock_client.chat.completions.create.side_effect = [
            *failures,
            self._mock_chat_response('{"result": "success"}')  # 最后一次成功
        ]
        
        with patch('time.sleep'):  # 避免实际等待
            result = chat_gpt_json(
                messages=self.test_messages,
                client=self.mock_client
            )
            
        self.assertEqual(result, {"result": "success"})
        self.assertEqual(
            self.mock_client.chat.completions.create.call_count,
            DEFAULT_RETRY_NUM
        )
    
    def test_retry_on_rate_limit(self):
        """测试限流错误时的重试机制"""
        error_response = httpx.Response(
            status_code=429,  # Rate limit status code
            content=b'{"error": "Rate limit exceeded"}',
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        )
        rate_limit_error = openai.RateLimitError(
            message="Rate limit exceeded",
            response=error_response,
            body={"error": "Rate limit exceeded"}
        )
        
        self.mock_client.chat.completions.create.side_effect = [
            rate_limit_error,  # 第1次失败
            rate_limit_error,  # 第2次失败
            self._mock_chat_response('{"result": "success"}')  # 第3次成功
        ]
        
        with patch('time.sleep'):  # 避免实际等待
            result = chat_gpt_json(
                messages=self.test_messages,
                client=self.mock_client
            )
            
        self.assertEqual(result, {"result": "success"})
        self.assertEqual(self.mock_client.chat.completions.create.call_count, 3)
            
    def test_no_retry_on_bad_request(self):
        """测试不应该重试的错误类型"""
        error_response = httpx.Response(
            status_code=400,
            content=b'{"error": "Invalid request"}',
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        )
        error = openai.BadRequestError(
            message="Invalid request",
            response=error_response,
            body={"error": "Invalid request"}
        )
        self.mock_client.chat.completions.create.side_effect = error
            
        with self.assertRaises(openai.BadRequestError):
            chat_gpt_json(
                messages=self.test_messages,
                client=self.mock_client
            )
        # 验证只调用了一次，没有重试
        self.mock_client.chat.completions.create.assert_called_once()

if __name__ == '__main__':
    unittest.main() 