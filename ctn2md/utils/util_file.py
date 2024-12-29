from dotenv import load_dotenv, find_dotenv
import os
import sys


if "./" not in sys.path:
    sys.path.append("./")

load_dotenv()

def get_root_dir() -> str:
    """获取项目根目录的绝对路径
    
    通过查找 .env 文件位置来确定项目根目录
    
    Returns:
        str: 项目根目录的绝对路径
    """
    root_dir = os.path.abspath(os.path.dirname(find_dotenv()))  
    return root_dir

def get_crc32_id(unique_str: str) -> str:
    """计算字符串的CRC32校验和
    
    Args:
        unique_str (str): 需要计算校验和的字符串

    Returns:
        str: 8位十六进制的CRC32校验和
    """
    import binascii
    input_bytes = unique_str.encode('utf-8')
    crc32_checksum = binascii.crc32(input_bytes)
    return format(crc32_checksum, '08x')


if __name__ == "__main__":
    # 测试根目录获取
    root = get_root_dir()
    print(f"项目根目录: {root}")
    
    # 测试CRC32计算
    test_strings = [
        "Hello, World!",
        "测试中文",
        "",  # 空字符串
    ]
    
    for s in test_strings:
        crc32 = get_crc32_id(s)
        print(f"字符串: {s!r:20} -> CRC32: {crc32}")