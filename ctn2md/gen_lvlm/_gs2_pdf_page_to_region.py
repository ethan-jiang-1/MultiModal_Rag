import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator
from typing import List, Tuple # , Optional
import logging
import time
load_dotenv()

from ctn2md.utils.util_logging import setup_logger_handlers

"""
https://github.com/ppaanngggg/yolo-doclaynet

DocLayNet can be found more details and download at this link. It has 11 labels:

Text: Regular paragraphs.
Picture: A graphic or photograph.
Caption: Special text outside a picture or table that introduces this picture or table.
Section-header: Any kind of heading in the text, except overall document title.
Footnote: Typically small text at the bottom of a page, with a number or symbol that is referred to in the text above.
Formula: Mathematical equation on its own line.
Table: Material arranged in a grid alignment with rows and columns, often with separator lines.
List-item: One element of a list, in a hanging shape, i.e., from the second line onwards the paragraph is indented more than the first line.
Page-header: Repeating elements like page number at the top, outside of the normal text flow.
Page-footer: Repeating elements like page number at the bottom, outside of the normal text flow.
Title: Overall title of a document, (almost) exclusively on the first page and typically appearing in large font.
"""

LABELS = {
    "0": "Caption",
    "1": "Footnote",
    "2": "Formula",
    "3": "List-item",
    "4": "Page-footer",
    "5": "Page-header",
    "6": "Picture",
    "7": "Section-header",
    "8": "Table",
    "9": "Text",
    "10": "Title"
}

class DocLayoutPrediction(BaseModel):
    boxes: List[List[float]]
    confidence: List[float]
    class_ids: List[float]
    
    @field_validator('boxes')
    @classmethod
    def validate_boxes(cls, v):
        if not all(len(box) == 4 for box in v):
            raise ValueError("Each box must contain exactly 4 coordinates")
        return v
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v, info):
        if len(v) != len(info.data.get('boxes', [])):
            raise ValueError("Number of confidence scores must match number of boxes")
        return v

class DocLayoutResponse(BaseModel):
    status: str
    predictions: List[DocLayoutPrediction]

def call_doclayout_yolo_endpoint(image_path: str) -> DocLayoutResponse:
    """调用YOLO API进行文档布局检测
    
    Args:
        image_path: 输入图像路径
        
    Returns:
        DocLayoutResponse: 包含状态和所有预测结果的响应对象
    """
    url = os.getenv("DOCLAYOUT_ENDPOINT")
    max_retries = 3
    
    with httpx.Client() as client:
        for attempt in range(max_retries):
            try:
                with open(image_path, "rb") as file:
                    files = {"file": file}
                    response = client.post(url, files=files, timeout=10.0)
                    response.raise_for_status()
                
                json_data = response.json()
                print("Status:", json_data["status"])
                data = DocLayoutResponse(**json_data)
                return data
                
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == max_retries - 1:  # Last attempt
                    print(f"Error: {response.status_code} - {response.text}")
                    return None
                
                delay = (attempt + 1) * 1
                logging.warning(f"Request attempt {attempt + 1} failed. Retrying in {delay}s... Error: {str(e)}")
                time.sleep(delay)

def extract_picture_regions(
    response: DocLayoutResponse, 
    conf_threshold: float = 0.5
) -> List[Tuple[float, float, float, float]]:
    """提取文档中置信度高于阈值的Picture区域
    
    Args:
        response: YOLO API的响应结果
        conf_threshold: 置信度阈值，默认0.5
        
    Returns:
        List[Tuple[float, float, float, float]]: Picture区域的边界框列表 [x1, y1, x2, y2]
    """
    picture_regions = []
    
    for prediction in response.predictions:
        for box, conf, class_id in zip(prediction.boxes, prediction.confidence, prediction.class_ids):
            # 只处理Picture类别(id=6)且置信度高于阈值的预测
            if int(class_id) == 6 and conf >= conf_threshold:
                # 转换为[x1, y1, x2, y2]格式
                x1, y1, x2, y2 = [float(coord) for coord in box]
                picture_regions.append((x1, y1, x2, y2))
    
    return picture_regions

# 使用示例：
if __name__ == "__main__":
    setup_logger_handlers() 
    image_path = r"_work/md_pdf_pages/cd725bb7-page_6.jpg"
    response = call_doclayout_yolo_endpoint(image_path)
    
    if response:
        # 提取置信度大于0.7的Picture区域
        picture_boxes = extract_picture_regions(response, conf_threshold=0.7)
        print(f"Found {len(picture_boxes)} high-confidence picture regions:")
        for box in picture_boxes:
            print(f"Box coordinates: {box}")