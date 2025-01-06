from typing import Dict, Any, Tuple
import json_repair
import asyncio
from dotenv import load_dotenv
load_dotenv()

from ctn2md.src.md_info_base import MdInfo
from ctn2md.utils_llm.llm_gen_vllm_instruction import gen_vllm_instruction_llm
from ctn2md.utils_vllm.vllm_img_description_qwen import generate_image_description_by_qwen
from ctn2md.utils_vllm.vllm_img_description_gpt import generate_image_description_by_gpt
from ctn2md.utils_vllm.vllm_img_description_ark import generate_image_description_by_ark

g_question_num = 9000

class ImageDescriptionGenerator:
    def __init__(self, md_info: MdInfo):
        self.md_info = md_info
        self.relevance_model = md_info.get_md_control("mctl_ti_img_relevance_model", "qwen")
        self.caption_model = md_info.get_md_control("mctl_ti_img_caption_model", "qwen")

    def _get_page_instruction(self, doc_title: str, content_around: str) -> str:
        """同步获取指令"""
        global g_question_num
        if self.relevance_model == "qwen":
            model = "qwen-turbo"
        elif self.relevance_model == "gpt":
            model = "gpt-4o-mini"
        elif self.relevance_model == "ark":
            model = "ep-20241220101421-4tj5f"
        else:
            raise ValueError(f"unsupported model {self.relevance_model}")
        
        instruction = gen_vllm_instruction_llm(doc_title, content_around, model=model, question_num=g_question_num)
        g_question_num += 1
        return instruction

    async def _get_page_instruction_async(self, doc_title: str, content_around: str) -> str:
        """异步获取指令"""
        # 注意：这里假设未来 gen_vllm_instruction_* 函数会有异步版本
        # 目前暂时使用同步版本
        return self._get_page_instruction(doc_title, content_around)

    def _gen_figure_info(self, doc_title: str, content_around: str, image_path_or_url: str) -> Dict[str, Any]:
        """同步生成图片信息"""
        instruction = self._get_page_instruction(doc_title, content_around)
        
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
            
        return json_repair.repair_json(resp, return_objects=True, ensure_ascii=True)

    async def _gen_figure_info_async(self, doc_title: str, content_around: str, image_path_or_url: str) -> Dict[str, Any]:
        """异步生成图片信息"""
        instruction = await self._get_page_instruction_async(doc_title, content_around)
        
        # 注意：这里假设未来 generate_image_description_* 函数会有异步版本
        # 目前暂时使用同步版本
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
            
        return json_repair.repair_json(resp, return_objects=True, ensure_ascii=True)

    def get_alt_text_and_description(self, img_url: str, content: str) -> Tuple[str, str]:
        """同步获取图片替代文本和描述"""
        doc_title = self.md_info.get_doc_title()
        resp = self._gen_figure_info(doc_title, content, img_url)
        return resp["FigureName"], resp["PictureDescription"]

    async def get_alt_text_and_description_async(self, img_url: str, content: str) -> Tuple[str, str]:
        """异步获取图片替代文本和描述"""
        doc_title = self.md_info.get_doc_title()
        resp = await self._gen_figure_info_async(doc_title, content, img_url)
        return resp["FigureName"], resp["PictureDescription"]


# 为保持向后兼容的全局函数
def get_img_alt_text_and_description(md_info: MdInfo, img_url: str, content: str) -> Tuple[str, str]:
    """同步版本"""
    generator = ImageDescriptionGenerator(md_info)
    return generator.get_alt_text_and_description(img_url, content)

async def get_img_alt_text_and_description_async(md_info: MdInfo, img_url: str, content: str) -> Tuple[str, str]:
    """异步版本"""
    generator = ImageDescriptionGenerator(md_info)
    return await generator.get_alt_text_and_description_async(img_url, content)


if __name__ == "__main__":
    from ctn2md.utils.util_logging import setup_logger_handlers
    setup_logger_handlers()

    # 测试数据
    class TestMdInfo:
        def get_md_control(self, key, default):
            return default

        def get_doc_title(self):
            return "Test Document"

    test_md_info = TestMdInfo()
    test_img_url = "https://img.ixintu.com/download/jpg/20210201/7cacc87485bdd0b5c721c7c100f67550_512_512.jpg!ys"
    test_content = "This is a test content about 神经网络，这个是个简单网络."

    # 同步测试
    print("\n=== Testing Synchronous Generation ===")
    try:
        alt_text, description = get_img_alt_text_and_description(
            test_md_info, test_img_url, test_content
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
                test_md_info, test_img_url, test_content
            )
            print(f"Alt Text: {alt_text}")
            print(f"Description: {description}")
        except Exception as e:
            print(f"Async generation error: {e}")

    asyncio.run(test_async()) 