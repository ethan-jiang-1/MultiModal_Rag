from dotenv import load_dotenv as _load_dotenv
import os
import sys
#import logging
import rich
#import random
import json
import re

_load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

SEP_FNAME_EXT = "___"
FNAME_MD_INFO = "info.json"
MD_INFO_VER = "0.1.0"

from HiQA.build_tool.util_md.util_ctn_type import CtnType

class MdInfo:
    def __init__(self, md_info_path_or_out_dir):
        last_chat = md_info_path_or_out_dir[-1]
        if (last_chat in ["/", "\\"]) or os.path.isdir(md_info_path_or_out_dir):
            self._md_info_path = os.path.join(md_info_path_or_out_dir, FNAME_MD_INFO)
        else:
            self._md_info_path = os.path.join(os.path.dirname(md_info_path_or_out_dir), FNAME_MD_INFO)

        self._out_dir = os.path.dirname(self._md_info_path)
        os.makedirs(self._out_dir, exist_ok=True)
        if not os.path.isfile(self._md_info_path):
            self._info = {"version": MD_INFO_VER}
            self.save()
        self._info = self.load() 

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
    
        md_info_path = os.path.join(dir_name, FNAME_MD_INFO)
        if os.path.isfile(md_info_path):
            return md_info_path
        return None

    def load(self):
        if os.path.isfile(self._md_info_path):
            import json_repair
            with open(self._md_info_path, 'r', encoding='utf-8') as file:
                data = file.read()
            self._info= json_repair.repair_json(data, return_objects=True, ensure_ascii=True)
        return self._info

    def save(self):
        json_str = json.dumps(self._info, indent=4, ensure_ascii=False)
        with open(self._md_info_path, 'w+', encoding='utf8') as f:
            f.write(json_str) 
        return self._md_info_path

    def get_out_dir(self):
        return self._out_dir

    def get_md_info_path(self):
        return self._md_info_path

    def set_doc_pathname(self, doc_pathname):
        if "path_org_doc" not in self._info:
            self._info["pathname_org_doc"] = doc_pathname
            self._info["streams"] = {}
        return self.save()

    def get_doc_pathname(self):
        return self.get("pathname_org_doc")

    def name_step_pathname(self, step_num):
        pathname_org_doc = self._info.get("pathname_org_doc", None)
        if pathname_org_doc is not None:
            basename = os.path.basename(pathname_org_doc)
            ext_name = basename.split(".")[-1]
            fname_step_md = basename.replace(f".{ext_name}", f"{SEP_FNAME_EXT}{ext_name}_s{step_num}.md")
            pathname_step_md = os.path.join(self._out_dir, fname_step_md)
            return pathname_step_md
        return None

    def name_src_n_dst_step_pathname(self, src_step_num):
        if src_step_num is None:
            streams = self._info.get("streams", None)
            if streams is None:
                raise ValueError("no streams in MdInfo")
            sorted_keys = sorted(streams.keys())
            src_step_num = int(sorted_keys[-1])
        pathname_src_step_md = self.name_step_pathname(src_step_num)
        pathname_dst_step_md = self.name_step_pathname(src_step_num+1)
        return pathname_src_step_md, pathname_dst_step_md            

    @classmethod
    def get_step_num_from_pathname(cls, pathname):
        pattern = r'_s(\d+)\.md$'
        match = re.search(pattern, pathname)
        if match:
            return int(match.group(1))
        return None

    def add_step_into_md_info_streams(self, pathname_step_md, actor=None):
        basename = os.path.basename(pathname_step_md)
        step_num = self.get_step_num_from_pathname(pathname_step_md)
        if isinstance(step_num, int):
            streams = self._info.get("streams", None)
            if streams is None:
                self._info["streams"] = {}

            self._info["streams"][str(step_num)] = {"fname": basename, 
                                                    "actor": actor}
            return self.save()
        return None

    def get_doc_type(self):
        pathname_org_doc = self._info.get("pathname_org_doc", None)
        if pathname_org_doc is not None:
            return pathname_org_doc.split(".")[-1].lower()
        return ""

    def get_ctn_type(self):
        doc_type = self.get_doc_type()
        return CtnType.get_ctn_type(doc_type)

    def get_fnames_pages(self):
        return self.get("fnames_pages", {})

    def update_info(self, dict_info):
        if isinstance(dict_info, dict):
            for key, val in dict_info.items():
                self._info[key] = val

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