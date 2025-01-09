import pytest
from mrag_app._app_qa_progress_step import ProgressStep
from mrag_app._rag_response import RagResponse
from mrag_vdb.dto.rag_answer import RagAnswer

@pytest.fixture
def sample_rag_answer():
    """创建一个示例RAG回答，使用真实场景的数据"""
    return RagAnswer(
        answer="椅背板与旁侧板的保留运动间隙应为5mm",
        answer_referenced="根据设计规范文档，椅背板与旁侧板的保留运动间隙要求为5mm，这样可以确保座椅调节时的顺畅运动。",
        source_names=["seat_design_spec.md", "design_guidelines.md"],
        source_titles=["座椅设计规范", "产品设计指南"],
        source_pnames=["/docs/specs/seat_design_spec.md", "/docs/guidelines/design_guidelines.md"],
        image_names=["seat_gap.png", "assembly_view.png"],
        image_titles=["座椅间隙示意图", "装配视图"],
        image_pnames=["/images/diagrams/seat_gap.png", "/images/assembly/assembly_view.png"]
    )

@pytest.fixture
def sample_progress_step():
    """创建一个示例进度步骤，使用实际的进度信息"""
    return ProgressStep(
        step="step2",
        progress=30,
        task_name="召回相关知识(raw)",
        extra_info="检索到2个相关文档"
    )

@pytest.fixture
def sample_rag_response(sample_rag_answer):
    """创建一个示例RAG响应，模拟完整的查询响应"""
    return RagResponse(
        req_id=12345,
        user_input="椅背板与旁侧板的保留运动间隙是多少？",
        rag_answer=sample_rag_answer
    )

@pytest.mark.unit
class TestProgressStep:
    """测试RAG查询进度步骤模型的功能"""
    
    def test_creation_with_all_fields(self, sample_progress_step):
        """测试创建包含所有字段的进度步骤"""
        assert sample_progress_step.step == "step2"
        assert sample_progress_step.progress == 30
        assert sample_progress_step.task_name == "召回相关知识(raw)"
        assert sample_progress_step.extra_info == "检索到2个相关文档"

    def test_creation_without_extra_info(self):
        """测试创建不包含额外信息的进度步骤"""
        step = ProgressStep(
            step="step1",
            progress=10,
            task_name="选择知识库:mrag"
        )
        assert step.step == "step1"
        assert step.progress == 10
        assert step.task_name == "选择知识库:mrag"
        assert step.extra_info is None

@pytest.mark.unit
class TestRagResponse:
    """测试RAG响应模型的核心功能"""
    
    def test_creation(self, sample_rag_response, sample_rag_answer):
        """测试RAG响应的基本创建"""
        assert sample_rag_response.status == "success"
        assert sample_rag_response.error_message is None
        assert sample_rag_response.req_id == 12345
        assert sample_rag_response.user_input == "椅背板与旁侧板的保留运动间隙是多少？"
        assert sample_rag_response.rag_answer == sample_rag_answer
        assert isinstance(sample_rag_response.progress_steps, list)
        assert len(sample_rag_response.progress_steps) == 0

    def test_factory_methods(self, sample_rag_answer):
        """测试RAG响应的工厂方法"""
        # 测试成功工厂方法
        success_response = RagResponse.from_success(
            req_id=12345,
            user_input="椅背板与旁侧板的保留运动间隙是多少？",
            rag_answer=sample_rag_answer
        )
        assert success_response.status == "success"
        assert success_response.error_message is None
        
        # 测试失败工厂方法
        error_response = RagResponse.from_error(
            req_id=12345,
            user_input="椅背板与旁侧板的保留运动间隙是多少？",
            error_msg="知识库连接失败: 无法访问文档存储"
        )
        assert error_response.status == "failed"
        assert error_response.error_message == "知识库连接失败: 无法访问文档存储"
        assert error_response.rag_answer.answer == ""

    def test_progress_tracking(self, sample_rag_response):
        """测试RAG响应的进度跟踪功能"""
        # 添加一个典型的进度序列
        sample_rag_response.add_progress("step1", 10, "选择知识库:mrag")
        sample_rag_response.add_progress("step2", 30, "召回相关知识(raw)", "检索到2个相关文档")
        sample_rag_response.add_progress("step3", 50, "召回相关知识(rerank)", "重排序完成")
        sample_rag_response.add_progress("step4", 70, "生成回答", "正在处理")
        sample_rag_response.add_progress("step5", 100, "完成回答")
        
        assert len(sample_rag_response.progress_steps) == 5
        assert sample_rag_response.progress_steps[0].progress == 10
        assert sample_rag_response.progress_steps[1].extra_info == "检索到2个相关文档"
        assert sample_rag_response.progress_steps[-1].progress == 100

    def test_progress_step_validation(self, sample_rag_response):
        """测试RAG响应进度步骤的验证规则"""
        # 测试进度值的边界
        sample_rag_response.add_progress("step1", 0, "开始查询")
        sample_rag_response.add_progress("step2", 100, "完成查询")
        
        # 验证进度值的范围限制
        with pytest.raises(ValueError, match="Input should be greater than or equal to 0"):
            ProgressStep(step="step3", progress=-1, task_name="无效进度")
        
        with pytest.raises(ValueError, match="Input should be less than or equal to 100"):
            ProgressStep(step="step4", progress=101, task_name="超出范围进度") 