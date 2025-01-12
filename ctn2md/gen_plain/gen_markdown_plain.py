from dotenv import load_dotenv
import os
import logging
import shutil
import json 

load_dotenv()

#from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo, MIFN, FHL_QUALITY_TYPE, PUBLIC_MIFN
from ctn2md.utils.util_markdown import find_all_image_refs

def _copy_img_files_in_markdown(doc_pathname:str, out_dir:str) -> list:
    """
    Scans the Markdown file for image references, copies the images from `src_dir` to `out_dir`.

    :param doc_pathname: Path to the Markdown file
    :param out_dir: Output directory where images will be copied
    """
    # Get the source directory of the Markdown file
    src_dir = os.path.dirname(doc_pathname)

    # Ensure the output directory exists
    os.makedirs(out_dir, exist_ok=True)

    image_refs = find_all_image_refs(doc_pathname)

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

def _copy_orginal_files(md_info:MdInfo, doc_pathname:str) -> str:
    pathname_s0_md = md_info.name_step_pathname(0)
    shutil.copy(doc_pathname, pathname_s0_md)
    logging.info(f"copy file from {doc_pathname} to {pathname_s0_md}")

    dir_org = os.path.dirname(doc_pathname)
    fname_final_json = MdInfo.get_fname_final_json()
    pname_final_json = os.path.join(dir_org, fname_final_json)
    if os.path.isfile(pname_final_json):
        fname_org_final_info = fname_final_json.replace(".json", "_org.json")
        pname_org_final_json = os.path.join(md_info.get_out_dir(), fname_org_final_info)
        if os.path.isfile(pname_final_json):
            shutil.copy(pname_final_json, pname_org_final_json)
            logging.info(f"copy file from {pname_final_json} to {pname_org_final_json}")

            with open(pname_org_final_json, "r", encoding="utf-8") as f:
                org_final_json = json.load(f)
            
            pname_org_doc = org_final_json.get(PUBLIC_MIFN.PATHNAME_ORG_DOC)
            pname_dst_doc = os.path.join(md_info.get_out_dir(), os.path.basename(pname_org_doc))
            if os.path.isfile(pname_org_doc):
                shutil.copy(pname_org_doc, pname_dst_doc)
                logging.info(f"copy file from {pname_org_doc} to {pname_dst_doc}")

                org_final_org_doc = org_final_json.get(PUBLIC_MIFN.PATHNAME_ORG_DOC, None)
                if org_final_org_doc is not None:
                    md_info[PUBLIC_MIFN.PATHNAME_SRC_DOC] = org_final_org_doc

    return pathname_s0_md
    

def gen_md_plain(doc_pathname, md_info):
    logging.info(f"##MDFLOW##: gen_md_plain started...")

    out_dir = md_info.get_out_dir()
    md_info.set_gen_engine("md2md:plain")
    md_info.set_doc_pathname(doc_pathname)
    md_info[MIFN.FHL_QUALITY] = FHL_QUALITY_TYPE.LOW

    pathname_final_md = md_info.name_step_pathname(-1)
    if pathname_final_md == doc_pathname:
        raise ValueError(f"src_md cannot be same as dst_md: {doc_pathname}")

    pathname_s0_md = _copy_orginal_files(md_info, doc_pathname)
    md_info.add_step_into_md_info_mdflow(pathname_s0_md, actor="gen_md_plain")
    md_info.save()

    img_refs = _copy_img_files_in_markdown(doc_pathname, out_dir)
    md_info[MIFN.FNAMES_IMGS] = img_refs
    md_info.save()

    md_info_path = md_info.get_md_info_path()

    logging.info(f"##MDFLOW##: gen_md_plain end")
    return md_info_path