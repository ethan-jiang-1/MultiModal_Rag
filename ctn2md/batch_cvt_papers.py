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

from ctn2md.ctn2md_converter_pdf_lvlm import do_content2md_convert as dcc_lvlm
from ctn2md.ctn2md_converter_all_lp import do_content2md_convert as dcc_lp
from mmbase.utils.util_logging import setup_logger_handlers

def batch_convert(doc_pathnames: List[str]):
    for ndx, doc_pathname in enumerate(doc_pathnames):
        logging.info("\n\n\n")
        logging.info(f"start to convert {ndx+1}/{len(doc_pathnames)}: {doc_pathname}")
        if not os.path.isfile(doc_pathname):
            logging.error(f"{doc_pathname} not eixist, skip")

        if doc_pathname.endswith(".pdf"):
            ret = dcc_lvlm(doc_pathname)
        else:
            ret = dcc_lp(doc_pathname)
        rich.print(ret)

if __name__ == "__main__":
    setup_logger_handlers()
    
    doc_pathnames = []
    doc_pathnames.append("datasrc/exam/raw_docs/papers/深度学习在视电阻率快速反演中的研究.pdf")
    doc_pathnames.append("datasrc/exam/raw_docs/papers/ChatGPT intimates a tantalizing future_compressed.pdf")
    doc_pathnames.append("datasrc/exam/raw_docs/papers/Long-Context LLMs Meet RAG_compressed.pdf")
    doc_pathnames.append("datasrc/exam/raw_docs/papers/YOU ONLY 2409.13695v1.pdf")
    doc_pathnames.append("datasrc/exam/raw_docs/papers/LongRAG.pdf")
    doc_pathnames.append("datasrc/exam/raw_docs/papers/DIFFERENTIAL TRANSFORMER 2410.05258v1.pdf")
    doc_pathnames.append("datasrc/exam/raw_docs/papers/Winning Solution For Meta KDD Cup’ 24 2410.00005v1.pdf")
    doc_pathnames.append("datasrc/exam/raw_docs/papers/Survey of different Large Language Model Architectures.pdf")
    doc_pathnames.append("datasrc/exam/raw_docs/papers/A Coin Has Two Sides.pdf")
    doc_pathnames.append("datasrc/exam/raw_docs/papers/attention_is_all_you_need.pdf")

    batch_convert(doc_pathnames)