import logging
import re
from typing import List
import rich 
import json_repair
from dotenv import load_dotenv
load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers, _LOGGER_NAME_PRG

class ProgressLogger:
    # 初始化类级别的变量
    _logger = logging.getLogger(_LOGGER_NAME_PRG)
    _logger_hooked = False
    _progress_history = []  # 记录所有进度信息
    _progress_status = {}

    @classmethod
    def _setup_handler(cls):
        """设置自定义日志处理器并将其添加到logger中"""
        
        # 定义自定义处理器类
        class ProgressHandler(logging.Handler):
            def emit(self, record):
                log_entry = self.format(record)
                
                if log_entry.find("```json") != -1:
                    cls._parse_and_store_status(log_entry)
                elif log_entry.find("step") != -1:
                    cls._parse_and_store_progress(log_entry)

        # 检查是否已经设置了处理器，避免重复添加
        if not cls._logger_hooked:
            cls._logger_hooked = True
            handler = ProgressHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))  # 使用简单的日志格式
            cls._logger.addHandler(handler)
    
    @classmethod
    def _parse_and_store_progress(cls, log_entry: str) -> None:
        """解析日志条目并存储到进度历史"""
        
        # 支持的格式示例:
        # - step1: 10%: 选择知识库:mrag
        # - step1.5：10%：查询进入
        # - step2: 20%: 处理结果#附加信息
        # - step10：100%：查询完成#成功
        pattern = r"step(\d+(?:\.\d)?)\s*[:：]\s*(\d+)%\s*[:：]\s*([^#]+)(?:#(.*))?"
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
            logging.warning(f"failed to parse step info: {log_entry}")
    
    @classmethod
    def _parse_and_store_status(cls, log_entry: str) -> None:
        if log_entry.find("```json") == -1:
            return 
        names = log_entry.split("```json")
        if len(names) == 2:
            dict_name = names[0]
            dict_json = json_repair.repair_json(names[1], ensure_ascii=True, return_objects=True)
            cls._progress_status[dict_name] = dict_json

    @classmethod
    def log_progress(cls, message: str) -> None:
        """使用自定义格式记录进度"""
        # 确保处理器已经设置
        cls._setup_handler()
        # 记录日志信息
        cls._logger.info(message)

    @classmethod
    def get_progress_history(cls) -> List[dict]:
        """返回所有进度历史记录"""
        return cls._progress_history.copy()

    @classmethod
    def get_progress_status(cls) -> dict:
        return cls._progress_status
    
    @classmethod
    def clear_progress_history(cls) -> None:
        """清除进度历史记录"""
        cls._progress_history.clear()
        cls._progress_status.clear()


if __name__ == "__main__":
    from mrag_app._app_qa_core import main_loop_gradio
    setup_logger_handlers()
    ProgressLogger._setup_handler()


    user_inputs = []
    #user_inputs.append("前后座椅H点参考距离是多少？")
    #user_inputs.append("Ai在人力资源领域前景趋势")
    #user_inputs.append("有哪些比亚迪的项目")
    #user_inputs.append("N-R17圆角的设计目标值是多少？/圆角目标值")
    user_inputs.append("靠背STO间隙要求是什么")
    #user_inputs.append("主管的培训课程涉及什么")

    user_query = user_inputs[0]
    ProgressLogger.clear_progress_history()
    
    main_loop_gradio(user_query)

    ret = ProgressLogger.get_progress_history()
    rich.print(ret)
    


