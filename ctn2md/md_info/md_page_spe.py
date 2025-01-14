import os 
import re

class SpecialPage:
    PAGE_FAILED_GEN_CONTENT_MARK = "**Failed to generate content**:"
    PAGE_MANUAL_CHANGED = "<!-- touched -->"

    @classmethod
    def does_page_have_failed_mark(cls, pname_page_md:str) -> bool:
        if not os.path.isfile(pname_page_md):
            return False

        with open(pname_page_md, "r", encoding="utf-8") as f:
            content = f.read()
        has_mark = content.find(cls.PAGE_FAILED_GEN_CONTENT_MARK) != -1
        return has_mark
    
    @classmethod
    def does_page_have_touched_mark(cls, pname_page_md:str) -> bool:
        if not os.path.isfile(pname_page_md):
            return False

        with open(pname_page_md, "r", encoding="utf-8") as f:
            content = f.read()
        has_mark = content.find(cls.PAGE_MANUAL_CHANGED) != -1
        return has_mark
    
    @classmethod
    def does_page_have_remote_image(cls, pname_page_md:str) -> bool:
        if not os.path.isfile(pname_page_md):
            return False

        with open(pname_page_md, "r", encoding="utf-8") as f:
            content = f.read()
        
        img_pattern = r'!\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)'
        matches = list(re.finditer(img_pattern, content))
        for match in matches:
            img_url = match.group(2)
            
            if img_url.startswith(('http://', 'https://')):
                return True
        return False

