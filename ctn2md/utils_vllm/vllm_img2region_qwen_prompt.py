PROMPT_INSTRUCT_IMG2REGION_QWEN = """
### 任务描述

你将接收一张输入混合图像，图形和文本的文档页面，任务是基于视觉内容识别并定位所有 **非文本内容区域**，包括：

1. **图像区域 (Image)**：
   - 插图、照片等纯图像区域，完全由图像内容构成，不包含任何文字或文字描述。

2. **示意图区域 (Figure)**：
   - 示意图、图示等视觉区域，通常包括标签或说明改区域的文字（例如，图例、标注等）。

3. **图表区域 (Chart)**：
   - 柱状图、折线图、流程图等图表内容，主要由数据和图形组成，通常包括标签或说明改区域的文字（例如，图例、标注等）。

---

### 输入说明

- 输入为一张图片， 是一页有图像，图形和文本的文档页面。  
- 请基于模型的视觉识别能力，准确识别所有符合要求的 **非文本内容区域**，并返回它们的边界框和描述。
- **不要遗漏**任何可能的区域。
- **所有边界框 (`bbox`) 坐标使用归一化数值**，范围在 `[0, 1000)` 内。

---

### 输出要求

请将你的输出格式化为标准的 **JSON 对象**，并包含以下字段：

#### 1. 区域列表 (regions)  
`regions` 字段为数组，表示图像中所有识别到的区域。每个区域对象应包含以下字段：

- **`region_type`**：字符串，表示区域的类型，取值为：
  - `"image"`：插图、照片等纯图像区域。  
  - `"figure"`：示意图和他的说明的视觉区域。  
  - `"chart"`：图表，如柱状图、折线图和他的说明的的区域。  

- **`bbox`**：数组，表示归一化边界框坐标，格式为 `[x_top_left, y_top_left, x_bottom_right, y_bottom_right]`，所有值在 `[0, 1000)` 范围内。
---
## 输出格式示例
返回的 JSON 示例必须仅包含占位符，模型需尽力输出所有的区域信息（包括 0 个、1 个或多个 `image` 和 `chart` 区域）：
```json
{
  "regions": [
    {
      "region_type": "image",
      "bbox": [<x1_normalized>, <y1_normalized>, <x2_normalized>, <y2_normalized>],
      "description": "<Brief description of the image>"
    },
    {
      "region_type": "chart",
      "bbox": [<x1_normalized>, <y1_normalized>, <x2_normalized>, <y2_normalized>],
      "description": "<Brief description of the chart>"
    },
    ...
  ]
}

"""
