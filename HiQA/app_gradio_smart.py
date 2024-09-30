#import time
import sys
#import gradio as gr
#import threading

if "./" not in sys.path:
    sys.path.append("./")


from HiQA.utils.util_logging import setup_logger_handlers
from HiQA.app_gradio_base import create_interface
from HiQA._app_log_monitor import ProgressLogger
from HiQA.qa_core import set_gpt_model

# 启动界面
if __name__ == "__main__":
    set_gpt_model("gpt-4o")
    setup_logger_handlers()
    ProgressLogger._setup_handler()

    interface = create_interface()
    interface.launch(share=True)
