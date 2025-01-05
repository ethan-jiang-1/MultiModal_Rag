from dotenv import load_dotenv

load_dotenv()

from mrag_vdb.utils.util_logging import setup_logger_handlers
from mrag_app._app_gradio_base import create_interface
from mrag_app._app_log_monitor import ProgressLogger
from mrag_vdb.dto.rag_runtime_settings import RagModelGptSel

# 启动界面
if __name__ == "__main__":
    RagModelGptSel.set_gpt_model("qwen-plus-1127")
    setup_logger_handlers()
    ProgressLogger._setup_handler()

    interface = create_interface()
    interface.launch(share=False)
