import os
from typing import List, Tuple, Optional
import logging
import rich
import fitz  # PyMuPDF
from dotenv import load_dotenv
load_dotenv()


from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.md_info.md_info_base import MdInfo, MIFN
from ctn2md.gen_base.utils.gen_utils import is_still_in_gen_mode

IMG_EXT = "jpg"  # or "png"
#IMG_EXT = "png"  # or "png"
JPG_QUALITY = 90 # 95


def _assign_final_doc_cnt_type(md_info:MdInfo, pdf_document:fitz.Document):
    from ctn2md.utils.util_ctn_type import CTN_TYPE
    doc_type = md_info.get_doc_type()
    md_info[MIFN.DOC_CTN_TYPE] = CTN_TYPE.get_ctn_type_by_doc_type(doc_type)
    if pdf_document is not None and len(pdf_document) > 0:
        page1 = pdf_document[0]
        page_width, page_height = page1.mediabox_size
        if md_info[MIFN.DOC_CTN_TYPE] == CTN_TYPE.PDF:
            if page_width > page_height:
                md_info[MIFN.DOC_CTN_TYPE] = CTN_TYPE.PPT
        md_info.save()

def parse_pdf_to_images(md_info: MdInfo, 
                        sel_page_indexes: Optional[List[int]] = None) -> List[Tuple[str, str, List[str]]]:
    """
    Parse PDF to images and save to output_dir.
    """

    output_dir = md_info.get_out_dir()
    pdf_path = md_info.get_doc_pathname()
    job_id = md_info.get_unique_job_id()

    if not os.path.isdir(output_dir):
        raise ValueError(f"output dir does not exit {output_dir}")
    if len(job_id) == 0:
        raise ValueError(f"invalid job_id {job_id}")

    if not is_still_in_gen_mode(md_info):
        clean_previous_images(output_dir, job_id)

    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    fnames_page = []

    for page_index, page in enumerate(pdf_document):
        page_index += 1

        fname_page_name = f'{job_id}-page_{page_index}.{IMG_EXT}'
        pname_page_name = os.path.join(output_dir, fname_page_name)

        if not is_still_in_gen_mode(md_info):
            if sel_page_indexes is not None:
                if page_index not in sel_page_indexes:
                    logging.info(f"skip {page_index} due to sel_page_indexes")
                    continue     

        logging.info(f'parse page: {page_index}')

        page_image = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        try:
            page_image.save(pname_page_name, jpg_quality=JPG_QUALITY)
            logging.info(f"pname_page_name saved {pname_page_name}")
        except Exception as ex:
            logging.exception(ex)
  
        fnames_page.append(fname_page_name)

    _assign_final_doc_cnt_type(md_info, pdf_document)
    pdf_document.close()
    return fnames_page

def clean_previous_images(output_dir:str, job_id:str):
    if not os.path.isdir(output_dir):
        return
    names = os.listdir(output_dir)
    for name in names:
        if not name.endswith(f".{IMG_EXT}"):
            continue
        if not name.startswith(job_id):
            continue
        pname = os.path.join(output_dir, name)
        if os.path.isfile(pname):
            logging.info(f"clearn image {name}")
            os.unlink(pname)

if __name__ == "__main__":
    #setup_logger_handlers(logging.DEBUG)
    setup_logger_handlers()

    doc_pathname = "datasrc/exam/raw_docs/papers/DeepSeek_V3.pdf"
    sel_page_indexes = None

    output_dir = MdInfo.get_suggested_out_dir(doc_pathname, suffix='ti')

    os.makedirs(output_dir, exist_ok=True)

    md_info = MdInfo(output_dir)
    md_info.set_doc_pathname(doc_pathname)

    image_infos = parse_pdf_to_images(md_info, sel_page_indexes=sel_page_indexes)
    rich.print(image_infos)
