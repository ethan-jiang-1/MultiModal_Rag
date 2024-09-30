from dotenv import load_dotenv 
import os
import sys
import logging
from pprint import pformat
import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_file import get_root_dir

def _test_one(user_input):
    global user_input_raw
    from HiQA.qa_core import do_core_query, _ensure_working_dir
    #from pprint import pprint

    _ensure_working_dir()
    dir_root = get_root_dir()
    dir_work = os.path.join(dir_root, "_work")
    os.makedirs(dir_work, exist_ok=True)
    
    user_input = user_input.strip()

    ret_dict = {}
    try:
        ret_dict = do_core_query(user_input, kb_name='test')
        pprint(ret_dict)
    except Exception as ex:
        logging.exception(ex)
        ret_dict = {"exception": str(ex)}

    try:
        user_input = user_input.replace("/", "_")
        qa_path = os.path.join(dir_work, "__" + user_input + ".txt")
        with open(qa_path, "w+") as f:
            output = pformat(ret_dict)
            f.write(output)
    except Exception as ex:
        logging.exception(ex)
    return ret_dict

if __name__ == "__main__":
    from pprint import pprint
    user_inputs = []
    user_inputs.append("前后座椅H点参考距离是多少？")
    #user_inputs.append("Ai在人力资源领域前景趋势")
    #user_inputs.append("有哪些比亚迪的项目")
    #user_inputs.append("N-R17圆角的设计目标值是多少？/圆角目标值")
    #user_inputs.append("靠背STO间隙要求是什么？")
    #user_inputs.append("主管的培训课程涉及什么")
    #user_inputs.append("有哪些关于电子电器的项目")

    #user_inputs.append("你好")
    #user_inputs.append("我什么都不知道，你能帮助我什么")
   # user_inputs.append("帮助我写一首唐诗吧")

    for user_input in user_inputs:
        try:
            ret_dict = _test_one(user_input)
            rich.print(ret_dict)
        except Exception as ex:
            logging.exception(ex)


