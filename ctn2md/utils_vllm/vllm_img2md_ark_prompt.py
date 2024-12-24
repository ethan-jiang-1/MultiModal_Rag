
PROMPT_INSTRUCT_IMG2MD_ARK = """
# Task:
Convert the given PDF page into Markdown format, maintaining the original layout and structure.

- **General Rules**:
  - Recognize and convert all content types, including text, lists, tables, and images, into Markdown.
  - Only include images that are explicitly marked within `red_rects` and provided in the `red_rects` list.
  - Place images within the Markdown flow, ensuring they appear naturally and logically at the appropriate position based on the PDF's layout and reading order.

- **Image Handling**:
  - For each image in `red_rects`, use the following format:
    ```markdown
    ![Title](<FileName> "<Caption>")
    ```
  - **Red Boxed Images (`red_rects`)**:
    - Images within red boxes (`red_rects`) are annotated in the top-left corner with their file names (e.g., `5ec48698-img_1_1.jpg`).
    - Use this file name as the **FileName** field in the Markdown image syntax.
  - **Title**:
    - Extract a concise, meaningful title from the image content.
    - The title must match the language of the PDF content.
  - **FileName**:
    - Use the exact file name as labeled in the `red_rects` list.
  - **Caption**:
    - Provide a detailed description in the original language of the PDF, including:
      - Key information about the image (e.g., data, trends, or subjects).
      - Observations or insights drawn from the image.
      - Any relevant background or context.

- **Special Rules for Image Placement**:
  - **Do not include images that are not marked within `red_rects`.**
  - Insert each image into the Markdown flow at the most natural position, directly following the related text or table. Avoid relocating images to the end of the Markdown output or grouping them together.

- **Language Consistency**:
  - Ensure all output, including titles and captions, is written in the original language of the PDF. **Do not translate.**

# `red_rects` Information:
{inst_img_rects}

# Output:
Provide the full content in Markdown format.

"""

PROMPT_INSTRUCT_IMG2MD_ARK_IMG_RECTS = """
- **Red Rectangles (`red_rects`)**:
  The following `red_rects` mark specific image regions in the PDF. Each red box is labeled in its top-left corner with the corresponding file name:
{img_rects}

- **Instructions**:
  - For each `red_rect`, generate a Markdown image entry:
    ```markdown
    ![Title](<FileName> "<Caption>")
    ```
  - Requirements:
    - **Title**: A short, meaningful title in the same language as the PDF content.
    - **FileName**: Use the exact file name annotated in the top-left corner of the red box.
    - **Caption**: Provide a detailed, contextually rich description in the same language, focusing on:
      - Key data, trends, and observations from the image.
      - The image’s relevance to the surrounding content.

  - **Placement Rules**:
    - Place each image **immediately after the content it relates to**, based on the natural reading order of the PDF.
    - Ensure the Markdown flow reflects the PDF’s layout, with images appearing logically within the text.
    - **Do not include images that are not explicitly marked within `red_rects`.**

  - **Validation**:
    - Verify all `red_rects` are processed exactly once and embedded at the correct position in the Markdown output.
"""

