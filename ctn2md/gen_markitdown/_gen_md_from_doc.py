#import logging  
import os
import shutil
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)

load_dotenv()

from ctn2md.src.md_info_base import MdInfo 
from mmbase.utils.util_logging import setup_logger_handlers
import rich
import re

def gen_md_from_doc(md_info:MdInfo, pname_unique_doc:str):
    import mammoth
    
    # 修改 style map 语法
    style_map = "\n".join([
        "p[style-name='heading 1'] => h1:fresh",
        "p[style-name='heading 2'] => h2:fresh",
        "p[style-name='heading 3'] => h3:fresh",
        "p[style-name='heading 4'] => h4:fresh",
        "p[style-name='heading 5'] => h5:fresh",
        "p[style-name='heading 6'] => h6:fresh",
        "p[style-name='标题 1'] => h1:fresh",
        "p[style-name='标题 2'] => h2:fresh",
        "p[style-name='标题 3'] => h3:fresh",
        "p[style-name='标题 4'] => h4:fresh",
        "p[style-name='标题 5'] => h5:fresh",
        "p[style-name='标题 6'] => h6:fresh",
        "p[style-name='Title'] => h1:fresh",
        "p[style-name='Subtitle'] => h2:fresh",
        "p[style-name='Normal'] => p:fresh",
        "p[style-name='dingdocnormal'] => p:fresh",
        "b => strong",
        "i => em",
        "u => em"
    ])

    logger.info(f"Converting document: {pname_unique_doc}")
    logger.info(f"Using style map:\n{style_map}")
    
    out_path = md_info.name_step_pathname(0)
    result = mammoth.convert_to_markdown(
        pname_unique_doc,
        style_map=style_map,
        ignore_empty_paragraphs=True
    )

    # 检查转换过程中的警告
    messages = result.messages
    for message in messages:
        logger.warning(message)

    # 后处理：将双下划线包裹的文本转换为标题
    markdown_content = result.value
    
    # 使用正则表达式处理双下划线标记的标题
    def replace_underscores(match):
        text = match.group(1)
        # 如果文本在单独的行上，转换为二级标题
        if text.strip() and (match.start() == 0 or markdown_content[match.start()-1] == '\n'):
            return f"## {text}"
        return match.group(0)
    
    markdown_content = re.sub(r'__([^_]+?)__', replace_underscores, markdown_content)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    logger.info(f"Conversion completed. Output saved to: {out_path}")
    return out_path


if __name__ == "__main__":
    setup_logger_handlers()

    md_info_path = "_output/ctn2md_misc__成都交通局_华为说明_mid/_info.json"
    md_info = MdInfo(md_info_path)

    unique_id = md_info.get_unique_job_id()
    src_pathname = md_info.get_doc_pathname()
    # 获取源文件的后缀名
    _, src_extension = os.path.splitext(src_pathname)
    pname_unique_doc = os.path.join(md_info.get_out_dir(), f"{unique_id}{src_extension}")
    shutil.copy(src_pathname, pname_unique_doc)

    ret = gen_md_from_doc(md_info, pname_unique_doc)
    rich.print(ret)