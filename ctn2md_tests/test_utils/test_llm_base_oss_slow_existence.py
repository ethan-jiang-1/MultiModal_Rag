import pytest
from unittest.mock import patch, MagicMock
from tenacity import RetryError

from ctn2md.utils_llm.llm_base_oss import upload_image_to_oss

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

def test_file_existence_check(mock_exists):
    """测试文件存在性检查"""
    mock_exists.return_value = False
    with pytest.raises(RetryError) as exc_info:
        upload_image_to_oss("nonexistent.jpg")
    assert isinstance(exc_info.value.__cause__, FileNotFoundError)
    assert "Image file not found" in str(exc_info.value.__cause__) 