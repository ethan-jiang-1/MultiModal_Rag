import pytest
from unittest.mock import patch
from tenacity import RetryError

from ctn2md.utils_llm.llm_base_tos import (
    upload_image_to_tos,
)

@pytest.fixture(autouse=True)
def mock_wait():
    """Mock掉等待时间，使其立即返回"""
    def no_wait(*args, **kwargs):
        return lambda retry_state: 0
    
    with patch('ctn2md.utils_llm.llm_base_tos.wait_exponential', no_wait):
        yield

@patch('ctn2md.utils_llm.llm_base_tos._upload_image_to_tos_core', return_value="http://fake.url")
@patch("os.path.exists", return_value=True)
def test_file_type_validation(mock_exists, mock_upload):
    """测试文件类型验证"""
    # 测试有效文件类型
    result = upload_image_to_tos("test.jpg")
    assert result == "http://fake.url"
    result = upload_image_to_tos("test.jpeg")
    assert result == "http://fake.url"
    result = upload_image_to_tos("test.png")
    assert result == "http://fake.url"
    result = upload_image_to_tos("test.gif")
    assert result == "http://fake.url"

    # 测试无效文件类型
    with pytest.raises(RetryError) as exc_info:
        upload_image_to_tos("test.pdf")
    assert isinstance(exc_info.value.__cause__, ValueError)
    assert "Unsupported file type" in str(exc_info.value.__cause__) 