from typing import Dict
import os
from llama_parse.utils import Language

_MIB_INFO_VER = "0.11.2"

# 环境变量配置
ENV_MODEL_FLOW = "ENV_MODEL_FLOW"              # models used for flow mode: gpt/qwen/ark
ENV_MODEL_GEN_LP = "ENV_MODEL_GEN_LP"         # models used for lp mode: gpt/qwen/ark
ENV_MODEL_GEN_LVLM = "ENV_MODEL_GEN_LVLM"     # models used for lvlm mode: gpt/qwen/ark
ENV_MODEL_GEN_LVLM_REGION = "ENV_MODEL_GEN_LVLM_REGION"  # models used for lvlm mode: gs0/gs1/gs2
ENV_MODEL_GEN_TI = "ENV_MODEL_GEN_TI"         # models used for textin mode: gpt/qwen/ark

class DefaultModelSource:
    @classmethod
    def get_flow_fix_heading_model(cls) -> str:
        return os.getenv(ENV_MODEL_FLOW, "qwen")
    
    @classmethod
    def get_flow_summarize_model(cls) -> str:
        return os.getenv(ENV_MODEL_FLOW, "qwen")
    
    @classmethod
    def get_gen_ti_img_relevance_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_TI, "qwen")
    
    @classmethod
    def get_gen_ti_img_caption_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_TI, "qwen")
    
    @classmethod
    def get_gen_lvlm_img2md_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LVLM, "qwen")
    
    @classmethod
    def get_gen_lvlm_img_relevance_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LVLM, "qwen")
    
    @classmethod
    def get_gen_lvlm_region_detect(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LVLM_REGION, "gs2")
    
    @classmethod
    def get_gen_lp_img_relevance_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LP, "qwen")
    
    @classmethod
    def get_gen_lp_img_caption_model(cls) -> str:
        return os.getenv(ENV_MODEL_GEN_LP, "qwen")

def get_default_md_control() -> Dict:
    # 通用配置
    general_controls = {
        "version": _MIB_INFO_VER,
        "mctl_move_aux_files": True,                    # 是否移动辅助文件
        "mctl_treat_doc_as_ctntype": "auto",           # 文档类型处理方式
        "mctl_ge_md_async": False,                     # 异步生成开关
        
        # 模型选择
        "mctl_fix_heading_model": DefaultModelSource.get_flow_fix_heading_model(),     # 标题修复模型: gpt/qwen/ark
        "mctl_summarize_model": DefaultModelSource.get_flow_summarize_model(),         # 摘要生成模型: gpt/qwen/ark
    }

    # LlamaParse专用配置
    llamaparse_controls = {
        # 图像处理
        "mctl_lp_min_img_relevance_score": 0.2,        # 图片相关性最小分数
        "mctl_lp_img_relevance_model": DefaultModelSource.get_gen_lp_img_relevance_model(),  # 图片相关性判断: qwen/gpt/ark
        "mctl_lp_img_caption_model": DefaultModelSource.get_gen_lp_img_caption_model(),      # 图片说明生成: qwen/gpt/ark
        "mctl_lp_need_image_ref": True,                # 是否需要图片引用
        "mctl_lp_img_to_heading": {},                  # 图片到标题的映射: {embed_img_name: PlcId:plc_id}
        
        # 文档处理
        "mctl_lp_langauge": Language.SIMPLIFIED_CHINESE,# 文档语言
        "mctl_lp_take_screenshot": False,              # 是否截图
        "mctl_lp_disable_ocr": False,                  # 是否禁用OCR
        "mctl_lp_premium_pages": [],                   # 高级模式下要提取的页面列表(页码从1开始)
    }

    # LVLM(Large Vision Language Model)专用配置
    lvlm_controls = {
        # 图像处理
        "mctl_lvlm_images_ignore": "",                 # 需要忽略的图片列表(逗号分隔)
        "mctl_lvlm_img2md_model": DefaultModelSource.get_gen_lvlm_img2md_model(),     # 图片转MD模型: gpt/qwen/ark
        "mctl_lvlm_region_detect": DefaultModelSource.get_gen_lvlm_region_detect(),   # 区域检测模型: gs0/gs1/gs2
        
        # 布局参数
        "mctl_lvlm_paint_page_content_area_ratios": (0.15, 0.15, 0.1, 0.1),  # 页面内容区域比例
        "mctl_lvlm_paint_max_area_ratio": 0.7,         # 最大区域比例
        "mctl_lvlm_paint_max_outside_ratio": 0.1,      # 最大外部比例
        "mctl_lvlm_paint_min_coverage_ratio": 0.7,     # 最小覆盖比例
        "mctl_lvlm_paint_content_area_buffer_ratio": 0.05,  # 内容区域缓冲比例
        
        # 距离参数
        "mctl_lvlm_paint_text_distance_ratio": (0.015, 0.015, 0.015, 0.028),  # 文本距离比例
        "mctl_lvlm_table_line_distance_ratio": 0.03,   # 表格线距离比例
        "mctl_lvlm_table_short_line_ratio": 0.03,      # 表格短线比例
        "mctl_lvlm_table_text_distance_ratio": (0.02, 0.02, 0.02, 0.02),  # 表格文本距离比例
    }

    # TextIn专用配置
    textin_controls = {
        "mctl_ti_img_relevance_model": DefaultModelSource.get_gen_ti_img_relevance_model(),  # 图片相关性判断: qwen/gpt/ark
        "mctl_ti_img_caption_model": DefaultModelSource.get_gen_ti_img_caption_model(),      # 图片说明生成: qwen/gpt/ark
    }

    # 合并所有配置
    return {
        **general_controls,
        **llamaparse_controls,
        **lvlm_controls,
        **textin_controls
    } 