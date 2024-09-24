from dotenv import load_dotenv, find_dotenv
import os, sys, logging, json
from pprint import pformat

load_dotenv()

def _get_root_dir():
    root_dir = os.path.abspath(os.path.dirname(find_dotenv()))  
    return root_dir

def _add_lib_paths():
    new_paths = []
    dir_root = _get_root_dir()
    dir_hiqa = os.path.join(dir_root, "HiQA")
    new_paths.append(dir_root)
    new_paths.append(dir_hiqa)
    #new_paths.append(os.path.dirname(__file__))
    for new_path in new_paths:
        if new_path not in sys.path:
            print(f"add sys_path: {new_path}")
            sys.path.append(new_path)

_add_lib_paths()

logging.basicConfig(level=logging.DEBUG)

def _setup_logger_handlers():
    from logging.handlers import TimedRotatingFileHandler

    # hook logging to output the log to stdout as well
    logger = logging.getLogger()
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)  # 为handler设置级别
    formatter = logging.Formatter('%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    log_dir = os.path.abspath(os.path.dirname(find_dotenv()))
    log_file = os.path.join(log_dir, "mmr.log")

    srs_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
    srs_handler.suffix = "%Y-%m-%d.log"
    formatter = logging.Formatter('%(asctime)s - PID:%(process)d - %(levelname)s - %(message)s')
    srs_handler.setFormatter(formatter)
    srs_handler.setLevel(logging.DEBUG)  # 为handler设置级别
    logger.addHandler(srs_handler)

_setup_logger_handlers()

def _ensure_working_dir():
    dir_root = _get_root_dir()
    dir_hiqa = os.path.join(dir_root, "HiQA")
    os.chdir(dir_hiqa)
    return dir_hiqa
   
_ensure_working_dir()

def _call_retrival(user_input):
    from HiQA.service.knowledge_client import get_knowledge
    import time 

    only_vec = False
    max_tokens = 8000
    dataset = 'test'

    begin = time.time()
    knowledge = get_knowledge(user_input, max_tokens, dataset, begin, only_vec=only_vec, verbose=True)
    #knowledge = _hack_knowledge(knowledge)

    return knowledge

# modification two: new instruction, beside the response, also answer which piece of knowleddge is relavent 

role = """Role: You are a helpful assistant, you will answer questions as a professional support agent.  please responds only in JSON format. The response's answer should be in the "answer" field of the JSON, and the relevant segment's source information should be included in the "citation" field of the JSON \n" Note:
1. When users ask questions, I will provide you with some information, please refer to the information and your own knowledge to answer.
2. Each data Paragraph begins with "*** New Knowledge Paragraph ***", the next line [Source File] xxx [Source File] indicates the source of the file, The next line [Knowledge Title] xxx [Knowledge Title] indicates the title of this section, and the next line [Knowledge Content] xxx [Knowledge Content] is the knowledge content you are referring to.
3. Your answers should be accurate and reasonable, but not summary.
4. If your own knowledge and given information cannot answer the user's question, do not answer and tell the user "Sorry, I cannot answer your question."
5. There are redundant parts in the reference materials provided by us. Please ignore the materials that are not relevant to the question.
6. If you are asked to answer a multiple choice question (single choice or multiple choice), analyze each choice first. After analyzing the choices, write the answer.
7. If you use the table in your answer, please output the table in markdown's table format. The format of the table must strictly use markdown's format.
8. If some data is not directly given, try to calculate through the given data first, show the calculation process, and then answer the question after the calculation step is complete.
9. Please focus on answering the user's question, do not answer with irrelevant information. 
10. The answer needs to be found in different "*** New Knowledge Paragraph ***" information segments. If the information is found in a specific segment, include the [Source File] of that segment in the "citation" part of the JSON response."""


def _call_generator(user_input, knowledge):
    from utils.openai_proxy import client

    resp = None
    chat_messages = None 

    try:
        model_name = 'gpt-4o'
        #model_name = "gpt-4o-mini"
        report = []
        # Looping over the response
        chat_messages=[
            {"role": "system",
                "content": role},
            {"role": "user",
                "content": f"According to the given knowledge, answer this question: {user_input}\nThe given knowledge is: \n{knowledge}"}
        ]
        resp = client.chat.completions.create(
                model=model_name,
                # model='gpt-4-32k',
                # max_tokens=4000,
                messages=chat_messages,
                stream=False,
                temperature=0.1 
        )
    except Exception as e:
        logging.exception(str(e))
    
    return resp, chat_messages

def _remove_ext(match):
    match_noext = os.path.basename(match)
    exts = [".csv", ".step1", ".pdf", ".docx", ".xlsx", ".md"]
    for i in range(len(exts)):
        for ext in exts:
            if match_noext.endswith(ext):
                match_noext = match_noext.replace(ext, "")
    return match_noext

def _locate_matched_raw_files(matches):
    from pathlib import Path
    dir_root = _get_root_dir()
    dir_raw = os.path.join(dir_root, "HiQA/datasets/raw")
    lst_names = os.listdir(dir_raw)
    lst_names = sorted(lst_names, reverse=True)

    matches_path = []
    for match in matches:
        match = match.strip()
        if len(match) > 0:
            match_noext = _remove_ext(match)
            fname_only = match_noext.strip().strip("\u3000")

            for name in lst_names:
                if name.find(fname_only) != -1:
                    fpath = os.path.join(dir_raw, name)
                    matches_path.append(fpath)
    return matches_path

# modification three,  pick up the information from response for which chunk is picked
def _check_soruce_matches(knowledge, response):
    import re
    pattern = r"(?<=\[Source File\]\s)[^\[]+(?=\s\[Source File\])"

    matches = []
    try:
        matches = re.findall(pattern, knowledge)
    except Exception as e:
        logging.exception(str(e))
    matches = _locate_matched_raw_files(matches)
    return matches

def _check_source_citation(citations):
    matches = []
    if isinstance(citations, str):
        citations = citations.split("[Source File]")

    if isinstance(citations, list):
        for citation in citations:
            matches_i = citation.replace("[Source File]", "").strip()
            if len(matches_i) > 0:
                matches.append(matches_i)

    matches = _locate_matched_raw_files(matches)
    return matches

def _find_images_plain_content(user_input, response_content, dataset):
    from HiQA.service.knowledge_client import search_images_from_response

    lst_image_n_title = []
    image_path_base = os.path.join(_get_root_dir(), "HiQA/datasets/test")
    try:
        images = search_images_from_response(user_input, response_content, dataset, image_path_base=image_path_base)
        for image_full_path, title, score, file_name, content in images[:1]:
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

def _get_final_json(response_json, user_input, dataset):
    response_answer = response_json.get("answer")

    image_content = str(response_json.get("citation"))
    lst_image_n_title = _find_images_plain_content(user_input, image_content, dataset)
    logging.info(f"##image_n_title_turple: {lst_image_n_title}") 

    citation = response_json["citation"]
    lst_source_matches = _check_source_citation(citation)
    logging.info(f"##source_matches:\n {lst_source_matches}")    
    return response_answer, lst_image_n_title, lst_source_matches


def _get_final_plain(response_content, user_input, dataset, knowledge):
    image_content = str(response_content)
    response_answer = response_content

    lst_image_n_title = _find_images_plain_content(user_input, image_content, dataset)
    logging.info(f"##image_n_title_turple: {lst_image_n_title}")

    lst_source_matches = _check_soruce_matches(knowledge, response_content)
    logging.info(f"##source_matches:\n {lst_source_matches}")  
    return response_answer, lst_image_n_title, lst_source_matches   

_hiqa_inited = False
def _init_hiqa():
    global _hiqa_inited
    if not _hiqa_inited:
        from HiQA.service.knowledge_client import init_state
        logging.info(f"##init_state: {init_state}")
        _hiqa_inited = True


def do_core_query(user_input):
    ret_dict = {}

    _init_hiqa()

    dataset ='test'
    logging.info("\n\n\n*********\n")
    logging.info(f"##do_core_query: {user_input}")

    knowledge = _call_retrival(user_input)
    logging.info(f"##knowledge:\n {knowledge}")
    if knowledge is None: 
         ret_dict["error"] = "knowledge is None"
         logging.error(f"##ret_dict: {ret_dict}")
         return ret_dict

    #modification one: hack knowledge - to hook knowledge number in chunks
    #knowledge = _hack_knowledge(knowledge)

    resp, chat_messages = _call_generator(user_input, knowledge)   
    if resp is None:
        ret_dict["error"] = "response is None"
        logging.error(f"##ret_dict: {ret_dict}")
        return ret_dict 

    response = resp.choices[0]
    logging.info(f"##response:\n {response}")

    response_content = response.message.content
    logging.info(f"##response_content:\n {response_content}")

    response_json = None
    try:
        response_content = response_content.replace("```json\n", "")
        response_content = response_content.replace("\n```", "")
        response_json = json.loads(response_content)
    except json.JSONDecodeError as ex:
        logging.exception(str(ex))
        logging.warning(f"####response is not json:\n {response_content}")

    if response_json is not None and "answer" in response_json and "citation" in response_json:
        response_answer, lst_image_n_title, lst_source_matches = _get_final_json(response_json, user_input, dataset)      
    else:
        response_answer, lst_image_n_title, lst_source_matches = _get_final_plain(response_content, user_input, dataset, knowledge)      

    #ret_dict["response"] = response 
    ret_dict["user_input"] = user_input
    ret_dict["response_answer"] = response_answer
    ret_dict["lst_source_matches"] = lst_source_matches
    ret_dict["lst_image_n_title"] = lst_image_n_title
    ret_dict["llm_response_content"] = response_content
    ret_dict["llm_response_json"] = response_json

    pretty_str = pformat(ret_dict)
    logging.info(f"##ret_dict:\n {pretty_str}")
    logging.info("")

    return ret_dict



if __name__ == "__main__":
    from pprint import pprint
    user_inputs = []
    #user_inputs.append("前后座椅H点参考距离是多少？")
    #user_inputs.append("Ai在人力资源领域前景趋势")
    #user_inputs.append("有哪些比亚迪的项目")
    #user_inputs.append("N-R17圆角的设计目标值是多少？/圆角目标值")
    user_inputs.append("靠背STO间隙要求是什么？")
    #user_inputs.append("主管的培训课程涉及什么")

    for user_input in user_inputs:
        try:
            ret_dict = do_core_query(user_input)
            pprint(ret_dict)
        except Exception as ex:
            logging.exception(ex)
