import pytest
from unittest.mock import patch, MagicMock
from tenacity import RetryError

from ctn2md.utils_llm.llm_base_oss import (
    upload_image_to_oss,
    _upload_image_to_oss_core,
)

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

def test_upload_core_failure(mock_oss):
    """直接测试上传核心函数失败的情况"""
    with pytest.raises(Exception) as exc_info:
        _upload_image_to_oss_core("test/object.jpg", "test.jpg")
    assert "Upload failed with status 403" in str(exc_info.value)

@patch('ctn2md.utils_llm.llm_base_oss._upload_image_to_oss_core')
def test_upload_failure_retry_count(mock_upload):
    """测试上传失败时的重试次数"""
    mock_upload.side_effect = Exception("Upload failed")
    
    with pytest.raises(RetryError):
        upload_image_to_oss("test.jpg")
    
    # 验证重试了3次
    assert mock_upload.call_count == 3
    # 验证每次调用的参数都一样
    for call_args in mock_upload.call_args_list:
        assert call_args[0][0].endswith("/test.jpg")  # object_name应该以文件名结尾
        assert call_args[0][1] == "test.jpg"  # image_path参数

@patch('ctn2md.utils_llm.llm_base_oss._upload_image_to_oss_core')
def test_upload_success_no_retry(mock_upload):
    """测试上传成功时不会重试"""
    mock_upload.return_value = "http://fake.url"
    
    result = upload_image_to_oss("test.jpg")
    
    # 验证只调用了一次
    assert mock_upload.call_count == 1
    assert result == "http://fake.url" 