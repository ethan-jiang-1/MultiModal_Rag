from dotenv import load_dotenv

load_dotenv()

from mmbase.utils.util_logging import setup_logger_handlers, get_logger_progress

class ProgressLogger:
    _progress_history = []
    _progress_status = {}
    _logger = None

    @classmethod
    def _setup_handler(cls):
        if cls._logger is None:
            setup_logger_handlers()
            cls._logger = get_logger_progress()

    @classmethod
    def clear_progress_history(cls):
        cls._progress_history = []
        cls._progress_status = {}

    @classmethod
    def get_progress_history(cls):
        return cls._progress_history.copy()

    @classmethod
    def get_progress_status(cls):
        return cls._progress_status.copy()

    @classmethod
    def log_progress(cls, message):
        cls._setup_handler()
        cls._logger.info(message)

        # 处理JSON状态更新
        if "```json" in message:
            key, json_str = message.split("```json", 1)
            json_str = json_str.strip("```")
            try:
                import json
                data = json.loads(json_str)
                cls._progress_status[key.strip()] = data
            except Exception:
                pass
            return

        # 处理进度信息
        parts = message.replace("：", ":").split(":", 2)  # 最多分割2次，保留后面的冒号
        if len(parts) >= 3:
            step = parts[0].strip()
            try:
                percentage = int(parts[1].replace("%", "").strip())
            except Exception:
                return

            task_info = parts[2].strip()
            extra_info = None
            if "#" in task_info:
                task_name, extra_info = task_info.split("#", 1)
            else:
                task_name = task_info

            progress_entry = {
                "step": float(step.replace("step", "").strip()),
                "percentage": percentage,
                "task_name": task_name.strip(),
                "extra_info": extra_info.strip() if extra_info else None
            }
            cls._progress_history.append(progress_entry)



