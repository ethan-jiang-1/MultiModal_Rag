PROMPT_INSTRUCT_IMG2MD_QWEN_START = """
# Task:
Perform OCR on the image.
- Recognize text, list, table and image.
- Convert tables to Markdown format.
- Convert image to markdown format with proper content in ![]()
- Use headings, paragraphs, lists and tables for structure.
- Ignore headers and footers.
- For figures: use `![Figure X](Figure X "caption")`.
{inst_img_rects}

# Output:
- Provide the first portion of text in Markdown format.
- Add "[ocr_end]" only when all OCR content has been output.
"""

PROMPT_INSTRUCT_IMG2MD_QWEN_START_IMG_RECTS = """
- 图片中用红色框和名称( {img_rects} )标注出了一些区域。如果区域是表格或者图片，使用 ![]() 的形式插入到输出内容中，否则直接输出文字内容。
"""

PROMPT_INSTRUCT_IMG2MD_QWEN_CONTINUE = """
# Task:
Continue the OCR task and provide the next portion in Markdown format.
- Add "[ocr_end]" only when all OCR content has been output.
"""

