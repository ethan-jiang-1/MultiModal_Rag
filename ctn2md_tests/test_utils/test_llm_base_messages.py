import pytest
from unittest.mock import patch
import os
from dotenv import load_dotenv
load_dotenv()

from ctn2md.utils_llm.llm_base import (
    get_gpt_messages,
    get_gpt_messages_multimodal,
    upload_image_to_cloud
)

def test_basic_message_construction():
    """测试基本消息构造"""
    # 测试完整消息（包含system和user）
    messages = get_gpt_messages(
        system_prompt="You are a helpful assistant",
        user_prompt="Hello!"
    )
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a helpful assistant"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hello!"
    
    # 测试空system prompt
    messages = get_gpt_messages(
        system_prompt="",
        user_prompt="Hello!"
    )
    assert len(messages) == 2
    assert messages[0]["content"] == ""
    
    # 测试None system prompt
    messages = get_gpt_messages(
        system_prompt=None,
        user_prompt="Hello!"
    )
    assert len(messages) == 2
    assert messages[0]["content"] == "None"

@pytest.fixture
def mock_env():
    """模拟环境变量"""
    with patch.dict(os.environ, {
        'ENV_MODEL_FLOW': 'default',  # 默认使用OSS
    }):
        yield

@pytest.fixture
def mock_upload():
    """模拟上传函数"""
    with patch('ctn2md.utils_llm.llm_base_oss.upload_image_to_oss') as mock:
        mock.return_value = "https://fake-oss-url/image.jpg"
        yield mock

def test_multimodal_message_with_local_image(mock_env, mock_upload):
    """测试带本地图片的多模态消息构造"""
    messages = get_gpt_messages_multimodal(
        system_prompt="Analyze this image",
        user_prompt="What's in this image?",
        image_path_or_url="local/path/image.jpg"
    )
    
    # 验证消息结构
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"][0]["type"] == "text"
    assert messages[0]["content"][0]["text"] == "Analyze this image"
    
    assert messages[1]["role"] == "user"
    assert len(messages[1]["content"]) == 2
    assert messages[1]["content"][0]["type"] == "text"
    assert messages[1]["content"][1]["type"] == "image_url"
    assert messages[1]["content"][1]["image_url"]["url"] == "https://fake-oss-url/image.jpg"
    
    # 验证上传函数被调用
    mock_upload.assert_called_once_with("local/path/image.jpg")

def test_multimodal_message_with_remote_url():
    """测试带远程URL的多模态消息构造"""
    remote_url = "https://example.com/image.jpg"
    messages = get_gpt_messages_multimodal(
        system_prompt="Analyze this image",
        user_prompt="What's in this image?",
        image_path_or_url=remote_url
    )
    
    # 验证消息结构
    assert len(messages) == 2
    assert messages[1]["content"][1]["image_url"]["url"] == remote_url

@patch.dict(os.environ, {'ENV_MODEL_FLOW': 'ark'})
@patch('ctn2md.utils_llm.llm_base_tos.upload_image_to_tos')
def test_image_upload_selection_tos(mock_tos_upload):
    """测试TOS上传选择"""
    mock_tos_upload.return_value = "https://fake-tos-url/image.jpg"
    
    result = upload_image_to_cloud("test.jpg")
    assert result == "https://fake-tos-url/image.jpg"
    mock_tos_upload.assert_called_once_with("test.jpg")

@patch.dict(os.environ, {'ENV_MODEL_FLOW': 'default'})
@patch('ctn2md.utils_llm.llm_base_oss.upload_image_to_oss')
def test_image_upload_selection_oss(mock_oss_upload):
    """测试OSS上传选择"""
    mock_oss_upload.return_value = "https://fake-oss-url/image.jpg"
    
    result = upload_image_to_cloud("test.jpg")
    assert result == "https://fake-oss-url/image.jpg"
    mock_oss_upload.assert_called_once_with("test.jpg")

def test_error_handling():
    """测试错误处理"""
    # 测试无效的图片路径
    with pytest.raises(Exception):
        get_gpt_messages_multimodal(
            system_prompt="test",
            user_prompt="test",
            image_path_or_url="nonexistent.jpg"
        )
    
    # 测试上传失败
    with patch('ctn2md.utils_llm.llm_base_oss.upload_image_to_oss') as mock:
        mock.side_effect = Exception("Upload failed")
        with pytest.raises(Exception):
            upload_image_to_cloud("test.jpg") 