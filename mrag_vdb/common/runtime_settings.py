
class ModelGptSel:
    _g_gpt_model = "gpt-4o-mini"
    SUPPORTED_MODELS = ["gpt-4o", "gpt-4o-mini", "qwen-max", "qwen-plus-1127", "qwen-turbo-1101"]

    @classmethod
    def get_gpt_model(cls):
        return cls._g_gpt_model

    @classmethod
    def set_gpt_model(cls, model_name):
        if cls.is_supported_gpt_model(model_name):
            cls._g_gpt_model = model_name
        return cls._g_gpt_model

    @classmethod
    def is_supported_gpt_model(cls, model_name):
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
    def set_kbname(cls, kbname):
        if cls.is_supported_kbname(kbname):
            cls._g_kb_name = kbname
        return cls._g_kb_name
    
    @classmethod
    def is_supported_kbname(cls, kbname):
        if kbname in cls.SUPPORTED_KBNAMES:
            return True 
        return False
