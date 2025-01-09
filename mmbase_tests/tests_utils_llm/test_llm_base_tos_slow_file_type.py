import pytest
from unittest.mock import patch
from tenacity import RetryError

from mmbase.utils_llm.llm_base_tos import (
    upload_image_to_tos,
)

@pytest.fixture(autouse=True)
def mock_wait():
    """Mock等待函数,避免实际的等待时间"""
    def no_wait(multiplier=1, min=0, max=1):
        return 0
    with patch('mmbase.utils_llm.llm_base_tos.wait_exponential', no_wait):
        yield

@patch('mmbase.utils_llm.llm_base_tos._upload_image_to_tos_core', return_value="http://fake.url")
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