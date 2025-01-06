import pytest
import os
from ctn2md.ctn2md_converter_ti import do_content2md_convert
from ctn2md.src.md_info_base import MdInfo

@pytest.fixture
def sample_doc(tmp_path):
    """创建一个示例文档用于测试"""
    doc_content = """# 测试文档

这是一个测试文档的内容。

## 第一章

这是第一章的内容。

## 第二章

这是第二章的内容。
"""
    doc_file = tmp_path / "test_doc.txt"
    doc_file.write_text(doc_content)
    return str(doc_file)

def test_do_content2md_convert_basic(sample_doc, tmp_path):
    """测试基本的文档转换功能"""
    out_dir = str(tmp_path / "output")
    result_json = do_content2md_convert(sample_doc, out_dir=out_dir)
    
    # 验证结果
    assert result_json is not None
    assert os.path.exists(result_json)
    
    # 验证生成的MdInfo
    md_info = MdInfo(result_json)
    assert md_info is not None

@pytest.mark.integration
def test_do_content2md_convert_with_controls(sample_doc, tmp_path):
    """测试带控制参数的文档转换"""
    out_dir = str(tmp_path / "output")
    mdcontrols = {
        "some_control": "value"
    }
    
    result_json = do_content2md_convert(
        sample_doc,
        out_dir=out_dir,
        enforced_gen=True,
        mdcontrols=mdcontrols
    )
    
    assert result_json is not None
    assert os.path.exists(result_json)

def test_do_content2md_convert_error_handling(tmp_path):
    """测试错误处理"""
    non_existent_file = str(tmp_path / "non_existent.txt")
    out_dir = str(tmp_path / "output")
    
    with pytest.raises(Exception):
        do_content2md_convert(non_existent_file, out_dir=out_dir) 