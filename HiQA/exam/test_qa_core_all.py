from dotenv import load_dotenv
import os
import sys
import logging
#import json
from pprint import pformat
import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_file import get_root_dir

user_input_raw = ''' 
前后座椅H点参考距离是多少？
椅背板与旁侧版的保留运动间隙是多少？
靠背最后位置时与侧板翻边的运动间隙是多少？
法规要求的前后排座椅距离是多少
前后排座椅距离的设计目标是多少？
UN-R17圆角的法规要求是多少/圆角法规
UN-R17圆角的设计目标值是多少？/圆角目标值
乘员保护的圆角要求是多少？/圆角设计要求
座垫STO间隙要求是什么？
靠背STO间隙要求是什么？
Ai在人力资源领域前景趋势
管理者的组织执行能力是什么？
该如何做好一个管理者
如何进行高效沟通
有哪些比亚迪的项目
有哪些关于电子电器的项目
考勤规则/考勤规则是什么
主管的培训课程涉及什么'''

def _test_all():
    global user_input_raw
    from HiQA.qa_core import do_core_query, _ensure_working_dir
    #from pprint import pprint

    _ensure_working_dir()
    dir_root = get_root_dir()
    dir_work = os.path.join(dir_root, "_work")
    os.makedirs(dir_work, exist_ok=True)
    
    user_input_raw = user_input_raw.strip()
    user_inputs = user_input_raw.split("\n")

    for user_input in user_inputs:
        user_input = user_input.strip()

        try:
            ret_dict = do_core_query(user_input, kb_name='test')
            rich.print(ret_dict)
        except Exception as ex:
            logging.exception(ex)
            ret_dict = {"exception": str(ex)}

        try:
            user_input = user_input.replace("/", "_")
            qa_path = os.path.join(dir_work, user_input + ".txt")
            with open(qa_path, "w+") as f:
                output = pformat(ret_dict)
                f.write(output)
        except Exception as ex:
            logging.exception(ex)

if __name__ == "__main__":
    _test_all()

