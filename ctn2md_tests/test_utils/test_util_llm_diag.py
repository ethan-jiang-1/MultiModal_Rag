import pytest
from unittest.mock import patch, MagicMock
#import os
#import json
from ctn2md.utils.util_llm_diag import (
    get_chat_messages,
    save_llm_diag_messages,
    load_llm_diag,
    get_question_num,
    set_question_num,
    get_next_question_num,
    do_diag_reproduce
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
    with patch('ctn2md.utils.util_llm_diag._get_root_dir') as mock_root:
        mock_root.return_value = str(tmp_path)
        
        save_llm_diag_messages(
            messages=sample_messages,
            response=sample_response,
            prefix="test",
            question_num=1
        )
        
        expected_file = tmp_path / "_work/llm_dialogs/llm_test_q1.txt"
        assert expected_file.exists()

def xtestx_load_llm_diag(mock_llm_file):
    # Debug prints
    with open(mock_llm_file, 'r') as f:
        file_content = f.read()
        print("\nFile contents:")
        print(file_content)
        
        # Print sections after splitting
        sections = file_content.split("\n\n~~~~--------~~~~\n\n")
        print("\nSections:")
        for i, section in enumerate(sections):
            print(f"\nSection {i}:")
            print(section)
        
    messages, answer, extra = load_llm_diag(mock_llm_file)
    
    # Debug prints
    print("\nParsed messages:")
    print(messages)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a helpful assistant"
    assert answer["content"] == "Hi there!"
    assert extra["model"] == "gpt4-o"
    assert extra["ver"] == 1.1

# Test error cases
def test_save_llm_diag_messages_empty_messages(tmp_path):
    with pytest.raises(ValueError, match="Messages cannot be empty"):
        save_llm_diag_messages(messages=[], response={})

def test_load_llm_diag_invalid_format(tmp_path):
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("invalid content")
    
    with pytest.raises(ValueError, match="Invalid file format: expected 3 sections"):
        load_llm_diag(str(invalid_file))

# Test do_diag_reproduce with mocks
@patch('ctn2md.utils.util_llm_diag._get_azure_gpt_client')
@patch('ctn2md.utils.util_llm_diag.chat_gpt_json')
def test_do_diag_reproduce(mock_chat_gpt_json, mock_get_client, mock_llm_file):
    # Mock the new response
    mock_chat_gpt_json.return_value = {
        "content": "Hi there!",
        "role": "assistant"
    }
    
    # Mock the client
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    answer_old, answer_new, diff = do_diag_reproduce(mock_llm_file)
    
    assert answer_old["content"] == "Hi there!"
    assert answer_new["content"] == "Hi there!"
    assert len(diff) == 0  # No differences in this case 