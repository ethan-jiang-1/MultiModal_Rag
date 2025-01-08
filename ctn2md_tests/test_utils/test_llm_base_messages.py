import pytest
from unittest.mock import patch
import os

from ctn2md.utils_llm.llm_base import (
    get_gpt_messages_multimodal,
    upload_image_to_cloud
)

@pytest.fixture
def test_image():
    """创建测试用的临时图片文件"""
    test_image_path = "test_image.jpg"
    with open(test_image_path, "wb") as f:
        f.write(b"fake image content")
    yield test_image_path
    # 清理测试文件
    if os.path.exists(test_image_path):
        os.remove(test_image_path)

@patch('ctn2md.utils_llm.llm_base.upload_image_to_cloud')
def test_multimodal_message_with_local_image(mock_upload, test_image):
    """测试本地图片的多模态消息构建"""
    mock_upload.return_value = "https://fake-url/image.jpg"
    
    messages = get_gpt_messages_multimodal(
        None,
        "Test prompt",
        test_image
    )
    
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"][0]["type"] == "text"
    assert messages[0]["content"][1]["type"] == "image_url"
    assert messages[0]["content"][1]["image_url"]["url"] == "https://fake-url/image.jpg"

@patch('ctn2md.utils_llm.llm_base.upload_image_to_cloud')
def test_multimodal_message_with_remote_url(mock_upload):
    """测试远程URL的多模态消息构建"""
    remote_url = "https://example.com/image.jpg"
    mock_upload.return_value = remote_url
    
    messages = get_gpt_messages_multimodal(
        None,
        "Test prompt",
        remote_url
    )
    
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"][0]["type"] == "text"
    assert messages[0]["content"][1]["type"] == "image_url"
    assert messages[0]["content"][1]["image_url"]["url"] == remote_url
    mock_upload.assert_not_called()

@patch.dict(os.environ, {'ENV_MODEL_FLOW': 'ark'})
@patch('ctn2md.utils_llm.llm_base_tos.upload_image_to_tos')
def test_image_upload_selection_tos(mock_tos_upload, test_image):
    """测试TOS上传选择"""
    mock_tos_upload.return_value = "https://fake-tos-url/image.jpg"
    
    result = upload_image_to_cloud(test_image)
    assert result == "https://fake-tos-url/image.jpg"
    mock_tos_upload.assert_called_once_with(test_image)

@patch.dict(os.environ, {'ENV_MODEL_FLOW': 'default'})
@patch('ctn2md.utils_llm.llm_base_oss.upload_image_to_oss')
def test_image_upload_selection_oss(mock_oss_upload, test_image):
    """测试OSS上传选择"""
    mock_oss_upload.return_value = "https://fake-oss-url/image.jpg"
    
    result = upload_image_to_cloud(test_image)
    assert result == "https://fake-oss-url/image.jpg"
    mock_oss_upload.assert_called_once_with(test_image)

@patch('ctn2md.utils_llm.llm_base_oss.upload_image_to_oss')
@patch('ctn2md.utils_llm.llm_base_tos.upload_image_to_tos')
@patch('os.path.exists')
def test_error_handling(mock_exists, mock_tos_upload, mock_oss_upload):
    """测试错误处理"""
    mock_exists.return_value = True
    
    # 测试无效的文件类型
    with pytest.raises(ValueError):
        upload_image_to_cloud("test.pdf")
    
    # 测试文件不存在
    mock_exists.return_value = False
    with pytest.raises(ValueError):
        upload_image_to_cloud("nonexistent.jpg") 