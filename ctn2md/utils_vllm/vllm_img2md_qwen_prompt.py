PROMPT_INSTRUCT_IMG2MD_QWEN = """
# Task
Convert PDF page to Markdown through direct content conversion:
- Convert EXACTLY what appears in the PDF
- Do NOT add interpretations or summaries
- Do NOT explain or describe the content
- Keep ONLY the original text and structure
- Never output image processing metadata or instructions

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
   - Heading Detection:
     * Only convert text to heading if it starts a new section, or use your best judgement
     * Continuing content from previous page is NOT a heading
     * Numbered sections (e.g., 14., 14.3, 16.2.1) are level 2+ headings (##, ###, etc.)
   - Heading Hierarchy:
     * Level 1 (#): Document title only, or when it starts a new part of the document.
     * Level 2 (##): Major sections
     * Level 3 (###): Subsections
     * Level 4 (####): Subsubsections
   - Identify Sections By:
     * Visual start of new content block
     * Numbering patterns (1., 1.1., I., 一., 第一章)
     * Visual prominence
     * Content relationships
   - Maintain Consistency:
     * Keep parallel sections at same level
     * Preserve original hierarchy
     * Ensure logical content flow
     * Continue section numbers from previous pages

3. Image Handling
   - Process red-rectangle-marked images only
   - Format: ![Title](<EXACT-Filename> "Description")
   - Rules:
     * Use only filenames with 'img'
     * Each filename once only
     * Keep original positions
     * Title and caption must accurately describe ALL visible content
     * Never output image metadata or processing information
     * Never add separate image information sections

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
- Include accurate title and caption
- Follow markdown syntax
- No metadata in output
"""


