class CTN_TYPE:
    """文档内容类型定义类
    
    用于标识和转换不同类型的文档内容。
    支持 PDF、PPT、DOC、XLS、MD 等常见文档格式。
    """
    # 支持的文档类型
    PDF = "PDF"
    PPT = "PPT"
    DOC = "DOC"
    XLS = "XLS"
    MD = "MD"

    # 特殊类型
    AUTO = "AUTO"
    UNKNOWN = "UNKNOWN"

    # 文档类型映射表
    _TYPE_MAPPING = {
        'pdf': PDF,
        'ppt': PPT,
        'pptx': PPT,
        'doc': DOC,
        'docx': DOC,
        'xls': XLS,
        'xlsx': XLS,
        'md': MD
    }

    @classmethod
    def get_ctn_type_by_doc_type(cls, doc_type: str) -> str:
        """根据文档类型获取内容类型

        Args:
            doc_type (str): 文档类型字符串，如 'pdf', 'docx' 等

        Returns:
            str: 标准化的内容类型字符串，未知类型返回 UNKNOWN
        """
        if not isinstance(doc_type, str):
            return cls.UNKNOWN

        clean_type = doc_type.replace(".", "").lower()
        return cls._TYPE_MAPPING.get(clean_type, cls.UNKNOWN)

    @classmethod
    def get_ctn_type_by_doc_pathname(cls, doc_pathname: str) -> str:
        """根据文档路径名获取内容类型

        Args:
            doc_pathname (str): 文档路径名

        Returns:
            str: 标准化的内容类型字符串，未知类型返回 UNKNOWN
        """
        try:
            ext_name = doc_pathname.split(".")[-1]
            return cls.get_ctn_type_by_doc_type(ext_name)
        except (AttributeError, IndexError):
            return cls.UNKNOWN

    @classmethod
    def is_valid_type(cls, ctn_type: str) -> bool:
        """检查是否为有效的内容类型

        Args:
            ctn_type (str): 要检查的内容类型字符串

        Returns:
            bool: 如果是有效的内容类型返回 True，否则返回 False
        """
        return ctn_type in {cls.PDF, cls.PPT, cls.DOC, cls.XLS, cls.MD, cls.AUTO}


if __name__ == "__main__":
    import rich

    def test_content_types():
        """测试内容类型转换"""
        test_cases = [
            # (输入, 期望输出, 描述)
            ("test.pdf", CTN_TYPE.PDF, "PDF文件"),
            ("doc/测试文档.docx", CTN_TYPE.DOC, "Word文档"),
            ("presentation.pptx", CTN_TYPE.PPT, "PPT文件"),
            ("data.xlsx", CTN_TYPE.XLS, "Excel文件"),
            ("readme.md", CTN_TYPE.MD, "Markdown文件"),
            ("unknown.xyz", CTN_TYPE.UNKNOWN, "未知类型"),
            ("no_extension", CTN_TYPE.UNKNOWN, "无扩展名"),
            (None, CTN_TYPE.UNKNOWN, "None输入"),
        ]

        for input_path, expected, desc in test_cases:
            try:
                result = CTN_TYPE.get_ctn_type_by_doc_pathname(input_path)
                success = result == expected
                color = "green" if success else "red"
                rich.print(f"[{color}]测试 {desc}: "
                          f"输入='{input_path}', "
                          f"期望='{expected}', "
                          f"实际='{result}' "
                          f"{'✓' if success else '✗'}[/{color}]")
            except Exception as e:
                rich.print(f"[red]测试 {desc} 发生异常: {str(e)}[/red]")

    def test_type_validation():
        """测试类型验证"""
        test_cases = [
            (CTN_TYPE.PDF, True, "PDF类型"),
            (CTN_TYPE.AUTO, True, "AUTO类型"),
            ("PDF", True, "PDF字符串"),
            ("UNKNOWN", False, "UNKNOWN类型"),
            ("invalid", False, "无效类型"),
            (None, False, "None输入"),
        ]

        for input_type, expected, desc in test_cases:
            try:
                result = CTN_TYPE.is_valid_type(input_type)
                success = result == expected
                color = "green" if success else "red"
                rich.print(f"[{color}]验证 {desc}: "
                          f"输入='{input_type}', "
                          f"期望={expected}, "
                          f"实际={result} "
                          f"{'✓' if success else '✗'}[/{color}]")
            except Exception as e:
                rich.print(f"[red]验证 {desc} 发生异常: {str(e)}[/red]")

    # 运行测试
    rich.print("\n[yellow]运行内容类型转换测试...[/yellow]")
    test_content_types()
    
    rich.print("\n[yellow]运行类型验证测试...[/yellow]")
    test_type_validation()