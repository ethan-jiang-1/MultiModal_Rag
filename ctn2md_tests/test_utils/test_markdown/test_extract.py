import pytest
from ctn2md.utils.util_markdown import extract_pure_text_from_markdown

@pytest.mark.parametrize("input_md,expected", [
    (
        "# Header\nThis is text",
        "Header This is text"
    ),
    (
        "<!-- comment -->\nText with comment",
        "Text with comment"
    ),
    (
        "**Bold** and *italic*",
        "Bold and italic"
    ),
    (
        "1. First item\n2. Second item",
        "1. First item 2. Second item"
    ),
    (
        "> Quoted text\nNormal text",
        "> Quoted text Normal text"
    )
])
def test_extract_pure_text_normal(input_md, expected):
    """Test various markdown syntax removal cases."""
    result = extract_pure_text_from_markdown(input_md)
    assert result == expected

@pytest.mark.parametrize("input_md,expected", [
    (
        "![Alt text](url.jpg)\nText with image",
        "Alt text Text with image"
    ),
    (
        "[Link](http://example.com)\nText with link",
        "Link Text with link"
    )
])
def test_extract_pure_text_image(input_md, expected):
    """Test image and link text extraction."""
    result = extract_pure_text_from_markdown(input_md)
    assert result == expected


@pytest.mark.parametrize("input_md,expected", [
    (
        """    # Main Header
    
    ## Sub Header""",
        "Main Header Sub Header"
    )
])
def test_extract_pure_text_multiple_lines(input_md, expected):
    """Test multiple line header extraction."""
    result = extract_pure_text_from_markdown(input_md)
    assert result == expected

def xtestx_extract_pure_text_complex():
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
    expected = "Main Header Sub Header This is a bold text with italic and code Image Alt Link Text List item 1 List item 2 Blockquote text"
    
    result = extract_pure_text_from_markdown(complex_md)
    assert result == expected 