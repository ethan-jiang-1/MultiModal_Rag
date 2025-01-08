import pytest
from unittest.mock import patch, MagicMock
import os
from freezegun import freeze_time

from ctn2md.utils_llm.llm_base_tos import (
    _generate_unique_name,
    upload_image_to_tos,
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

@pytest.fixture
def mock_env():
    """Mock TOS环境变量"""
    env_vars = {
        'VOLC_ACCESSKEY': 'fake-key',
        'VOLC_SECRETKEY': 'fake-secret',
        'VOLC_ENDPOINT': 'tos-cn-beijing.volces.com',
        'VOLC_BUCKET_NAME': 'fake-bucket'
    }
    with patch.dict('os.environ', env_vars):
        yield env_vars

@pytest.fixture(autouse=True)
def mock_http_client():
    """Mock HTTP客户端，避免实际的网络请求"""
    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__enter__.return_value.head.return_value = mock_response
        yield mock_client

@freeze_time("2024-01-08")
def test_generate_unique_name():
    """测试文件名生成函数"""
    result = _generate_unique_name("test/path/image.jpg")
    expected = "202401/image.jpg"
    assert result == expected

@patch('tos.TosClient')
@patch('tos.Auth')
@freeze_time("2024-01-08")
def test_upload_success(mock_auth, mock_tos, test_image, mock_env):
    """测试成功上传场景"""
    mock_client = MagicMock()
    mock_tos.return_value = mock_client
    
    mock_client.put_object.return_value = MagicMock(etag="fake-etag")

    result = upload_image_to_tos(test_image)
    
    expected_url = f"https://fake-bucket.tos-cn-beijing.volces.com/202401/test_image.jpg"
    assert result == expected_url 