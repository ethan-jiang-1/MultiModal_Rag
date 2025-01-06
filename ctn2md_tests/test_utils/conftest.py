import pytest
#from pathlib import Path

@pytest.fixture
def sample_markdown_file(tmp_path):
    """Create a temporary markdown file with test content."""
    content = """
    # Test Header
    
    This is a test markdown file.
    
    ![Test Image](test.jpg)
    
    [Test Link](http://test.com)
    
    <!-- Test Comment -->
    """
    md_file = tmp_path / "test.md"
    md_file.write_text(content)
    return md_file

@pytest.fixture
def sample_images():
    """Return a list of sample image references."""
    return [
        "test1.jpg",
        "http://example.com/image.png",
        "./relative/path/image.gif"
    ]

@pytest.fixture
def complex_markdown_content():
    """Return a complex markdown content for testing."""
    return """
    # Main Title
    
    ## Section 1
    
    This is **bold** and *italic* text.
    
    - List item 1
    - List item 2
    
    > Blockquote here
    
    ![Image 1](img1.jpg)
    ![Image 2](img2.png)
    
    [Link 1](http://example1.com)
    [Link 2](http://example2.com)
    
    <!-- Comment 1 -->
    <!-- Comment 2 -->
    
    ### Subsection
    
    ```python
    def test():
        pass
    ```
    """ 