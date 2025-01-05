from typing import List

class RagModelGptSel:
    """
    GPT model selection settings.
    Manages the selection and validation of GPT models.
    """
    _g_gpt_model: str = "gpt-4o-mini"

    SUPPORTED_MODELS: List[str] = [
        "gpt-4o", 
        "gpt-4o-mini", 
        "qwen-max", 
        "qwen-plus-1127", 
        "qwen-turbo-1101", 
        "ep-20241220101421-4tj5f",  # Doubao-pro-256K
        "ep-20241220101727-tcdfv"   # Doubao-pro-32K
    ]

    @classmethod
    def get_gpt_model(cls) -> str:
        """Get current GPT model name."""
        return cls._g_gpt_model

    @classmethod
    def set_gpt_model(cls, model_name: str) -> str:
        """Set GPT model if supported."""
        if cls.is_supported_gpt_model(model_name):
            cls._g_gpt_model = model_name
        return cls._g_gpt_model

    @classmethod
    def is_supported_gpt_model(cls, model_name: str) -> bool:
        """Check if model is supported."""
        return model_name in cls.SUPPORTED_MODELS


class RagKbNameSel:
    """
    Knowledge base selection settings.
    Manages the selection and validation of knowledge base names.
    """
    _g_kb_name: str = "mrag"
    SUPPORTED_KBNAMES: List[str] = ["mrag", "papers"]

    @classmethod
    def get_kbname(cls) -> str:
        """Get current knowledge base name."""
        return cls._g_kb_name

    @classmethod
    def set_kbname(cls, kbname: str) -> str:
        """Set knowledge base name if supported."""
        if cls.is_supported_kbname(kbname):
            cls._g_kb_name = kbname
        return cls._g_kb_name

    @classmethod
    def is_supported_kbname(cls, kbname: str) -> bool:
        """Check if knowledge base name is supported."""
        return kbname in cls.SUPPORTED_KBNAMES


class RagRetrievalNum:
    """
    Retrieval number settings.
    Manages the number of items to retrieve.
    """
    _g_retrieval_num: int = 20
    SUPPORTED_NUMS: List[int] = [10, 20, 40, 60]

    @classmethod
    def get_retrieval_num(cls) -> int:
        """Get current retrieval number."""
        return cls._g_retrieval_num

    @classmethod
    def set_retrieval_num(cls, retrieval_num: int) -> int:
        """Set retrieval number if supported."""
        if retrieval_num in cls.SUPPORTED_NUMS:
            cls._g_retrieval_num = retrieval_num
        return cls._g_retrieval_num


if __name__ == "__main__":
    # Test GPT model selection
    print(f"Current GPT model: {RagModelGptSel.get_gpt_model()}")
    RagModelGptSel.set_gpt_model("gpt-4o")
    print(f"After setting GPT model: {RagModelGptSel.get_gpt_model()}")
    
    # Test KB name selection
    print(f"\nCurrent KB name: {RagKbNameSel.get_kbname()}")
    RagKbNameSel.set_kbname("papers")
    print(f"After setting KB name: {RagKbNameSel.get_kbname()}")
    
    # Test retrieval number
    print(f"\nCurrent retrieval num: {RagRetrievalNum.get_retrieval_num()}")
    RagRetrievalNum.set_retrieval_num(40)
    print(f"After setting retrieval num: {RagRetrievalNum.get_retrieval_num()}")