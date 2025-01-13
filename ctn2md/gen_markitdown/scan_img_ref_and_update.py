from typing import List
import os
from rich import print
from dotenv import load_dotenv
load_dotenv()

from ctn2md.src.md_info_base import MdInfo, PUBLIC_MIFN
from ctn2md.gen_markitdown.scan_img.scanner import ImageReferenceScanner
from ctn2md.gen_markitdown.scan_img.models import ImageReference
from ctn2md.gen_markitdown.scan_img.description_generator import ImageDescriptionGenerator

# 加载环境变量
load_dotenv()

def scan_img_ref_and_update(md_info: MdInfo, pname_step0: str) -> List[ImageReference]:
    """扫描markdown文件中的图片引用并更新md_info
    
    Args:
        md_info: MdInfo对象
        pname_step0: markdown文件路径
        
    Returns:
        List[ImageReference]: 图片引用列表
    """
    # 扫描图片引用
    scanner = ImageReferenceScanner(context_chars=200)
    references = scanner.scan_file(pname_step0)
    
    # 为每个引用生成figure_name和description
    idg = ImageDescriptionGenerator(md_info.get_cache_dir())
    for i, ref in enumerate(references, 1):
        if ref.needs_update():
            figure_name, description = idg.generate_description(
                md_info.get_doc_title(),
                ref.context_before,
                ref.context_after,
                os.path.join(md_info.get_out_dir(), ref.ref_name),
                ref.ref_name,
                i
            )
            ref.update_description(figure_name, description)
    
    # 更新md_info
    image_files = [ref.ref_name for ref in references]
    md_info[PUBLIC_MIFN.FNAMES_IMGS] = image_files
    
    return references

if __name__ == "__main__":
    # 测试目录和文件
    test_dir = "_output/ctn2md_misc__成都交通局_华为说明_mid"
    test_file = os.path.join(test_dir, "成都交通局-华为说明___docx_s0.md")
    
    # 创建md_info对象
    md_info = MdInfo(test_dir)
    
    # 检查文件是否存在
    if not os.path.exists(test_file):
        print(f"[red]Error: File not found: {test_file}[/red]")
        exit(1)
        
    # 扫描图片引用
    references = scan_img_ref_and_update(md_info, test_file)
    print(references)
    
    # 打印结果
    print("\n[blue]找到的图片引用:[/blue]")
    for ref in references:
        print(f"\n图片: {ref.ref_name}")
        print(f"行号: {ref.line_number}")
        if ref.needs_update():
            print("[yellow]需要更新figure_name和description[/yellow]")
        else:
            print(f"figure_name: {ref.figure_name}")
            print(f"description: {ref.image_description}")
        print(f"Markdown格式: {ref.to_markdown()}")
        print(f"前文: {ref.context_before}")
        print(f"后文: {ref.context_after}")
        
    print(f"\n[blue]更新后的md_info.FNAMES_IMGS:[/blue]")
    print(md_info[PUBLIC_MIFN.FNAMES_IMGS])