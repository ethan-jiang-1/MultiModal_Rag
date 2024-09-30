import logging
import re
#import time
import sys
#import gradio as gr
import rich 

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers, _LOGGER_NAME_PRG

class ProgressLogger:
    # 初始化类级别的变量
    _logger = logging.getLogger(_LOGGER_NAME_PRG)
    _logger_hooked = False
    _progress_history = []  # 记录所有进度信息

    @classmethod
    def _setup_handler(cls):
        """设置自定义日志处理器并将其添加到logger中"""
        
        # 定义自定义处理器类
        class ProgressHandler(logging.Handler):
            def emit(self, record):
                log_entry = self.format(record)
                # 解析日志条目并更新进度
                cls._parse_and_store_progress(log_entry)

        # 检查是否已经设置了处理器，避免重复添加
        if not cls._logger_hooked:
            cls._logger_hooked = True
            handler = ProgressHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))  # 使用简单的日志格式
            cls._logger.addHandler(handler)
    
    @classmethod
    def _parse_and_store_progress(cls, log_entry):
        """解析日志条目并存储到进度历史"""
        
        # 使用正则表达式解析格式 "stepN; percentage: task_name: extra_info"
        #pattern = r"step(\d+\.\d):\s*(\d+)%:\s*(.*?):\s*(.*)"
        pattern = r"step(\d+\.\d):\s*(\d+)%:\s*([^#]+)(?:#(.*))?"
        match = re.match(pattern, log_entry)
        
        if match:
            step, percentage, task_name, extra_info = match.groups()
            # 将解析的内容存储到进度历史

            entry = {
                "step": float(step),
                "percentage": int(percentage),
                "task_name": task_name.strip(),
                "extra_info": extra_info
            }
            cls._progress_history.append(entry)
        else:
            logging.warning(f"failed to parse: {log_entry}")
    
    @classmethod
    def log_progress(cls, message):
        """使用自定义格式记录进度"""
        # 确保处理器已经设置
        cls._setup_handler()
        # 记录日志信息
        cls._logger.info(message)

    @classmethod
    def get_progress_history(cls):
        """返回所有进度历史记录"""
        return cls._progress_history.copy()
    
    @classmethod
    def clear_progress_history(cls):
        """清除进度历史记录"""
        cls._progress_history.clear()


if __name__ == "__main__":
    from HiQA.qa_gradio import main_loop_gradio
    setup_logger_handlers()
    ProgressLogger._setup_handler()


    user_inputs = []
    #user_inputs.append("前后座椅H点参考距离是多少？")
    #user_inputs.append("Ai在人力资源领域前景趋势")
    #user_inputs.append("有哪些比亚迪的项目")
    #user_inputs.append("N-R17圆角的设计目标值是多少？/圆角目标值")
    user_inputs.append("靠背STO间隙要求是什么？")
    #user_inputs.append("主管的培训课程涉及什么")

    user_query = user_inputs[0]
    ProgressLogger.clear_progress_history()
    
    main_loop_gradio(user_query)

    ret = ProgressLogger.get_progress_history()
    rich.print(ret)
    


