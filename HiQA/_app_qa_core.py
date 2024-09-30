from dotenv import load_dotenv
import os
import sys
import logging
#from pprint import pformat
import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers, get_logger_progress
from HiQA.utils.util_file import get_root_dir

setup_logger_handlers()
logger_prg = get_logger_progress()

def _ensure_working_dir():
    dir_root = get_root_dir()
    dir_hiqa = os.path.join(dir_root, "HiQA")
    os.chdir(dir_hiqa)
    return dir_hiqa
   
_ensure_working_dir()

from qa_core import do_core_query as _do_core_query

g_ret = {}
def main_loop_gradio(user_input, kb_name="test"):
    global g_ret
    g_ret = {}

    try: 
        logger_prg.info("step0.5: 5%: 查询进入")
        ret = _do_core_query(user_input, kb_name=kb_name)

        g_ret = ret 
        logger_prg.info("step6.5: 100%: 查询退出")
        g_ret["status"] = "success"
    except Exception as ex:
        logging.exception(ex)
        logger_prg.info(f"step0.0: 0%: 查询异常#{str(ex)}")
        g_ret["status"] = f"failed:{str(ex)}"
        
    return 

def get_main_ret():
    global g_ret 
    return g_ret


if __name__ == "__main__":
    #from pprint import pprint
    user_inputs = []
    #user_inputs.append("前后座椅H点参考距离是多少？")
    #user_inputs.append("Ai在人力资源领域前景趋势")
    #user_inputs.append("有哪些比亚迪的项目")
    #user_inputs.append("N-R17圆角的设计目标值是多少？/圆角目标值")
    user_inputs.append("靠背STO间隙要求是什么？")
    #user_inputs.append("主管的培训课程涉及什么")

    for user_input in user_inputs:
        try:
            main_loop_gradio(user_input)
            ret_dict = get_main_ret()
            rich.print(ret_dict)
        except Exception as ex:
            logging.exception(ex)
