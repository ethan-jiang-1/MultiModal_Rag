from typing import List
from dotenv import load_dotenv
import os
import logging
import rich
import asyncio
import time

load_dotenv()


from ctn2md.utils_gen.gen_base import get_job_id
from ctn2md.utils_gen.gen_base import is_still_in_gen_mode
from ctn2md.gen_ti.ti_pdf_pages_to_images import parse_pdf_to_images
from ctn2md.gen_ti.ti_pdf_images_to_mds import convert_images_to_mds, convert_images_to_mds_async
from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN

def gen_pages_ti(md_info:MdInfo, mdcontrols:dict = None, skip_gen_mds: bool = False, sel_page_indexes: List[int] = None) -> str:
    start_time = time.time()
    try:
        pathname_doc = md_info.get_doc_pathname()
        job_id = get_job_id(pathname_doc)
        md_info[MIFN.TI_CUR_JOB_ID] = job_id

        if isinstance(mdcontrols, dict):
            md_info.update_mdcontrols(mdcontrols)

        logging.info(f"GPL: generate image pages job_id:{job_id}")
        # Step1: convert all pdf pages to images
        fnames_page_image = parse_pdf_to_images(md_info, sel_page_indexes=sel_page_indexes)
        rich.print(fnames_page_image)
        md_info[MIFN.FNAMES_SNPS] = fnames_page_image
        md_info.save()

        # Step2: Convert images to mds by LVLM
        if not skip_gen_mds or is_still_in_gen_mode(md_info):
            logging.info(f"GPL: convert images to mds")
            convert_images_to_mds(md_info, fnames_page_image)
            logging.info(f"GPL: page generated")
        else:
            logging.warning(f"GPL: skip convert images to mds")

        return md_info.save()
    except Exception as e:
        logging.error(f"Failed to process document {pathname_doc}")
        logging.exception(e)
        raise
    finally:
        elapsed_time = time.time() - start_time
        logging.info(f"🕒 Synchronous processing completed in {elapsed_time:.2f} seconds")

async def gen_pages_ti_async(md_info:MdInfo, mdcontrols:dict = None, skip_gen_mds: bool = False, sel_page_indexes: List[int] = None) -> str:
    start_time = time.time()
    pathname_doc = md_info.get_doc_pathname()
    try:
        job_id = get_job_id(pathname_doc)
        md_info[MIFN.TI_CUR_JOB_ID] = job_id

        if isinstance(mdcontrols, dict):
            md_info.update_mdcontrols(mdcontrols)

        logging.info(f"GPL: generate image pages job_id:{job_id} for {pathname_doc}")
        # Step1: convert all pdf pages to images
        fnames_page_image = parse_pdf_to_images(md_info, sel_page_indexes=sel_page_indexes)
        rich.print(fnames_page_image)
        md_info[MIFN.FNAMES_SNPS] = fnames_page_image
        md_info.save()

        # Step2: Convert images to mds by LVLM
        if not skip_gen_mds or is_still_in_gen_mode(md_info):
            logging.info(f"GPL: convert images to mds")
            await convert_images_to_mds_async(md_info, fnames_page_image)
            logging.info(f"GPL: page generated")
        else:
            logging.warning(f"GPL: skip convert images to mds")

        return md_info.save()
    except Exception as e:
        logging.error(f"Failed to process document {pathname_doc}")
        logging.exception(e)
        raise
    finally:
        elapsed_time = time.time() - start_time
        logging.info(f"⚡ Asynchronous processing completed in {elapsed_time:.2f} seconds for {pathname_doc}")

if __name__ == "__main__":
    setup_logger_handlers()

    #doc_pathname = "datasrc/exam/raw_docs/papers/DeepSeek_V3.pdf"
    #doc_pathname = "datasrc/exam/raw_docs/mrag/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    doc_pathname = "datasrc/exam/raw_docs/papers/ “AI+应用”百花齐放，新质生产力前景广阔pdf.pdf"

    #sel_page_indexes = []
    sel_page_indexes = None

    #mdcontrols = None
    mdcontrols = None
    skip_gen_mds = True

    output_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix='ti')
    os.makedirs(output_dir, exist_ok=True)
    job_id = get_job_id(doc_pathname)

    md_info = MdInfo(output_dir)
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.TI_CUR_JOB_ID] = job_id
    
    need_sync = False 
    if need_sync:
        # 同步测试
        ret = gen_pages_ti(md_info, mdcontrols=mdcontrols, skip_gen_mds=skip_gen_mds)
        rich.print("Sync result:", ret)
    else:
        # 异步测试
        async def test_async():
            ret = await gen_pages_ti_async(md_info, mdcontrols=mdcontrols, skip_gen_mds=skip_gen_mds)
            return ret

        ret = asyncio.run(test_async())
        rich.print("Async result:", ret)

