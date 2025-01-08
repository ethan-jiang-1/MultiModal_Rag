import pytest
from unittest.mock import patch, MagicMock
import os
from freezegun import freeze_time
from tenacity import RetryError

from ctn2md.utils_llm.llm_base_tos import (
    _generate_unique_name,
    upload_image_to_tos,
    ALLOWED_EXTENSIONS
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

@freeze_time("2024-01-08")
def test_generate_unique_name():
    """测试文件名生成函数"""
    result = _generate_unique_name("test/path/image.jpg")
    expected = "202401/image.jpg"
    assert result == expected

def test_file_type_validation():
    """测试文件类型验证"""
    # 测试有效文件类型
    for ext in ALLOWED_EXTENSIONS:
        test_path = f"test{ext}"
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("ctn2md.utils_llm.llm_base_tos._upload_image_to_tos_core") as mock_upload:
                mock_upload.return_value = "http://fake.url"
                upload_image_to_tos(test_path)  # 如果抛出异常，pytest会自动处理失败

    # 测试无效文件类型
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        with pytest.raises(RetryError):
            upload_image_to_tos("test.pdf")

def test_file_existence_check():
    """测试文件存在性检查"""
    with pytest.raises(RetryError):
        upload_image_to_tos("nonexistent.jpg")

@patch('tos.TosClient')
@patch('tos.Auth')
@patch('httpx.Client')
@freeze_time("2024-01-08")
def test_upload_success(mock_httpx, mock_auth, mock_tos, test_image, mock_env):
    """测试成功上传场景"""
    # 配置所有需要的mock
    mock_client = MagicMock()
    mock_tos.return_value = mock_client
    
    # Mock TOS操作的返回值
    mock_client.put_object.return_value = MagicMock(etag="fake-etag")
    
    # Mock httpx响应
    mock_http_client = MagicMock()
    mock_httpx.return_value.__enter__.return_value = mock_http_client
    mock_http_client.head.return_value = MagicMock(status_code=200)

    # 执行上传
    result = upload_image_to_tos(test_image)
    
    # 验证结果
    expected_url = f"https://fake-bucket.tos-cn-beijing.volces.com/202401/test_image.jpg"
    assert result == expected_url

@patch('tos.TosClient')
@patch('tos.Auth')
def test_upload_failure_retry(mock_auth, mock_tos, test_image, mock_env):
    """测试上传失败重试机制"""
    mock_client = MagicMock()
    mock_tos.return_value = mock_client
    
    # 模拟上传失败
    mock_client.put_object.side_effect = Exception("Upload failed")
    
    # 验证重试后仍然失败
    with pytest.raises(RetryError):
        upload_image_to_tos(test_image)
    
    # 验证重试次数（默认3次）
    assert mock_client.put_object.call_count == 3 