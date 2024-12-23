
class ModelGptSel:
    _g_gpt_model = "gpt-4o-mini"
    SUPPORTED_MODELS = ["gpt-4o", "gpt-4o-mini", "qwen-max", "qwen-plus-1127", "qwen-turbo-1101"]

    @classmethod
    def get_gpt_model(cls) -> str:
        return cls._g_gpt_model

    @classmethod
    def set_gpt_model(cls, model_name: str) -> str:
        if cls.is_supported_gpt_model(model_name):
            cls._g_gpt_model = model_name
        return cls._g_gpt_model

    @classmethod
    def is_supported_gpt_model(cls, model_name: str) -> bool:
        if model_name in cls.SUPPORTED_MODELS:
            return True 
        return False
    
class KbNameSel:
    _g_kb_name = "mrag"
    SUPPORTED_KBNAMES = ["mrag", "papers"]

    @classmethod
    def get_kbname(cls):
        return cls._g_kb_name 
    
    @classmethod
    def set_kbname(cls, kbname: str):
        if cls.is_supported_kbname(kbname):
            cls._g_kb_name = kbname
        return cls._g_kb_name
    
    @classmethod
    def is_supported_kbname(cls, kbname:str) -> bool:
        if kbname in cls.SUPPORTED_KBNAMES:
            return True 
        return False

class RetrivalNum:
    _g_retival_num = 20 
    SUPPORTED_NUMS = [10, 20, 40, 60]

    @classmethod
    def get_retrival_num(cls) -> int:
        return cls._g_retival_num
    
    @classmethod
    def set_retrival_num(cls, retrival_num:int) -> int:
        cls._g_retival_num = retrival_num
        return cls._g_retival_num