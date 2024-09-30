from dotenv import load_dotenv, find_dotenv
import sys
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import colorlog

load_dotenv()

_LOGGER_NAME_LLM = "llm_call"
_LOGGER_NAME_PRG = "app_gradio"

logging.basicConfig(level=logging.INFO)

logger_inited = False

def get_logger_llm():
    logger_llm = logging.getLogger(_LOGGER_NAME_LLM)
    logger_llm.propagate = False
    return logger_llm

def get_logger_progress():
    logger_prg = logging.getLogger(_LOGGER_NAME_PRG)
    logger_prg.propagate = False
    return logger_prg

def _get_log_dir():
    log_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    log_dir = os.path.join(log_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def _get_log_pathname_main():
    log_dir = _get_log_dir()
    srs_name = os.environ.get("SRS_LOG_NAME", "hiqa.log")
    log_srs_file = os.path.join(log_dir, srs_name)
    return log_srs_file


def _get_log_pathname_error():
    log_dir = _get_log_dir()
    sre_name = os.environ.get("SRS_LOGE_NAME", "hiqa_error.log")
    log_sre_file = os.path.join(log_dir, sre_name)
    return log_sre_file

def _get_log_pathname_llm():
    log_dir = _get_log_dir()
    srs_name = os.environ.get("SRS_LOGM_NAME", "hiqa_llm.log")
    log_srl_file = os.path.join(log_dir, srs_name)
    return log_srl_file

def _get_log_pathname_progress():
    log_dir = _get_log_dir()
    srs_name = os.environ.get("SRS_LOGP_NAME", "hiqa_prg.log")
    log_srp_file = os.path.join(log_dir, srs_name)
    return log_srp_file

hooked_logger_names = []

g_stdout_handler = None
g_progress_handler = None
g_error_handler = None
g_progress_handler = None 

def _get_handler_stdout():
    global g_stdout_handler
    if g_stdout_handler is not None:
        return g_stdout_handler

    g_stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    #formatter = logging.Formatter('%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s')
    g_stdout_handler.setFormatter(formatter)
    g_stdout_handler.setLevel(logging.DEBUG)  # 为handler设置级别
    return g_stdout_handler

def _get_handler_main():
    global g_progress_handler
    if g_progress_handler is not None:
        return g_progress_handler

    log_srs_file = _get_log_pathname_main()
    g_progress_handler = TimedRotatingFileHandler(log_srs_file, when="midnight", interval=1, backupCount=30, delay=True, encoding="utf-8")
    g_progress_handler.suffix = "%Y-%m-%d.log"
    formatter = logging.Formatter('%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s')
    g_progress_handler.setFormatter(formatter)
    g_progress_handler.setLevel(logging.INFO)  # 为handler设置级别
    return g_progress_handler


def _get_handler_error():
    global g_error_handler
    if g_error_handler is not None:
        return g_error_handler

    log_sre_file = _get_log_pathname_error()
    g_error_handler = TimedRotatingFileHandler(log_sre_file, when="midnight", interval=7, backupCount=30, delay=True, encoding="utf-8")
    g_error_handler.suffix = "%Y-%m-%d.log"
    formatter = logging.Formatter('%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s')
    g_error_handler.setFormatter(formatter)
    g_error_handler.setLevel(logging.ERROR)  # 为handler设置级别
    return g_error_handler

def _get_handler_progress():
    global g_progress_handler
    if g_progress_handler is not None:
        return g_progress_handler

    log_srp_file = _get_log_pathname_progress()
    g_progress_handler = TimedRotatingFileHandler(log_srp_file, when="midnight", interval=1, backupCount=30, delay=True, encoding="utf-8")
    g_progress_handler.suffix = "%Y-%m-%d.log"
    formatter = logging.Formatter('%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s')
    g_progress_handler.setFormatter(formatter)
    g_progress_handler.setLevel(logging.INFO)  # 为handler设置级别
    return g_progress_handler

def hook_handlers(logger):
    global hooked_logger_names

    if logger is None:
        return 

    if not hasattr(logger, "name"):
        return  

    if logger.name in hooked_logger_names:
        return 

    logger.propagate = False

    hooked_logger_names.append(logger.name)
    print(f"logger {logger.name} hooked")

    handlder_stdout = _get_handler_stdout()
    if handlder_stdout not in logger.handlers:
        logger.addHandler(handlder_stdout)

    handler_main = _get_handler_main()
    if handler_main not in logger.handlers:
        logger.addHandler(handler_main)

    handler_error = _get_handler_error()
    if handler_error not in logger.handlers:
        logger.addHandler(handler_error)


def _setup_logger_llm():
    logger_llm = logging.getLogger(_LOGGER_NAME_LLM)
    logger_llm.propagate = False

    log_srl_file = _get_log_pathname_llm()
    srl_handler = TimedRotatingFileHandler(log_srl_file, when="midnight", interval=1, backupCount=30, delay=True, encoding="utf-8")
    srl_handler.suffix = "%Y-%m-%d.log"
    formatter = logging.Formatter('%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s')
    srl_handler.setFormatter(formatter)
    srl_handler.setLevel(logging.DEBUG)  # 为handler设置级别
    logger_llm.addHandler(srl_handler)

def _setup_logger_prg():
    logger_prg = logging.getLogger(_LOGGER_NAME_PRG)
    logger_prg.propagate = False

    log_srg_file = _get_log_pathname_progress()
    srl_handler = TimedRotatingFileHandler(log_srg_file, when="midnight", interval=1, backupCount=30, delay=True, encoding="utf-8")
    srl_handler.suffix = "%Y-%m-%d.log"
    formatter = logging.Formatter('%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s')
    srl_handler.setFormatter(formatter)
    srl_handler.setLevel(logging.DEBUG)  # 为handler设置级别
    logger_prg.addHandler(srl_handler)


def setup_logger_handlers():
    global logger_inited 
    if logger_inited:
        return 

    logger_inited = True

    # hook logging to output the log to stdout as well
    logger = logging.getLogger()
    hook_handlers(logger)

    logger = logging.getLogger('openai')
    hook_handlers(logger) 

    logger = logging.getLogger('httpx')
    hook_handlers(logger)

    os.environ["OPENAI_LOG"] = "debug"
    _setup_logger_llm()
    _setup_logger_prg()


def _move_log_files(log_filename):
    import shutil
    try:
        log_filename_bak = log_filename + ".bak"
        if os.path.isfile(log_filename_bak):
            os.unlink(log_filename_bak)

        if os.path.isfile(log_filename):
            shutil.copy(log_filename, log_filename_bak)
            logging.info(f"MLF: moving {log_filename} to {log_filename_bak}")
            if os.path.isfile(log_filename):
                os.unlink(log_filename)

    except Exception as ex: 
        logging.exception(str(ex))


def reset_log_files():
    logging.info("RLF: move log (srs, sre) files")
    log_srs_file = _get_log_pathname_main()
    _move_log_files(log_srs_file)

    log_sre_file = _get_log_pathname_error()
    _move_log_files(log_sre_file)
    logging.info("RLF: move log (srs, sre) done")


if __name__ == "__main__":
    setup_logger_handlers()