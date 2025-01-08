import pytest
from unittest.mock import patch, MagicMock
import os
from tenacity import RetryError, wait_none

from ctn2md.utils_llm.llm_base_oss import (
    upload_image_to_oss,
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

@pytest.fixture(autouse=True)
def mock_retry():
    """Mock重试装饰器，使用 wait_none 来立即重试而不等待"""
    with patch('tenacity.wait_exponential', return_value=wait_none()):
        yield

@pytest.fixture(autouse=True)
def mock_http_client():
    """Mock HTTP客户端，避免实际的网络请求"""
    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__enter__.return_value.head.return_value = mock_response
        yield mock_client

@patch('ctn2md.utils_llm.llm_base_oss._upload_image_to_oss_core')
def test_file_type_validation(mock_upload):
    """测试文件类型验证"""
    mock_upload.return_value = "http://fake.url"
    
    # 只测试一个有效文件类型
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        result = upload_image_to_oss("test.jpg")
        assert result == "http://fake.url"

    # 测试一个无效文件类型
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        with pytest.raises(RetryError) as exc_info:
            upload_image_to_oss("test.pdf")
        assert isinstance(exc_info.value.__cause__, ValueError)
        assert "Unsupported file type" in str(exc_info.value.__cause__)

@patch('os.path.exists')
def test_file_existence_check(mock_exists):
    """测试文件存在性检查"""
    mock_exists.return_value = False
    with pytest.raises(RetryError) as exc_info:
        upload_image_to_oss("nonexistent.jpg")
    assert isinstance(exc_info.value.__cause__, FileNotFoundError)
    assert "Image file not found" in str(exc_info.value.__cause__)

@patch('oss2.Bucket')
@patch('oss2.Auth')
def test_upload_failure_retry(mock_auth, mock_bucket, test_image):
    """测试上传失败重试机制"""
    mock_bucket_instance = MagicMock()
    mock_bucket.return_value = mock_bucket_instance
    
    # 模拟上传失败
    mock_bucket_instance.object_exists.return_value = False
    mock_bucket_instance.put_object.side_effect = Exception("Upload failed")
    
    # 验证重试后仍然失败
    with pytest.raises(RetryError) as exc_info:
        upload_image_to_oss(test_image)
    assert "Upload failed" in str(exc_info.value.__cause__)
    
    # 验证重试了3次
    assert mock_bucket_instance.put_object.call_count == 3 