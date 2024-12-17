PROMPT_INSTRUCT_IMG2REGION_QWEN = """
### 任务描述

你将接收一页文档的图片，任务是基于视觉内容识别并定位所有的 **非典型文本区域**，包括：

1. **图像区域 (Image)**：  
   - 插图、照片等纯图像区域，不包含任何文字。区域应完全由图像内容构成。

2. **示意图区域 (Figure)**：  
   - 示意图、图示等非文本区域，通常没有文字或只有少量描述。

3. **图表区域 (Chart)**：  
   - 柱状图、折线图、流程图等图表区域，仅包含数据和图形，不包含文本描述。

---

### 输入说明

- 输入为一页文档的图片。  
- 基于视觉内容，识别并返回文档页中所有符合上述要求的 **非典型文本区域**，包括区域的边界框坐标。  
- **所有边界框 (`bbox`) 的坐标值使用归一化数值**，范围在 `[0, 1000)` 内。

---

### 输出要求

返回的 **JSON 对象** 必须包含以下字段：

#### 1. 区域列表 (regions)  
`regions` 字段为数组，表示文档页中识别到的所有区域。每个区域对象应包含以下字段：

- **`region_type`**：字符串，表示区域的类型，取值为：
  - `"image"`：插图、照片等纯图像区域。  
  - `"figure"`：示意图区域。  
  - `"chart"`：图表区域。

- **`bbox`**：数组，表示归一化边界框坐标，格式为 `[x_top_left, y_top_left, x_bottom_right, y_bottom_right]`，所有值在 `[0, 1000)` 范围内。

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
