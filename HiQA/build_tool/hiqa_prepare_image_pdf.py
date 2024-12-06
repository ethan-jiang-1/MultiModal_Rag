import fitz
from PIL import Image
import sys
import logging

if "./" not in sys.path:
    sys.path.append("./")

import os
import shutil
import re
import tqdm

from HiQA.build_tool.img_tools import parse_page_svg
from HiQA.utils.util_file import get_root_dir
from HiQA.utils.util_logging import setup_logger_handlers
from ctn2md.utils_llm.vllm_description import generate_image_description

def _save_crop_image_and_description(cropped_img, pathname_no_ext):
    image_pathname = pathname_no_ext + '.png'
    # print(image_name)
    try:
        cropped_img.save(image_pathname)
    except Exception as e:
        logging.exception(e)
        return None
    
    if not os.path.isfile(image_pathname):
        return None
    
    try:
        title = os.path.basename(pathname_no_ext).split("_img")[0]
        # Handle text extraction around the image
        # text_content = get_text_around_image(blocks[skip_block:], i, lang)
        instruction = f"这是一张在'{title}'文件中的图片， 请简单描述一下这张图片。" 
        text_content = generate_image_description(image_pathname, instruction=instruction)
        # title = get_title_of_image(blocks[skip_block:], i, lang)
        logging.error("text_content is None")
        if text_content is None:
            return None
    except Exception as e:
        logging.exception(e)
        return None

    # print(text_content[:30])
    # print(title)

    # Save the description to a .txt file
    desc_pathname = f'{pathname_no_ext}.txt'
    with open(desc_pathname, 'w',
              encoding='utf-8') as text_file:
        line3desc = title + '\n' + \
                    text_content.replace('\n', ' ') + \
                    f'\nbase name:{title}'
        text_file.write(line3desc)

    return desc_pathname


def load_imgs_from_pdf(kb_name,
                       filename,
                       dpi=300,
                       skip_page_front=0,
                       skip_page_back=1,
                       skip_block=5,
                       lang='CN'):
    """
    Load pdf file, covert to image, description and index it
    :param lang:
    :param skip_block:
    :param skip_page_back:
    :param skip_page_front:
    :param dpi:
    :param file:
    :return:
    """

    directory = os.path.join(r'./datasets', kb_name)
    file_path = os.path.join(directory, 'src_docs', filename)
    doc = fitz.open(file_path)

    # load pages
    pages = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        pages.append(page)

    # increase dpi to 300
    dpi = int(dpi)
    scale = dpi / 72  # default dpi of pdf is 72
    matrix = fitz.Matrix(scale, scale)
    skip_block = int(skip_block)

    base_name = filename.split('.pdf')[0]
    img_root_dir = os.path.join(directory, 'images', base_name)
    if os.path.exists(img_root_dir):
        shutil.rmtree(img_root_dir)
    os.mkdir(img_root_dir)

    for page in pages[int(skip_page_front
                          ):-int(skip_page_back)]:  # skip final page

        # part1: get image with description in png-pdf
        p1dict = page.get_text('dict')
        blocks = p1dict['blocks']
        page_pix = page.get_pixmap(matrix=matrix, dpi=dpi)
        page_im = Image.frombytes("RGB", (page_pix.width, page_pix.height),
                                  page_pix.samples)

        saved_path_no_exts = []  # need to remove if inner a svg image
        for i, block in enumerate(blocks[int(skip_block):]
                                  ):  # head and tail of pages should be ignore
            if 'image' in block:
                # try:
                bbox = block['bbox']
                # skip image that width=398 and hight=137 -> Typically LOGO
                # TODO: ignore: ethan_hiqa_new_doc? skip some special case
                # if (bbox[2] - bbox[0])*scale - LOGO_WIDTH <= 10 and (bbox[3] - bbox[1])*scale - LOGO_HEIGHT <= 10:
                #     continue
                # Scale the bbox coordinates
                cropped_img = page_im.crop([int(i * scale) for i in bbox])
                number = block['number']

                pathname_no_ext = img_root_dir + f'/{base_name}_imgbmp_{page.number}_{number}'

                if _save_crop_image_and_description(cropped_img, pathname_no_ext) is None:
                    continue

                saved_path_no_exts.append((pathname_no_ext, [int(i * scale) for i in bbox]))
            # except:
            #     pass

        # part2: get image with description in svg-pdf
        try:
            svg = page.get_svg_image(matrix=fitz.Identity)
            image_clips, svg_blocks = parse_page_svg(svg, page.number)
            for clip in image_clips:

                transform = []
                for item in clip[0]:
                    # print(item, type(item))
                    if item[0] == '.':
                        transform.append(float('0' + item))
                    elif item[0] == '-':
                        transform.append(float('-0' + item[1:]))
                    else:
                        transform.append(float(item))
                d = clip[1]
                page_id = clip[2] # noqa
                block_id = clip[3]
                matches = re.findall(r'H(\d+\.?\d*)V(\d+\.?\d*)', d)
                float_values = [float(value) for value in matches[0]]
                box_width = float_values[0]
                box_height = float_values[1]
                width_scale = transform[0]
                height_scale = transform[3]
                width_move = transform[4]
                height_move = transform[5]
                x1 = width_move * scale
                y1 = height_move * scale
                # x1=347*scale
                # y1=587*scale
                x2 = x1 + box_width * width_scale * scale
                y2 = y1 + box_height * height_scale * scale

                if y1 > y2:
                    y1, y2 = y2, y1

                # print(x1, y1, x2, y2)
                # 3. 截取并保存图像

                # check images in saved, if in or similar, delete it from file system
                for i, (file_name, bbox) in enumerate(saved_path_no_exts):
                    if (abs(bbox[0] - x1) < 10\
                            and abs(bbox[1] - y1) < 10\
                            and abs(bbox[2] - x2) < 10\
                            and abs(bbox[3] - y2) < 10) or \
                            (bbox[0]>x1-10 and bbox[1]>y1-10 and bbox[2]<x2+10 and bbox[3]<y2+10):
                        os.remove(file_name + '.png')
                        os.remove(file_name + '.txt')
                        saved_path_no_exts.pop(i)
                        break

                cropped_img = page_im.crop(
                    (int(x1), int(y1), int(x2), int(y2)))
                
                pathname_no_ext = img_root_dir + f'/{base_name}_imgsvg_{page.number}_{block_id}'
                _save_crop_image_and_description(cropped_img, pathname_no_ext)

        except Exception as e:
            # some page dont have svg image
            logging.exception(e)
            pass
    return img_root_dir


# Basic usage, convert all pdfs in a path and build index.
def rebuild_img_index_from_pdf(kb_name, reforced=False):
    from HiQA.build_tool.imgs_index import build_imgs_index

    os.makedirs(f'./datasets/{kb_name}/images', exist_ok=True)
    os.makedirs(f'./datasets/{kb_name}/indexes', exist_ok=True)
    os.makedirs(f'./datasets/{kb_name}/src_docs', exist_ok=True)

    if reforced:
        for filename in os.listdir(f'./datasrc/{kb_name}/raw_docs'):
            if filename.endswith('.pdf'):
                src_path = f'./datasrc/{kb_name}/raw_docs/{filename}'
                dst_path = f'./datasets/{kb_name}/src_docs/{filename}'
                shutil.copy(src_path, dst_path)
    
        file_names = os.listdir(f'./datasets/{kb_name}/src_docs')
        file_names = sorted(file_names)
        for pdf_filename in tqdm.tqdm(file_names):
            # TODO: ignore: ethan_hiqa_new_doc? why we need such hack? bug_fix we have hard time to extract image from scanned file
            if pdf_filename.find("业绩案例") != -1:
                continue
            load_imgs_from_pdf(kb_name, pdf_filename)

    build_imgs_index(kb_name)

if __name__ == "__main__":
    dir_root = get_root_dir()
    os.chdir(dir_root)
    setup_logger_handlers()

    #kb_name = "test"
    kb_name = "exam"
    rebuild_img_index_from_pdf(kb_name, reforced=True)
