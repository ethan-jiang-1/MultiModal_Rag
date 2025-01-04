import os
import sys
from typing import List, Tuple
import logging
import re
import asyncio

if './' not in sys.path:
    sys.path.append("./")

from ctn2md.src.md_info_base import MIFN, MdInfo
from ctn2md.utils_gen.gen_base import get_job_id
from ctn2md.gen_ti._ti_img_description import (
    get_img_alt_text_and_description,
    get_img_alt_text_and_description_async
)
from ctn2md.gen_ti._ti_get_image import (
    download_remote_image_ti,
    download_remote_image_ti_async
)


class ImageReferenceUpdater:
    def __init__(self, md_info: MdInfo, page_index: int, pname_page_md: str):
        self.md_info = md_info
        self.page_index = page_index
        self.pname_page_md = pname_page_md
        self.job_id = md_info[MIFN.TI_CUR_JOB_ID] or get_job_id(md_info.get_unique_job_id())
        self.output_dir = md_info.get_out_dir()
        
    def _read_content(self) -> str:
        """读取markdown内容"""
        with open(self.pname_page_md, 'r', encoding='utf-8') as f:
            return f.read()

    def _save_content(self, content: str):
        """保存markdown内容"""
        with open(self.pname_page_md, 'w', encoding='utf-8') as f:
            f.write(content)

    async def _process_image_async(
        self, 
        img_url: str, 
        img_ndx: int,
        content: str
    ) -> Tuple[str, str, str]:
        """异步处理单个图片"""
        # 生成本地文件名
        img_ext = os.path.splitext(img_url)[1] or '.png'
        local_fname = f"{self.job_id}_p{self.page_index}_{img_ndx}{img_ext}"
        local_path = os.path.join(self.output_dir, local_fname)

        # 并行执行下载和描述生成
        download_task = download_remote_image_ti_async(img_url, local_path)
        desc_task = get_img_alt_text_and_description_async(self.md_info, img_url, content)
        
        # 等待两个任务完成
        _, (alt_text, description) = await asyncio.gather(download_task, desc_task)

        return local_fname, alt_text, description

    def _process_image_sync(
        self, 
        img_url: str, 
        img_ndx: int,
        content: str
    ) -> Tuple[str, str, str]:
        """同步处理单个图片"""
        # 生成本地文件名
        img_ext = os.path.splitext(img_url)[1] or '.png'
        local_fname = f"{self.job_id}_p{self.page_index}_{img_ndx}{img_ext}"
        local_path = os.path.join(self.output_dir, local_fname)

        # 顺序执行下载和描述生成
        download_remote_image_ti(img_url, local_path)
        alt_text, description = get_img_alt_text_and_description(self.md_info, img_url, content)

        return local_fname, alt_text, description

    async def _update_refs_async(self, process_image_func) -> List[str]:
        """异步版本的更新逻辑"""
        content = self._read_content()
        img_pattern = r'!\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)'
        matches = list(re.finditer(img_pattern, content))
        
        local_ref_image_paths = []
        new_content = content
        
        img_ndx = 0
        for match in matches:
            img_url = match.group(2)
            
            # 跳过本地图片
            if not img_url.startswith(('http://', 'https://')):
                if os.path.exists(os.path.join(self.output_dir, img_url)):
                    local_ref_image_paths.append(img_url)
                continue
                
            img_ndx += 1
            try:
                local_fname, alt_text, description = await process_image_func(
                    img_url, img_ndx, content
                )
                
                # 更新markdown引用
                old_img_md = match.group(0)
                new_img_md = f'![{alt_text}]({local_fname}{" \""+description+"\"" if description else ""})'
                new_content = new_content.replace(old_img_md, new_img_md)
                
                local_ref_image_paths.append(local_fname)
                logging.info(f"Processed image: {img_url} -> {local_fname}")
                
            except Exception as e:
                logging.error(f"Failed to process image {img_url}: {str(e)}")
                logging.exception(e)
                continue
        
        if new_content != content:
            self._save_content(new_content)
            logging.info(f"Updated markdown file: {self.pname_page_md}")
        
        return local_ref_image_paths

    def _update_refs_sync(self, process_image_func) -> List[str]:
        """同步版本的更新逻辑"""
        content = self._read_content()
        img_pattern = r'!\[(.*?)\]\((.*?)(?:\s+"(.*?)")?\)'
        matches = list(re.finditer(img_pattern, content))
        
        local_ref_image_paths = []
        new_content = content
        
        img_ndx = 0
        for match in matches:
            img_url = match.group(2)
            
            # 跳过本地图片
            if not img_url.startswith(('http://', 'https://')):
                if os.path.exists(os.path.join(self.output_dir, img_url)):
                    local_ref_image_paths.append(img_url)
                continue
                
            img_ndx += 1
            try:
                local_fname, alt_text, description = process_image_func(
                    img_url, img_ndx, content
                )
                
                # 更新markdown引用
                old_img_md = match.group(0)
                new_img_md = f'![{alt_text}]({local_fname}{" \""+description+"\"" if description else ""})'
                new_content = new_content.replace(old_img_md, new_img_md)
                
                local_ref_image_paths.append(local_fname)
                logging.info(f"Processed image: {img_url} -> {local_fname}")
                
            except Exception as e:
                logging.error(f"Failed to process image {img_url}: {str(e)}")
                logging.exception(e)
                continue
        
        if new_content != content:
            self._save_content(new_content)
            logging.info(f"Updated markdown file: {self.pname_page_md}")
        
        return local_ref_image_paths

    def update_refs_sync(self) -> List[str]:
        """同步更新图片引用"""
        return self._update_refs_sync(self._process_image_sync)

    async def update_refs_async(self) -> List[str]:
        """异步更新图片引用"""
        return await self._update_refs_async(self._process_image_async)


# 保持原有接口的兼容性
def update_page_md_with_ref_imgs(md_info: MdInfo, page_index: int, pname_page_md: str) -> List[str]:
    """同步版本"""
    updater = ImageReferenceUpdater(md_info, page_index, pname_page_md)
    return updater.update_refs_sync()

async def update_page_md_with_ref_imgs_async(md_info: MdInfo, page_index: int, pname_page_md: str) -> List[str]:
    """异步版本"""
    updater = ImageReferenceUpdater(md_info, page_index, pname_page_md)
    return await updater.update_refs_async()


if __name__ == "__main__":
    from ctn2md.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()

    # 测试数据
    class TestMdInfo:
        def __getitem__(self, key):
            return None
        
        def get_unique_job_id(self):
            return "test_job"
        
        def get_out_dir(self):
            return "_work/test_output"
        
        def get_md_control(self, key, default):
            return default
        
        def get_doc_title(self):
            return "Test Document"

    # 创建测试markdown文件
    test_md = """# Test Document
![test](https://img.ixintu.com/download/jpg/20210201/7cacc87485bdd0b5c721c7c100f67550_512_512.jpg!ys "这是一个测试图片") 这里是其他文字
"""
    os.makedirs("_work/test_output", exist_ok=True)
    test_md_path = "_work/test_output/test_sync.md"
    with open(test_md_path, "w", encoding="utf-8") as f:
        f.write(test_md)

    # 同步测试
    print("\n=== Testing Synchronous Update ===")
    try:
        result = update_page_md_with_ref_imgs(TestMdInfo(), 1, test_md_path)
        print(f"Processed files: {result}")
    except Exception as e:
        print(f"Sync update error: {e}")

    # 异步测试
    print("\n=== Testing Asynchronous Update ===")
    test_md_path = "_work/test_output/test_async.md"
    with open(test_md_path, "w", encoding="utf-8") as f:
        f.write(test_md)

    async def test_async():
        try:
            result = await update_page_md_with_ref_imgs_async(TestMdInfo(), 1, test_md_path)
            print(f"Processed files: {result}")
        except Exception as e:
            print(f"Async update error: {e}")

    asyncio.run(test_async())