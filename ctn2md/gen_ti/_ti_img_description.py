from typing import Tuple
import json_repair
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()
import os
import zlib

from ctn2md.src.md_info_base import MdInfo
from ctn2md.utils_llm.llm_gen_vllm_instruction import gen_vllm_instruction_llm
from ctn2md.utils_vllm.vllm_img_description_qwen import generate_image_description_by_qwen
from ctn2md.utils_vllm.vllm_img_description_gpt import generate_image_description_by_gpt
from ctn2md.utils_vllm.vllm_img_description_ark import generate_image_description_by_ark
from pydantic import BaseModel

g_question_num = 9000

class ImageDescription(BaseModel):
    FigureName: str | None  # 图像名称,如果无关则为None
    RelevanceScore: float   # 相关性分数(0-10)
    Explanation: str        # 相关性判断依据说明
    PictureDescription: str # 图像的详细内容描述

class ImageDescriptionGenerator:
    def __init__(self, md_info: MdInfo):
        self.md_info = md_info
        self.relevance_model = md_info.get_md_control("mctl_ti_img_relevance_model", "qwen")
        self.caption_model = md_info.get_md_control("mctl_ti_img_caption_model", "qwen")
        self.cache_dir = md_info.get_cache_dir()
        os.makedirs(self.cache_dir, exist_ok=True)

    def _calculate_instruction_cache_name(self, local_path: str, doc_title: str, content_around: str, model: str) -> str:
        """计算instruction缓存文件名"""
        basename = os.path.splitext(os.path.basename(local_path))[0]
        title_crc = format(zlib.crc32(doc_title.encode()), '08x')
        content_crc = format(zlib.crc32(content_around.encode()), '08x')
        return f"{basename}_instruct_{model}_{title_crc}_{content_crc}.txt"

    def _get_page_instruction(self, doc_title: str, content_around: str, local_path: str) -> str:
        """同步获取指令,使用缓存"""
        # 确定模型
        if self.relevance_model == "qwen":
            model = "qwen-turbo"
        elif self.relevance_model == "gpt":
            model = "gpt-4o-mini"
        elif self.relevance_model == "ark":
            model = "ep-20241220101421-4tj5f"
        else:
            raise ValueError(f"unsupported model {self.relevance_model}")

        # 检查缓存
        cache_file = self._calculate_instruction_cache_name(local_path, doc_title, content_around, self.relevance_model)
        cache_path = os.path.join(self.cache_dir, cache_file)
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read().strip()

        # 生成新instruction
        global g_question_num
        instruction = gen_vllm_instruction_llm(doc_title, content_around, model=model, question_num=g_question_num)
        g_question_num += 1

        # 如果生成成功则缓存
        if instruction:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(instruction)

        return instruction

    async def _get_page_instruction_async(self, doc_title: str, content_around: str, local_path: str) -> str:
        """异步获取指令"""
        # 注意：这里假设未来 gen_vllm_instruction_* 函数会有异步版本
        # 目前暂时使用同步版本
        return self._get_page_instruction(doc_title, content_around, local_path)

    def _calculate_description_cache_name(self, local_path: str, instruction: str, model: str) -> str:
        """计算description缓存文件名"""
        basename = os.path.splitext(os.path.basename(local_path))[0]
        inst_crc = format(zlib.crc32(instruction.encode()), '08x')
        
        # 使用local_path文件内容的CRC32 
        if os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                content_crc = format(zlib.crc32(f.read()), '08x')
        else:
            content_crc = "00000000"
            
        return f"{basename}_desc_{model}_{inst_crc}_{content_crc}.json"

    def _generate_description(self, image_path_or_url: str, instruction: str, local_path: str) -> ImageDescription:
        """共享的描述生成逻辑,使用缓存"""
        # 检查缓存
        cache_file = self._calculate_description_cache_name(local_path, instruction, self.caption_model)
        cache_path = os.path.join(self.cache_dir, cache_file)
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                return ImageDescription(**json_data)

        # 生成新描述
        if self.caption_model == "qwen":
            resp = generate_image_description_by_qwen(image_path_or_url, instruction=instruction)
        elif self.caption_model == "gpt":
            resp = generate_image_description_by_gpt(image_path_or_url, instruction=instruction)
        elif self.caption_model == "ark":
            resp = generate_image_description_by_ark(image_path_or_url, instruction=instruction)
        else:
            raise ValueError(f"unsupported model: {self.caption_model}")

        if resp is None:
            raise ValueError("response is None")
            
        json_data = json_repair.repair_json(resp, return_objects=True, ensure_ascii=True)
        description = ImageDescription(**json_data)

        # 如果生成成功则缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(description.model_dump(), f, ensure_ascii=False, indent=2)

        return description

    def _gen_figure_info(self, doc_title: str, content_around: str, image_path_or_url: str, local_path: str) -> ImageDescription:
        """同步生成图片信息"""
        instruction = self._get_page_instruction(doc_title, content_around, local_path)
        return self._generate_description(image_path_or_url, instruction, local_path)

    async def _gen_figure_info_async(self, doc_title: str, content_around: str, image_path_or_url: str, local_path: str) -> ImageDescription:
        """异步生成图片信息"""
        instruction = await self._get_page_instruction_async(doc_title, content_around, local_path)
        return self._generate_description(image_path_or_url, instruction, local_path)

    def get_alt_text_and_description(self, img_url: str, local_path: str, content: str) -> Tuple[str, str]:
        """同步获取图片替代文本和描述"""
        doc_title = self.md_info.get_doc_title()
        resp = self._gen_figure_info(doc_title, content, img_url, local_path)
        return resp.FigureName, resp.PictureDescription

    async def get_alt_text_and_description_async(self, img_url: str, local_path: str, content: str) -> Tuple[str, str]:
        """异步获取图片替代文本和描述"""
        doc_title = self.md_info.get_doc_title()
        resp = await self._gen_figure_info_async(doc_title, content, img_url, local_path)
        return resp.FigureName, resp.PictureDescription


# 为保持向后兼容的全局函数
def get_img_alt_text_and_description(md_info: MdInfo, img_url: str, local_path: str, content: str) -> Tuple[str, str]:
    """同步版本"""
    generator = ImageDescriptionGenerator(md_info)
    return generator.get_alt_text_and_description(img_url, local_path, content)

async def get_img_alt_text_and_description_async(md_info: MdInfo, img_url: str, local_path: str, content: str) -> Tuple[str, str]:
    """异步版本"""
    generator = ImageDescriptionGenerator(md_info)
    return await generator.get_alt_text_and_description_async(img_url, local_path, content)


if __name__ == "__main__":
    from mmbase.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()

    # 测试数据
    class TestMdInfo:
        def get_md_control(self, key, default):
            return default

        def get_doc_title(self):
            return "Test Document"
        
        def get_cache_dir(self):
            cache_dir = "_work/test_cache"
            os.makedirs(cache_dir, exist_ok=True)
            return cache_dir

    test_md_info = TestMdInfo()
    test_img_url = "https://img.ixintu.com/download/jpg/20210201/7cacc87485bdd0b5c721c7c100f67550_512_512.jpg!ys"
    test_content = "This is a test content about 神经网络，这个是个简单网络."
    test_local_path = "test_image.jpg"  # 测试用的本地路径

    # 同步测试
    print("\n=== Testing Synchronous Generation ===")
    try:
        alt_text, description = get_img_alt_text_and_description(
            test_md_info, test_img_url, test_local_path, test_content
        )
        print(f"Alt Text: {alt_text}")
        print(f"Description: {description}")
    except Exception as e:
        print(f"Sync generation error: {e}")

    # 异步测试
    print("\n=== Testing Asynchronous Generation ===")
    
    async def test_async():
        try:
            alt_text, description = await get_img_alt_text_and_description_async(
                test_md_info, test_img_url, test_local_path, test_content
            )
            print(f"Alt Text: {alt_text}")
            print(f"Description: {description}")
        except Exception as e:
            print(f"Async generation error: {e}")

    asyncio.run(test_async()) 