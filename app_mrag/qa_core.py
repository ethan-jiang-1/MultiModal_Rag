from dotenv import load_dotenv 
#import os
import sys
import logging
import json
import random
from pprint import pformat
import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")


from md2vdb.utils.util_logging import setup_logger_handlers, get_logger_progress
from md2vdb.query.query2section_raw import query2section_raw_on_multiple_collection
from md2vdb.query.query2section_reranked import query2sortedsections_reranked
from md2vdb.query.query2knowledge import knowledge_retrieve, form_knowledge_sections
from md2vdb.query.query2knowledge import query_rewerite

setup_logger_handlers()
logger_prg = get_logger_progress()

def do_core_query(user_input, kb_name='mrag', limit=10):
    logging.info(f"do_core_query: {user_input} on {kb_name}")
    ret_dict = {}

    logger_prg.info("step1.0: 10%: 初始化知识库")

    req_id = random.randint(10000, 99999)

    logging.info(f"\n\n\n***** REQ{req_id} started ****")
    logging.info(f"##do_core_query: {user_input} on {kb_name}")
    ret_dict["req_id"] = req_id
    ret_dict["user_input"] = user_input
    ret_dict["response_answer"] = ""
    ret_dict["lst_source_matches"] = []
    ret_dict["lst_image_n_title"] = []

    logger_prg.info("step1.1 20%: 查询重写")
    collection_names = [kb_name]
    query = user_input
    query = query_rewerite(query, collection_names)

    logger_prg.info("step2.0: 30%: 召回相关知识(raw)")
    scored_sections_raw = query2section_raw_on_multiple_collection(collection_names, query, limit=limit)
    logging.info(f"##knowledge:\n {scored_sections_raw}")
    if scored_sections_raw is None: 
         ret_dict["response_answer"] = "ERROR: retrival knowledge is None"
         logging.error(f"##ret_dict(e0): {ret_dict}")
         return ret_dict

    logger_prg.info("step3.0: 40%: 召回相关知识(rerank)")
    scored_sections_reranked = query2sortedsections_reranked(query, scored_sections_raw)

    logger_prg.info("step4.0: 50%: 组织整理知识")
    knowledge = form_knowledge_sections(scored_sections_reranked)

    logger_prg.info("step4.0: 60%: 组织回答#综合知识(文本)")
    resp = knowledge_retrieve(query, knowledge, scored_sections_reranked) 
    if resp is None:
        ret_dict["response_answer"] = "ERROR: llm response is None"
        ret_dict["debug_resp"] = resp
        logging.error(f"##ret_dict(e1): {ret_dict}")
        return ret_dict 

    logger_prg.info("step5.0: 80%: 组织回答#综合知识(图像)")
    resp = knowledge_retrieve(query, knowledge, scored_sections_reranked) 
    if resp is None:
        ret_dict["response_answer"] = "ERROR: llm response is None"
        ret_dict["debug_resp"] = resp
        logging.error(f"##ret_dict(e1): {ret_dict}")
        return ret_dict 

    #ret_dict["response"] = response 
    resp["answer"] = resp["simple_answer"]
    ret_dict["user_input"] = user_input
    ret_dict["response_answer"] = resp["simple_answer"]
    ret_dict["lst_source_matches"] = resp["referenced_documents"]
    ret_dict["lst_image_n_title"] = []
    ret_dict["llm_response_json"] = resp

    pretty_str = pformat(ret_dict)
    logging.info(f"##ret_dict: \n {pretty_str}")
    logging.info(f"\n**** REQ{req_id}:ended ****\n\n")
    logging.info("")

    ret_dict_json_str = json.dumps(ret_dict, ensure_ascii=True, indent=4)
    logger_prg.info("step6.0: 90%: 回答生成")
    logger_prg.info(f"ret_dict: ```json\n {ret_dict_json_str}\n")
    return ret_dict



if __name__ == "__main__":
    #from pprint import pprint
    user_inputs = []
    #user_inputs.append("前后座椅H点参考距离是多少？")
    #user_inputs.append("Ai在人力资源领域前景趋势")
    #user_inputs.append("有哪些比亚迪的项目")
    #user_inputs.append("N-R17圆角的设计目标值是多少？/圆角目标值")
    #user_inputs.append("靠背STO间隙要求是什么？")
    #user_inputs.append("主管的培训课程涉及什么")
    user_inputs.append("椅背板与旁侧板的保留运动间隙是多少？")

    for user_input in user_inputs:
        try:
            ret_dict = do_core_query(user_input, kb_name="mrag")
            rich.print(ret_dict)
        except Exception as ex:
            logging.exception(ex)
