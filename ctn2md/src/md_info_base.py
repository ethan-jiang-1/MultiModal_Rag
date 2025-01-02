from typing import List, Tuple
from dotenv import load_dotenv as _load_dotenv
import os
import sys
import logging
import rich
#import random
import json
import re
import json_repair
import shutil
#from enum import Enum

_load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from llama_parse.utils import Language
from ctn2md.utils.util_ctn_type import CTN_TYPE
from ctn2md.utils.util_file import get_crc32_id

_MIB_INFO_VER = "0.9.2"
_MIB_SEP_FNAME_EXT = "___"
_MIB_FNAME_MD_INFO = "_info.json"
_MIB_FNAME_MD_CONTROL_INFO = "_info_ctrl.json"
_MIB_FNAME_FINAL_INFO = "_final_info.json"
_MIB_DEFAULT_OUT_ROOT = "_output"
_MIB_CTN2MD_LEAD = "ctn2md"
_MIB_AUX_SUBDIR = "_aux"

ENV_MODEL_FLOW = "ENV_MODEL_FLOW"  # models used for flow mode: gpt/qwen/ark
ENV_MODEL_GEN_LP = "ENV_MODEL_GEN_LP"  # models used for lp mode: gpt/qwen/ark
ENV_MODEL_GEN_LVLM = "ENV_MODEL_GEN_LVLM"  # models used for lvlm mode: gpt/qwen/ark
ENV_MODEL_GEN_LVLM_REGION = "ENV_MODEL_GEN_LVLM_REGION"  # models used for lvlm mode: gpt/qwen/ark/gs1/gs0
ENV_MODEL_GEN_TI = "ENV_MODEL_GEN_TI"  # models used for textin mode: gpt/qwen/ark
class FHL_QUALITY_TYPE:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Names of the field in _info.json  (read_write)
class PUBLIC_MIFN:
    VERSION = "version"
    GEN_ENGINE = "parse_engine"
    PATHNAME_ORG_DOC = "pathname_org_doc"
    PATHNAME_SRC_DOC = "pathname_src_doc"
    FNAME_ORG_DOC = "fname_org_doc"

    DOC_UNIQUE_ID = "doc_unique_id"
    DOC_CTN_TYPE = "doc_content_type"
    DOC_NAME_TITLE = "doc_title_name"
    DOC_LOGIC_TITLE = "doc_title_logic"
    DOC_SUMMARY = "doc_summary"

    FNAMES_SECS = "fnames_secs" 
    FNAMES_IMGS = "fnames_imgs"
    FNAMES_SNPS = "fnames_snps"

    FNAME_FINAL_MD = "fname_final_md"
    FNAME_FINAL_SUM = "fname_final_sum"

# Names of the field in _info.json  (read_write)
class MIFN(PUBLIC_MIFN):  # Markdown Field Name
    FNAMES_MD_TBLS = "fnames_md_tbls"
    FNAMES_MD_PAGES = "fnames_md_pages"

    MDFLOW = "mdflow"
    MDCONTROL = "mdcontrol"
    MDPARAMS = "mdparams"

    FHL_QUALITY = "fhl_quality"
    FHL_ORG = "fhl_org"
    FHL_MAP_O2N = "fhl_map_o2n"

    MD_SECTIONS = "md_sections"

    # fields required by llamaparse converter
    LP_FNAMES_P_PAGES = "lp_fnames_p_pages"
    LP_FFNAMES_P_IMGS = "lp_fnames_p_imgs"
    LP_FNAMES_P_TBLS = "lp_fnames_p_tbls"
    LP_FNAMES_P_SNPS = "lp_fnames_p_snps"
    LP_CUR_JOB_ID = "lp_cur_job_id"
    LP_JOB_ID_HISTORY = "lp_job_ids"
    LP_CUR_JOB_METADATA = "lp_cur_job_metadata"
    LP_FNAME_JSON_RESULT_NORMAL = "lp_fname_json_result_normal"
    LP_FNAME_JSON_RESULT_PREMIUM = "lp_fname_json_result_premium"
    LP_I2H_NORMAL = "lp_img2hd_normal"
    LP_I2H_PREMIUM = "lp_img2hd_premium"
    LP_P2M_INFO = "lp_p2m_info"

    # fields required by lvlm converter
    LVLM_CUR_JOB_ID = "lvlm_cur_job_id"
    LVLM_IMAGE_INFOS = "lvlm_image_infos"

    # fields required by textin converter
    TI_CUR_JOB_ID = "ti_cur_job_id"
    TI_MAP_PAGE2REF_IMGS = "ti_map_page2ref_imgs"    

class DefaultModelSource:
    @classmethod
    def get_flow_fix_heading_model(cls) -> str:
        return os.getenv(ENV_MODEL_FLOW, "ark")
    
    @classmethod
    def get_flow_summarize_model(cls) -> str:
        return os.getenv(ENV_MODEL_FLOW, "ark")
    
    @classmethod
    def get_gen_lvlm_img2md_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LVLM, "gpt")
    
    @classmethod
    def get_gen_lvlm_img_relevance_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LVLM, "gpt")
    
    @classmethod
    def get_gen_lvlm_region_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LVLM_REGION, "gs2")
    
    @classmethod
    def get_gen_lp_img_relevance_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LP, "ark")
    
    @classmethod
    def get_gen_lp_img_caption_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LP, "ark")
    
    @classmethod
    def get_gen_ti_img_relevance_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_TI, "ark")
    
    @classmethod
    def get_gen_ti_img_caption_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_TI, "ark")

    

# Names of the field in _info_ctrl.json (read_only)
# dictionary used to control inner flow...
def _get_defualt_md_contrl():
    _DEFAULT_MDCONTROL = {
        "version": _MIB_INFO_VER,
        "mctl_move_aux_files": True,
        "mctl_treat_doc_as_ctntype": "auto",

        "mctl_fix_heading_model": DefaultModelSource.get_flow_fix_heading_model(), # gpt/qwen/ark
        "mctl_summarize_model": DefaultModelSource.get_flow_summarize_model(), # gpt/qwen/ark

        # controls required by llamaparse conversion
        "mctl_lp_min_img_relevance_score": 0.2,
        "mctl_lp_img_relevance_model": DefaultModelSource.get_gen_lp_img_relevance_model(), # qwen/gpt/ark
        "mctl_lp_img_caption_model": DefaultModelSource.get_gen_lp_img_caption_model(), # qwen/gpt/ark
        "mctl_lp_need_image_ref": True,
        "mctl_lp_langauge": Language.SIMPLIFIED_CHINESE,
        "mctl_lp_take_screenshot": False,
        "mctl_lp_disable_ocr": False,
        "mctl_lp_premium_pages": [], # The target pages to extract text from documents in perminum mode. 
                                     # list of page numbers. The first page of the document is page 1

        "mctl_lp_img_to_heading": {}, # dictionary: key: embed_img_name/page_img_name (without job_id) to val: PlcId:plc_id

        # controls required by lvlm conversion
        "mctl_lvlm_images_ignore": "", # list of image need to be ignore, seprated by comma
        
        "mctl_lvlm_img2md_model": DefaultModelSource.get_gen_lvlm_img2md_model(), # gpt/qwen/ark
        "mctl_lvlm_region_model": DefaultModelSource.get_gen_lvlm_region_model(), # gpt/qwen/ark/gs1/gs0

        "mctl_lvlm_paint_page_content_area_ratios":(0.15, 0.15, 0.1, 0.1),
        "mctl_lvlm_paint_max_area_ratio": 0.7,
        "mctl_lvlm_paint_max_outside_ratio": 0.1,
        "mctl_lvlm_paint_min_coverage_ratio": 0.7,
        "mctl_lvlm_paint_content_area_buffer_ratio": 0.05,
        "mctl_lvlm_paint_text_distance_ratio": (0.015, 0.015, 0.015, 0.028), 

        "mctl_lvlm_table_line_distance_ratio": 0.03,
        "mctl_lvlm_table_short_line_ratio":0.03,
        "mctl_lvlm_table_text_distance_ratio": (0.02, 0.02, 0.02, 0.02),

        "mctl_ti_img_relevance_model": DefaultModelSource.get_gen_ti_img_relevance_model(), # qwen/gpt/ark
        "mctl_ti_img_caption_model": DefaultModelSource.get_gen_ti_img_caption_model(), # qwen/gpt/ark
    }
    return _DEFAULT_MDCONTROL

class MdInfo:
    def __init__(self, md_info_path_or_out_dir:str):
        if not isinstance(md_info_path_or_out_dir, str):
            raise ValueError(f"MdInfo.init: expect string as path here: {md_info_path_or_out_dir}")

        self._md_info_path = self._get_suggested_md_info_path(md_info_path_or_out_dir)
        self._md_info_control_path = os.path.join(os.path.dirname(self._md_info_path), _MIB_FNAME_MD_CONTROL_INFO)

        self._out_dir = os.path.dirname(self._md_info_path)
        os.makedirs(self._out_dir, exist_ok=True)
        aux_dir = self.get_aux_dir()
        os.makedirs(aux_dir, exist_ok=True)

        self._migrate()

    def __str__(self):
        # 直接使用字典的__str__方法
        return str(self._info)

    def __repr__(self):
        # 直接使用字典的__repr__方法
        return repr(self._info)
    
    @classmethod
    def _get_suggested_md_info_path(cls, md_info_path_or_out_dir:str):
        if os.path.isdir(md_info_path_or_out_dir):
            md_info_path = os.path.join(md_info_path_or_out_dir, _MIB_FNAME_MD_INFO)
            return md_info_path
        elif os.path.isfile(md_info_path_or_out_dir) and md_info_path_or_out_dir.endswith(".json"):
            return md_info_path_or_out_dir
        raise ValueError(f"not able to suggest md_info_path for {md_info_path_or_out_dir}")

    @classmethod
    def find_md_info_path(cls, out_dir_or_file_in_out_dir:str) -> str:
        if os.path.isfile(out_dir_or_file_in_out_dir):
            dir_name = os.path.dirname(out_dir_or_file_in_out_dir)
        elif os.path.isdir(out_dir_or_file_in_out_dir):
            dir_name = out_dir_or_file_in_out_dir
        else:
            return None
    
        md_info_path = os.path.join(dir_name, _MIB_FNAME_MD_INFO)
        if os.path.isfile(md_info_path):
            return md_info_path
        return None

    @classmethod
    def extract_doc_title(cls, pathname_org_doc:str) -> str:
        """
        提取文档标题，
        :param pathname_org_doc: 原始文档路径
        :return: 文档标题（去掉后缀名、无关顺序标记和多余内容）
        """
        if not isinstance(pathname_org_doc, str):
            return ""
    
        # 获取文件名部分（不包括路径）
        file_name = os.path.basename(pathname_org_doc)
        
        # 找到最后一个点的位置，确保只去掉最后的后缀
        last_dot_index = file_name.rfind('.')
        if last_dot_index != -1:
            file_name = file_name[:last_dot_index]
        
        # 定义要替换的标点符号集合，包括中文标点符号
        punctuation = r'[#\*\-·‘’“”\"\'、。，\.，,.?!;:]|[\u3000-\u303F]'  # 包括了常见的中文标点符号

        # 定义要替换的空白字符集合
        whitespace = r'[\u3000\s]'  # 匹配所有空白字符，包括全角空格和半角空格

        # 替换文件名中的标点符号和空白字符为下划线
        doc_title = re.sub(punctuation, '_', file_name)  # 替换标点符号
        doc_title = re.sub(whitespace, '_', doc_title)  # 替换空白字符

        for ext in ["pdf", "doc", "docx", "ppt", "pptx"]:
            dd_ext = "___" + ext 
            if doc_title.endswith(dd_ext):
                doc_title = doc_title[:len(doc_title) - len(dd_ext)]
        
        return doc_title
    
    @classmethod
    def _recover_kbname_and_doc_title(cls, dirname:str) -> Tuple[str, str]:
        # 固定前缀和可能的后缀
        prefix = _MIB_CTN2MD_LEAD
        suffixes = ["_lvlm", "_lp", "_md", "_usio"]
        
        core_name_with_suffix = dirname[len(prefix) + 1:]

        # 检查并去掉后缀
        core_name = core_name_with_suffix
        for suffix in suffixes:
            if core_name_with_suffix.endswith(suffix):
                core_name = core_name_with_suffix[:-len(suffix)]
                break
            
        split_index = core_name.find("__")
        if split_index != -1:
            kb_name = core_name[:split_index]
            doc_title = core_name[split_index + 2:]  # 跳过双下划线
            return kb_name, doc_title
        else:
            raise ValueError("not able to recover kb_name and doc_title")

    @classmethod
    def get_suggested_out_dir(cls, pathname_org_doc:str, suffix:str = "")->str:
        dir_name = os.path.dirname(pathname_org_doc)
        kb_name = os.path.basename(dir_name)
        doc_title = cls.extract_doc_title(pathname_org_doc)
        if pathname_org_doc.endswith(".md"):
            if kb_name.startswith(_MIB_CTN2MD_LEAD):
                kb_name, doc_title = cls._recover_kbname_and_doc_title(kb_name)

        out_dir = f"{_MIB_DEFAULT_OUT_ROOT}/{_MIB_CTN2MD_LEAD}_{kb_name}__{doc_title}"
        if len(suffix) != 0:
            out_dir += f"_{suffix}"
        else:
            raise ValueError("suffix is a must for out_dir")
        return out_dir

    @classmethod
    def get_fname_final_json(cls) -> str:
        return _MIB_FNAME_FINAL_INFO

    @classmethod
    def get_fname_md_info(cls) -> str:
        return _MIB_FNAME_MD_INFO

    def load(self) -> dict:
        if os.path.isfile(self._md_info_path):
            with open(self._md_info_path, 'r', encoding='utf-8') as file:
                data = file.read()
            self._info= json_repair.repair_json(data, return_objects=True, ensure_ascii=True)
        return self._info

    def save(self) -> str:
        json_str = json.dumps(self._info, indent=4, ensure_ascii=False)
        with open(self._md_info_path, 'w+', encoding='utf8') as f:
            f.write(json_str) 
        return self._md_info_path
    
    def _is_able_to_migrate(self,  version_in_md_info:str):
        current_version = _MIB_INFO_VER # major.minor.build_no
        cmajor, cminor, cbn = current_version.split(".")
        vmajor, vminor, vbn = version_in_md_info.split(".")
        if cmajor != vmajor:
            return False 
        if cminor != vminor:
            return False 
        return True

    def _migrate(self):
        if os.path.isfile(self._md_info_path):
            self._info = self.load()
            if not self._is_able_to_migrate(self._info[MIFN.VERSION]):
                raise ValueError(f"Version is not compatiable, Please delete the outputfolder {self.get_out_dir()} and retry.")
            self._info[MIFN.VERSION] = _MIB_INFO_VER
        else:
            self._info = {MIFN.VERSION: _MIB_INFO_VER}

        if MIFN.MDFLOW not in self._info:
            self._info[MIFN.MDFLOW] = {}
        if MIFN.MDPARAMS not in self._info:
            self._info[MIFN.MDPARAMS] = {}

        for fnames in [MIFN.FNAMES_MD_PAGES, MIFN.FNAMES_IMGS, MIFN.FNAMES_MD_TBLS,MIFN.FNAMES_SNPS]:
            if fnames not in self._info:
                self._info[fnames] = []

        self._load_md_control()
        self.save()

    def _load_md_control(self):
        if not os.path.isfile(self._md_info_control_path):
            json_str = json.dumps(_get_defualt_md_contrl(), indent=4, ensure_ascii=False)
            with open(self._md_info_control_path, 'w+', encoding='utf8') as f:
                f.write(json_str) 

        with open(self._md_info_control_path, 'r', encoding='utf-8') as file:
            data = file.read()
        md_control = json_repair.repair_json(data, return_objects=True, ensure_ascii=False)

        self._md_control = md_control

    def update_mdcontrols(self, mdcontrols: dict):
        if isinstance(mdcontrols, dict):
            for key, val in mdcontrols.items():
                old_val = None
                if key in self._md_control:
                    old_val = self._md_control[key]
                self._md_control[key] = val
                if isinstance(val, str):
                    os.environ[key] = val
                if old_val is not None and old_val != val:
                    logging.info(f"alter md_controls {key}: form {old_val} to {val}")
        self.save()

    def get_out_dir(self) -> str:
        os.makedirs(self._out_dir, exist_ok=True)
        return self._out_dir

    def get_aux_dir(self) -> str:
        aux_dir = os.path.join(self._out_dir, _MIB_AUX_SUBDIR)
        os.makedirs(aux_dir, exist_ok=True)
        return aux_dir

    def get_md_info_path(self) -> str:
        return self._md_info_path

    def get_unique_job_id(self) -> str:
        job_ids = self._info.get(MIFN.LP_JOB_ID_HISTORY, [])
        if len(job_ids) > 0:
            return job_ids[0]
        return self.get_doc_title()

    def set_doc_pathname(self, doc_pathname: str) -> str:
        if MIFN.PATHNAME_ORG_DOC not in self._info:
            self._info[MIFN.PATHNAME_ORG_DOC] = doc_pathname
            self._info[MIFN.FNAME_ORG_DOC] = os.path.basename(doc_pathname)
            self._info[MIFN.DOC_UNIQUE_ID] = self.get_doc_title() + "_" + get_crc32_id(doc_pathname)
            self._copy_org_doc()
        return self.save()

    def _copy_org_doc(self):
        try:
            src_path = self._info[MIFN.PATHNAME_ORG_DOC]
            basename = os.path.basename(src_path)
            dst_path = os.path.join(self.get_out_dir(), basename)
            shutil.copy(src_path, dst_path)
        except Exception as ex:
            logging.exception(ex)
    
    def set_gen_engine(self, gen_engine_name:str):
        self._info[MIFN.GEN_ENGINE] = gen_engine_name

    def get_gen_engine(self) -> str:
        return self._info.get(MIFN.GEN_ENGINE, None)

    def get_doc_pathname(self) -> str:
        return self.get(MIFN.PATHNAME_ORG_DOC)
    
    def get_doc_title(self) -> str:
        return self.extract_doc_title(self.get(MIFN.PATHNAME_ORG_DOC))
    
    def get_md_control(self, mdctrl_name:str, default_val:object)->object:
        if mdctrl_name in os.environ:
            return os.environ[mdctrl_name]
        return self._md_control.get(mdctrl_name, default_val)

    def get_md_control_notouch(self, mdctrl_name:str, default_val:object)->List[str]:
        lst = self._md_control.get(mdctrl_name, default_val)
        if len(lst) > 0:
            xset = set()
            for pn in lst:
                if isinstance(pn, int):
                    xset.add(pn)
                elif isinstance(pn, str):
                    if pn.find("-") != -1:
                        pns = pn.split("-")
                        pn_s = int(pns[0])
                        pn_e = int(pns[1])
                        for pnn in range(pn_s, pn_e):
                            xset.add(pnn)
                    else:
                        xset.add(int(pn))
            lst = list(xset)
            lst = sorted(lst)
        return lst

    def set_md_params(self, mdparam_name:str, val:object) -> object:
        if isinstance(mdparam_name, str):
            self._info[MIFN.MDPARAMS][mdparam_name] = val
            return val 
        return None 
    
    def get_md_params(self, mdparam_name:str, default_val:object) -> object:
        return self._info[MIFN.MDPARAMS].get(mdparam_name, default_val)

    def name_step_pathname(self, step_num:int) -> str:
        pathname_org_doc = self._info.get(MIFN.PATHNAME_ORG_DOC, None)
        if pathname_org_doc is not None:
            basename = os.path.basename(pathname_org_doc)
            ext_name = basename.split(".")[-1]
            if ext_name == "md":
                if step_num == -1:
                    fname_step_md = basename
                else:
                    fname_step_md = basename.replace(f".{ext_name}", f"_s{step_num}.md")                
            else:
                if step_num == -1:
                    fname_step_md = basename.replace(f".{ext_name}", f"{_MIB_SEP_FNAME_EXT}{ext_name}.md")
                else:
                    fname_step_md = basename.replace(f".{ext_name}", f"{_MIB_SEP_FNAME_EXT}{ext_name}_s{step_num}.md")
            pathname_step_md = os.path.join(self._out_dir, fname_step_md)
            return pathname_step_md
        return None

    def name_src_n_dst_step_pathname(self, src_step_num:int, dst_step_num:int = None) -> Tuple[str, str]:
        if src_step_num is None:
            src_step_num = self.get_last_step_num()
        pathname_src_step_md = self.name_step_pathname(src_step_num)
        if dst_step_num is None:
            dst_step_num = src_step_num + 1
        pathname_dst_step_md = self.name_step_pathname(dst_step_num)
        return pathname_src_step_md, pathname_dst_step_md 

    def get_last_step_num(self) -> int:
        mdflow = self._info.get(MIFN.MDFLOW, None)
        if mdflow is None:
            raise ValueError("no mdflow in MdInfo")
        sorted_keys = sorted(mdflow.keys())
        src_step_num = int(sorted_keys[-1])
        return src_step_num

    @classmethod
    def get_step_num_from_pathname(cls, pathname:str) -> int:
        pattern = r'_s(\d+)\.md$'
        match = re.search(pattern, pathname)
        if match:
            return int(match.group(1))
        return None

    def add_step_into_md_info_mdflow(self, pathname_step_md:str, actor:str = None, extra: dict = None)->str:
        basename = os.path.basename(pathname_step_md)
        step_num = self.get_step_num_from_pathname(pathname_step_md)
        if isinstance(step_num, int):
            mdflow = self._info.get(MIFN.MDFLOW, None)
            if mdflow is None:
                self._info[MIFN.MDFLOW] = {}

            flow = {"fname": basename, 
                    "actor": actor}
            if extra is not None:
                flow["extra"] = extra

            self._info[MIFN.MDFLOW][str(step_num)] = flow
            return self.save()
        return None

    def get_doc_type(self) -> str:
        pathname_org_doc = self._info.get(MIFN.PATHNAME_ORG_DOC, None)
        if pathname_org_doc is not None:
            return pathname_org_doc.split(".")[-1].lower()
        return ""

    def get_ctn_type(self) -> str:
        doc_type = self.get_doc_type()
        ctn_type = CTN_TYPE.get_ctn_type_by_doc_type(doc_type)
        # if we have ctn_type defined, using ctn_type
        ctn_type = self._info.get(MIFN.DOC_CTN_TYPE, ctn_type)
        return ctn_type

    def get_fnames_pages(self) -> List[str]:
        return self.get(MIFN.FNAMES_MD_PAGES, {})

    def get(self, key:str, default=None) -> object:
        return self._info.get(key, default)

    def __getitem__(self, key:str) -> object:
        return self._info.get(key)

    def set(self, key:str, value:object):
        self._info[key] = value

    def __setitem__(self, key:str, value:object):
        self._info[key] = value

    def __contains__(self, key:str):
        # 这个方法会在使用in操作符时被调用
        return key in self._info




if __name__ == "__main__":
    import random

    pathnames = []
    pathnames.append("_output/ctn2md_23/AIGC时代的人力资源管理进化(徐刚)___pdf_s0.md")
    pathnames.append("_output/ctn2md_23/AIGC时代的人力资源管理进化(徐刚)___pdf_s10.md")
    pathnames.append("_output/ctn2md_23/AIGC时代的人力资源管理进化(徐刚)___pdf_s.md")
    #pathnames.append("AIGC时代的人力资源管理进化(徐刚)___pdf_s100.md")
 
    for ndx, pathname in enumerate(pathnames):
        num = MdInfo.get_step_num_from_pathname(pathname)
        print(ndx, num)
        print(MdInfo.extract_doc_title(pathname))

    out_dir = f"_output/ctn2md_{random.randint(10,99)}"
    os.makedirs(out_dir, exist_ok=True)
    print(out_dir)
    md_info = MdInfo(out_dir)
    md_info["hi"] = 10
    print(md_info["hi"])
    md_info.save()

    md_info_path = "_output/ctn2md_21/info.json"
    md_info = MdInfo(md_info_path)
    rich.print(md_info)

    #md_info_path = "_output/ctn2md_21/AIGC时代的人力资源管理进化(徐刚)___pdf_s0.md"
    md_info_path = "_output/ctn2md_mrag__4__前后排座椅间距定义_P1_lp/_info.json"
    md_info = MdInfo(md_info_path)
    rich.print(md_info)

    md_info_path = "_output/ctn2md_21"
    md_info = MdInfo(md_info_path)
    rich.print(md_info) 