import os
#import json
import pytest
from unittest.mock import patch, MagicMock
from deepdiff import DeepDiff
from ctn2md.utils.util_llm_diag import (
    get_chat_messages,
    set_question_num,
    get_question_num,
    get_next_question_num,
    save_llm_diag_messages,
    save_llm_diag_prompt,
    load_llm_diag,
    do_diag_reproduce,
    _json_loads_repair,
    ENV_QUESTION_NUM,
    LLM_DIAG_SEP,
    LLM_DIAG_LED,
    LLM_DIAG_ROL,
)


def test_get_chat_messages():
    """测试生成对话消息格式"""
    system_prompt = "You are a helpful assistant."
    user_prompt = "Hello!"
    
    messages = get_chat_messages(system_prompt, user_prompt)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == system_prompt
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == user_prompt


def test_question_num_operations():
    """测试问题编号相关操作"""
    # 测试设置和获取
    set_question_num(5)
    assert get_question_num() == 5
    assert os.environ[ENV_QUESTION_NUM] == "5"
    
    # 测试获取下一个编号
    next_num = get_next_question_num()
    assert next_num == 6
    assert get_question_num() == 6
    
    # 测试默认值
    os.environ.pop(ENV_QUESTION_NUM, None)
    assert get_question_num() == 0


@pytest.fixture
def temp_work_dir(tmp_path):
    """创建临时工作目录"""
    work_dir = tmp_path / "_work" / "llm_dialogs"
    work_dir.mkdir(parents=True)
    return work_dir


@pytest.fixture
def mock_root_dir(temp_work_dir, monkeypatch):
    """模拟项目根目录"""
    def mock_get_root_dir():
        return str(temp_work_dir.parent.parent)
    
    monkeypatch.setattr("ctn2md.utils.util_llm_diag._get_root_dir", mock_get_root_dir)
    return mock_get_root_dir()


def test_save_llm_diag_messages(mock_root_dir, temp_work_dir):
    """测试保存LLM对话记录"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
    response = {"choices": [{"message": {"content": "Hi there!"}}]}
    
    set_question_num(1)
    save_llm_diag_messages(
        messages=messages,
        response=response,
        model="gpt4-o",
        prefix="test",
        is_json_response=True
    )
    
    # 验证文件是否创建
    expected_file = temp_work_dir / "llm_test_q1.txt"
    assert expected_file.exists()
    
    # 验证文件内容
    content = expected_file.read_text(encoding='utf-8')
    assert LLM_DIAG_SEP in content
    assert "You are a helpful assistant" in content
    assert "Hi there!" in content


def test_save_llm_diag_prompt(mock_root_dir, temp_work_dir):
    """测试保存简单提示词对话记录"""
    prompt = "Hello!"
    system_prompt = "You are a helpful assistant."
    response = "Hi there!"
    
    set_question_num(1)
    save_llm_diag_prompt(
        prompt=prompt,
        response=response,
        system_prompt=system_prompt,
        prefix="test",
        is_json_response=False
    )
    
    # 验证文件是否创建
    expected_file = temp_work_dir / "llm_test_q1.txt"
    assert expected_file.exists()
    
    # 验证文件内容
    content = expected_file.read_text(encoding='utf-8')
    assert system_prompt in content
    assert prompt in content
    assert response in content


def test_load_llm_diag(mock_root_dir, temp_work_dir):
    """测试加载LLM对话记录"""
    # 创建测试文件
    test_content = (
        f"{LLM_DIAG_LED}role{LLM_DIAG_ROL}system\n"
        f"{LLM_DIAG_LED}content{LLM_DIAG_ROL}You are a helpful assistant.\n\n"
        f"{LLM_DIAG_LED}role{LLM_DIAG_ROL}user\n"
        f"{LLM_DIAG_LED}content{LLM_DIAG_ROL}Hello!\n\n"
        f"{LLM_DIAG_SEP}\n"
        '{"response": "Hi there!"}\n'
        f"{LLM_DIAG_SEP}\n"
        '{"model": "gpt4-o", "temperature": 0.3, "top_p": 0.9, "ver": 1.1}\n'
    )
    
    test_file = temp_work_dir / "test_dialog.txt"
    test_file.write_text(test_content, encoding='utf-8')
    
    # 加载并验证
    messages, answer, extra = load_llm_diag(str(test_file))
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert answer == {"response": "Hi there!"}
    assert extra["model"] == "gpt4-o"
    assert extra["ver"] == 1.1


@pytest.mark.parametrize("input_json,expected", [
    ('{"key": "value"}', {"key": "value"}),  # 正常JSON
    ("{'key': 'value'}", {"key": "value"}),  # 使用单引号
    ('{"key": value}', {"key": "value"}),    # 缺少引号
])
def test_json_loads_repair(input_json, expected):
    """测试JSON修复功能"""
    result = _json_loads_repair(input_json)
    assert result == expected


@patch("ctn2md.utils.util_llm_diag._get_azure_gpt_client")
@patch("ctn2md.utils.util_llm_diag.chat_gpt_json")
def test_do_diag_reproduce(mock_chat_gpt_json, mock_get_client, mock_root_dir, temp_work_dir):
    """测试诊断重现功能"""
    # 创建测试文件
    test_content = (
        f"{LLM_DIAG_LED}role{LLM_DIAG_ROL}system\n"
        f"{LLM_DIAG_LED}content{LLM_DIAG_ROL}You are a helpful assistant.\n\n"
        f"{LLM_DIAG_LED}role{LLM_DIAG_ROL}user\n"
        f"{LLM_DIAG_LED}content{LLM_DIAG_ROL}Hello!\n\n"
        f"{LLM_DIAG_SEP}\n"
        '{"response": "Hi there!"}\n'
        f"{LLM_DIAG_SEP}\n"
        '{"model": "gpt4-o", "temperature": 0.3, "top_p": 0.9, "ver": 1.1, "is_json_response": true}\n'
    )
    
    test_file = temp_work_dir / "test_dialog.txt"
    test_file.write_text(test_content, encoding='utf-8')
    
    # 模拟新的响应
    mock_chat_gpt_json.return_value = {"response": "Hello there!"}
    mock_get_client.return_value = MagicMock()
    
    # 执行重现
    answer_old, answer_new, diff = do_diag_reproduce(str(test_file))
    
    assert answer_old == {"response": "Hi there!"}
    assert answer_new == {"response": "Hello there!"}
    assert isinstance(diff, DeepDiff)


def test_invalid_file_format(temp_work_dir):
    """测试无效文件格式处理"""
    # 创建格式无效的测试文件
    test_file = temp_work_dir / "invalid_format.txt"
    test_file.write_text("Invalid content without proper sections", encoding='utf-8')
    
    with pytest.raises(ValueError, match="Invalid file format"):
        load_llm_diag(str(test_file))


def test_empty_messages():
    """测试空消息列表处理"""
    with pytest.raises(ValueError, match="Messages cannot be empty"):
        save_llm_diag_messages([], "response") 