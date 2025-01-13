import logging
import shutil
import os
from dotenv import load_dotenv
import mammoth
import rich

load_dotenv()

from ctn2md.src.md_info_base import MdInfo
from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.gen_markitdown.doc2md.mammoth_style_map import get_mammoth_style_map
from ctn2md.gen_markitdown.doc2md.mammoth_transform import mammoth_transform_document
from ctn2md.gen_markitdown.doc2md.mammoth_image_exporter import ImageExporter

logger = logging.getLogger(__name__)

def _get_unique_doc_pathname(md_info: MdInfo) -> str:
    unique_id = md_info.get_unique_job_id()
    src_pathname = md_info.get_doc_pathname()
    src_suffix = os.path.splitext(src_pathname)[1]
    unique_doc_pathname = os.path.join(md_info.get_out_dir(), f"{unique_id}{src_suffix}")
    shutil.copy(src_pathname, unique_doc_pathname)
    return unique_doc_pathname

def gen_md_from_doc(doc_path: str, output_dir: str) -> str:
    """
    Convert a docx file to markdown format.
    :param doc_path: path to the docx file
    :param output_dir: path to the output directory
    :param style_map: style map for mammoth
    :param logger: logger instance
    :return: path to the generated markdown file
    """
    # 设置样式映射
    style_map = get_mammoth_style_map()

    unique_doc_pathname = _get_unique_doc_pathname(md_info)

    logger.info(f"Converting document: {unique_doc_pathname}")

    # 设置图片导出器的状态
    ImageExporter.set_output_dir(md_info.get_out_dir(), md_info.get_unique_job_id())
    # 转换文档
    with open(unique_doc_pathname, "rb") as docx_file:
        result = mammoth.convert_to_markdown(
            docx_file,
            style_map=style_map,
            transform_document=mammoth_transform_document,
            convert_image=mammoth.images.img_element
        )
    # 写入结果，确保不转义特殊字符
    markdown_content = result.value
    markdown_content = ImageExporter.recover_img_ref(markdown_content)
    
    pathname_step0 = md_info.name_step_pathname(0)
    with open(pathname_step0, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    logger.info(f"Markdown file generated: {pathname_step0}")

    return pathname_step0

def generate_markdown_markitdown(md_info: MdInfo) -> str:
    """生成Markdown文件
    
    Args:
        md_info: Markdown信息对象
        
    Returns:
        生成的Markdown文件路径
    """
    # 获取唯一的文档路径
    pathname_step0 = gen_md_from_doc(
        doc_path=md_info.get_doc_pathname(),
        output_dir=md_info.get_out_dir()
    )   
    # 生成Markdown文件
    pathname_step0 = md_info.name_step_pathname(0)
    
    return pathname_step0


if __name__ == "__main__":
    # 设置日志
    logger.setLevel(logging.DEBUG)
    
    # 创建日志目录
    setup_logger_handlers()

    #md_info_path = "_output/ctn2md_mrag__1__座椅STO间隙_P1_px2m/_info.json"
    md_info_path = "_output/ctn2md_misc__成都交通局_华为说明_mid/_info.json"
    md_info = MdInfo(md_info_path)

    ret = generate_markdown_markitdown(md_info)
    rich.print(ret)