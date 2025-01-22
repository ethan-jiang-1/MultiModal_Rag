"""
LLM对话功能测试 - 测试JSON和文本格式的对话功能
"""

import unittest
from unittest.mock import Mock, patch
import json
import openai
import httpx

from mmbase.utils_llm.llm_base import (
    chat_gpt_json,
    chat_gpt_plain,
    jsons_load_repair,
    DEFAULT_RETRY_NUM
)

class TestLLMChatBasic(unittest.TestCase):
    """测试LLM基本对话功能"""
    
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
        
    def test_json_chat_basic(self):
        """测试基本的JSON对话"""
        expected_response = {"response": "Hello! How can I help?"}
        mock_response = self._mock_chat_response(json.dumps(expected_response))
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = chat_gpt_json(
            messages=self.test_messages,
            client=self.mock_client
        )
        
        self.assertEqual(result, expected_response)
        self.mock_client.chat.completions.create.assert_called_once()
        
    def test_json_chat_parameters(self):
        """测试JSON对话的参数设置"""
        mock_response = self._mock_chat_response('{"result": "success"}')
        self.mock_client.chat.completions.create.return_value = mock_response
        
        chat_gpt_json(
            messages=self.test_messages,
            model="gpt-4",
            temperature=0.5,
            top_p=0.8,
            client=self.mock_client
        )
        
        call_kwargs = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["model"], "gpt-4")
        self.assertEqual(call_kwargs["temperature"], 0.5)
        self.assertEqual(call_kwargs["top_p"], 0.8)
        self.assertEqual(call_kwargs["response_format"], {"type": "json_object"})
        
    def test_plain_chat_basic(self):
        """测试基本的文本对话"""
        expected_text = "Hello! How can I help?"
        mock_response = self._mock_chat_response(expected_text)
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = chat_gpt_plain(
            messages=self.test_messages,
            client=self.mock_client
        )
        
        self.assertEqual(result, expected_text)
        call_kwargs = self.mock_client.chat.completions.create.call_args[1]
        self.assertNotIn("response_format", call_kwargs)
        
    def test_json_repair(self):
        """测试JSON修复功能"""
        # 测试缺少引号的JSON
        invalid_json = '{key: "value"}'
        repaired = jsons_load_repair(invalid_json)
        self.assertEqual(repaired, {"key": "value"})
        
        # 测试多余逗号的JSON
        invalid_json = '{"key": "value",}'
        repaired = jsons_load_repair(invalid_json)
        self.assertEqual(repaired, {"key": "value"})
        
    def test_empty_messages(self):
        """测试空消息列表 - 基本验证"""
        # 完全禁用重试机制
        with patch('mmbase.utils_llm.llm_base.retry', lambda *args, **kwargs: lambda f: f):
            with self.assertRaises(ValueError):
                chat_gpt_json(messages=[], client=self.mock_client)

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