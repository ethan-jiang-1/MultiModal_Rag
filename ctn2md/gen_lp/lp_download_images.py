from typing import List, Dict, Tuple
import os
import json
import logging
from dotenv import load_dotenv
from llama_parse import LlamaParse

load_dotenv()

from ctn2md.src.md_info_base import MdInfo

FNAME_FAILED_IMAGE = "failed_image_downloads.json"
MAX_RETRY_ATTEMPTS = 3

def _verify_image(path: str) -> bool:
    """验证图片文件的完整性"""
    try:
        return os.path.exists(path) and os.path.getsize(path) > 0
    except Exception as e:
        logging.error(f"Failed to verify image {path}: {e}")
        return False

def _load_failed_records(aux_dir: str) -> Dict[str, int]:
    """加载失败记录"""
    path = os.path.join(aux_dir, FNAME_FAILED_IMAGE)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load download records: {e}")
        return {}

def _save_failed_records(aux_dir: str, records: Dict[str, int]) -> None:
    """保存失败记录"""
    path = os.path.join(aux_dir, FNAME_FAILED_IMAGE)
    try:
        if not records:
            if os.path.exists(path):
                os.remove(path)
            return
        with open(path, 'w') as f:
            json.dump(records, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save download records: {e}")

def _process_download_results(images: List[dict], aux_dir: str) -> Tuple[List[dict], Dict[str, int]]:
    """处理下载结果，更新失败记录"""
    failed_records = _load_failed_records(aux_dir)
    
    for image in images:
        path = image["path"]
        if not _verify_image(path):
            attempts = failed_records.get(path, 0) + 1
            if attempts <= MAX_RETRY_ATTEMPTS:
                failed_records[path] = attempts
                logging.error(f"Failed to download {path} (attempt {attempts}/{MAX_RETRY_ATTEMPTS})")
        elif path in failed_records:
            del failed_records[path]
            logging.info(f"Successfully downloaded {path}")
        image["download_success"] = _verify_image(path)
    
    _save_failed_records(aux_dir, failed_records)
    return images, failed_records

def safe_download_images(parser: LlamaParse, json_result: List[dict], md_info: MdInfo) -> List[dict]:
    """下载图片的主入口函数"""
    if not json_result:
        logging.warning("Empty JSON result")
        return []

    # 确保目录存在
    out_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(aux_dir, exist_ok=True)

    try:
        # 下载图片
        images = parser.get_images(json_result, out_dir)
        # 处理下载结果
        images, _ = _process_download_results(images, aux_dir)
        return images
    except Exception as e:
        logging.error(f"Download process failed: {e}")
        return []

def _print_download_stats(images: List[dict], aux_dir: str) -> None:
    """打印下载统计信息"""
    total = len(images)
    success = sum(1 for img in images if img.get("download_success", False))
    print(f"\n下载统计: 总数={total}, 成功={success}, 失败={total-success}")

    # 检查失败记录
    failed_records = _load_failed_records(aux_dir)
    if failed_records:
        print("\n失败记录:")
        for path, attempts in failed_records.items():
            print(f"- {path}: {attempts}/{MAX_RETRY_ATTEMPTS} 次尝试")

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

        json_result = parser.get_json_result(doc_pathname)
        images = safe_download_images(parser, json_result, md_info)
        _print_download_stats(images, md_info.get_aux_dir())
    except Exception as e:
        logging.error(f"Process failed: {e}")
        exit(1)
