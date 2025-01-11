"""
章节层级注入模块的主入口
负责协调标题层级注入和文件分割的整体流程
"""
import logging
import rich
from dotenv import load_dotenv

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.utils.util_markdown import read_markdown_file
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.src.inject_section_hierarchy.hierarchy_processor import process_markdown_hierarchy
from ctn2md.src.inject_section_hierarchy.file_splitter import split_sections_to_files, clear_section_files

def inject_section_hierarchy(md_info_path:str, src_step_num:int = None, dst_step_num:int = None)-> str:
    """
    注入章节层级信息的主入口函数。
    处理 Markdown 文件，添加层级描述，并将文件分割成多个部分。

    :param md_info_path: md_info 文件路径
    :param src_step_num: 源步骤编号
    :param dst_step_num: 目标步骤编号
    :return: 更新后的 md_info 文件路径
    """
    logging.info(f"##MDFLOW##: 开始处理文件 {md_info_path} [step {src_step_num}->{dst_step_num}]")
    md_info = MdInfo(md_info_path)

    pathname_src_step_md, pathname_dst_step_md = md_info.name_src_n_dst_step_pathname(src_step_num, dst_step_num=dst_step_num)
    if pathname_src_step_md is None or pathname_dst_step_md is None:
        raise ValueError(f"未找到源文件或目标文件: {pathname_src_step_md} -> {pathname_dst_step_md}")

    # 读取源文件
    md_text = read_markdown_file(pathname_src_step_md)
    
    # 处理标题层级
    md_text_new = process_markdown_hierarchy(md_text, md_info)
    logging.info(f"已处理标题层级: {pathname_src_step_md}")

    # 保存处理后的文件
    with open(pathname_dst_step_md, "w+", encoding='utf-8') as f:
        f.write(md_text_new)
    logging.info(f"已保存处理结果: {pathname_dst_step_md}")

    # 分割文件
    output_dir = md_info.get_out_dir()
    clear_section_files(output_dir)
    sdsec_names = split_sections_to_files(md_text_new, md_info)
    md_info[MIFN.FNAMES_SECS] = sdsec_names
    logging.info(f"已分割为 {len(sdsec_names)} 个章节文件: {output_dir}")
    
    # 更新并保存 md_info
    md_info.add_step_into_md_info_mdflow(pathname_dst_step_md, actor="fix_section_heirarchy")
    md_info_path = md_info.save()
    logging.info(f"##MDFLOW##: 处理完成 {md_info_path}")
    return md_info_path

if __name__ == "__main__":
    setup_logger_handlers()

    src_step_num = 1
    dst_step_num = 21
    #md_info_path = "_output/ctn2md_深度学习在视电阻率快速反演中的研究/_info.json"
    #md_info_path = "_output/ctn2md_-波士顿咨询：银行业生成式AI应用报告（2023）/_info.json"
    md_info_path = "_output/ctn2md_mrag__4__前后排座椅间距定义_P1_lp/_info.json"

    md_info_path = inject_section_hierarchy(md_info_path, src_step_num=src_step_num, dst_step_num=dst_step_num)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)