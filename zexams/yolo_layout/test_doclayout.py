import httpx
import rich
import os
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator
from typing import List # , Optional
import cv2
#import numpy as np
from pathlib import Path
#import numpy as np
import time

load_dotenv()

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

def call_yolo_endpoint(image_path: str) -> DocLayoutResponse:
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
                print("Predictions:", json_data["predictions"])
                data = DocLayoutResponse(**json_data)
                return data
                
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == max_retries - 1:  # Last attempt
                    print(f"Error: {str(e)}")
                    return None
                
                delay = (attempt + 1) * 1
                print(f"Request attempt {attempt + 1} failed. Retrying in {delay}s... Error: {str(e)}")
                time.sleep(delay)

def draw_predictions(
    image_path: str, 
    response: DocLayoutResponse, 
    output_path: str = None,
    conf_threshold: float = 0.5,
) -> None:
    """在图像上绘制预测结果
    
    Args:
        image_path: 原始图像路径
        response: YOLO API响应对象
        output_path: 输出图像路径
        conf_threshold: 置信度阈值，只显示高于此阈值的预测结果，默认0.5
    """
    # 读取图像
    image = cv2.imread(image_path)
    
    # 如果未指定输出路径，则自动生成
    if output_path is None:
        output_path = str(Path(image_path).parent / f"{Path(image_path).stem}_pred.jpg")
    
    # 为不同类别设置不同颜色
    colors = {
        6: (0, 0, 255),  # Picture用红色 (BGR格式)
    }
    
    # 预定义非红色系的颜色（BGR格式）
    safe_colors = [
        (255, 255, 0),   # 青色
        (0, 255, 0),     # 绿色
        (255, 128, 0),   # 浅蓝色
        (255, 255, 128), # 浅青色
        (128, 255, 0),   # 黄绿色
        (0, 255, 128),   # 春绿色
        (128, 255, 128), # 浅绿色
        (0, 128, 255),   # 橙色
        (255, 128, 128), # 浅蓝色
        (0, 255, 255),   # 黄色
    ]
    
    # 为其他类别分配预定义的颜色
    color_idx = 0
    for i in range(len(LABELS)):
        if i != 6:  # 除了Picture之外
            colors[i] = safe_colors[color_idx % len(safe_colors)]
            color_idx += 1
    
    # 对每个预测结果进行绘制
    for prediction in response.predictions:
        for box, conf, class_id in zip(prediction.boxes, prediction.confidence, prediction.class_ids):
            if conf >= conf_threshold:
                # 获取坐标
                x1, y1, x2, y2 = [int(coord) for coord in box]
                class_id_int = int(class_id)
                
                # 获取类别标签和颜色
                label = LABELS[str(class_id_int)]
                color = colors[class_id_int]
                
                # Picture类别用粗线，其他类别用细线
                thickness = 4 if class_id_int == 6 else 2
                
                # 绘制边界框
                cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
                
                # 准备标签文本
                text = f"{label}: {conf:.2f}"
                
                # 获取文本大小
                (text_width, text_height), baseline = cv2.getTextSize(
                    text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
                )
                
                # 绘制标签背景
                cv2.rectangle(
                    image,
                    (x1, y1 - text_height - baseline - 5),
                    (x1 + text_width, y1),
                    color,
                    -1,
                )
                
                # 绘制标签文本
                cv2.putText(
                    image,
                    text,
                    (x1, y1 - baseline - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )
    
    # 保存结果
    cv2.imwrite(output_path, image)
    print(f"Prediction visualization saved to: {output_path}")

if __name__ == "__main__":
    #image_path = r"_work/md_pdf_pages/5ec48698-page_1.jpg" 
    #image_path = r"_work/md_pdf_pages/bd72132b-page_3.jpg"
    #image_path = r"_work/md_pdf_pages/bd72132b-page_4.jpg"
    #image_path = r"_work/md_pdf_pages/c3c1d78a-page_7.jpg"
    image_path = r"_work/md_pdf_pages/cd725bb7-page_6.jpg"

    # 输出路径
    #output_path = image_path.replace(".jpg", "_pred.jpg")
    output_path = image_path.replace(".jpg", "_pred.jpg")
    response = call_yolo_endpoint(image_path)

    if response:
        print(f"Status: {response.status}")
        rich.print(response.predictions)
        draw_predictions(image_path, response, output_path=output_path, conf_threshold=0.5)
