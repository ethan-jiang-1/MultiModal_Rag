#import fitz
#from PIL import Image
import sys
import logging

if "./" not in sys.path:
    sys.path.append("./")

# # from HiQA.service.keyword_setting import load_keywords

from whoosh.index import create_in  # , open_dir
from whoosh.fields import Schema, ID, TEXT
#from whoosh.qparser import QueryParser
import os
import shutil
#import re
#import tqdm

from HiQA.build_tool.img_tools import ChineseAnalyzer
#from HiQA.build_tool.img_tools import parse_page_svg
#from HiQA.build_tool.vl_description import generate_image_description

ix = None
writer = None


def build_imgs_index(kb_name, lang='CN'):
    # Define the schema for the index
    if lang == 'CN':
        schema = Schema(file_name=ID(stored=True),
                        content=TEXT(analyzer=ChineseAnalyzer(), stored=True))
    else:
        schema = Schema(file_name=ID(stored=True), content=TEXT(stored=True))

    directory = os.path.join(r'./HiQA/datasets', kb_name)
    index_path = os.path.join(directory, 'indexes')

    # Create an index in a directory
    if os.path.exists(index_path):
        shutil.rmtree(index_path)
    os.mkdir(index_path)
    # temp_index_dir = index_path
    # temp_index_dir = tempfile.mkdtemp(prefix='index_')

    global ix
    if ix is None:
        ix = create_in(index_path, schema)
    global writer
    if writer is None:
        writer = ix.writer()

    # Add documents to the index
    # base_name = os.path.basename(file).split('.')[0]
    # image_path = f'images{base_name}'
    # writer = ix.writer()
    img_path = os.path.join(directory, 'images')
    for filename in os.listdir(img_path):
        file_path = os.path.join(img_path, filename)
        if not os.path.isdir(file_path):
            continue
        for file in os.listdir(file_path):
            if file.endswith('.txt'):
                doc_path = os.path.join(file_path, file)
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    writer.add_document(file_name=file[:-4], content=content)
                except Exception as e:
                    print(doc_path)
                    logging.exception(e)
            # print('==========')
            # print(content)
            # print("==========")

    writer.commit()
    # return ix


if __name__ == "__main__":
    build_imgs_index('test')