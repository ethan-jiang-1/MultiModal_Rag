PROMPT_INSTRUCT_IMG2MD_ARK = """
# Task
Convert the given PDF page into Markdown format, maintaining EXACT image positions and content formatting.

# Core Principles
1. Strict Content Preservation:
   - Convert content AS IS without "improvements"
   - Keep original spacing, layout, and formatting
   - NO decorative elements or style enhancements
   - STOP if you find yourself repeating the same pattern more than 16 times
   - For repetitive patterns (like "..." in TOC), use simple spacing instead
   - Focus on meaningful content over decorative elements

2. Content Priority:
   - Focus on key information and structure
   - For repetitive decorative elements (like "..." or "___"):
     * IGNORE these patterns after they appear more than 10 times
     * Use simple spacing to connect content
     * Preserve the actual content they connect
   - Prioritize:
     * Main text and headings
     * Tables and meaningful structure
     * Images and their captions
     * Actual content relationships

3. Image Processing Rules:
   - Process ONLY images with red rectangles and filenames
   - Use EXACT filenames from red rectangles
   - Place images at their ORIGINAL positions
   - Match content with correct filenames
   - NO image collection at document end

# Markdown Conversion
1. Text Content:
   - Convert to plain Markdown
   - Keep original formatting
   - Preserve spacing and alignment
   - NO format "improvements"
   - Skip repetitive decorative patterns

2. Image Format:
   ```markdown
   ![Title](<EXACT-Filename> "Description of THIS specific image's content")
   ```
   - Filename: Must match red rectangle label
   - Title/Description: Describe actual image content
   - Insert at original position

# Quality Control
1. Content Check:
   - All text converted exactly as shown
   - NO added formatting or styling
   - Original layout preserved
   - NO excessive repetition

2. Image Check:
   - All valid images included
   - Correct filename-content pairs
   - Original positions maintained
   - NO skipped images

# Image Information
{inst_img_rects}

# Expected Output
- Clean, minimal Markdown
- Images at original positions
- Exact content preservation
- NO format enhancements
- NO excessive repetition
- NO collected images at end
"""

PROMPT_INSTRUCT_IMG2MD_ARK_IMG_RECTS = """
- **Red Rectangles (`red_rects`) Identification**:
  - Each image region is marked with a red rectangular border in the PDF
  - File names are located in the top-left corner of each red box
  - Format: The file names follow the pattern `XXXXXXXX-img_YY_ZZ.jpg`:
    - XXXXXXXX: 8-character document ID
    - YY: page number in the document
    - ZZ: image sequence number on that page
{img_rects}

- **Markdown Image Generation**:
  - For each `red_rect`, create a Markdown image entry:
    ```markdown
    ![Title](<FileName> "<Caption>")
    ```
  - Component Requirements:
    - **Title**: 
      - Brief (3-10 words)
      - Descriptive of the image content
      - Same language as the PDF
      - Example: "Temperature Distribution Graph" or "System Architecture Diagram"
    
    - **FileName**: 
      - Use the EXACT filename from the red box
      - Do not modify or reformat the filename
    
    - **Caption**: 
      - Structure:
        1. Main content description (1-2 sentences)
        2. Key features or data points (if applicable)
        3. Relationship to surrounding text (1 sentence)
      - Length: 2-4 sentences
      - Language: Same as the PDF content
      - Focus: Technical accuracy and context relevance

  - **Image Placement Rules**:
    - Place each image in its natural reading order within the Markdown text
    - Insert the image where it logically appears in the original document flow
    - Keep the original document's content sequence
    - Maintain the relationship between text and images

  - **Quality Control**:
    1. Verify each `red_rect` is processed exactly once
    2. Check filename accuracy against the red box label
    3. Ensure all images are placed in logical reading order
    4. Validate that no unmarked images are included
"""

