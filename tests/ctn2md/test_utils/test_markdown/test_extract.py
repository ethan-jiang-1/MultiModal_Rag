import pytest
from ctn2md.utils.util_markdown import extract_pure_text_from_markdown

@pytest.mark.parametrize("input_md,expected", [
    (
        "# Header\nThis is text",
        "HeaderThisistext"
    ),
    (
        "![image](url.jpg)\nText with image",
        "Textwithimage"
    ),
    (
        "[Link](http://example.com)\nText with link",
        "LinkTextwithlink"
    ),
    (
        "<!-- comment -->\nText with comment",
        "Textwithcomment"
    ),
    (
        "**Bold** and *italic*",
        "Boldanditalic"
    ),
])
def test_extract_pure_text(input_md, expected):
    """Test various markdown syntax removal cases."""
    result = extract_pure_text_from_markdown(input_md)
    assert result == expected

def test_extract_pure_text_complex():
    """Test complex markdown document with multiple elements."""
    complex_md = """
    # Main Header
    
    ## Sub Header
    
    This is a **bold** text with *italic* and `code`.
    
    ![Image Alt](image.jpg)
    
    [Link Text](http://example.com)
    
    <!-- This is a comment -->
    
    1. List item 1
    2. List item 2
    
    > Blockquote text
    """
    result = extract_pure_text_from_markdown(complex_md)
    # 验证所有格式标记都被移除，只保留纯文本
    assert "MainHeader" in result
    assert "SubHeader" in result
    assert "Thisisaboldtextwithitalicandcode" in result
    assert "Listitem1" in result
    assert "Listitem2" in result
    assert "Blockquotetext" in result
    assert "<!--" not in result
    assert "![" not in result
    assert "[" not in result 