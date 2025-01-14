import logging
import shutil
import os
from dotenv import load_dotenv
import rich
import markitdown

load_dotenv()

#from ctn2md.gen_base.scan_img_ref_and_update import scan_img_ref_and_update
from ctn2md.md_info.md_info_base import MdInfo
from mmbase.utils.util_logging import setup_logger_handlers


logger = logging.getLogger(__name__)

def _get_unique_doc_pathname(md_info: MdInfo) -> str:
    unique_id = md_info.get_unique_job_id()
    src_pathname = md_info.get_doc_pathname()
    src_suffix = os.path.splitext(src_pathname)[1]
    unique_doc_pathname = os.path.join(md_info.get_out_dir(), f"{unique_id}{src_suffix}")
    shutil.copy(src_pathname, unique_doc_pathname)
    return unique_doc_pathname

def gen_md_from_xls(md_info: MdInfo) -> str:
    """
    Convert a docx file to markdown format.
    """
    unique_doc_pathname = _get_unique_doc_pathname(md_info)
    print(unique_doc_pathname)

    md_converter = markitdown.MarkItDown()
    ret = md_converter.convert_local(unique_doc_pathname)

    markdown_content = ret.text_content
    pathname_step0 = md_info.name_step_pathname(0)
    with open(pathname_step0, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    # 扫描图片引用
    #scan_img_ref_and_update(md_info, pathname_step0)

    logger.info(f"Markdown file generated: {pathname_step0}")

    return pathname_step0

if __name__ == "__main__":
    # 设置日志
    logger.setLevel(logging.DEBUG)
    
    # 创建日志目录
    setup_logger_handlers()

    #md_info_path = "_output/ctn2md_mrag__1__座椅STO间隙_P1_px2m/_info.json"
    #md_info_path = "_output/ctn2md_misc__成都交通局_华为说明_mid/_info.json"
    md_info_path = "_output/ctn2md_mrag__主管培训课程清单_mid/_info.json"

    md_info = MdInfo(md_info_path)

    ret = gen_md_from_xls(md_info)
    rich.print(ret)