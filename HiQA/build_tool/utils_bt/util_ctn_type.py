class CtnType:
    PDF = "pdf"
    PPT = "ppt"
    DOC = "doc"
    XLS = "xls"
    UNKNOWN = "unknown"

    @classmethod
    def get_ctn_type(cls, doc_type):
        if isinstance(doc_type, str):
            doc_type = doc_type.replace(".", "")
            doc_type = doc_type.lower()
            if doc_type in ["pdf"]:
                return cls.PDF
            elif doc_type in ["ppt", "pptx"]:
                return cls.PPT
            elif doc_type in ["doc", "docx"]:
                return cls.DOC
            elif doc_type in ["xls", "xlsx"]:
                return cls.XLS
        
        return cls.UNKNOWN