import pytest
from unittest.mock import MagicMock
from openai import OpenAI, RateLimitError, BadRequestError
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from tenacity import RetryError
from ctn2md.utils_llm.llm_base import (
    chat_gpt_json,
    chat_gpt_plain,
    get_gpt_messages
)

@pytest.fixture
def mock_messages():
    """模拟消息列表"""
    return get_gpt_messages(
        system_prompt="You are a helpful assistant",
        user_prompt="Hello!"
    )

@pytest.fixture
def mock_chat_completion():
    """模拟ChatCompletion响应"""
    completion = MagicMock(spec=ChatCompletion)
    message = MagicMock(spec=ChatCompletionMessage)
    message.content = '{"response": "Hello! How can I help you?"}'
    completion.choices = [MagicMock(message=message)]
    completion.model = "gpt-4"
    completion.usage = MagicMock(completion_tokens=20)
    return completion

@pytest.fixture
def mock_client():
    """模拟OpenAI客户端"""
    client = MagicMock(spec=OpenAI)
    completions = MagicMock()
    completions.create = MagicMock()
    chat = MagicMock()
    chat.completions = completions
    client.chat = chat
    return client

def test_chat_gpt_json_basic(mock_messages, mock_chat_completion, mock_client):
    """测试基本的JSON响应"""
    mock_client.chat.completions.create.return_value = mock_chat_completion
    
    result = chat_gpt_json(
        messages=mock_messages,
        model="gpt-4",
        client=mock_client
    )
    
    assert result == {"response": "Hello! How can I help you?"}
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4",
        messages=mock_messages,
        temperature=0.1,
        top_p=0.9,
        response_format={"type": "json_object"}
    )

def test_chat_gpt_json_empty_messages(mock_client):
    """测试空消息列表"""
    with pytest.raises(RetryError) as exc_info:
        chat_gpt_json(messages=[], client=mock_client)
    
    assert isinstance(exc_info.value.__cause__, ValueError)
    assert str(exc_info.value.__cause__) == "Messages cannot be empty"

def test_chat_gpt_json_rate_limit(mock_messages, mock_client, mock_chat_completion):
    """测试速率限制处理"""
    # 模拟连续的速率限制错误
    mock_client.chat.completions.create.side_effect = [
        RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={"error": {"message": "Rate limit exceeded"}}
        ),
        RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={"error": {"message": "Rate limit exceeded"}}
        ),
        mock_chat_completion  # 第三次尝试成功
    ]
    
    result = chat_gpt_json(
        messages=mock_messages,
        model="gpt-4",
        client=mock_client
    )
    
    assert result == {"response": "Hello! How can I help you?"}
    assert mock_client.chat.completions.create.call_count == 3

def test_chat_gpt_plain_basic(mock_messages, mock_client):
    """测试基本的文本响应"""
    # 模拟纯文本响应
    completion = MagicMock(spec=ChatCompletion)
    message = MagicMock(spec=ChatCompletionMessage)
    message.content = "Hello! How can I help you?"
    completion.choices = [MagicMock(message=message)]
    completion.model = "gpt-4"
    completion.usage = MagicMock(completion_tokens=20)
    mock_client.chat.completions.create.return_value = completion
    
    result = chat_gpt_plain(
        messages=mock_messages,
        model="gpt-4",
        client=mock_client
    )
    
    assert result == "Hello! How can I help you?"
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4",
        messages=mock_messages,
        temperature=0.1,
        top_p=0.9
    )

def test_chat_gpt_plain_empty_messages(mock_client):
    """测试空消息列表"""
    mock_client.chat.completions.create.side_effect = BadRequestError(
        message="Invalid 'messages': empty array",
        response=MagicMock(status_code=400),
        body={"error": {"message": "Invalid 'messages': empty array"}}
    )
    
    with pytest.raises(BadRequestError):
        chat_gpt_plain(messages=[], client=mock_client)

def test_chat_gpt_plain_rate_limit(mock_messages, mock_client, mock_chat_completion):
    """测试速率限制处理"""
    # 模拟连续的速率限制错误
    mock_client.chat.completions.create.side_effect = [
        RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={"error": {"message": "Rate limit exceeded"}}
        ),
        RateLimitError(
            message="Rate limit exceeded",
            response=MagicMock(status_code=429),
            body={"error": {"message": "Rate limit exceeded"}}
        ),
        mock_chat_completion  # 第三次尝试成功
    ]
    
    result = chat_gpt_plain(
        messages=mock_messages,
        model="gpt-4",
        client=mock_client
    )
    
    assert result == '{"response": "Hello! How can I help you?"}'
    assert mock_client.chat.completions.create.call_count == 3

def test_chat_gpt_bad_request(mock_messages, mock_client):
    """测试错误请求处理"""
    mock_client.chat.completions.create.side_effect = BadRequestError(
        message="Invalid request",
        response=MagicMock(status_code=400),
        body={"error": {"message": "Invalid request"}}
    )
    
    with pytest.raises(BadRequestError):
        chat_gpt_json(
            messages=mock_messages,
            model="gpt-4",
            client=mock_client
        ) 