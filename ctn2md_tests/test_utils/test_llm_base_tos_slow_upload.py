import pytest
from unittest.mock import patch, MagicMock
from tenacity import RetryError

from ctn2md.utils_llm.llm_base_tos import (
    upload_image_to_tos,
    _upload_image_to_tos_core,
)

@pytest.fixture(autouse=True)
def mock_wait():
    """Mock掉等待时间，使其立即返回"""
    def no_wait(*args, **kwargs):
        return lambda retry_state: 0
    
    with patch('ctn2md.utils_llm.llm_base_tos.wait_exponential', no_wait):
        yield

def test_upload_core_failure():
    """直接测试上传核心函数失败的情况"""
    mock_file = MagicMock()
    mock_file.__enter__.return_value = "fake_file_content"
    
    with patch('os.path.exists', return_value=True), \
         patch('tos.TosClient') as mock_tos, \
         patch('tos.Auth'), \
         patch('builtins.open', return_value=mock_file), \
         patch('httpx.Client') as mock_http:
        
        # 配置 HTTP 客户端
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_http.return_value.__enter__.return_value.head.return_value = mock_response
        
        # 配置 TOS 客户端
        mock_client = MagicMock()
        mock_tos.return_value = mock_client
        
        # 模拟上传失败 - 无 ETag
        result = MagicMock()
        delattr(result, 'etag')  # 移除 etag 属性
        mock_client.put_object.return_value = result
        
        with pytest.raises(Exception) as exc_info:
            _upload_image_to_tos_core("test/object.jpg", "test.jpg")
        assert "Upload failed: no ETag returned" in str(exc_info.value)

@patch('ctn2md.utils_llm.llm_base_tos._upload_image_to_tos_core')
def test_upload_failure_retry_count(mock_upload):
    """测试上传失败时的重试次数"""
    mock_upload.side_effect = Exception("Upload failed")
    
    with patch('os.path.exists', return_value=True):
        with pytest.raises(RetryError) as exc_info:
            upload_image_to_tos("test.jpg")
        assert isinstance(exc_info.value.__cause__, Exception)
        assert "Upload failed" in str(exc_info.value.__cause__)

@patch('ctn2md.utils_llm.llm_base_tos._upload_image_to_tos_core')
def test_upload_success_no_retry(mock_upload):
    """测试上传成功时不会重试"""
    mock_upload.return_value = "http://fake.url"
    
    with patch('os.path.exists', return_value=True):
        result = upload_image_to_tos("test.jpg")
        
        # 验证只调用了一次
        assert mock_upload.call_count == 1
        assert result == "http://fake.url" 