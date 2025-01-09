import pytest
from unittest.mock import patch, MagicMock
import os
from openai import OpenAI, AzureOpenAI, OpenAIError
from dotenv import load_dotenv
load_dotenv()

from mmbase.utils_llm.llm_base import (
    get_azure_gpt_client,
    get_dashscope_client,
    get_ark_client
)

@pytest.fixture
def mock_env_azure():
    """模拟Azure环境变量"""
    env_vars = {
        'OPENAI_API_KEY': 'fake-azure-key',
        'OPENAI_BASE_URL': 'https://fake-azure-endpoint',
        'AZURE_OPENAI_VERSION': '2024-02-01'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def mock_env_dashscope():
    """模拟DashScope环境变量"""
    env_vars = {
        'DASHSCOPE_API_KEY': 'fake-dashscope-key'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def mock_env_ark():
    """模拟Ark环境变量"""
    env_vars = {
        'ARK_API_KEY': 'fake-ark-key'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

def test_azure_client_initialization(mock_env_azure):
    """测试Azure客户端初始化"""
    client = get_azure_gpt_client()
    
    assert isinstance(client, AzureOpenAI)
    assert client.api_key == mock_env_azure['OPENAI_API_KEY']
    assert str(client.base_url).rstrip('/') == mock_env_azure['OPENAI_BASE_URL'] + '/openai'

def test_dashscope_client_initialization(mock_env_dashscope):
    """测试DashScope客户端初始化"""
    client = get_dashscope_client()
    
    assert isinstance(client, OpenAI)
    assert client.api_key == mock_env_dashscope['DASHSCOPE_API_KEY']
    assert str(client.base_url).rstrip('/') == "https://dashscope.aliyuncs.com/compatible-mode/v1"

def test_ark_client_initialization(mock_env_ark):
    """测试Ark客户端初始化"""
    client = get_ark_client()
    
    assert isinstance(client, OpenAI)
    assert client.api_key == mock_env_ark['ARK_API_KEY']
    assert str(client.base_url).rstrip('/') == "https://ark.cn-beijing.volces.com/api/v3"

def test_missing_env_vars():
    """测试缺少环境变量的情况"""
    # 测试Azure客户端
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(OpenAIError):
            get_azure_gpt_client()
    
    # 测试DashScope客户端
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(OpenAIError):
            get_dashscope_client()
    
    # 测试Ark客户端
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(OpenAIError):
            get_ark_client()

@patch('openai.OpenAI')
@patch('openai.AzureOpenAI')
def test_client_api_calls(mock_azure, mock_openai):
    """测试客户端API调用"""
    # 配置mock
    mock_azure_instance = MagicMock()
    mock_azure.return_value = mock_azure_instance
    mock_openai_instance = MagicMock()
    mock_openai.return_value = mock_openai_instance
    
    # 模拟API调用失败
    mock_azure_instance.chat.completions.create.side_effect = OpenAIError("API Error")
    mock_openai_instance.chat.completions.create.side_effect = OpenAIError("API Error")
    
    # 测试Azure客户端
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'fake-key',
        'OPENAI_BASE_URL': 'https://fake-endpoint',
        'AZURE_OPENAI_VERSION': '2024-02-01'
    }):
        client = get_azure_gpt_client()
        with pytest.raises(OpenAIError):
            client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "test"}]
            )
    
    # 测试DashScope客户端
    with patch.dict(os.environ, {
        'DASHSCOPE_API_KEY': 'fake-key'
    }):
        client = get_dashscope_client()
        with pytest.raises(OpenAIError):
            client.chat.completions.create(
                model="qwen-max",
                messages=[{"role": "user", "content": "test"}]
            )
    
    # 测试Ark客户端
    with patch.dict(os.environ, {
        'ARK_API_KEY': 'fake-key'
    }):
        client = get_ark_client()
        with pytest.raises(OpenAIError):
            client.chat.completions.create(
                model="qwen-max",
                messages=[{"role": "user", "content": "test"}]
            ) 