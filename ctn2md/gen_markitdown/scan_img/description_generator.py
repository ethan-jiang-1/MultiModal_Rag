import re
import os
import zlib
import cv2
import numpy as np
import json
import json_repair
from typing import Optional, Tuple
from pydantic import BaseModel

from ctn2md.utils_llm.llm_gen_vllm_instruction import gen_vllm_instruction_llm
from ctn2md.utils_vllm.vllm_img_description_qwen import generate_image_description_by_qwen
from ctn2md.utils_vllm.vllm_img_description_gpt import generate_image_description_by_gpt
from ctn2md.utils_vllm.vllm_img_description_ark import generate_image_description_by_ark

g_question_num = 9000

class ImageDescription(BaseModel):
    FigureName: str | None  # 图像名称,如果无关则为None
    RelevanceScore: float   # 相关性分数(0-10)
    Explanation: str        # 相关性判断依据说明
    PictureDescription: str # 图像的详细内容描述

class ImageDescriptionGenerator:
    """生成图片的figure_name和description"""
    
    def __init__(self, 
                 cache_dir: str = "_work/cache", 
                 relevance_model: str = "qwen", 
                 caption_model: str = "qwen"):
        """初始化生成器
        
        Args:
            doc_title: 文档标题
            cache_dir: 缓存目录
            relevance_model: 相关性判断模型 ("qwen", "gpt", "ark")
            caption_model: 图片描述生成模型 ("qwen", "gpt", "ark")
        """
        self.cache_dir = cache_dir
        self.relevance_model = relevance_model
        self.caption_model = caption_model
        os.makedirs(cache_dir, exist_ok=True)

    def get_image_features(self, image_path: str) -> str:
        """获取图像特征,用于缓存判断"""
        img = cv2.imread(image_path)
        if img is None:
            return "invalid"
            
        # 1. 尺寸特征 (更大容差)
        height, width = img.shape[:2]
        height_round = round(height/20.0) * 20
        width_round = round(width/20.0) * 20
        
        # 2. 感知哈希 (pHash)
        resized = cv2.resize(img, (32, 32))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        dct = cv2.dct(np.float32(gray))
        dct_low = dct[:8, :8]
        avg = dct_low.mean()
        binary_hash = ['1' if freq > avg else '0' for freq in dct_low.flatten()]
        hex_hash = ''
        for i in range(0, len(binary_hash), 4):
            value = int(''.join(binary_hash[i:i+4]), 2)
            hex_hash += format(value, 'x')
        
        return f"{width_round}x{height_round}_{hex_hash}"

    def _calculate_instruction_cache_name(self, local_path: str, doc_title: str, content_around: str, model: str) -> str:
        """计算instruction缓存文件名"""
        basename = os.path.splitext(os.path.basename(local_path))[0]
        title_crc = format(zlib.crc32(doc_title.encode()), '08x')
        content_crc = format(zlib.crc32(content_around.encode()), '08x')
        return f"{basename}_instruct_{model}_{title_crc}_{content_crc}.txt"
    
    def _get_image_instruction(self, doc_title: str, image_path: str, content_around: str) -> str:
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
        cache_file = self._calculate_instruction_cache_name(image_path, doc_title, content_around, self.relevance_model)
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

    def _calculate_description_cache_name(self, local_path: str, content_around: str, model: str) -> str:
        """计算缓存文件名"""
        basename = os.path.splitext(os.path.basename(local_path))[0]
        content_crc = format(zlib.crc32(content_around.encode()), '08x')
        
        # 使用图像特征
        if os.path.exists(local_path):
            img_features = self.get_image_features(local_path)
        else:
            img_features = "invalid"
            
        return f"{basename}_desc_{model}_{content_crc}_{img_features}.json"

    def generate_description(self, doc_title: str, context_before: str, context_after: str, 
                           image_path: str, ref_name: str, index: int) -> Tuple[str, str]:
        """根据上下文和图片生成figure_name和description
        
        Args:
            context_before: 图片前的上下文
            context_after: 图片后的上下文
            image_path: 图片路径
            ref_name: 图片文件名
            index: 图片序号
            
        Returns:
            Tuple[str, str]: (figure_name, description)
        """
        # 合并上下文
        content_around = f"{context_before} {context_after}"
        
        # 检查缓存
        cache_file = self._calculate_description_cache_name(image_path, content_around, self.caption_model)
        cache_path = os.path.join(self.cache_dir, cache_file)
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                desc = ImageDescription(**json_data)
                return desc.FigureName or f"图{index}", desc.PictureDescription

        # 生成instruction
        instruction = self._get_image_instruction(doc_title, image_path, content_around)

        # 生成描述
        if self.caption_model == "qwen":
            resp = generate_image_description_by_qwen(image_path, instruction=instruction)
        elif self.caption_model == "gpt":
            resp = generate_image_description_by_gpt(image_path, instruction=instruction)
        elif self.caption_model == "ark":
            resp = generate_image_description_by_ark(image_path, instruction=instruction)
        else:
            raise ValueError(f"unsupported model: {self.caption_model}")

        if resp is None:
            # 如果生成失败，回退到简单规则
            return self._generate_simple_description(context_before, context_after, ref_name, index)
            
        # 解析响应
        json_data = json_repair.repair_json(resp, return_objects=True, ensure_ascii=True)
        description = ImageDescription(**json_data)

        # 缓存结果
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(description.model_dump(), f, ensure_ascii=False, indent=2)

        return description.FigureName or f"图{index}", description.PictureDescription

    def _generate_simple_description(self, context_before: str, context_after: str, 
                                   ref_name: str, index: int) -> Tuple[str, str]:
        """使用简单规则生成描述（作为后备方案）"""
        # 尝试从上下文中提取标题
        title = self._extract_title_from_context(context_before, context_after)
        
        if not title:
            title = f"图{index}"
            
        return title, f"图{index} {title}"
        
    def _extract_title_from_context(self, context_before: str, context_after: str) -> Optional[str]:
        """从上下文中提取标题"""
        # 尝试从前文中提取
        title = self._extract_from_text(context_before)
        if title:
            return title
            
        # 尝试从后文中提取
        title = self._extract_from_text(context_after)
        return title
        
    def _extract_from_text(self, text: str) -> Optional[str]:
        """从文本中提取标题"""
        sentences = re.split('[。；]', text)
        
        for sent in sentences:
            if len(sent) > 50:
                continue
                
            if "图" in sent and not re.search(r'[^\w\s\u4e00-\u9fff]', sent):
                title = sent.strip()
                if title:
                    return title
                    
        return None 

if __name__ == "__main__":
    # 测试图片路径和上下文
    test_image = "_work/fitz_lvlm/145ca70f-img_4_2.png"  # 替换为实际的测试图片路径
    ref_name = "145ca70f-img_4_2.png"

    test_context_before = """
    下面这张图展示了Transformer中的Scaled Dot-Product Attention机制的详细结构。
    """
    test_context_after = """
    如图所示，该注意力机制包含Query(Q)、Key(K)和Value(V)三个线性变换，通过点积和缩放操作计算注意力权重。
    """
    
    # 创建测试用的缓存目录
    test_cache_dir = "_work/test_cache1"
    os.makedirs(test_cache_dir, exist_ok=True)
    
    print("=== Testing image description generation ===")
    try:
        generator = ImageDescriptionGenerator(
            cache_dir=test_cache_dir
        )
        
        figure_name, description = generator.generate_description(
            doc_title="神经网络结构说明文档",
            context_before=test_context_before,
            context_after=test_context_after,
            image_path=test_image,
            ref_name=ref_name,
            index=1
        )
        
        print(f"Figure Name: {figure_name}")
        print(f"Description: {description}")
        
    except Exception as e:
        print(f"Error: {str(e)}") 