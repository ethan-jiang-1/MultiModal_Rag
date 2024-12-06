from dotenv import load_dotenv
import os
import sys
import logging
import rich
#import random
import re
import shutil

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from ctn2md.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN
from ctn2md.utils.util_ctn_type import CTN_TYPE


def _copy_img_files_in_markdown(doc_pathname, out_dir):
    """
    Scans the Markdown file for image references, copies the images from `src_dir` to `out_dir`.

    :param doc_pathname: Path to the Markdown file
    :param out_dir: Output directory where images will be copied
    """
    # Get the source directory of the Markdown file
    src_dir = os.path.dirname(doc_pathname)

    # Ensure the output directory exists
    os.makedirs(out_dir, exist_ok=True)

    # Read the content of the Markdown file
    with open(doc_pathname, 'r', encoding='utf-8') as md_file:
        content = md_file.read()

    # Find all image URLs in the Markdown file (ignoring tooltips or labels)
    image_refs = re.findall(r'!\[.*?\]\(([^\)]+?)\s*(?:\".*?\")?\)', content)

    # Process each image reference
    for ref_url in image_refs:
        # Resolve the full source path of the image
        src_path = os.path.join(src_dir, ref_url)

        # If the source path exists, copy it to the output directory
        if os.path.exists(src_path):
            # Compute the destination path
            dest_path = os.path.join(out_dir, ref_url)

            # Create directories for the destination path if necessary
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Copy the file
            shutil.copy2(src_path, dest_path)
            logging.info(f"Copied: {src_path} -> {dest_path}")
        else:
            logging.info(f"Warning: File not found - {src_path}")
    return image_refs
    

def gen_md_plain(doc_pathname, md_info):
    logging.info(f"##MDFLOW##: gen_md_plain started...")

    out_dir = md_info.get_out_dir()
    md_info.set_gen_engine("llamaparse:plain")
    md_info.set_doc_pathname(doc_pathname)

    pathname_s0_md = md_info.name_step_pathname(0)
    shutil.copy(doc_pathname, pathname_s0_md)
    md_info.add_step_into_md_info_mdflow(pathname_s0_md, actor="gen_md_plain")
    md_info.save()

    img_refs = _copy_img_files_in_markdown(doc_pathname, out_dir)
    md_info[MIFN.FNAMES_IMGS] = img_refs
    md_info.save()

    md_info_path = md_info.get_md_info_path()

    logging.info(f"##MDFLOW##: gen_md_plain end")
    return md_info_path


class GenMd_Plain:
    @classmethod
    def generate_markdown(cls,
                          doc_pathname, 
                          out_dir=None, 
                          enforced_gen=False, 
                          mdcontrols=None):
        if not cls.does_support_doc_type(doc_pathname):
            raise ValueError(f"GenMd_Plain does not support {doc_pathname}")

        md_info_path = None
        gen_needed = False
        if not enforced_gen:
            md_info = MdInfo(out_dir)
            md_info_path = md_info.get_md_info_path()
            pathname_s0_md = md_info.name_step_pathname(0)
            if (pathname_s0_md is None) or (not os.path.exists(pathname_s0_md)):
                gen_needed = True
        else:
            gen_needed = True

        if gen_needed:
            md_info_path = gen_md_plain(doc_pathname, md_info)
            if md_info_path is None:
                return None

        if mdcontrols is not None:
            md_info.update_mdcontrols(mdcontrols)
        return md_info_path

    @classmethod
    def need_followup_step(cls, step_name):
        if step_name == "fix_headings_plc_by_gpt":
            return True 
        return True

    @classmethod
    def does_support_doc_type(cls, doc_pathname):
        ctn_type = CTN_TYPE.get_ctn_type_by_doc_pathname(doc_pathname)
        if ctn_type in [CTN_TYPE.MD]:
            return True
        return False


if __name__ == "__main__":
    #doc_pathname = "_work/ctn2md_attention_is_all_you_need/attention_is_all_you_need___pdf_s0.md"
    doc_pathname = "_work/ctn2md_attention_is_all_you_need/attention_is_all_you_need___pdf.md"

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname)
    md_info = MdInfo(out_dir)

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = gen_md_plain(doc_pathname, md_info)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)