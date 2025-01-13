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
     * A line is a heading if it has a number prefix (e.g., 14.3, 16.2.1)
     * Document title (#) appears only on the first page of document
     * Continuing paragraphs from previous page are NOT headings
   - Heading Levels:
     * Level 1 (#): Main document title only
     * Level 2 (##): Single number sections (1., 2., etc.)
     * Level 3 (###): Double number sections (1.1, 2.1, etc.)
     * Level 4 (####): Triple number sections (1.1.1, etc.)
   - Identify Sections By:
     * Number prefix at start of line
     * Visual spacing before and after
     * Content indentation
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


