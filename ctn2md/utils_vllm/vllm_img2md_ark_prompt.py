PROMPT_INSTRUCT_IMG2MD_ARK = """
# Task
Convert the given PDF page into Markdown format, maintaining EXACT image positions and correct image identification.

# Critical Rules for Images
1. Strict Image Identification:
   - Each image MUST use its EXACT filename from its red rectangle
   - Match each image's content with its correct filename
   - Example: If `5ec48698-img_1_1.jpg` shows a data chart, use that EXACT filename for the chart
   - NO mixing up or swapping of filenames

2. Strict Position Preservation:
   - Process document in EXACT top-to-bottom order
   - Insert each image WHERE IT APPEARS in the PDF
   - STOP and insert image Markdown as soon as you encounter an image
   - NEVER collect images for later insertion

3. Image Markdown Format:
   ```markdown
   ![Title](<EXACT-Filename> "Description of THIS specific image's content")
   ```
   - Filename: Must match the red rectangle label
   - Title and Description: Must describe THIS image's actual content
   - Verify filename matches content before inserting

# Processing Steps
1. For EACH content element from TOP to BOTTOM:
   - If it's text → Convert to Markdown
   - If it's an image → IMMEDIATELY insert image Markdown with correct filename
   - Continue to next element
   
2. For EACH image:
   - Look at the image content
   - Find its matching filename in red rectangle
   - Verify content matches filename
   - Insert AT CURRENT POSITION
   - Check off image from tracking list

# Quality Control
1. Image Position Check:
   - Each image appears WHERE it was in PDF
   - NO images grouped at end
   
2. Image Identification Check:
   - Each filename matches its image content
   - NO swapped or mixed-up filenames
   
3. Completeness Check:
   - ALL images processed
   - Each image used exactly once
   - Correct filename-content pairs

# Image Information
{inst_img_rects}

# Expected Output
- Images in their ORIGINAL positions
- CORRECT filename-content matching
- NO image collection at end
- NO skipped images
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

