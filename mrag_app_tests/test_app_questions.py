#import pytest
from mrag_app._app_questions import QUESTION_LIST_MRAG, QUESTION_LIST_PAPERS

def test_question_list_mrag_format():
    """测试MRAG问题列表的格式"""
    # 确保是字符串类型
    assert isinstance(QUESTION_LIST_MRAG, str)
    
    # 确保包含标题
    assert "### 问题列表：" in QUESTION_LIST_MRAG
    
    # 将问题列表分割成行
    lines = QUESTION_LIST_MRAG.strip().split("\n")
    questions = [line for line in lines if line.strip() and line.strip()[0].isdigit()]
    
    # 测试问题格式
    for question in questions:
        # 检查问题格式：数字. 问题内容
        assert question.strip()[0].isdigit(), f"问题应该以数字开头: {question}"
        assert ". " in question, f"问题格式应该是'数字. 问题内容': {question}"
        
        # 检查问题内容不为空
        question_content = question.split(". ", 1)[1]
        assert len(question_content.strip()) > 0, f"问题内容不能为空: {question}"

def test_question_list_mrag_content():
    """测试MRAG问题列表的内容"""
    # 确保包含特定的关键问题
    key_questions = [
        "前后座椅H点参考距离是多少？",
        "椅背板与旁侧板的保留运动间隙是多少？",
        "靠背STO间隙要求是什么？",
        "主管的培训课程涉及什么"
    ]
    
    for question in key_questions:
        assert question in QUESTION_LIST_MRAG, f"问题列表应该包含关键问题: {question}"

def test_question_list_papers_format():
    """测试论文问题列表的格式"""
    # 确保是字符串类型
    assert isinstance(QUESTION_LIST_PAPERS, str)
    
    # 确保包含标题
    assert "### 问题列表：" in QUESTION_LIST_PAPERS
    
    # 将问题列表分割成行
    lines = QUESTION_LIST_PAPERS.strip().split("\n")
    questions = [line for line in lines if line.strip() and line.strip()[0].isdigit()]
    
    # 测试问题格式
    for question in questions:
        # 检查问题格式：数字. 问题内容
        assert question.strip()[0].isdigit(), f"问题应该以数字开头: {question}"
        assert ". " in question, f"问题格式应该是'数字. 问题内容': {question}"
        
        # 检查问题内容不为空
        question_content = question.split(". ", 1)[1]
        assert len(question_content.strip()) > 0, f"问题内容不能为空: {question}"

def test_question_list_papers_content():
    """测试论文问题列表的内容"""
    # 确保包含特定的关键问题
    assert "什么是神经网络？" in QUESTION_LIST_PAPERS, "问题列表应该包含关于神经网络的问题"

def test_question_lists_independence():
    """测试两个问题列表的独立性"""
    # 确保两个列表是不同的
    assert QUESTION_LIST_MRAG != QUESTION_LIST_PAPERS
    
    # 提取MRAG问题
    mrag_questions = [line.split(". ", 1)[1].strip() 
                     for line in QUESTION_LIST_MRAG.strip().split("\n") 
                     if line.strip() and line.strip()[0].isdigit()]
    
    # 提取Papers问题
    papers_questions = [line.split(". ", 1)[1].strip() 
                       for line in QUESTION_LIST_PAPERS.strip().split("\n") 
                       if line.strip() and line.strip()[0].isdigit()]
    
    # 确保没有重复的问题
    for mrag_q in mrag_questions:
        assert mrag_q not in papers_questions, f"问题在两个列表中重复出现: {mrag_q}"

def test_question_numbering():
    """测试问题编号的连续性"""
    def get_question_numbers(question_list):
        numbers = []
        for line in question_list.strip().split("\n"):
            if line.strip() and line.strip()[0].isdigit():
                num = int(line.split(".")[0])
                numbers.append(num)
        return numbers
    
    # 测试MRAG问题编号
    mrag_numbers = get_question_numbers(QUESTION_LIST_MRAG)
    assert mrag_numbers == list(range(1, len(mrag_numbers) + 1)), "MRAG问题编号应该连续"
    
    # 测试Papers问题编号
    papers_numbers = get_question_numbers(QUESTION_LIST_PAPERS)
    assert papers_numbers == list(range(1, len(papers_numbers) + 1)), "Papers问题编号应该连续" 