from dotenv import load_dotenv as _load_dotenv
import os
import sys
#import logging
import rich
#import random
import json
import re
import json_repair

_load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from llama_parse.utils import Language
from ctn2md.utils.util_ctn_type import CTN_TYPE

_MIB_INFO_VER = "0.4.0"
_MIB_SEP_FNAME_EXT = "___"
_MIB_FNAME_MD_INFO = "_info.json"
_MIB_FNAME_MD_CONTROL_INFO = "_info_ctrl.json"
_MIB_DEFAULT_OUT_ROOT = "_work"

# Names of the field in _info.json  (read_write)
class MIFN:  # Markdown Field Name
    VERSION = "version"

    PATHNAME_ORG_DOC = "pathname_org_doc"

    MDFLOW = "mdflow"
    MDCONTROL = "mdcontrol"
    MDPARAMS = "mdparams"

    FNAMES_PAGES = "fnames_pages"
    FNAMES_IMGS = "fnames_imgs"
    FNAMES_TBLS = "fnames_tbls"
    FNAMES_SNPS = "fnames_snps"

    FNAMES_P_PAGES = "fnames_p_pages"
    FNAMES_P_IMGS = "fnames_p_imgs"
    FNAMES_P_TBLS = "fnames_p_tbls"
    FNAMES_P_SNPS = "fnames_p_snps"

    CTN_TYPE = "content_type"

    GEN_ENGINE = "parse_engine"

    LP_JOB_ID_HISTORY = "lp_job_ids"
    LP_CUR_JOB_ID = "lp_cur_job_id"
    LP_CUR_JOB_METADATA = "lp_cur_job_metadata"

    LP_FNAME_JSON_RESULT_NORMAL = "lp_fname_json_result_normal"
    LP_FNAME_JSON_RESULT_PREMIUM = "lp_fname_json_result_premium"

    LP_I2H_NORMAL = "lp_img2hd_normal"
    LP_I2H_PREMIUM = "lp_img2hd_premium"

    LP_P2M_INFO = "lp_p2m_info"

    FHL_ORG = "fhl_org"
    FHL_MAP_O2N = "fhl_map_o2n"

    IMG_FIGURES = "img_figures"

    MD_SECTIONS = "md_sections"
    FNAMES_SECS = "fnames_secs"

    FNAME_FINAL_MD = "fname_final_md"
    FNAME_FINAL_SUM = "fname_final_sum"

# Names of the field in _info_ctrl.json (read_only)
# dictionary used to control inner flow...
_DEFAULT_MDCONTROL = {
    "mctl_min_img_relevance_score": 0.2,
    "mctl_move_aux_files": True,
    "mctl_need_image_ref": True,

    "mctl_treat_doc_as_ctntype": "auto",

    "mctl_lp_langauge": Language.SIMPLIFIED_CHINESE,
    "mctl_lp_take_screenshot": False,
    "mctl_lp_disable_ocr": False,
    "mctl_lp_premium_pages": "", # The target pages to extract text from documents. 
                                 # Describe as a comma separated list of page numbers. The first page of the document is page 0

    "mctl_lp_img_to_heading": {} # dictionary: key: embed_img_name/page_img_name (without job_id) to val: PlcId:plc_id
}

class MdInfo:
    def __init__(self, md_info_path_or_out_dir):
        if not isinstance(md_info_path_or_out_dir, str):
            raise ValueError(f"MdInfo.init: expect string as path here: {md_info_path_or_out_dir}")

        last_chat = md_info_path_or_out_dir[-1]
        if (last_chat in ["/", "\\"]) or os.path.isdir(md_info_path_or_out_dir):
            self._md_info_path = os.path.join(md_info_path_or_out_dir, _MIB_FNAME_MD_INFO)
        else:
            self._md_info_path = os.path.join(os.path.dirname(md_info_path_or_out_dir), _MIB_FNAME_MD_INFO)
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
    def find_md_info_path(cls, out_dir_or_file_in_out_dir):
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
    def extract_doc_title(cls, pathname_org_doc):
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
        
        return doc_title

    @classmethod
    def get_suggested_out_dir(cls, pathname_org_doc):
        doc_title = cls.extract_doc_title(pathname_org_doc)
        out_dir = f"{_MIB_DEFAULT_OUT_ROOT}/ctn2md_{doc_title}"
        return out_dir

    def load(self):
        if os.path.isfile(self._md_info_path):
            with open(self._md_info_path, 'r', encoding='utf-8') as file:
                data = file.read()
            self._info= json_repair.repair_json(data, return_objects=True, ensure_ascii=True)
        return self._info

    def save(self):
        json_str = json.dumps(self._info, indent=4, ensure_ascii=False)
        with open(self._md_info_path, 'w+', encoding='utf8') as f:
            f.write(json_str) 
        return self._md_info_path

    def _migrate(self):
        if os.path.isfile(self._md_info_path):
            self._info = self.load()
            self._info[MIFN.VERSION] = _MIB_INFO_VER
        else:
            self._info = {MIFN.VERSION: _MIB_INFO_VER}

        if MIFN.MDFLOW not in self._info:
            self._info[MIFN.MDFLOW] = {}
        if MIFN.MDPARAMS not in self._info:
            self._info[MIFN.MDPARAMS] = {}

        for fnames in [MIFN.FNAMES_PAGES, MIFN.FNAMES_IMGS, MIFN.FNAMES_TBLS,MIFN.FNAMES_SNPS]:
            if fnames not in self._info:
                self._info[fnames] = []
        for fnames in [MIFN.FNAMES_P_PAGES, MIFN.FNAMES_P_IMGS, MIFN.FNAMES_P_TBLS,MIFN.FNAMES_P_SNPS]:
            if fnames not in self._info:
                self._info[fnames] = []

        self._load_md_control()
        self.save()

    def _load_md_control(self):
        if not os.path.isfile(self._md_info_control_path):
            json_str = json.dumps(_DEFAULT_MDCONTROL, indent=4, ensure_ascii=False)
            with open(self._md_info_control_path, 'w+', encoding='utf8') as f:
                f.write(json_str) 

        with open(self._md_info_control_path, 'r', encoding='utf-8') as file:
            data = file.read()
        md_control = json_repair.repair_json(data, return_objects=True, ensure_ascii=False)

        self._md_control = md_control

    def update_mdcontrols(self, mdcontrols):
        if isinstance(mdcontrols, dict):
            for key, val in mdcontrols.items():
                self._md_control[key] = val
        self.save()

    def get_out_dir(self):
        os.makedirs(self._out_dir, exist_ok=True)
        return self._out_dir

    def get_aux_dir(self):
        aux_dir = os.path.join(self._out_dir, "_aux")
        os.makedirs(aux_dir, exist_ok=True)
        return aux_dir

    def get_md_info_path(self):
        return self._md_info_path

    def get_unique_job_id(self):
        job_ids = self._info.get(MIFN.LP_JOB_ID_HISTORY, [])
        if len(job_ids) > 0:
            return job_ids[0]
        return self.get_doc_title()

    def set_doc_pathname(self, doc_pathname):
        if MIFN.PATHNAME_ORG_DOC not in self._info:
            self._info[MIFN.PATHNAME_ORG_DOC] = doc_pathname
        return self.save()
    
    def set_gen_engine(self, gen_engine_name):
        self._info[MIFN.GEN_ENGINE] = gen_engine_name

    def get_gen_engine(self):
        return self._info.get(MIFN.GEN_ENGINE, None)

    def get_doc_pathname(self):
        return self.get(MIFN.PATHNAME_ORG_DOC)
    
    def get_doc_title(self):
        return self.extract_doc_title(self.get(MIFN.PATHNAME_ORG_DOC))
    
    def get_md_control(self, mdctrl_name, default_val):
        return self._md_control.get(mdctrl_name, default_val)

    def set_md_params(self, mdparam_name, val):
        if isinstance(mdparam_name, str):
            self._info[MIFN.MDPARAMS][mdparam_name] = val
            return val 
        return None 
    
    def get_md_params(self, mdparam_name, default_val):
        return self._info[MIFN.MDPARAMS].get(mdparam_name, default_val)

    def name_step_pathname(self, step_num):
        pathname_org_doc = self._info.get(MIFN.PATHNAME_ORG_DOC, None)
        if pathname_org_doc is not None:
            basename = os.path.basename(pathname_org_doc)
            ext_name = basename.split(".")[-1]
            if step_num == -1:
                fname_step_md = basename.replace(f".{ext_name}", f"{_MIB_SEP_FNAME_EXT}{ext_name}.md")
            else:
                fname_step_md = basename.replace(f".{ext_name}", f"{_MIB_SEP_FNAME_EXT}{ext_name}_s{step_num}.md")
            pathname_step_md = os.path.join(self._out_dir, fname_step_md)
            return pathname_step_md
        return None

    def name_src_n_dst_step_pathname(self, src_step_num, dst_step_num=None):
        if src_step_num is None:
            src_step_num = self.get_last_step_num()
        pathname_src_step_md = self.name_step_pathname(src_step_num)
        if dst_step_num is None:
            dst_step_num = src_step_num + 1
        pathname_dst_step_md = self.name_step_pathname(dst_step_num)
        return pathname_src_step_md, pathname_dst_step_md 

    def get_last_step_num(self):
        mdflow = self._info.get(MIFN.MDFLOW, None)
        if mdflow is None:
            raise ValueError("no mdflow in MdInfo")
        sorted_keys = sorted(mdflow.keys())
        src_step_num = int(sorted_keys[-1])
        return src_step_num

    @classmethod
    def get_step_num_from_pathname(cls, pathname):
        pattern = r'_s(\d+)\.md$'
        match = re.search(pattern, pathname)
        if match:
            return int(match.group(1))
        return None

    def add_step_into_md_info_mdflow(self, pathname_step_md, actor=None, extra=None):
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

    def get_doc_type(self):
        pathname_org_doc = self._info.get(MIFN.PATHNAME_ORG_DOC, None)
        if pathname_org_doc is not None:
            return pathname_org_doc.split(".")[-1].lower()
        return ""

    def get_ctn_type(self):
        doc_type = self.get_doc_type()
        ctn_type = CTN_TYPE.get_ctn_type_by_doc_type(doc_type)
        # if we have ctn_type defined, using ctn_type
        ctn_type = self._info.get(MIFN.CTN_TYPE, ctn_type)
        return ctn_type

    def get_fnames_pages(self):
        return self.get(MIFN.FNAMES_PAGES, {})

    def get(self, key, default=None):
        return self._info.get(key, default)

    def __getitem__(self, key):
        return self._info.get(key)

    def set(self, key, value):
        self._info[key] = value

    def __setitem__(self, key, value):
        self._info[key] = value

    def __contains__(self, key):
        # 这个方法会在使用in操作符时被调用
        return key in self._info




if __name__ == "__main__":
    import random

    pathnames = []
    pathnames.append("_work/ctn2md_23/AIGC时代的人力资源管理进化(徐刚)___pdf_s0.md")
    pathnames.append("_work/ctn2md_23/AIGC时代的人力资源管理进化(徐刚)___pdf_s10.md")
    pathnames.append("_work/ctn2md_23/AIGC时代的人力资源管理进化(徐刚)___pdf_s.md")
    pathnames.append("AIGC时代的人力资源管理进化(徐刚)___pdf_s100.md")
 
    for ndx, pathname in enumerate(pathnames):
        num = MdInfo.get_step_num_from_pathname(pathname)
        print(ndx, num)
        print(MdInfo.extract_doc_title(pathname))

    out_dir = f"_work/ctn2md_{random.randint(10,99)}"
    os.makedirs(out_dir, exist_ok=True)
    print(out_dir)
    md_info = MdInfo(out_dir)
    md_info["hi"] = 10
    print(md_info["hi"])
    md_info.save()

    md_info_path = "_work/ctn2md_21/info.json"
    md_info = MdInfo(md_info_path)
    rich.print(md_info)

    md_info_path = "_work/ctn2md_21/AIGC时代的人力资源管理进化(徐刚)___pdf_s0.md"
    md_info = MdInfo(md_info_path)
    rich.print(md_info)

    md_info_path = "_work/ctn2md_21"
    md_info = MdInfo(md_info_path)
    rich.print(md_info)