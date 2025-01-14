from dotenv import load_dotenv
import os
import logging
import rich
import asyncio

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.utils.util_markdown import read_markdown_file
from ctn2md.md_info.md_info_base import MdInfo, MIFN
from ctn2md.gen_textin.ti_gen_pages import gen_pages_ti, gen_pages_ti_async

def _construct_s0_md_from_pages(md_info:MdInfo) -> str:
    """异步版本的构建函数"""
    out_dir = md_info.get_out_dir()
    aux_dir = md_info.get_aux_dir()
    fnames_pages = md_info[MIFN.FNAMES_MD_PAGES]
    if len(fnames_pages) == 0:
        raise ValueError(f"{MIFN.FNAMES_MD_PAGES} is empty")
    pathname_step0 = md_info.name_step_pathname(0)

    full_md_text = ""
    for fname_page in fnames_pages:
        fname_page = os.path.basename(fname_page)
        pname_page = os.path.join(out_dir, fname_page)
        if not os.path.isfile(pname_page):
            pname_page = os.path.join(aux_dir, fname_page)       
            if not os.path.isfile(pname_page):
                raise ValueError(f"not able to find page md for {fname_page} to construct s0 document")       
        md_text = read_markdown_file(pname_page)
        if len(full_md_text) != 0:
            full_md_text += "\n"
        full_md_text += md_text

    with open(pathname_step0, "w+", encoding='utf-8') as f: 
        f.write(full_md_text)
    return pathname_step0

async def generate_markdown_textin_async(md_info:MdInfo) -> str:
    """异步版本的主函数"""
    doc_pathname = md_info.get_doc_pathname()
    if (doc_pathname is None) or (not os.path.isfile(doc_pathname)):
        raise ValueError(f"doc_pathname is not valid {doc_pathname}")

    out_dir = md_info.get_out_dir()
    os.makedirs(out_dir, exist_ok=True)

    await gen_pages_ti_async(md_info)

    pathname_step0 = _construct_s0_md_from_pages(md_info)
    md_info.add_step_into_md_info_mdflow(pathname_step0, actor=f"generate_markdown_ti_async")
    md_info.save()

    logging.info(f"original doc: {doc_pathname}")
    logging.info(f"fname_output: {os.path.basename(pathname_step0)}")
    
    md_info_path = md_info.save()
    return md_info_path

def generate_markdown_textin(md_info:MdInfo) -> str:
    """同步版本的主函数"""
    doc_pathname = md_info.get_doc_pathname()
    if (doc_pathname is None) or (not os.path.isfile(doc_pathname)):
        raise ValueError(f"doc_pathname is not valid {doc_pathname}")

    out_dir = md_info.get_out_dir()
    os.makedirs(out_dir, exist_ok=True)

    gen_pages_ti(md_info)

    pathname_step0 = _construct_s0_md_from_pages(md_info)
    md_info.add_step_into_md_info_mdflow(pathname_step0, actor=f"generate_markdown_ti")
    md_info.save()

    logging.info(f"original doc: {doc_pathname}")
    logging.info(f"fname_output: {os.path.basename(pathname_step0)}")
    
    md_info_path = md_info.save()
    return md_info_path

if __name__ == "__main__":
    setup_logger_handlers()

    need_normal_step=False
    need_preminum_step=True
    
    #md_info_path = "_output/ctn2md_papers____AI+应用_百花齐放_新质生产力前景广阔pdf_ti/_info.json"
    md_info_path = "_output/ctn2md_mrag__业绩案例_上汽内外饰DRE外包框架服务合同_ti/_info.json"
    md_info = MdInfo(md_info_path)

    need_sync = True
    if need_sync:
        # 同步测试
        print("\n=== Testing Synchronous Generation ===")
        ret = generate_markdown_textin(md_info)
        rich.print(f"Sync result: {ret}")

    else:
        # 异步测试
        print("\n=== Testing Asynchronous Generation ===")

        async def test_async():
            ret = await generate_markdown_textin_async(md_info)
            rich.print(f"Async result: {ret}")

        asyncio.run(test_async())