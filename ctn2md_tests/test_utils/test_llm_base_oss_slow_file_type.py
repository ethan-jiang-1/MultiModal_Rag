import pytest
from unittest.mock import patch, MagicMock
from tenacity import RetryError

from ctn2md.utils_llm.llm_base_oss import (
    upload_image_to_oss,
    validate_image_file_type,
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

def test_file_type_validation_direct():
    """直接测试文件类型验证函数"""
    # 测试有效文件类型
    validate_image_file_type("test.jpg")  # 不应该抛出异常
    validate_image_file_type("test.jpeg")  # 不应该抛出异常
    validate_image_file_type("test.png")  # 不应该抛出异常
    validate_image_file_type("test.gif")  # 不应该抛出异常

    # 测试无效文件类型
    with pytest.raises(ValueError) as exc_info:
        validate_image_file_type("test.pdf")
    assert "Unsupported file type" in str(exc_info.value)

@patch('ctn2md.utils_llm.llm_base_oss._upload_image_to_oss_core')
def test_upload_with_invalid_file_type(mock_upload):
    """测试通过上传函数的文件类型验证"""
    mock_upload.return_value = "http://fake.url"
    
    # 测试有效文件类型
    result = upload_image_to_oss("test.jpg")
    assert result == "http://fake.url"

    # 测试无效文件类型
    with pytest.raises(RetryError) as exc_info:
        upload_image_to_oss("test.pdf")
    assert isinstance(exc_info.value.__cause__, ValueError)
    assert "Unsupported file type" in str(exc_info.value.__cause__) 