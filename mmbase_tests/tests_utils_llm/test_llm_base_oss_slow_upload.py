import pytest
from unittest.mock import patch, MagicMock
from tenacity import RetryError

from mmbase.utils_llm.llm_base_oss import (
    upload_image_to_oss,
)
from mmbase.utils.util_logging import setup_logger_handlers

@pytest.fixture(autouse=True)
def mock_exists():
    """Mock文件存在检查,默认返回True"""
    with patch('os.path.exists', return_value=True) as mock:
        yield mock

@pytest.fixture(autouse=True)
def mock_http_client():
    """Mock HTTP客户端,避免实际的网络请求"""
    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__enter__.return_value.head.return_value = mock_response
        yield mock_client

@pytest.fixture(autouse=True)
def mock_oss():
    """Mock OSS操作"""
    with patch('oss2.Auth'), \
         patch('oss2.Bucket') as mock_bucket, \
         patch('builtins.open', create=True):
        mock_bucket.return_value.object_exists.return_value = False
        mock_result = MagicMock()
        mock_result.status = 403
        mock_bucket.return_value.put_object.return_value = mock_result
        yield mock_bucket

@pytest.fixture(autouse=True)
def setup():
    setup_logger_handlers()
    yield

@pytest.fixture(autouse=True)
def mock_wait():
    """Mock等待函数,避免实际的等待时间"""
    def no_wait(multiplier=1, min=0, max=1):
        return 0
    with patch('mmbase.utils_llm.llm_base_oss.wait_exponential', no_wait):
        yield

@patch('mmbase.utils_llm.llm_base_oss._upload_image_to_oss_core')
def test_upload_failure(mock_upload):
    """测试上传失败的情况"""
    mock_upload.side_effect = Exception("Upload failed")
    
    with pytest.raises(RetryError):
        upload_image_to_oss("test.jpg")

@patch('mmbase.utils_llm.llm_base_oss._upload_image_to_oss_core')
def test_upload_failure_retry_count(mock_upload):
    """测试上传失败时的重试次数"""
    mock_upload.side_effect = Exception("Upload failed")
    
    with pytest.raises(RetryError):
        upload_image_to_oss("test.jpg")
    
    assert mock_upload.call_count == 3  # 默认重试3次

@patch('mmbase.utils_llm.llm_base_oss._upload_image_to_oss_core')
def test_upload_success_no_retry(mock_upload):
    """测试上传成功时不需要重试"""
    mock_upload.return_value = "http://fake.url"
    
    result = upload_image_to_oss("test.jpg")
    assert result == "http://fake.url"
    assert mock_upload.call_count == 1  # 成功时只调用一次 