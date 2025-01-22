"""
LLM JSON功能测试 - 测试JSON格式处理和修复功能
"""

import unittest
from unittest.mock import Mock
import json

from mmbase.utils_llm.llm_base import (
    chat_gpt_json,
    jsons_load_repair
)

class TestLLMChatJSON(unittest.TestCase):
    """测试LLM的JSON处理功能"""
    
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
        
    def test_json_response_parsing(self):
        """测试JSON响应解析"""
        test_cases = [
            # 标准JSON
            ('{"key": "value"}', {"key": "value"}),
            # 嵌套JSON
            ('{"outer": {"inner": 42}}', {"outer": {"inner": 42}}),
            # 数组JSON
            ('{"items": [1, 2, 3]}', {"items": [1, 2, 3]}),
        ]
        
        for input_json, expected in test_cases:
            mock_response = self._mock_chat_response(input_json)
            self.mock_client.chat.completions.create.return_value = mock_response
            
            result = chat_gpt_json(
                messages=self.test_messages,
                client=self.mock_client
            )
            
            self.assertEqual(result, expected)
            
    def test_json_repair(self):
        """测试JSON修复功能"""
        test_cases = [
            # 缺少引号的JSON
            ('{key: "value"}', {"key": "value"}),
            # 多余逗号的JSON
            ('{"key": "value",}', {"key": "value"}),
            # 单引号替换
            ("{'key': 'value'}", {"key": "value"}),
            # 缺少引号的嵌套JSON
            ('{outer: {inner: "value"}}', {"outer": {"inner": "value"}}),
        ]
        
        for invalid_json, expected in test_cases:
            repaired = jsons_load_repair(invalid_json)
            self.assertEqual(repaired, expected)
            
    def test_json_format_validation(self):
        """测试JSON格式验证"""
        mock_response = self._mock_chat_response('{"result": "success"}')
        self.mock_client.chat.completions.create.return_value = mock_response
        
        result = chat_gpt_json(
            messages=self.test_messages,
            client=self.mock_client
        )
        
        # 验证返回的是字典类型
        self.assertIsInstance(result, dict)
        # 验证API调用时设置了正确的响应格式
        call_kwargs = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_kwargs["response_format"], {"type": "json_object"})

if __name__ == '__main__':
    unittest.main() 