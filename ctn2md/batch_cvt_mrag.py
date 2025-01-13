from typing import List
from dotenv import load_dotenv
import os
import logging
import rich


load_dotenv()

if __name__ == "__main__":
    from dotenv import find_dotenv
    _root_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    os.chdir(_root_dir)

from mmbase.utils.util_logging import setup_logger_handlers
from ctn2md.gen_lvlm.lvlm_pdf_pages_to_images import normalize_path
from ctn2md.cvt_selector import convert_document

def batch_convert(doc_pathnames: List[str]):
    for ndx, doc_pathname in enumerate(doc_pathnames):
        logging.info("\n\n\n")
        logging.info(f"start to convert {ndx+1}/{len(doc_pathnames)}: {doc_pathname}")
        if not os.path.isfile(doc_pathname):
            logging.error(f"{doc_pathname} not exist, skip")
            continue

        try:
            doc_pathname = normalize_path(doc_pathname)
            result = convert_document(doc_pathname) 
            rich.print(result)
        except Exception as ex:
            logging.error(f"Error converting {doc_pathname}: {str(ex)}")
            continue

if __name__ == "__main__":
    setup_logger_handlers()
    
    doc_pathnames = []
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/AIGC时代的人力资源管理进化(徐刚).pdf"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/业绩案例、上汽内外饰部CAD外包框架服务合同.pdf"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/业绩案例、比亚迪SJ项目低压线束设计技术服务合同（电子电器）.pdf"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/业绩案例、比亚迪ST2H项目低压线束设计技术服务合同（电子电器）.pdf"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/业绩案例、比亚迪车架总成技术服务合同.pdf"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/业绩案例、比亚迪铝大梁式车架及副车架设计外包中标通知书.pdf"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/业绩案例、比亚迪驻场线束设计技术服务合同（电子电器）.pdf"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/1. 座椅STO间隙 P1.pptx"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/2. 座垫与钢丝间隙 P1.pptx"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/3. 头枕杆圆角定义 P1.pptx"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/4. 前后排座椅间距定义 P1.pptx"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/5. back panel 与环境匹配工程校核_P2.pptx"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/6. 前后排座椅H点距离要求 P1.pptx"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/管理者角色定位与认知课程大纲.docx"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/考勤修改统一规则.xlsx"))
    doc_pathnames.append(normalize_path("datasrc/exam/raw_docs/mrag/高效沟通之黄金三角模型课程大纲.docx"))

    batch_convert(doc_pathnames)