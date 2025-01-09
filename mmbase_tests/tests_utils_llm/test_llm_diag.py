import pytest
from unittest.mock import patch 
#import os
#import json
from mmbase.utils_llm.llm_diag import (
    get_chat_messages,
    save_llm_diag_messages,
    get_question_num,
    set_question_num,
    get_next_question_num 
)

# Fixtures
@pytest.fixture
def sample_messages():
    return [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello!"}
    ]

@pytest.fixture
def sample_response():
    return {"content": "Hi there!", "role": "assistant"}

@pytest.fixture
def mock_llm_file(tmp_path):
    content = """~~~~role::::system
~~~~content::::You are a helpful assistant

~~~~role::::user
~~~~content::::Hello!

~~~~--------~~~~

{
    "content": "Hi there!",
    "role": "assistant"
}

~~~~--------~~~~

{
    "top_p": 0.8,
    "temperature": 0.2,
    "is_json_response": true,
    "model": "gpt4-o",
    "ver": 1.1,
    "max_token": null
}"""
    file_path = tmp_path / "test_llm_dialog.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(file_path)

# Tests for basic utility functions
def test_get_chat_messages():
    system_prompt = "You are a helpful assistant"
    user_prompt = "Hello!"
    messages = get_chat_messages(system_prompt, user_prompt)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == system_prompt
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == user_prompt

def test_question_num_operations():
    # Test setting and getting question number
    set_question_num(5)
    assert get_question_num() == 5
    
    # Test getting next question number
    next_num = get_next_question_num()
    assert next_num == 6
    assert get_question_num() == 6

# Tests for file operations
def test_save_llm_diag_messages(tmp_path, sample_messages, sample_response):
    with patch('mmbase.utils_llm.llm_diag._get_root_dir') as mock_root:
        mock_root.return_value = str(tmp_path)
        
        save_llm_diag_messages(
            messages=sample_messages,
            response=sample_response,
            prefix="test",
            question_num=1
        )
        
        expected_file = tmp_path / "_work/llm_dialogs/llm_test_q1.txt"
        assert expected_file.exists()
