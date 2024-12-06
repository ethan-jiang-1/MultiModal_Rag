from dotenv import load_dotenv 
import os
import sys
import logging
import json
import random
from pprint import pformat
import rich
import json_repair

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")


from HiQA.utils.util_logging import setup_logger_handlers, get_logger_progress
from HiQA.utils.util_file import get_root_dir
from HiQA.utils.util_llm_diag import save_llm_diag_messages

setup_logger_handlers()
logger_prg = get_logger_progress()

def _ensure_working_dir():
    dir_root = get_root_dir()
    dir_hiqa = os.path.join(dir_root, "HiQA")
    os.chdir(dir_hiqa)
    return dir_hiqa
   
_ensure_working_dir()

g_gpt_model = "gpt-4o"
def get_gpt_model():
    global g_gpt_model
    return g_gpt_model

def set_gpt_model(model_name):
    global g_gpt_model
    if model_name in ["gpt-4o", "gpt-4o-mini"]:
        g_gpt_model = model_name
    return g_gpt_model

def is_valid_json(response_json_string):
    try:
        json.loads(response_json_string)
        return True
    except ValueError:
        return False


def is_fixable_json(response_json_string):
    try:
        ret = json_loads_repair(response_json_string)
        return ret
    except Exception as ex:
        logging.exception(str(ex))
    return None


def json_loads_repair(response_json_string):
    if is_valid_json(response_json_string):
        return json.loads(response_json_string)
    else:
        logging.warning(f"try to repair json: {response_json_string}")
        ret = json_repair.repair_json(response_json_string, return_objects=True)
        return ret

def _call_retrival(user_input, kb_name):
    #import time 
    knowledge = None 
    try:
        from HiQA.service.knowledge_client import get_knowledge, DEFAULT_KLG_MAX_TOKENS

        only_vec = False
        max_token = DEFAULT_KLG_MAX_TOKENS

        knowledge = get_knowledge(user_input, kb_name, max_token=max_token, only_vec=only_vec, verbose=True)

        #knowledge = _hack_knowledge(knowledge)
        rich.print(knowledge)
    except Exception as ex:
        logging.exception(str(ex))
        logging.error(f"CR: exception occured {ex}")
        raise ex

    return knowledge


def _call_generator(user_input, knowledge):
    from HiQA.utils.openai_proxy import client
    from HiQA.qa_core_prompt import SYSTEM_PROMPT, USER_PROMPT

    resp = None
    chat_messages = None 

    try:
        model_name = get_gpt_model()
        # report = []
        # Looping over the response
        system_prompt = SYSTEM_PROMPT
        user_prompt = USER_PROMPT.replace("{user_input}", user_input).replace("{knowledge}", knowledge)
        temperature=0.1
        top_p=0.9
        chat_messages=[
            {"role": "system",
             "content": system_prompt},
            {"role": "user",
             "content": user_prompt}
        ]
        resp = client.chat.completions.create(
                model=model_name,
                # max_tokens=4000,
                messages=chat_messages,
                stream=False,
                temperature=temperature,
                top_p=top_p,
                timeout=120
        )
        save_llm_diag_messages(chat_messages, resp, model=model_name, temperature=temperature, top_p=top_p, prefix="qacore")
    except Exception as e:
        logging.exception(str(e))
        logging.error(f"CG: exception occured: {e}")
    
    return resp, chat_messages

def _remove_known_source_ext(match):
    match_noext = os.path.basename(match)
    exts = [".csv", ".step1", ".pdf", ".docx", ".xlsx", ".md"]
    for i in range(len(exts)):
        for ext in exts:
            if match_noext.endswith(ext):
                match_noext = match_noext.replace(ext, "")
    return match_noext

def _locate_matched_src_doc_names(source_filenames_from_citation, kb_name):
    #from pathlib import Path
    dir_root = get_root_dir()
    dir_raw = os.path.join(dir_root, f"datasets/{kb_name}/src_docs")
    
    lst_names = os.listdir(dir_raw)
    lst_names = sorted(lst_names, reverse=True)

    lst_matched_fullpathnames = []
    for source_filename in source_filenames_from_citation:
        source_filename = source_filename.strip()
        if len(source_filename) > 0:
            match_noext = _remove_known_source_ext(source_filename)
            fname_only = match_noext.strip().strip("\u3000")

            for name in lst_names:
                if name.find(fname_only) != -1:
                    fpath = os.path.join(dir_raw, name)
                    lst_matched_fullpathnames.append(fpath)
    return lst_matched_fullpathnames

# TODO: ignore: ethan_hiqa_new_image - wait for new structure (discard the old appoach of HiQA later)
def _locate_matched_image_names(image_filenames_from_citation, kb_name):
    #from pathlib import Path
    dir_root = get_root_dir()
    dir_raw = os.path.join(dir_root, f"datasets/{kb_name}/images")
    
    lst_names = os.listdir(dir_raw)
    lst_names = sorted(lst_names, reverse=True)

    lst_matched_fullpathnames = []
    for source_filename in image_filenames_from_citation:
        source_filename = source_filename.strip()
        if len(source_filename) > 0:
            match_noext = _remove_known_source_ext(source_filename)
            fname_only = match_noext.strip().strip("\u3000")

            for name in lst_names:
                if name.find(fname_only) != -1:
                    fpath = os.path.join(dir_raw, name)
                    lst_matched_fullpathnames.append(fpath)
    return lst_matched_fullpathnames

def _find_source_matches_from_citation_sources(citations_sources, kb_name):
    source_filenames_from_citation = []

    if isinstance(citations_sources, list):
        for citation in citations_sources:
            src_path = citation.replace("[Source File]", "").strip()
            if len(src_path) > 0:
                source_filenames_from_citation.append(src_path)

    source_matched_fullpathnames = _locate_matched_src_doc_names(source_filenames_from_citation, kb_name)
    return source_matched_fullpathnames

def _decode_markdown_image_path(encoded_string):
    from urllib.parse import unquote

    # 原始字符串
    #encoded_string = "![前后座椅H点距离参考图](img%5C6%20%E5%89%8D%E5%90%8E%E6%8E%92%E5%BA%A7%E6%A4%85H%E7%82%B9%E8%B7%9D%E7%A6%BB%E8%A6%81%E6%B1%82%20P10.png)"

    # 提取文件路径部分
    start = encoded_string.find("(") + 1
    end = encoded_string.find(")")
    encoded_path = encoded_string[start:end]

    # 解码文件路径
    decoded_path = unquote(encoded_path)
    return decoded_path

def _find_image_matches_from_citation_images(citations_images, kb_name):
    image_filenames_from_citation = []

    if isinstance(citations_images, list):
        for citation in citations_images:
            image_path = _decode_markdown_image_path(citation)
            if len(image_path) > 0:
                image_filenames_from_citation.append(image_path)

    images_matched_fullpathnames = _locate_matched_image_names(image_filenames_from_citation, kb_name)
    return images_matched_fullpathnames

def _find_images_json_content(user_input, response_content, kb_name, source_match):
    from HiQA.service.knowledge_client import search_images_from_response

    lst_image_n_title = []
    try:
        images_descs = search_images_from_response(user_input, response_content, kb_name, source_match)
        for image_full_path, title, score, file_name, content in images_descs[:1]:
            file_name = '_'.join(file_name.split('_')[:-3])
            
            if title != 'Title not found':
                image_title = title
            else:
                image_title = ""
            lst_image_n_title.append({"image":image_full_path, 
                                    "title":image_title})
    except Exception as e:
        logging.exception(str(e))
    return lst_image_n_title

def _get_composited_response_based_on_initial_response_json(response_json, user_input, kb_name):
    response_answer = response_json.get("answer")

    lst_source_matches = []
    citation_sources = response_json.get("citation_sources", None)
    if isinstance(citation_sources, list):
        lst_source_matches = _find_source_matches_from_citation_sources(citation_sources, kb_name)
        logging.info(f"##source_matches:\n {lst_source_matches}")

    lst_image_matches = []
    citation_images = response_json.get("citation_images", None)    
    if isinstance(citation_images, list):
        lst_image_matches = _find_image_matches_from_citation_images(citation_images, kb_name)
        logging.info(f"##image_matches:\n {lst_image_matches}")

    lst_image_n_title = []
    logger_prg.info("step5.1: 92%: 组织回答#信息源头IMG")
    for source_match in lst_source_matches:
        image_content = str(response_json.get("answer"))
        xlst_image_n_title = _find_images_json_content(user_input, image_content, kb_name, source_match)

        if xlst_image_n_title is not None:
            lst_image_n_title.extend(xlst_image_n_title)

    logging.info(f"##image_n_title_turple: {lst_image_n_title}") 

    return response_answer, lst_image_n_title, lst_source_matches

_hiqa_inited = False
def _init_hiqa(kb_name):
    global _hiqa_inited
    if not _hiqa_inited:
        from HiQA.service.knowledge_client import init_kc
        ret = init_kc(kb_name)
        logging.info(f"##init_kc: {ret}")
        _hiqa_inited = True


def do_core_query(user_input, kb_name='test'):
    ret_dict = {}

    logger_prg.info("step1.0: 10%: 初始化知识库")
    _init_hiqa(kb_name)

    req_id = random.randint(10000, 99999)

    logging.info(f"\n\n\n***** REQ{req_id} started ****")
    logging.info(f"##do_core_query: {user_input} on {kb_name}")
    ret_dict["req_id"] = req_id
    ret_dict["user_input"] = user_input
    ret_dict["response_answer"] = ""
    ret_dict["lst_source_matches"] = []
    ret_dict["lst_image_n_title"] = []

    logger_prg.info("step2.0: 20%: 召回相关知识")
    knowledge = _call_retrival(user_input, kb_name)
    logging.info(f"##knowledge:\n {knowledge}")
    if knowledge is None: 
         ret_dict["response_answer"] = "ERROR: retrival knowledge is None"
         logging.error(f"##ret_dict(e0): {ret_dict}")
         return ret_dict

    #modification one: hack knowledge - to hook knowledge number in chunks
    #knowledge = _hack_knowledge(knowledge)

    logger_prg.info("step3.0: 50%: 组织回答#综合知识")
    resp, chat_messages = _call_generator(user_input, knowledge)   
    if resp is None or not hasattr(resp, "choices"):
        ret_dict["response_answer"] = "ERROR: llm response is None"
        ret_dict["debug_resp"] = resp
        logging.error(f"##ret_dict(e1): {ret_dict}")
        return ret_dict 

    response = resp.choices[0]
    logging.info(f"##response:\n {response}")
    if not hasattr(response, "message"): 
        ret_dict["response_answer"] = "ERROR: llm response is invalid"
        ret_dict["debug_resp"] = resp
        ret_dict["debug_response"] = response
        logging.error(f"##ret_dict(e2): {ret_dict}")
        return ret_dict         

    logger_prg.info("step4.0: 80%: 组织回答#解析回答")
    response_content = response.message.content
    logging.info(f"##response_content:\n {response_content}")

    response_json = None
    try:
        response_json = json_loads_repair(response_content)
    except Exception as ex:
        logging.exception(str(ex))
        logging.warning(f"####response is not json:\n {response_content}")

    logger_prg.info("step5.0: 90%: 组织回答#信息源头")
    try:
        response_answer, lst_image_n_title, lst_source_matches = "", [], []
        if response_json is not None \
           and "answer" in response_json \
           and "citation_sources" in response_json \
           and "citation_images" in response_json:
            response_answer, lst_image_n_title, lst_source_matches = _get_composited_response_based_on_initial_response_json(response_json, user_input, kb_name)      
    except Exception as ex: 
        logging.exception(str(ex))
        ret_dict["response_answer"] = "ERROR: failed to process image or source" 
        ret_dict["debug_ex"] = str(ex) 

    #ret_dict["response"] = response 
    ret_dict["user_input"] = user_input
    ret_dict["response_answer"] = response_answer
    ret_dict["lst_source_matches"] = lst_source_matches
    ret_dict["lst_image_n_title"] = lst_image_n_title
    #ret_dict["llm_response_content"] = response_content
    ret_dict["llm_response_json"] = response_json

    pretty_str = pformat(ret_dict)
    logging.info(f"##ret_dict: \n {pretty_str}")
    logging.info(f"\n**** REQ{req_id}:ended ****\n\n")
    logging.info("")

    ret_dict_json_str = json.dumps(ret_dict, ensure_ascii=True, indent=4)
    logger_prg.info("step6.0: 95%: 回答生成")
    logger_prg.info(f"ret_dict: ```json\n {ret_dict_json_str}\n")
    return ret_dict



if __name__ == "__main__":
    #from pprint import pprint
    user_inputs = []
    #user_inputs.append("前后座椅H点参考距离是多少？")
    #user_inputs.append("Ai在人力资源领域前景趋势")
    #user_inputs.append("有哪些比亚迪的项目")
    #user_inputs.append("N-R17圆角的设计目标值是多少？/圆角目标值")
    user_inputs.append("靠背STO间隙要求是什么？")
    #user_inputs.append("主管的培训课程涉及什么")

    for user_input in user_inputs:
        try:
            ret_dict = do_core_query(user_input, kb_name="test")
            rich.print(ret_dict)
        except Exception as ex:
            logging.exception(ex)
