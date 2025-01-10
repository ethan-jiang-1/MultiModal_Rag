from typing import List, Dict
import os
import json
import logging
from dotenv import load_dotenv
from llama_parse import LlamaParse

load_dotenv()

from ctn2md.src.md_info_base import MdInfo

def _verify_image_file(file_path: str) -> bool:
    """验证下载的图片文件是否完整且可访问"""
    try:
        if not os.path.exists(file_path):
            return False
        if os.path.getsize(file_path) == 0:
            return False
        return True
    except Exception as e:
        logging.error(f"Error verifying image file {file_path}: {str(e)}")
        return False

def _load_failed_downloads(md_info: MdInfo) -> Dict[str, int]:
    """加载之前失败的下载记录"""
    failed_downloads_path = os.path.join(md_info.get_aux_dir(), "failed_image_downloads.json")
    if os.path.exists(failed_downloads_path):
        try:
            with open(failed_downloads_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading failed downloads: {str(e)}")
    return {}

def _save_failed_downloads(md_info: MdInfo, failed_downloads: Dict[str, int]) -> None:
    """保存失败的下载记录"""
    if not failed_downloads:
        # 如果没有失败的下载，删除记录文件
        failed_downloads_path = os.path.join(md_info.get_aux_dir(), "failed_image_downloads.json")
        if os.path.exists(failed_downloads_path):
            os.remove(failed_downloads_path)
        return
    
    try:
        failed_downloads_path = os.path.join(md_info.get_aux_dir(), "failed_image_downloads.json")
        with open(failed_downloads_path, 'w') as f:
            json.dump(failed_downloads, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving failed downloads: {str(e)}")

def safe_download_images(parser: LlamaParse, json_result: List[dict], md_info: MdInfo) -> List[dict]:
    """安全地下载图片，记录失败的下载，并重试之前失败的下载"""
    out_dir = md_info.get_out_dir()
    
    # 确保输出目录存在且可写
    if not os.path.exists(out_dir):
        try:
            os.makedirs(out_dir)
        except Exception as e:
            logging.error(f"Failed to create output directory {out_dir}: {str(e)}")
            return []
    
    if not os.access(out_dir, os.W_OK):
        logging.error(f"Output directory {out_dir} is not writable")
        return []
    
    # 加载之前失败的下载记录
    failed_downloads = _load_failed_downloads(md_info)
    
    try:
        # 使用 LlamaParse 下载图片
        images = parser.get_images(json_result, out_dir)
        
        # 验证下载的图片并更新失败记录
        for image in images:
            path = image["path"]
            if not _verify_image_file(path):
                failed_downloads[path] = failed_downloads.get(path, 0) + 1
                logging.error(f"Failed to download {path}")
            elif path in failed_downloads:
                # 如果这次成功了，从失败记录中移除
                del failed_downloads[path]
                logging.info(f"Successfully downloaded previously failed image: {path}")
        
        # 保存失败记录
        _save_failed_downloads(md_info, failed_downloads)
        
        # 返回所有图片信息，包括下载状态
        for image in images:
            image["download_success"] = _verify_image_file(image["path"])
        
        return images
        
    except Exception as e:
        logging.error(f"Error downloading images: {str(e)}")
        return []

if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()

    # 测试用例：使用一个已知的文档进行测试
    md_info_path = "_output/ctn2md_mrag__4__前后排座椅间距定义_P1_lp/_info.json"
    print(f"\n测试文件: {md_info_path}")
    
    if not os.path.exists(md_info_path):
        print(f"错误: 文件不存在 {md_info_path}")
        exit(1)
        
    md_info = MdInfo(md_info_path)
    print(f"输出目录: {md_info.get_out_dir()}")
    print(f"辅助目录: {md_info.get_aux_dir()}")

    # 获取 LlamaParse 实例
    LLAMAPARSE_API_KEY = os.environ.get("LLAMAPARSE_API_KEY")
    if not LLAMAPARSE_API_KEY:
        print("错误: 未设置 LLAMAPARSE_API_KEY 环境变量")
        exit(1)
        
    parser = LlamaParse(
        api_key=LLAMAPARSE_API_KEY,
        result_type="markdown",
        verbose=True
    )

    # 加载文档
    doc_pathname = md_info.get_doc_pathname()
    print(f"文档路径: {doc_pathname}")
    
    if not os.path.exists(doc_pathname):
        print(f"错误: 文档不存在 {doc_pathname}")
        exit(1)
        
    try:
        print("\n开始解析文档...")
        json_result = parser.get_json_result(doc_pathname)
        print(f"解析完成，结果长度: {len(json_result)}")
    except Exception as e:
        print(f"错误: 解析文档失败: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

    # 下载图片并打印结果
    print("\n开始下载图片...")
    images = safe_download_images(parser, json_result, md_info)
    
    # 打印下载结果统计
    total = len(images)
    success = sum(1 for img in images if img.get("download_success", False))
    failed = total - success
    
    print(f"\n下载统计:")
    print(f"总图片数: {total}")
    print(f"成功下载: {success}")
    print(f"下载失败: {failed}")

    # 检查失败记录文件
    failed_downloads_path = os.path.join(md_info.get_aux_dir(), "failed_image_downloads.json")
    if os.path.exists(failed_downloads_path):
        print(f"\n失败记录文件: {failed_downloads_path}")
        with open(failed_downloads_path, 'r') as f:
            failed_records = json.load(f)
            print(f"失败记录数: {len(failed_records)}")
            for path, attempts in failed_records.items():
                print(f"- {path}: 失败 {attempts} 次")
