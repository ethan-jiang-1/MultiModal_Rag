import pytest
from unittest.mock import patch
from tenacity import RetryError

from ctn2md.utils_llm.llm_base_tos import upload_image_to_tos

@pytest.fixture(autouse=True)
def mock_wait():
    """Mock掉等待时间，使其立即返回"""
    def no_wait(*args, **kwargs):
        return lambda retry_state: 0
    
    with patch('ctn2md.utils_llm.llm_base_tos.wait_exponential', no_wait):
        yield

@patch('os.path.exists')
def test_file_existence_check(mock_exists):
    """测试文件存在性检查"""
    mock_exists.return_value = False
    with pytest.raises(RetryError) as exc_info:
        upload_image_to_tos("nonexistent.jpg")
    assert isinstance(exc_info.value.__cause__, FileNotFoundError)
    assert "Image file not found" in str(exc_info.value.__cause__) 