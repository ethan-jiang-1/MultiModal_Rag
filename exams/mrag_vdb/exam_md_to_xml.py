import rich 

from markdown import markdown
from bs4 import BeautifulSoup

def markdown_to_html_with_ids(markdown_text):
    """
    Convert a Markdown document to HTML with block-level elements annotated with unique IDs using BeautifulSoup.

    Args:
        markdown_text (str): The input Markdown text.

    Returns:
        str: The entire content converted to HTML with unique IDs for block-level elements.
    """
    # Convert Markdown to HTML
    html_content = markdown(markdown_text)

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Initialize ID counters
    paragraph_seq = 1
    table_seq = 1
    image_seq = 1
    list_seq = 1
    formula_seq = 1
    header_seq = 1
    blockquote_seq = 1
    hr_seq = 1

    # Assign unique IDs to block-level elements
    for element in soup.find_all(['p', 'table', 'img', 'ul', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'hr']):
        if element.name == 'p':
            element['id'] = f'paragraph_{paragraph_seq}'
            paragraph_seq += 1
        elif element.name == 'table':
            element['id'] = f'table_{table_seq}'
            table_seq += 1
        elif element.name == 'img':
            element['id'] = f'image_{image_seq}'
            image_seq += 1
        elif element.name == 'ul':
            element['id'] = f'list_{list_seq}'
            list_seq += 1
        elif element.name == 'pre':  # Assuming formulas are in <pre> tags
            element['id'] = f'formula_{formula_seq}'
            formula_seq += 1
        elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            element['id'] = f'header_{header_seq}'
            header_seq += 1
        elif element.name == 'blockquote':
            element['id'] = f'blockquote_{blockquote_seq}'
            blockquote_seq += 1
        elif element.name == 'hr':
            element['id'] = f'hr_{hr_seq}'
            hr_seq += 1

    # Return the modified HTML as a string
    return str(soup)

# Example usage
markdown_text = """# Example Document

## Section 1

This is a paragraph in section 1.

![A complex diagram](diagram.png "A very long image description")

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

- List item 1
- List item 2

> This is a blockquote.

---

## Section 2

This is a paragraph in section 2.

Another paragraph in section 2.

$$
int_a^b f(x) dx = F(b) - F(a)
$$

![Another diagram](diagram2.png "Another very detailed description")
"""

html_result = markdown_to_html_with_ids(markdown_text)
print(html_result)
print()
rich.print(html_result)