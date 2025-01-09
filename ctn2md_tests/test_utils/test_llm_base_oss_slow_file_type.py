import pytest
from unittest.mock import patch, MagicMock
from tenacity import RetryError

from ctn2md.utils_llm.llm_base_oss import (
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
def setup():
    setup_logger_handlers()
    yield

@patch('ctn2md.utils_llm.llm_base_oss._upload_image_to_oss_core')
def test_file_type_validation(mock_upload):
    """测试文件类型验证"""
    mock_upload.return_value = "http://fake.url"
    
    # 测试有效文件类型
    result = upload_image_to_oss("test.jpg")
    assert result == "http://fake.url"
    result = upload_image_to_oss("test.jpeg")
    assert result == "http://fake.url"
    result = upload_image_to_oss("test.png")
    assert result == "http://fake.url"
    result = upload_image_to_oss("test.gif")
    assert result == "http://fake.url"

    # 测试无效文件类型
    with pytest.raises(RetryError) as exc_info:
        upload_image_to_oss("test.pdf")
    assert isinstance(exc_info.value.__cause__, ValueError)
    assert "Unsupported file type" in str(exc_info.value.__cause__) 