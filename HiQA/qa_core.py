from dotenv import load_dotenv, find_dotenv
import os, sys, logging
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
    new_paths.append(os.path.dirname(__file__))
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

role = """Role: You are a helpful assistant, you will answer questions as a professional support agent.\n" Note:
1. When users ask questions, I will provide you with some information, please refer to the information and your own knowledge to answer.
2. Each data Paragraph begins with "*** New Knowledge Paragraph ***", the next line [Source File] xxx [Source File] indicates the source of the file, The next line [Knowledge Title] xxx [Knowledge Title] indicates the title of this section, and the next line [Knowledge Content] xxx [Knowledge Content] is the knowledge content you are referring to.
3. Your answers should be accurate and reasonable, but not summary.
4. If your own knowledge and given information cannot answer the user's question, do not answer and tell the user "Sorry, I cannot answer your question."
5. There are redundant parts in the reference materials provided by us. Please ignore the materials that are not relevant to the question.
6. If you are asked to answer a multiple choice question (single choice or multiple choice), analyze each choice first. After analyzing the choices, write the answer.
7. If you use the table in your answer, please output the table in markdown's table format. The format of the table must strictly use markdown's format.
8. If some data is not directly given, try to calculate through the given data first, show the calculation process, and then answer the question after the calculation step is complete.
9. Please focus on answering the user's question, do not answer with irrelevant information."""


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
                stream=False
        )
    except Exception as e:
        logging.exception(str(e))
    
    return resp, chat_messages

def _check_soruce_matches(knowledge, response):
    import re
    pattern = r"(?<=\[Source File\]\s)[^\[]+(?=\s\[Source File\])"

    matches = []
    try:
        matches = re.findall(pattern, knowledge)
    except Exception as e:
        logging.exception(str(e))
    return matches

def _find_images(user_input, response_content, dataset):
    from service.knowledge_client import search_images_from_response

    image_n_title_turple = []
    try:
        images = search_images_from_response(user_input, response_content, dataset)
        for image_full_path, title, score, file_name, content in images[:1]:
            file_name = '_'.join(file_name.split('_')[:-3])
            
            if title != 'Title not found':
                image_title = "Source - " + file_name + ",\t" + title
            else:
                image_title = "Source - " + file_name
            image_n_title_turple.append((image_full_path, image_title))
    except Exception as e:
        logging.exception(str(e))
    return image_n_title_turple


def do_core_query(user_input):
    ret_dict = {}

    dataset ='test'
    logging.info("\n\n\n*********\n")
    logging.info(f"##do_core_query: {user_input}")

    from HiQA.service.knowledge_client import init_state
    logging.info(f"##init_state: {init_state}")

    knowledge = _call_retrival(user_input)
    logging.info(f"##knowledge:\n {knowledge}")
    if knowledge is None: 
         ret_dict["error"] = "knowledge is None"
         logging.error(f"##ret_dict: {ret_dict}")
         return ret_dict

    resp, chat_messages = _call_generator(user_input, knowledge)   
    if resp is None:
        ret_dict["error"] = "response is None"
        logging.error(f"##ret_dict: {ret_dict}")
        return ret_dict 

    response = resp.choices[0]
    logging.info(f"##response:\n {response}")

    response_content = response.message.content
    logging.info(f"##response_content:\n {response_content}")

    lst_source_matches = _check_soruce_matches(knowledge, response)
    logging.info(f"##source_matches:\n {lst_source_matches}") 

    lst_image_n_title_turple = _find_images(user_input, response_content, dataset)
    logging.info(f"##image_n_title_turple: {lst_image_n_title_turple}")

    #ret_dict["response"] = response 
    ret_dict["response_content"] = response_content
    ret_dict["lst_source_matches"] = lst_source_matches
    ret_dict["lst_image_n_title_turple"] = lst_image_n_title_turple

    pretty_str = pformat(ret_dict)
    logging.info(f"##ret_dict:\n {pretty_str}")
    logging.info("")

    return ret_dict



if __name__ == "__main__":
    from pprint import pprint
    #user_input = "前后座椅H点参考距离是多少？"
    user_input = "Ai在人力资源领域前景趋势"

    ret_dict = do_core_query(user_input)
    pprint(ret_dict)

