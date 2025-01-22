"""
LLM基本对话功能测试 - 测试基本的对话交互
"""

import unittest
from unittest.mock import Mock, patch
import json

from mmbase.utils_llm.llm_base import (
    chat_gpt_json,
    chat_gpt_plain,
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
        
    def test_empty_messages(self):
        """测试空消息列表 - 基本验证"""
        # 完全禁用重试机制
        with patch('mmbase.utils_llm.llm_base.retry', lambda *args, **kwargs: lambda f: f):
            with self.assertRaises(ValueError):
                chat_gpt_json(messages=[], client=self.mock_client)

if __name__ == '__main__':
    unittest.main() 