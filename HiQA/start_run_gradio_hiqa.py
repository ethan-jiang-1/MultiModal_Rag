#!/usr/bin/env python3

import subprocess
import re
import threading
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_file import get_root_dir

# 初始化共享 URL 变量
share_url = None

# 定义捕获函数
def stream_output(stream, tag):
    global share_url
    for line in iter(stream.readline, ""):
        if tag == "stdout":
            print(line.strip())
            # 检查共享 URL
            url_match = re.search(r"(https:\/\/[a-zA-Z0-9\-]+\.gradio\.live)", line)
            if url_match and not share_url:
                share_url = url_match.group(1)

                # 获取当前日期和时间
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 生成捕获的消息并附带时间戳
                capture_message = f"\n{'='*40}\nTimestamp: {timestamp}\nCaptured URL: {share_url}\n{'='*40}\n"
                print(capture_message)
                
                # 追加写入到 share_url.txt 文件
                with open("share_url.txt", "a") as f:
                    f.write(capture_message)
                    
        elif tag == "stderr":
            print(f"Error Output: {line.strip()}")


def main():
    root_dir = get_root_dir()
    print(f"change working dir to {root_dir}")
    print("captured url saved in share_url.txt")
    os.chdir(root_dir)

    # 启动 Gradio 应用的子进程
    process = subprocess.Popen(
        ["python", "-u", "HiQA/app_gradio.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 创建线程分别捕获 stdout 和 stderr
    stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, "stdout"))
    stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, "stderr"))

    # 启动线程
    stdout_thread.start()
    stderr_thread.start()

    # 等待子进程结束
    process.wait()

    # 确保所有线程结束
    stdout_thread.join()
    stderr_thread.join()

if __name__ == "__main__":
    main()
