
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
