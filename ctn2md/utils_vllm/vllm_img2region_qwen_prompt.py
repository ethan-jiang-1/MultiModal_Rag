PROMPT_INSTRUCT_IMG2REGION_QWEN = """
# Task Description

You are provided with an image of a document page. Identify and analyze the **regions of interest**, which include:

1. **Full Page Region**:
   - Represents the boundary of the entire page content.

2. **Non-typical Regions**:
   - **Image**: Illustrations, diagrams, etc.
   - **Table**: Structured grids with rows and columns.
   - **Chart**: Flowcharts, bar charts, line charts, etc.
   - **List**: Non-continuous itemized content.

---

## Input Image Information
The input image may have been resized, cropped, or padded during preprocessing. Your task is to return:
1. The actual dimensions of the image **as processed by the model**.
2. Whether the image has been **resized or padded**:
   - If resized, specify the resizing method (e.g., "aspect-ratio preserved").
   - If padded, specify the padding dimensions for top, bottom, left, and right (in pixels).

---

## Output Requirements

### 1. Processed Image Dimensions
- Return the actual dimensions of the processed image (`width` and `height` in pixels).
- Include details of any resizing or padding applied during preprocessing.

### 2. Region Bounding Boxes
- Each region's bounding box (`bbox`) must be expressed as `[x_top_left, y_top_left, width, height]` in pixels, relative to the **processed image dimensions**.
- Ensure the bounding box values are adjusted to exclude any padding (if applicable).

### 3. Additional Details
- Include the following metadata about image processing:
  - `resized`: Whether the image was resized (`true` or `false`).
  - `aspect_ratio_preserved`: Whether the aspect ratio was preserved during resizing (`true` or `false`).
  - `padding`: If padding was applied, include the padding dimensions for `top`, `bottom`, `left`, and `right` (in pixels).

---

## Final Output Format
The result must be a JSON object with the following structure:

```json
{
  "image_size": {
    "width": "<processed_image_width>",
    "height": "<processed_image_height>"
  },
  "image_processing_info": {
    "resized": <true_or_false>,
    "aspect_ratio_preserved": <true_or_false>,
    "padding": {
      "top": <padding_top_pixels>,
      "bottom": <padding_bottom_pixels>,
      "left": <padding_left_pixels>,
      "right": <padding_right_pixels>
    }
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
    },
    ...
  ]
}
"""
