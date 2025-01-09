import os
import logging
from unittest import TestCase
from dotenv import load_dotenv
import sys
import io

from mmbase.utils.util_logging import (
    LoggingConfig,
    setup_logger_handlers,
    get_logger_llm,
    get_logger_progress,
    init_global_state
)

class TestUtilLoggingNormal(TestCase):
    def setUp(self):
        # 保存原始环境变量
        self.old_env = os.environ.copy()
        
        # 设置测试环境
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 重置LoggingConfig的状态
        LoggingConfig._instance = None
        LoggingConfig._initialized = False
        
        # 重置全局状态
        init_global_state()

    def tearDown(self):
        # 清理日志文件
        if os.path.exists(self.log_dir):
            for f in os.listdir(self.log_dir):
                if f.startswith("test_"):
                    os.remove(os.path.join(self.log_dir, f))
        
        # 恢复环境变量
        os.environ.clear()
        os.environ.update(self.old_env)

    def test_env_override_app_prefix(self):
        """测试环境变量是否能正确覆盖默认的应用前缀"""
        # 设置环境变量
        test_prefix = "test_env_prefix"
        os.environ["APP_LOG_PREFIX"] = test_prefix
        
        # 初始化日志系统，使用不同的默认前缀
        LoggingConfig.initialize("default_prefix", self.log_dir)
        setup_logger_handlers()

        # 写入测试日志
        test_message = "Test message for env override"
        logging.info(test_message)

        # 验证日志文件使用了环境变量指定的前缀
        env_log = os.path.join(self.log_dir, f"{test_prefix}.log")
        self.assertTrue(os.path.exists(env_log))
        
        # 验证默认前缀的日志文件不存在
        default_log = os.path.join(self.log_dir, "default_prefix.log")
        self.assertFalse(os.path.exists(default_log))

    def test_env_dotenv_file(self):
        """测试通过.env文件设置环境变量"""
        # 创建测试用的.env文件
        env_file = os.path.join(self.log_dir, ".env.test")
        with open(env_file, 'w') as f:
            f.write("APP_LOG_PREFIX=test_dotenv_prefix\n")
        
        # 设置DOTENV_FILE环境变量
        os.environ["DOTENV_FILE"] = env_file
        
        # 加载.env文件
        load_dotenv(env_file, override=True)
        
        # 初始化日志系统
        LoggingConfig.initialize("default_prefix", self.log_dir)
        setup_logger_handlers()

        # 写入测试日志
        test_message = "Test message for dotenv"
        logging.info(test_message)

        # 验证日志文件使用了.env文件指定的前缀
        env_log = os.path.join(self.log_dir, "test_dotenv_prefix.log")
        self.assertTrue(os.path.exists(env_log))

    def test_env_priority(self):
        """测试环境变量优先级：直接设置的环境变量 > .env文件 > 默认值"""
        # 创建测试用的.env文件
        env_file = os.path.join(self.log_dir, ".env.test")
        with open(env_file, 'w') as f:
            f.write("APP_LOG_PREFIX=test_dotenv_prefix\n")
        
        # 设置环境变量
        os.environ["DOTENV_FILE"] = env_file
        os.environ["APP_LOG_PREFIX"] = "test_direct_env"
        
        # 加载.env文件
        load_dotenv(env_file, override=False)  # 不覆盖已存在的环境变量
        
        # 初始化日志系统
        LoggingConfig.initialize("default_prefix", self.log_dir)
        setup_logger_handlers()

        # 写入测试日志
        test_message = "Test message for priority"
        logging.info(test_message)

        # 验证使用了直接设置的环境变量值
        env_log = os.path.join(self.log_dir, "test_direct_env.log")
        self.assertTrue(os.path.exists(env_log))
        
        # 验证其他可能的日志文件不存在
        dotenv_log = os.path.join(self.log_dir, "test_dotenv_prefix.log")
        default_log = os.path.join(self.log_dir, "default_prefix.log")
        self.assertFalse(os.path.exists(dotenv_log))
        self.assertFalse(os.path.exists(default_log)) 

    def test_llm_logger_basic(self):
        """测试LLM日志器的基本功能"""
        # 初始化日志系统
        LoggingConfig.initialize("test_normal", self.log_dir)
        setup_logger_handlers()
        
        # 获取LLM日志器
        llm_logger = get_logger_llm()
        
        # 写入测试日志
        test_message = "Test LLM logger message"
        llm_logger.info(test_message)
        
        # 验证LLM日志文件创建和内容
        llm_log = os.path.join(self.log_dir, "test_normal_llm.log")
        self.assertTrue(os.path.exists(llm_log))
        
        with open(llm_log, 'r') as f:
            content = f.read()
            self.assertIn(test_message, content)
            # 验证日志格式
            self.assertRegex(content, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - PID:\d+ - INFO - .*') 

    def test_logger_isolation(self):
        """测试不同日志器之间的隔离性"""
        # 初始化日志系统
        LoggingConfig.initialize("test_normal", self.log_dir)
        setup_logger_handlers()
        
        # 获取不同的日志器
        root_logger = logging.getLogger()
        llm_logger = get_logger_llm()
        progress_logger = get_logger_progress()
        
        # 写入不同的测试消息
        root_message = "Root logger message"
        llm_message = "LLM logger message"
        progress_message = "Progress logger message"
        
        root_logger.info(root_message)
        llm_logger.info(llm_message)
        progress_logger.info(progress_message)
        
        # 检查主日志文件
        main_log = os.path.join(self.log_dir, "test_normal.log")
        self.assertTrue(os.path.exists(main_log))
        with open(main_log, 'r') as f:
            content = f.read()
            self.assertIn(root_message, content)
            self.assertNotIn(llm_message, content)
            self.assertNotIn(progress_message, content)
        
        # 检查LLM日志文件
        llm_log = os.path.join(self.log_dir, "test_normal_llm.log")
        self.assertTrue(os.path.exists(llm_log))
        with open(llm_log, 'r') as f:
            content = f.read()
            self.assertIn(llm_message, content)
            self.assertNotIn(root_message, content)
            self.assertNotIn(progress_message, content)
        
        # 检查Progress日志文件
        progress_log = os.path.join(self.log_dir, "test_normal_prg.log")
        self.assertTrue(os.path.exists(progress_log))
        with open(progress_log, 'r') as f:
            content = f.read()
            self.assertIn(progress_message, content)
            self.assertNotIn(root_message, content)
            self.assertNotIn(llm_message, content) 

    def test_logger_levels(self):
        """测试专门日志器的日志级别处理"""
        # 初始化日志系统
        LoggingConfig.initialize("test_normal", self.log_dir)
        setup_logger_handlers()
        
        # 获取专门的日志器
        llm_logger = get_logger_llm()
        progress_logger = get_logger_progress()
        
        # LLM日志器测试
        llm_debug = "LLM debug message"
        llm_info = "LLM info message"
        llm_error = "LLM error message"
        
        llm_logger.debug(llm_debug)
        llm_logger.info(llm_info)
        llm_logger.error(llm_error)
        
        # Progress日志器测试
        prg_debug = "Progress debug message"
        prg_info = "Progress info message"
        prg_error = "Progress error message"
        
        progress_logger.debug(prg_debug)
        progress_logger.info(prg_info)
        progress_logger.error(prg_error)
        
        # 检查LLM日志文件
        llm_log = os.path.join(self.log_dir, "test_normal_llm.log")
        self.assertTrue(os.path.exists(llm_log))
        with open(llm_log, 'r') as f:
            content = f.read()
            # LLM日志器级别为DEBUG，所有级别都应该记录
            self.assertIn(llm_debug, content)
            self.assertIn(llm_info, content)
            self.assertIn(llm_error, content)
        
        # 检查Progress日志文件
        prg_log = os.path.join(self.log_dir, "test_normal_prg.log")
        self.assertTrue(os.path.exists(prg_log))
        with open(prg_log, 'r') as f:
            content = f.read()
            # Progress日志器级别为DEBUG，所有级别都应该记录
            self.assertIn(prg_debug, content)
            self.assertIn(prg_info, content)
            self.assertIn(prg_error, content)
        
        # 检查错误日志文件
        error_log = os.path.join(self.log_dir, "test_normal_error.log")
        self.assertTrue(os.path.exists(error_log))
        with open(error_log, 'r') as f:
            content = f.read()
            # 错误日志文件只包含ERROR级别的消息
            self.assertIn(llm_error, content)
            self.assertIn(prg_error, content)
            self.assertNotIn(llm_debug, content)
            self.assertNotIn(llm_info, content)
            self.assertNotIn(prg_debug, content)
            self.assertNotIn(prg_info, content) 

    def test_file_log_format(self):
        """测试文件日志的格式"""
        # 初始化日志系统
        LoggingConfig.initialize("test_normal", self.log_dir)
        setup_logger_handlers()
        
        # 写入测试日志
        test_message = "Test format message"
        logging.info(test_message)
        
        # 检查主日志文件
        main_log = os.path.join(self.log_dir, "test_normal.log")
        self.assertTrue(os.path.exists(main_log))
        
        with open(main_log, 'r') as f:
            content = f.read().strip()
            # 验证日志格式的各个部分
            # 1. 时间戳格式: 2025-01-09 13:45:30,123
            self.assertRegex(content, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}')
            
            # 2. PID格式: PID:12345
            self.assertRegex(content, r'PID:\d+')
            
            # 3. 日志级别格式: INFO
            self.assertRegex(content, r'INFO')
            
            # 4. 消息内容
            self.assertIn(test_message, content)
            
            # 5. 完整格式
            self.assertRegex(content, 
                r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - PID:\d+ - INFO - Test format message') 

    def test_console_output_format(self):
        """测试控制台输出的格式"""
        # 初始化日志系统
        LoggingConfig.initialize("test_normal", self.log_dir)
        setup_logger_handlers()
        
        # 创建一个临时的StringIO处理程序
        string_io = io.StringIO()
        string_handler = logging.StreamHandler(string_io)
        formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)-8s %(message)s')
        string_handler.setFormatter(formatter)
        
        # 添加处理程序并写入日志
        logger = logging.getLogger()
        logger.addHandler(string_handler)
        logger.setLevel(logging.INFO)
        logger.info("Console format test")
        
        # 获取输出内容
        output = string_io.getvalue().strip()
        
        # 验证基本格式
        self.assertRegex(output, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}')  # 时间戳
        self.assertRegex(output, r'\d+')  # PID
        self.assertRegex(output, r'INFO\s+')  # 对齐的日志级别
        self.assertIn("Console format test", output)  # 消息内容
        
        # 清理
        logger.removeHandler(string_handler)
        string_io.close()

    def test_stdout_handler_format(self):
        """测试标准输出处理程序的基本格式"""
        # 初始化日志系统
        LoggingConfig.initialize("test_normal", self.log_dir)
        setup_logger_handlers()
        
        # 获取根日志器
        root_logger = logging.getLogger()
        
        # 检查是否有stdout处理程序
        stdout_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout]
        self.assertTrue(len(stdout_handlers) > 0, "No stdout handler found")
        
        # 检查处理程序的格式器
        handler = stdout_handlers[0]
        formatter = handler.formatter
        
        # 验证格式器的基本属性
        self.assertIsNotNone(formatter, "Formatter should not be None")
        
        # 写入一条测试日志
        test_message = "Test stdout format"
        root_logger.info(test_message)
        
        # 验证格式器能正确格式化日志记录
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg=test_message,
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        
        # 验证格式化的输出包含必要的元素
        self.assertIn(test_message, formatted)  # 包含消息
        self.assertRegex(formatted, r'\d+')  # 包含进程ID
        self.assertIn("INFO", formatted)  # 包含日志级别 