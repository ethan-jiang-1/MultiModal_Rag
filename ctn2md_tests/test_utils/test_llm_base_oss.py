import pytest
from unittest.mock import patch, MagicMock
import os
from freezegun import freeze_time

from ctn2md.utils_llm.llm_base_oss import (
    _generate_unique_name,
    upload_image_to_oss,
)
from mmbase.utils.util_logging import setup_logger_handlers

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

@pytest.fixture(autouse=True)
def mock_http_client():
    """Mock HTTP客户端，避免实际的网络请求"""
    with patch('httpx.Client') as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.return_value.__enter__.return_value.head.return_value = mock_response
        yield mock_client

@pytest.fixture(autouse=True)
def setup():
    setup_logger_handlers()
    yield

@freeze_time("2024-01-08")
def test_generate_unique_name():
    """测试文件名生成函数"""
    result = _generate_unique_name("test/path/image.jpg")
    expected = "202401/image.jpg"
    assert result == expected

@patch('oss2.Bucket')
@patch('oss2.Auth')
@freeze_time("2024-01-08")
def test_upload_success(mock_auth, mock_bucket, test_image):
    """测试成功上传场景"""
    mock_bucket_instance = MagicMock()
    mock_bucket.return_value = mock_bucket_instance
    
    mock_bucket_instance.object_exists.return_value = False
    mock_bucket_instance.put_object.return_value = MagicMock(status=200, etag="fake-etag")
    mock_bucket_instance.get_object_meta.return_value = MagicMock(status=200)
    mock_bucket_instance.sign_url.return_value = "http://fake.url?signature"

    result = upload_image_to_oss(test_image)
    
    assert result.startswith("http://fake.url")
    assert "ETag=fake-etag" in result 