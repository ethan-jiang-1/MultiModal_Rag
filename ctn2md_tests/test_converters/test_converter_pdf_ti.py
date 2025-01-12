import pytest
import os
from unittest.mock import patch
from ctn2md.ctn2md_converter_pdf_ti import do_content2md_convert
from ctn2md.src.md_info_base import MdInfo
from ctn2md.src_gen.ctn2md_gen_md_textin import GenMd_TextIn


def test_do_content2md_convert_error_handling(tmp_path):
    """测试错误处理"""
    non_existent_file = str(tmp_path / "non_existent.txt")
    out_dir = str(tmp_path / "output")
    
    with pytest.raises(Exception):
        do_content2md_convert(non_existent_file, out_dir=out_dir) 


def xtestx_do_content2md_convert_calls_does_gen_needed(tmp_path):
    """测试正常PDF文件时是否正确调用GenMd_TextIn.does_gen_needed"""
    # 准备测试文件和目录
    test_pdf = str(tmp_path / "test.pdf")
    out_dir = str(tmp_path / "output")
    os.makedirs(out_dir, exist_ok=True)
    
    # 创建一个空的PDF文件用于测试
    with open(test_pdf, 'wb') as f:
        f.write(b'%PDF-1.4\n')  # 最小的PDF文件头
    
    # 使用mock来跟踪does_gen_needed的调用
    with patch.object(GenMd_TextIn, 'does_gen_needed') as mock_does_gen_needed:
        # 设置mock的返回值
        mock_does_gen_needed.return_value = (MdInfo(out_dir), True)
        
        # 执行转换
        do_content2md_convert(test_pdf, out_dir=out_dir)
        
        # 验证does_gen_needed被调用，并且参数正确
        mock_does_gen_needed.assert_called_once() 