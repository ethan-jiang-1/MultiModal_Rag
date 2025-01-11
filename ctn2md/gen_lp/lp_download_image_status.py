from typing import Dict, Optional # , List
import os
import json
#import time
import logging
from datetime import datetime

class ImageStatusTracker:
    """图片状态跟踪器，用于管理图片的下载和重用状态"""
    
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        self.status_file = os.path.join(cache_dir, "image_status.json")
        self._status = self._load_status()
        # 当前批次的统计
        self._current_batch = {
            "processed": set(),  # 处理过的图片路径
            "success": set(),    # 成功的图片路径
            "failed": set()      # 失败的图片路径
        }
        
    def _load_status(self) -> dict:
        """加载状态文件"""
        if not os.path.exists(self.status_file):
            return {"image_map": {}, "failed_attempts": {}}
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load status file: {e}")
            return {"image_map": {}, "failed_attempts": {}}
            
    def _save_status(self) -> None:
        """保存状态到文件"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self._status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to save status file: {e}")
            
    def _verify_image(self, path: str) -> bool:
        """验证图片文件的完整性"""
        try:
            return os.path.exists(path) and os.path.getsize(path) > 0
        except Exception as e:
            logging.error(f"Failed to verify image {path}: {e}")
            return False
            
    def find_existing_image(self, new_path: str) -> Optional[str]:
        """查找可重用的现有图片"""
        self._current_batch["processed"].add(new_path)
        
        base_name = os.path.basename(new_path)
        image_info = self._status["image_map"].get(base_name)
        
        if not image_info:
            return None
            
        # 首先尝试最后一次成功的路径
        last_success = image_info.get("last_success")
        if last_success and self._verify_image(last_success):
            return last_success
            
        # 如果最后成功的路径无效，尝试其他路径
        for path in image_info.get("paths", []):
            if path != last_success and self._verify_image(path):
                return path
                
        return None
        
    def record_success(self, path: str) -> None:
        """记录成功下载的图片"""
        self._current_batch["processed"].add(path)
        self._current_batch["success"].add(path)
        if path in self._current_batch["failed"]:
            self._current_batch["failed"].remove(path)
        
        base_name = os.path.basename(path)
        
        # 更新图片映射
        if base_name not in self._status["image_map"]:
            self._status["image_map"][base_name] = {"paths": [], "last_success": None}
            
        image_info = self._status["image_map"][base_name]
        if path not in image_info["paths"]:
            image_info["paths"].append(path)
        image_info["last_success"] = path
        
        # 清除失败记录（如果存在）
        if path in self._status["failed_attempts"]:
            del self._status["failed_attempts"][path]
            
        self._save_status()
        
    def record_failure(self, path: str, max_attempts: int = 3) -> bool:
        """
        记录下载失败的图片
        返回是否还可以继续尝试
        """
        self._current_batch["processed"].add(path)
        self._current_batch["failed"].add(path)
        if path in self._current_batch["success"]:
            self._current_batch["success"].remove(path)
            
        now = datetime.now().isoformat()
        
        if path not in self._status["failed_attempts"]:
            self._status["failed_attempts"][path] = {"count": 0, "last_attempt": now}
            
        failed = self._status["failed_attempts"][path]
        failed["count"] += 1
        failed["last_attempt"] = now
        
        self._save_status()
        return failed["count"] < max_attempts
        
    def get_stats(self) -> Dict[str, int]:
        """获取当前批次的统计信息"""
        return {
            "total": len(self._current_batch["processed"]),
            "success": len(self._current_batch["success"]),
            "failed": len(self._current_batch["failed"])
        }
        
    def print_status(self) -> None:
        """打印当前状态"""
        stats = self.get_stats()
        print(f"\n图片状态统计:")
        print(f"- 总数: {stats['total']}")
        print(f"- 成功: {stats['success']}")
        print(f"- 失败: {stats['failed']}")
        
        if self._current_batch["failed"]:
            print("\n失败记录:")
            for path in self._current_batch["failed"]:
                info = self._status["failed_attempts"][path]
                print(f"- {path}: {info['count']} 次尝试，最后尝试时间: {info['last_attempt']}") 