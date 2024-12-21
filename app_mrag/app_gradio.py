#import time
import sys
#import gradio as gr
#import threading

if "./" not in sys.path:
    sys.path.append("./")


from md2vdb.utils.util_logging import setup_logger_handlers
from app_mrag.app_gradio_base import create_interface
from app_mrag._app_log_monitor import ProgressLogger
from md2vdb.utils.util_model import set_gpt_model

# 启动界面
if __name__ == "__main__":
    set_gpt_model("gpt-4o")
    setup_logger_handlers()
    ProgressLogger._setup_handler()

    interface = create_interface()
    interface.launch(share=True)
