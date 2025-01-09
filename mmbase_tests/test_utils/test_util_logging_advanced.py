import os
import time
import logging
import multiprocessing
import psutil
from unittest import TestCase
from concurrent.futures import ThreadPoolExecutor, as_completed

from mmbase.utils.util_logging import (
    LoggingConfig,
    setup_logger_handlers,
    get_logger_llm,
    get_logger_progress,
    init_global_state
)

def process_logging_worker(process_id: int, log_dir: str) -> None:
    """多进程日志记录的工作函数"""
    # 在子进程中重新初始化日志系统
    LoggingConfig._instance = None
    LoggingConfig._initialized = False
    init_global_state()
    
    # 初始化日志系统
    LoggingConfig.initialize("test_advanced", log_dir)
    setup_logger_handlers()
    
    logger = logging.getLogger(f"process_{process_id}")
    for i in range(100):
        logger.info(f"Process {process_id} - Message {i}")
        time.sleep(0.01)

class TestUtilLoggingAdvanced(TestCase):
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

    def test_concurrent_logging(self):
        """测试并发日志记录的正确性"""
        # 初始化日志系统
        LoggingConfig.initialize("test_advanced", self.log_dir)
        setup_logger_handlers()
        
        # 获取不同的日志器
        root_logger = logging.getLogger()
        llm_logger = get_logger_llm()
        progress_logger = get_logger_progress()
        
        # 创建消息列表
        num_messages = 1000
        root_messages = [f"Root message {i}" for i in range(num_messages)]
        llm_messages = [f"LLM message {i}" for i in range(num_messages)]
        progress_messages = [f"Progress message {i}" for i in range(num_messages)]
        
        # 定义日志记录函数
        def log_messages(logger, messages):
            for msg in messages:
                logger.info(msg)
                # 添加一些随机延迟以增加并发的机会
                time.sleep(0.001)
        
        # 使用线程池并发记录日志
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(log_messages, root_logger, root_messages),
                executor.submit(log_messages, llm_logger, llm_messages),
                executor.submit(log_messages, progress_logger, progress_messages)
            ]
            # 等待所有任务完成
            for future in as_completed(futures):
                future.result()
        
        # 验证日志文件的完整性
        # 1. 主日志文件
        main_log = os.path.join(self.log_dir, "test_advanced.log")
        self.assertTrue(os.path.exists(main_log))
        with open(main_log, 'r') as f:
            content = f.read()
            # 验证所有root消息都被记录
            for msg in root_messages:
                self.assertIn(msg, content)
            # 验证没有其他日志器的消息
            self.assertNotIn("LLM message", content)
            self.assertNotIn("Progress message", content)
        
        # 2. LLM日志文件
        llm_log = os.path.join(self.log_dir, "test_advanced_llm.log")
        self.assertTrue(os.path.exists(llm_log))
        with open(llm_log, 'r') as f:
            content = f.read()
            # 验证所有LLM消息都被记录
            for msg in llm_messages:
                self.assertIn(msg, content)
            # 验证没有其他日志器的消息
            self.assertNotIn("Root message", content)
            self.assertNotIn("Progress message", content)
        
        # 3. Progress日志文件
        progress_log = os.path.join(self.log_dir, "test_advanced_prg.log")
        self.assertTrue(os.path.exists(progress_log))
        with open(progress_log, 'r') as f:
            content = f.read()
            # 验证所有Progress消息都被记录
            for msg in progress_messages:
                self.assertIn(msg, content)
            # 验证没有其他日志器的消息
            self.assertNotIn("Root message", content)
            self.assertNotIn("LLM message", content)
            
        # 4. 验证日志顺序
        def verify_log_order(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # 提取时间戳
                timestamps = []
                for line in lines:
                    try:
                        timestamp_str = line.split(' - ')[0]
                        timestamp = time.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                        timestamps.append(timestamp)
                    except (ValueError, IndexError):
                        continue
                # 验证时间戳是否按顺序
                self.assertEqual(timestamps, sorted(timestamps)) 

    def test_exception_handling(self):
        """测试并发日志记录时的异常处理"""
        LoggingConfig.initialize("test_advanced", self.log_dir)
        setup_logger_handlers()
        
        error_logger = logging.getLogger("error_test")
        
        def generate_error():
            try:
                raise ValueError("Test error")
            except Exception:
                error_logger.error("Error occurred", exc_info=True)
        
        # 并发产生错误
        num_errors = 50
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_error) for _ in range(num_errors)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass
        
        # 验证错误日志
        error_log = os.path.join(self.log_dir, "test_advanced_error.log")
        self.assertTrue(os.path.exists(error_log))
        
        with open(error_log, 'r') as f:
            content = f.read()
            # 每个错误会产生两行：一行是错误消息，一行是堆栈跟踪
            # 所以我们只检查堆栈跟踪中的错误消息数量
            self.assertEqual(content.count("ValueError: Test error"), num_errors)
            self.assertEqual(content.count("Error occurred"), num_errors)

    def test_multiprocess_logging(self):
        """测试多进程日志记录"""
        # 初始化主进程的日志系统
        LoggingConfig.initialize("test_advanced", self.log_dir)
        setup_logger_handlers()
        
        num_processes = 4
        processes = []
        
        for i in range(num_processes):
            p = multiprocessing.Process(
                target=process_logging_worker,
                args=(i, self.log_dir)
            )
            processes.append(p)
            p.start()
        
        for p in processes:
            p.join()
        
        # 验证日志文件
        main_log = os.path.join(self.log_dir, "test_advanced.log")
        self.assertTrue(os.path.exists(main_log))
        
        with open(main_log, 'r') as f:
            content = f.read()
            # 验证每个进程的消息都被正确记录
            for proc_id in range(num_processes):
                for msg_id in range(100):
                    self.assertIn(f"Process {proc_id} - Message {msg_id}", content)

    def test_memory_usage(self):
        """测试大量并发日志记录时的内存使用情况"""
        LoggingConfig.initialize("test_advanced", self.log_dir)
        setup_logger_handlers()
        
        logger = logging.getLogger()
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # 生成大量日志
        num_messages = 10000
        message_size = 1024  # 1KB
        large_message = "X" * message_size
        
        def log_batch(start_idx, count):
            for i in range(start_idx, start_idx + count):
                logger.info(f"{large_message} - {i}")
        
        # 使用多线程记录日志
        batch_size = num_messages // 10
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(0, num_messages, batch_size):
                futures.append(executor.submit(log_batch, i, batch_size))
            
            for future in as_completed(futures):
                future.result()
        
        # 检查内存使用
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 验证内存增长不超过合理范围 (例如50MB)
        max_allowed_increase = 50 * 1024 * 1024  # 50MB
        self.assertLess(memory_increase, max_allowed_increase, 
                       f"Memory increase ({memory_increase / 1024 / 1024:.2f}MB) exceeds limit") 