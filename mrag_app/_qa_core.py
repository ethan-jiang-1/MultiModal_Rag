from dotenv import load_dotenv 
import logging
import json
import random
from pprint import pformat
import rich
import html

load_dotenv()

from mrag_vdb.utils.util_logging import setup_logger_handlers, get_logger_progress
from mrag_vdb.query.query2section_raw import query2section_raw_on_multiple_collection
from mrag_vdb.query.query2section_reranked import query2sortedsections_reranked
from mrag_vdb.knowledge.query2knowledge import gen_answer_from_knowledge_snippets, form_knowledge_snippets
from mrag_vdb.knowledge.query2knowledge import query_rewerite, compose_rag_answer
from mrag_vdb.common.runtime_settings import KbNameSel

setup_logger_handlers()
logger_prg = get_logger_progress()

def do_core_query(user_input, kb_name=None, limit=10):
    if kb_name is None:
        kb_name = KbNameSel.get_kbname()

    logging.info(f"do_core_query: {user_input} on {kb_name}")
    ret_dict = {}

    logger_prg.info(f"step1.0: 10%: 选择知识库:{kb_name}")

    req_id = random.randint(10000, 99999)

    logging.info(f"\n\n\n***** REQ{req_id} started ****")
    logging.info(f"##do_core_query: {user_input} on {kb_name}")
    ret_dict["req_id"] = req_id
    ret_dict["user_input"] = user_input
    ret_dict["response_answer"] = ""
    ret_dict["lst_source_names"] = []
    ret_dict["lst_source_title"] = []
    ret_dict["lst_image_names"] = []
    ret_dict["lst_image_titles"] = []

    logger_prg.info("step1.1: 20%: 准备查询(改写)")
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
    knowledge_snippets = form_knowledge_snippets(scored_sections_reranked)

    logger_prg.info("step4.0: 60%: 组织回答#综合知识(文本)")
    resp = gen_answer_from_knowledge_snippets(query, knowledge_snippets) 
    if resp is None:
        ret_dict["response_answer"] = "ERROR: llm response is None"
        ret_dict["debug_resp"] = resp
        logging.error(f"##ret_dict(e1): {ret_dict}")
        return ret_dict 

    logger_prg.info("step5.0: 80%: 组织回答#综合知识(图像)")
    rag_answer = compose_rag_answer(query, resp, scored_sections_reranked) 
    if rag_answer is None:
        ret_dict["response_answer"] = "ERROR: llm response is None"
        ret_dict["debug_resp"] = resp
        logging.error(f"##ret_dict(e1): {ret_dict}")
        return ret_dict 

    sub_text = html.escape(rag_answer.answer_referenced.replace("\n", " "))
    sub_text = f"\n\n\n<sub>{sub_text}</sub>\n"

    ret_dict["user_input"] = user_input
    ret_dict["rag_answer"] = rag_answer.model_dump()
    ret_dict["response_answer"] = rag_answer.answer + sub_text
    ret_dict["response_answer_referenced"] = rag_answer.answer_referenced
    ret_dict["lst_source_names"] = rag_answer.source_names
    ret_dict["lst_source_titles"] = rag_answer.source_titles
    ret_dict["lst_source_pnames"] = rag_answer.source_pnames
    ret_dict["lst_image_names"] = rag_answer.image_names
    ret_dict["lst_image_titles"] = rag_answer.image_titles
    ret_dict["lst_image_pnames"] = rag_answer.image_pnames

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
