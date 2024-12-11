PROMPT_INSTRUCT_IMG2REGION_QWEN = """
# Task Description

You are provided with a page of content. Please identify and analyze the **regions of the page**, which include:

1. **Full Page Region**:
   - Represents the boundary of the entire content within the page.

2. **Non-Typical Text Regions** (Focus on):
   - **Image**: Illustrations, pictures, diagrams, etc.
   - **Chart**: Flowcharts, bar charts, line charts, or any graphical data representation.

---

## Input Image Information
- The model processes the input image, which may involve resizing, cropping, or padding. The `image_size` field must reflect the **actual dimensions of the image as processed by the model**.

---

## Output Requirements

### 1. Image Dimensions
- Return the `width` and `height` of the image as seen by the model after internal processing (in pixels).

### 2. Region Bounding Boxes
- For each region, return a `bbox` in the format `[x_top_left, y_top_left, width, height]`:
  - `x_top_left`: The x-coordinate of the top-left corner of the bounding box.
  - `y_top_left`: The y-coordinate of the top-left corner of the bounding box.
  - `width`: The width of the bounding box (in pixels).
  - `height`: The height of the bounding box (in pixels).
- Ensure that the bounding box fully encloses the region, including margins or other related elements.

### 3. Region Independence
- **Non-overlapping Regions**:
  - Each region must be **independent** and **non-overlapping** with any other region.
  - If a potential overlap is detected, adjust the bounding boxes to ensure no intersection.

### 4. Region Information
- **Full Page Region**:
  - `type`: Use `"full_page"` to indicate the full page content region.
  - `bbox`: Must cover the entire content area, starting at the top-left corner and extending to the full width and height of the `image_size`.
  - `description`: Use `"Entire page content"` or a similar concise description.
- **Non-Typical Text Regions**:
  - `type`: Use `"image"` or `"chart"`.
  - `description`: Provide a concise description of the region's content.

---

## Notes
- Always include the full page region (`full_page`) as the first entry in the `regions` list.
- Ensure all `bbox` values are within the dimensions defined by `image_size`.
- Ensure regions are **non-overlapping**:
  - For any two bounding boxes, their intersection area must be zero.
- Return the regions in the following order:
  1. Full page region.
  2. Non-typical text regions, ordered from top to bottom.

---

## Output Format

The result must be a JSON object with the following structure:

```json
{
  "image_size": {
    "width": "<processed_image_width>",
    "height": "<processed_image_height>"
  },
  "regions": [
    {
      "type": "full_page",
      "bbox": [<x_top_left>, <y_top_left>, <width>, <height>],
      "description": "Entire page content"
    },
    {
      "type": "<type_of_region>",
      "bbox": [<x_top_left>, <y_top_left>, <width>, <height>],
      "description": "<region_description>"
    }
  ]
}
"""
