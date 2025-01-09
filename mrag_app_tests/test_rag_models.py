import pytest
from mrag_app._app_qa_progress_step import ProgressStep
from mrag_app._rag_response import RagResponse
from mrag_vdb.dto.rag_answer import RagAnswer

@pytest.fixture
def sample_rag_answer():
    """创建一个示例RAG回答"""
    return RagAnswer(
        answer="测试回答",
        answer_referenced="带引用的回答"
    )

@pytest.fixture
def sample_progress_step():
    """创建一个示例进度步骤"""
    return ProgressStep(
        step="step1",
        progress=50,
        task_name="测试任务",
        extra_info="额外信息"
    )

@pytest.fixture
def sample_rag_response(sample_rag_answer):
    """创建一个示例RAG响应"""
    return RagResponse(
        req_id=12345,
        user_input="测试问题",
        rag_answer=sample_rag_answer
    )

@pytest.mark.unit
class TestProgressStep:
    """测试RAG查询进度步骤模型的功能"""
    
    def test_creation_with_all_fields(self, sample_progress_step):
        """测试创建包含所有字段的进度步骤"""
        assert sample_progress_step.step == "step1"
        assert sample_progress_step.progress == 50
        assert sample_progress_step.task_name == "测试任务"
        assert sample_progress_step.extra_info == "额外信息"

    def test_creation_without_extra_info(self):
        """测试创建不包含额外信息的进度步骤"""
        step = ProgressStep(
            step="step2",
            progress=75,
            task_name="测试任务2"
        )
        assert step.step == "step2"
        assert step.progress == 75
        assert step.task_name == "测试任务2"
        assert step.extra_info is None

@pytest.mark.unit
class TestRagResponse:
    """测试RAG响应模型的核心功能"""
    
    def test_creation(self, sample_rag_response, sample_rag_answer):
        """测试RAG响应的基本创建"""
        assert sample_rag_response.status == "success"
        assert sample_rag_response.error_message is None
        assert sample_rag_response.req_id == 12345
        assert sample_rag_response.user_input == "测试问题"
        assert sample_rag_response.rag_answer == sample_rag_answer
        assert isinstance(sample_rag_response.progress_steps, list)
        assert len(sample_rag_response.progress_steps) == 0

    def test_factory_methods(self, sample_rag_answer):
        """测试RAG响应的工厂方法"""
        # 测试成功工厂方法
        success_response = RagResponse.from_success(
            req_id=12345,
            user_input="测试问题",
            rag_answer=sample_rag_answer
        )
        assert success_response.status == "success"
        assert success_response.error_message is None
        
        # 测试失败工厂方法
        error_response = RagResponse.from_error(
            req_id=12345,
            user_input="测试问题",
            error_msg="测试错误"
        )
        assert error_response.status == "failed"
        assert error_response.error_message == "测试错误"
        assert error_response.rag_answer.answer == ""

    def test_progress_tracking(self, sample_rag_response):
        """测试RAG响应的进度跟踪功能"""
        # 添加进度
        sample_rag_response.add_progress("step1", 25, "任务1", "额外信息1")
        sample_rag_response.add_progress("step2", 50, "任务2")
        sample_rag_response.add_progress("step3", 75, "任务3", "额外信息3")
        
        assert len(sample_rag_response.progress_steps) == 3
        assert sample_rag_response.progress_steps[0].progress == 25
        assert sample_rag_response.progress_steps[1].extra_info is None
        assert sample_rag_response.progress_steps[2].task_name == "任务3"

    def test_progress_step_validation(self, sample_rag_response):
        """测试RAG响应进度步骤的验证规则"""
        # 测试进度值的边界
        sample_rag_response.add_progress("step1", 0, "最小进度")
        sample_rag_response.add_progress("step2", 100, "最大进度")
        
        # 使用 Field 验证规则
        with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
            ProgressStep(step="step3", progress=-1, task_name="负进度")
        
        with pytest.raises(ValueError, match="Input should be less than or equal to 100"):
            ProgressStep(step="step4", progress=101, task_name="超过100的进度") 