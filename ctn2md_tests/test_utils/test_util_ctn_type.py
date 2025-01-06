import pytest
from ctn2md.utils.util_ctn_type import CTN_TYPE


@pytest.mark.parametrize("doc_type, expected", [
    ("pdf", CTN_TYPE.PDF),
    ("PDF", CTN_TYPE.PDF),
    ("docx", CTN_TYPE.DOC),
    ("pptx", CTN_TYPE.PPT),
    ("xlsx", CTN_TYPE.XLS),
    ("md", CTN_TYPE.MD),
    ("unknown", CTN_TYPE.UNKNOWN),
    ("", CTN_TYPE.UNKNOWN),
    (None, CTN_TYPE.UNKNOWN),
])
def test_get_ctn_type_by_doc_type(doc_type, expected):
    """测试根据文档类型获取内容类型的功能"""
    assert CTN_TYPE.get_ctn_type_by_doc_type(doc_type) == expected


@pytest.mark.parametrize("pathname, expected", [
    ("test.pdf", CTN_TYPE.PDF),
    ("path/to/doc/测试文档.docx", CTN_TYPE.DOC),
    ("presentation.pptx", CTN_TYPE.PPT),
    ("data.xlsx", CTN_TYPE.XLS),
    ("readme.md", CTN_TYPE.MD),
    ("unknown.xyz", CTN_TYPE.UNKNOWN),
    ("no_extension", CTN_TYPE.UNKNOWN),
    ("", CTN_TYPE.UNKNOWN),
])
def test_get_ctn_type_by_doc_pathname(pathname, expected):
    """测试根据文档路径名获取内容类型的功能"""
    assert CTN_TYPE.get_ctn_type_by_doc_pathname(pathname) == expected


@pytest.mark.parametrize("ctn_type, expected", [
    (CTN_TYPE.PDF, True),
    (CTN_TYPE.DOC, True),
    (CTN_TYPE.PPT, True),
    (CTN_TYPE.XLS, True),
    (CTN_TYPE.MD, True),
    (CTN_TYPE.AUTO, True),
    (CTN_TYPE.UNKNOWN, False),
    ("INVALID", False),
    ("", False),
    (None, False),
])
def test_is_valid_type(ctn_type, expected):
    """测试内容类型验证功能"""
    assert CTN_TYPE.is_valid_type(ctn_type) == expected


def test_type_mapping_consistency():
    """测试类型映射的一致性"""
    # 确保所有映射的值都是有效的内容类型
    for mapped_type in CTN_TYPE._TYPE_MAPPING.values():
        assert CTN_TYPE.is_valid_type(mapped_type), f"映射类型 {mapped_type} 应该是有效的" 