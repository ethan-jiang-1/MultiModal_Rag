PROMPT_INSTRUCT_IMG2MD_QWEN = """
# Task
Convert PDF page to Markdown, focusing on content that provides actual knowledge or information to readers.

# Core Rules
1. Content Value Assessment
   - Key Question: "Does this text provide actual information to readers?"
   - Include Content When:
     * It teaches something new
     * It provides context or explanation
     * It connects ideas or concepts
     * It presents technical details
   - Exclude Content When:
     * It only describes document structure (page numbers, sections)
     * It repeats across pages (headers, footers)
     * It serves administrative purposes only
     * It would make no sense if read alone

2. Document Structure
   - Heading Hierarchy:
     * Level 1 (#): Document title only
     * Level 2 (##): Major sections
     * Level 3 (###): Subsections
     * Level 4 (####): Subsubsections
   - Identify Sections By:
     * Numbering patterns (1., 1.1., I., 一., 第一章)
     * Visual prominence
     * Content relationships
   - Maintain Consistency:
     * Keep parallel sections at same level
     * Preserve original hierarchy
     * Ensure logical content flow

3. Image Handling
   - Process red-rectangle-marked images only
   - Format: ![Title](<EXACT-Filename> "Description")
   - Rules:
     * Use only filenames with 'img'
     * Each filename once only
     * Keep original positions
     * Provide meaningful titles (3-10 words)
     * Write descriptive captions (2-4 sentences)

# Image Information
{inst_img_rects}
"""

PROMPT_INSTRUCT_IMG2MD_QWEN_IMG_RECTS = """
# Image Processing Guide
- Each red box marks one image
- Filename in top-left of box: {img_rects}
- Format: ![Title](<Filename> "Caption")
- Keep original positions
- Ensure meaningful descriptions

# Validation
- Use exact filenames
- Include title and caption
- Follow markdown syntax
"""


