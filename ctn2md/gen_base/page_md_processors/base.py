from dotenv import load_dotenv
import os
import logging

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from abc import ABC, abstractmethod
from typing import Any

class BaseProcessor(ABC):
    """处理器基类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def process(self, *args: Any, **kwargs: Any) -> Any:
        """处理方法，需要被子类实现"""
        pass 