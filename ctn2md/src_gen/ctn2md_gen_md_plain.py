from dotenv import load_dotenv
import os
#import logging
import rich

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.src.md_info_base import MdInfo
from ctn2md.utils.util_ctn_type import CTN_TYPE
from ctn2md.src_gen.ctn2md_gen_md_base import GenMd_Base


class GenMd_Plain(GenMd_Base):
    SUPPORT_CNT_TYPES = [CTN_TYPE.MD]
    OD_SUFFIX = "md"

    @classmethod
    def generate_markdown(cls,
                          doc_pathname, 
                          out_dir=None, 
                          enforced_gen=False, 
                          mdcontrols=None):
        if not cls.does_support_doc_type(doc_pathname):
            raise ValueError(f"GenMd_Plain does not support '{doc_pathname}'")

        md_info, gen_needed = cls.does_gen_needed(doc_pathname, out_dir, enforced_gen)

        if isinstance(mdcontrols, dict):
            md_info.update_mdcontrols(mdcontrols)
            md_info.save()

        if gen_needed:
            md_info_path = cls._gen_md_core(doc_pathname, md_info)
            if md_info_path is None:
                return None

        return md_info.get_md_info_path()

    @classmethod
    def need_followup_step(cls, step_name):
        if step_name == "fix_headings_plc_by_llm":
            return False 
        return True
    
    @classmethod
    def _gen_md_core(cls, doc_pathname, md_info):
        from ctn2md.gen_plain.gen_markdown_plain import gen_md_plain
        return gen_md_plain(doc_pathname, md_info)


if __name__ == "__main__":
    #doc_pathname = "_output/ctn2md_attention_is_all_you_need/attention_is_all_you_need___pdf_s0.md"
    #doc_pathname = "_output/ctn2md_attention_is_all_you_need/attention_is_all_you_need___pdf.md"
    #doc_pathname = "_output/ctn2md_AIGC时代的人力资源管理进化(徐刚)_lp/AIGC时代的人力资源管理进化(徐刚)___pdf.md"
    doc_pathname = "_work/ctn2md_mrag__业绩案例_上汽内外饰DRE外包框架服务合同_lvlm/业绩案例、上汽内外饰DRE外包框架服务合同___pdf.md"

    out_dir = MdInfo.get_suggested_out_dir(doc_pathname, GenMd_Plain.OD_SUFFIX)
    md_info = MdInfo(out_dir)

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    md_info_path = GenMd_Plain.generate_markdown(doc_pathname, out_dir=out_dir)
    print(md_info_path)

    md_info = MdInfo(md_info_path)
    rich.print(md_info)
    print(md_info_path)