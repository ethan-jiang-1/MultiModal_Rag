from dotenv import load_dotenv
import os
from typing import List, Dict

load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from ctn2md.gen_base.page_md_processors.base import BaseProcessor

class ActionExecutor(BaseProcessor):
    """动作执行器：负责执行各种页面处理动作"""
    
    def process(self, page_content: List[str], actions: List[Dict]) -> List[str]:
        """执行页面动作
        
        Args:
            page_content: 页面内容行列表
            actions: 需要执行的动作列表
        
        Returns:
            处理后的页面内容行列表
        """
        if not actions:
            return page_content
            
        content = page_content.copy()
        
        for action in actions:
            action_type = action.get('type')
            if action_type == 'remove':
                content = self._execute_remove(content, action)
            elif action_type == 'modify':
                content = self._execute_modify(content, action)
            elif action_type == 'merge':
                content = self._execute_merge(content, action)
            else:
                self.logger.warning(f"Unknown action type: {action_type}")
                
        return content
    
    def _execute_remove(self, content: List[str], action: Dict) -> List[str]:
        """执行移除动作"""
        position = action.get('position', {})
        lines = position.get('lines', [])
        
        if not lines:
            return content
            
        # 创建新的内容列表，排除需要移除的行
        new_content = []
        for idx, line in enumerate(content):
            if idx not in lines:
                new_content.append(line)
                
        self.logger.info(f"Removed {len(lines)} lines")
        return new_content
    
    def _execute_modify(self, content: List[str], action: Dict) -> List[str]:
        """执行修改动作"""
        position = action.get('position', {})
        params = action.get('params', {})
        
        line_number = position.get('line')
        new_content = params.get('content')
        
        if line_number is None or new_content is None:
            return content
            
        # 修改指定行的内容
        if 0 <= line_number < len(content):
            content[line_number] = new_content
            self.logger.info(f"Modified line {line_number}")
            
        return content
    
    def _execute_merge(self, content: List[str], action: Dict) -> List[str]:
        """执行合并动作"""
        position = action.get('position', {})
        params = action.get('params', {})
        
        start_line = position.get('start')
        end_line = position.get('end')
        merged_content = params.get('content')
        
        if None in (start_line, end_line, merged_content):
            return content
            
        # 替换指定范围的内容
        if 0 <= start_line <= end_line < len(content):
            new_content = (
                content[:start_line] +
                [merged_content] +
                content[end_line + 1:]
            )
            self.logger.info(f"Merged lines {start_line}-{end_line}")
            return new_content
            
        return content 