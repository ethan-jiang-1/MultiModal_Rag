PROMPT_INSTRUCT_IMG2MD_ARK = """
# Task
Convert PDF page to Markdown, preserving visual structure and image positions.

# Core Rules
1. Content Conversion
   - Convert ALL visual content to clean Markdown:
     * Figure captions (e.g., "Figure X: ...")
     * Explanatory text
     * Technical descriptions
     * References to figures/sections
   - Preserve original layout and spacing
   - Focus on meaningful content over decorative elements
   - Skip repetitive patterns after 10+ occurrences, such as ..... or ---- .
   - Critical Text Rules:
     * Capture ALL figure captions completely
     * Include ALL explanatory paragraphs
     * Maintain ALL technical details
     * Preserve cross-references
     * Keep numerical data and measurements

2. Structure Recognition
   - Convert visual headings based on:
     * Hierarchical numbering (e.g., 1., 1.1., I. II. 一. 二， 第一章，第二章etc.)
     * Visual prominence (size, weight, spacing)
     * Standalone positioning
     * Content flow breaks
   - Use appropriate heading levels (#, ##, ###)

3. Image Processing
   - Process images marked with red rectangles
   - Format: ![Title](<EXACT-Filename> "Description")
   - Critical Rules:
     * Each filename MUST be used EXACTLY ONCE
     * Each red rectangle corresponds to ONE unique image
     * Never reuse the same filename for different images
     * Verify filename-content match before using
   - Place at original positions
   - Title: Brief description (3-10 words)
   - Caption: Content description + context (2-4 sentences)

# Quality Requirements
1. Content
   - 100% content preservation for:
     * Main text and paragraphs
     * Titles and headings
     * Captions and descriptions
     * Lists and enumerations
     * Tables and structured content
     * Footnotes and references
   - Clean, minimal formatting
   - Natural reading flow
   - No content omission

2. Images
   - All marked images included ONCE only
   - One-to-one mapping: one filename → one image
   - No filename reuse
   - Correct filename usage
   - Original positioning
   - Meaningful titles/captions

3. Structure
   - Clear heading hierarchy
   - Logical content flow
   - Original layout preserved

# Image Information
{inst_img_rects}
"""

PROMPT_INSTRUCT_IMG2MD_ARK_IMG_RECTS = """
# Image Region Processing
1. Red Rectangle Identification
   - Each image marked with red border
   - Filename located in top-left of red box
   - {img_rects}

2. Markdown Image Format
   - Required format: ![Title](<Filename> "Caption")
   - Components:
     * Title: Brief visual description (3-10 words)
     * Filename: EXACT match from red box
     * Caption: Content description (2-4 sentences)

3. Placement Rules
   - Maintain original document position
   - Follow natural reading flow
   - Preserve text-image relationships

4. Quality Standards
   - Process each red rectangle exactly once
   - Use precise filenames
   - Ensure logical placement
   - Provide meaningful descriptions

# Format Validation
- Start with '![' for all images
- Use exact filenames without modification
- Include both title and caption
- Maintain proper markdown syntax
"""


