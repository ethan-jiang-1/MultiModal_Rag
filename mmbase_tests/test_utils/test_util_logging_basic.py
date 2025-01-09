import os
import logging
from unittest import TestCase

from mmbase.utils.util_logging import (
    LoggingConfig,
    setup_logger_handlers,
    reset_log_files,
    init_global_state
)

class TestUtilLoggingBasic(TestCase):
    def setUp(self):
        # 保存原始环境变量
        self.old_env = os.environ.copy()
        
        # 设置测试环境
        self.test_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.log_dir = os.path.join(self.test_dir, "logs")
        
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

    def test_singleton_pattern(self):
        """测试LoggingConfig是否正确实现了单例模式"""
        # 初始化配置
        LoggingConfig.initialize("test_basic", self.log_dir)
        
        # 获取两个实例
        config1 = LoggingConfig.get_instance()
        config2 = LoggingConfig.get_instance()
        
        # 验证是同一个实例
        self.assertIs(config1, config2)
        
        # 验证配置值
        self.assertEqual(config1.app_prefix, "test_basic")

    def test_log_directory_creation(self):
        """测试日志目录的创建功能"""
        # 删除已存在的日志目录
        if os.path.exists(self.log_dir):
            import shutil
            shutil.rmtree(self.log_dir)
            
        # 初始化日志系统
        LoggingConfig.initialize("test_basic", self.log_dir)
        setup_logger_handlers()
        
        # 验证目录被创建
        self.assertTrue(os.path.exists(self.log_dir))
        self.assertTrue(os.path.isdir(self.log_dir))

    def test_basic_logging_levels(self):
        """测试基本的日志级别功能"""
        # 初始化日志系统
        LoggingConfig.initialize("test_basic", self.log_dir)
        setup_logger_handlers()
        
        # 写入不同级别的日志
        logging.debug("Debug message")
        logging.info("Info message")
        logging.warning("Warning message")
        logging.error("Error message")
        
        # 检查主日志文件
        main_log = os.path.join(self.log_dir, "test_basic.log")
        self.assertTrue(os.path.exists(main_log))
        
        with open(main_log, 'r') as f:
            content = f.read()
            # Debug级别默认不应该出现
            self.assertNotIn("Debug message", content)
            # Info及以上级别应该出现
            self.assertIn("Info message", content)
            self.assertIn("Warning message", content)
            self.assertIn("Error message", content)
        
        # 检查错误日志文件
        error_log = os.path.join(self.log_dir, "test_basic_error.log")
        self.assertTrue(os.path.exists(error_log))
        
        with open(error_log, 'r') as f:
            content = f.read()
            # 只有Error级别应该出现
            self.assertNotIn("Debug message", content)
            self.assertNotIn("Info message", content)
            self.assertNotIn("Warning message", content)
            self.assertIn("Error message", content)

    def test_basic_file_creation(self):
        """测试基本的日志文件创建功能"""
        # 初始化日志系统
        LoggingConfig.initialize("test_basic", self.log_dir)
        setup_logger_handlers()
        
        # 写入一条日志
        test_message = "Test log message"
        logging.info(test_message)
        
        # 验证文件创建和内容
        main_log = os.path.join(self.log_dir, "test_basic.log")
        self.assertTrue(os.path.exists(main_log))
        
        with open(main_log, 'r') as f:
            content = f.read()
            self.assertIn(test_message, content)
            # 验证日志格式
            self.assertRegex(content, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}.*INFO.*Test log message')

    def test_reset_log_files(self):
        """测试日志文件的重置功能"""
        # 初始化日志系统
        LoggingConfig.initialize("test_basic", self.log_dir)
        setup_logger_handlers()

        # 写入一些日志
        logging.info("Test message before reset")
        
        # 重置日志文件
        reset_log_files()

        # 检查.bak文件是否存在
        main_log_bak = os.path.join(self.log_dir, "test_basic.log.bak")
        self.assertTrue(os.path.exists(main_log_bak)) 