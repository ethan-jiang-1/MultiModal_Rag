from typing import List, TypedDict, Optional, Tuple
import os
import logging
import shutil
from dotenv import load_dotenv
from llama_parse import LlamaParse

load_dotenv()

from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.gen_lp._download_image_status import ImageStatusTracker

class OCRResult(TypedDict):
    """OCR识别结果"""
    x: int           # OCR区域左上角x坐标
    y: int           # OCR区域左上角y坐标
    w: int           # OCR区域宽度
    h: int           # OCR区域高度
    confidence: str  # 置信度
    text: str        # 识别的文本

class LlamaParseImage(TypedDict):
    """LlamaParse返回的图片信息"""
    name: str                    # 图片文件名
    height: int                  # 图片高度
    width: int                   # 图片宽度
    x: float                     # 图片在页面中的x坐标
    y: float                     # 图片在页面中的y坐标
    original_width: int          # 原始宽度
    original_height: int         # 原始高度
    ocr: Optional[List[OCRResult]]  # OCR结果（可选）
    path: str                    # 图片保存路径

def _analyse_download_status(json_result: List[dict], md_info: MdInfo) -> Tuple[list, list]:
    """分析需要下载的图片状态
    
    Args:
        json_result: LlamaParse 返回的解析结果
        md_info: 文档信息对象
        
    Returns:
        tuple[list, list]: (需要下载的图片列表, 已存在的图片列表)
    """
    unique_job_id = md_info.get_unique_job_id()
    out_dir = md_info.get_out_dir()
    
    # 收集所有需要的图片信息
    required_images = []
    for result in json_result:
        cur_job_id = result["job_id"]
        for page in result["pages"]:
            if "images" not in page:
                continue
            for image in page["images"]:
                # 构建目标 unique_job_id 的路径
                target_name = f"{unique_job_id}-{image['name']}"
                target_path = os.path.join(out_dir, target_name)
                
                image_info = {
                    "cur_job_id": cur_job_id,
                    "image_name": image["name"],
                    "target_path": target_path,
                    "page_number": page["page"],
                    "original_data": image
                }
                required_images.append(image_info)
    
    # 分析哪些图片需要下载，哪些已存在
    to_download = []
    existing = []
    status_tracker = ImageStatusTracker(md_info.get_cache_dir())
    
    for img_info in required_images:
        if status_tracker._verify_image(img_info["target_path"]):
            existing.append(img_info)
        else:
            to_download.append(img_info)
            
    return to_download, existing

def safe_download_images(parser: LlamaParse, json_result: List[dict], md_info: MdInfo) -> List[LlamaParseImage]:
    """下载图片的主入口函数，支持断点续传
    
    Args:
        parser: LlamaParse实例
        json_result: LlamaParse解析结果
        md_info: 文档信息对象
        
    Returns:
        List[LlamaParseImage]: 成功下载的图片信息列表
    """
    if not json_result:
        logging.warning("Empty JSON result")
        return []

    # 确保目录存在
    out_dir = md_info.get_out_dir()

    try:
        # 分析下载状态
        to_download, existing = _analyse_download_status(json_result, md_info)
        
        status_tracker = ImageStatusTracker(md_info.get_cache_dir())
        
        # 处理已存在的图片
        images = []
        for img_info in existing:
            logging.info(f"Image already exists: {img_info['target_path']}")
            img_data = img_info["original_data"].copy()
            img_data["path"] = img_info["target_path"]
            images.append(img_data)
            status_tracker.record_success(img_info["target_path"])
            
        # 下载缺失的图片
        for img_info in to_download:
            try:
                # 先下载到临时路径（使用当前 job_id）
                temp_path = os.path.join(out_dir, f"{img_info['cur_job_id']}-{img_info['image_name']}")
                
                # 使用 parser 下载图片
                image_data = img_info["original_data"].copy()
                image_data["path"] = temp_path
                
                # 下载图片
                parser.get_images([{
                    "job_id": img_info["cur_job_id"],
                    "pages": [{
                        "page": img_info["page_number"],
                        "images": [img_info["original_data"]]
                    }]
                }], out_dir)
                
                # 如果下载成功，移动到最终路径
                if status_tracker._verify_image(temp_path):
                    shutil.move(temp_path, img_info["target_path"])
                    image_data["path"] = img_info["target_path"]
                    images.append(image_data)
                    status_tracker.record_success(img_info["target_path"])
                    logging.info(f"Successfully downloaded and moved image to: {img_info['target_path']}")
                else:
                    if not status_tracker.record_failure(img_info["target_path"]):
                        logging.error(f"Max retry attempts reached for {img_info['target_path']}")
                        
            except Exception as e:
                logging.error(f"Failed to download image {img_info['image_name']}: {e}")
                if not status_tracker.record_failure(img_info["target_path"]):
                    logging.error(f"Max retry attempts reached for {img_info['target_path']}")

        # 打印状态
        status_tracker.print_status()
        
        # 验证是否所有必需的图片都已获取
        if len(images) == len(to_download) + len(existing):
            logging.info("All required images have been successfully processed")
        else:
            logging.warning(f"Some images are missing: {len(images)} of {len(to_download) + len(existing)} obtained")
            
        return images
        
    except Exception as e:
        logging.error(f"Download process failed: {e}")
        return []

def check_images_completeness(json_result: List[dict], md_info: MdInfo) -> Tuple[bool, List[str]]:
    """检查图片是否完整下载
    
    Args:
        json_result: LlamaParse 返回的解析结果
        md_info: 文档信息对象
        
    Returns:
        Tuple[bool, List[str]]: (是否完整, 缺失的图片列表)
    """
    to_download, existing = _analyse_download_status(json_result, md_info)
    
    if not to_download:
        logging.info("所有图片都已完整下载")
        return True, []
    
    missing_images = [f"{img_info['image_name']} (Page {img_info['page_number']})" for img_info in to_download]
    logging.warning(f"发现 {len(missing_images)} 个缺失图片: {', '.join(missing_images)}")
    return False, missing_images

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()

    # 测试用例
    md_info_path = "_output/ctn2md_mrag__4__前后排座椅间距定义_P1_lp/_info.json"
    if not os.path.exists(md_info_path):
        logging.error(f"Test file not found: {md_info_path}")
        exit(1)

    md_info = MdInfo(md_info_path)
    LLAMAPARSE_API_KEY = os.environ.get("LLAMAPARSE_API_KEY")
    if not LLAMAPARSE_API_KEY:
        logging.error("LLAMAPARSE_API_KEY not set")
        exit(1)

    parser = LlamaParse(
        api_key=LLAMAPARSE_API_KEY,
        result_type="markdown",
        verbose=True
    )

    try:
        doc_pathname = md_info.get_doc_pathname()
        if not os.path.exists(doc_pathname):
            raise FileNotFoundError(f"Document not found: {doc_pathname}")

        # 第一次调用
        print("\n=== 第一次调用 ===")
        json_result = parser.get_json_result(doc_pathname)
        
        # 检查图片完整性
        print("\n检查图片完整性:")
        is_complete, missing = check_images_completeness(json_result, md_info)
        if not is_complete:
            print(f"缺失的图片: {missing}")
        
        images = safe_download_images(parser, json_result, md_info)
        
        # 再次检查完整性
        print("\n下载后再次检查完整性:")
        is_complete, missing = check_images_completeness(json_result, md_info)
        if not is_complete:
            print(f"缺失的图片: {missing}")
        
        # 第二次调用，验证图片重用功能
        print("\n=== 第二次调用 ===")
        json_result = parser.get_json_result(doc_pathname)
        images = safe_download_images(parser, json_result, md_info)
        
        # 打印job_id历史
        print("\nJob ID 历史记录:")
        print(md_info.get(MIFN.LP_JOB_ID_HISTORY, []))
        
    except Exception as e:
        logging.error(f"Process failed: {e}")
        exit(1)
