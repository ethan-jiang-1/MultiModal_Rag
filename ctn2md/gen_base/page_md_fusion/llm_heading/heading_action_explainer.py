"""Heading Action Explainer

This module provides explanation functionality for heading analysis results.
"""
from typing import List, Optional

from ctn2md.gen_base.page_md_fusion.llm_heading.da_schemas_heading import (
    HeadingValidation, HeadingRemoveInfo, HeadingStructureValidation,
    _HeadingWarningInfo, HeadingErrorType, HeadingValidationScope,
    HeadingLevelGapType, HeadingCrossPageIssueType, HeadingHeaderPattern,
    DocumentAnalysisHeading, HeadingInfo, HeadingContext, HeadingRemoveReason
)

class HeadingActionExplainer:
    """Explains heading analysis actions and results."""
    
    def __init__(self, doc_analysis: DocumentAnalysisHeading):
        """Initialize with document analysis results."""
        self.doc_analysis = doc_analysis
        
    def _format_confidence(self, confidence: float) -> str:
        """Format confidence level with description."""
        if confidence >= 0.95:
            return f"{confidence:.2f} (完全确信)"
        elif confidence >= 0.90:
            return f"{confidence:.2f} (高度确信)"
        elif confidence >= 0.85:
            return f"{confidence:.2f} (较为确信)"
        else:
            return f"{confidence:.2f} (基本确信)"
            
    def _explain_heading_validation(self, validation: HeadingValidation) -> str:
        """Generate detailed explanation for heading validation."""
        parts = []
        
        # Validation status
        if validation.is_valid:
            parts.append("✓ 标题有效")
        else:
            parts.append("✗ 标题无效")
            
        # Level information
        if validation.current_level:
            parts.append(f"当前层级: {validation.current_level}")
        if validation.expected_level:
            parts.append(f"期望层级: {validation.expected_level}")
            
        # Error type explanation
        if validation.error_type:
            error_desc = {
                HeadingErrorType.WRONG_LEVEL: "层级错误",
                HeadingErrorType.NEEDS_LEVEL: "需要确定层级",
                HeadingErrorType.NOT_HEADING: "不是标题",
                HeadingErrorType.MISSING: "缺失必要标题",
                HeadingErrorType.WRONG_FORMAT: "格式错误",
                HeadingErrorType.INCONSISTENT: "与文档风格不一致"
            }
            parts.append(f"错误类型: {error_desc[validation.error_type]}")
            
        # Validation scope
        scope_desc = {
            HeadingValidationScope.SINGLE_PAGE: "单页判断",
            HeadingValidationScope.CROSS_PAGE: "跨页判断"
        }
        parts.append(f"判断范围: {scope_desc[validation.validation_scope]}")
        
        # Context information
        if validation.context:
            ctx = validation.context
            if ctx.prev_heading_id:
                prev_heading = self._get_heading_by_id(ctx.prev_heading_id)
                if prev_heading:
                    parts.append(f"上文标题: {prev_heading.content[:10]}...")
                    parts.append(f"上文层级: {prev_heading.current_level}")
            if ctx.is_cross_page:
                parts.append("跨页相关")
                
        # Confidence
        parts.append(f"置信度: {self._format_confidence(validation.confidence)}")
        
        return "\n".join(parts)
        
    def _explain_remove_info(self, remove: HeadingRemoveInfo) -> str:
        """Generate explanation for header/footer removal."""
        parts = []
        
        # Basic information
        parts.append(f"页码: {remove.page}")
        parts.append(f"行号: {', '.join(map(str, remove.lines))}")
        
        # Removal reason
        reason_desc = {
            HeadingRemoveReason.HEADER: "页眉",
            HeadingRemoveReason.FOOTER: "页脚",
            HeadingRemoveReason.DUPLICATE: "重复内容",
            HeadingRemoveReason.NOISE: "噪声内容",
            HeadingRemoveReason.SEPARATOR: "分隔符"
        }
        parts.append(f"类型: {reason_desc[remove.reason]}")
        
        # Pattern description
        pattern_desc = {
            HeadingHeaderPattern.TITLE_PAGE: "标题页",
            HeadingHeaderPattern.TITLE_NUMBER: "标题+页码",
            HeadingHeaderPattern.NUMBER_ONLY: "仅页码",
            HeadingHeaderPattern.CHAPTER_TITLE: "章节标题",
            HeadingHeaderPattern.CUSTOM: "自定义格式"
        }
        parts.append(f"模式: {pattern_desc[remove.pattern]}")
        
        # Confidence
        parts.append(f"置信度: {self._format_confidence(remove.confidence)}")
        
        return "\n".join(parts)
        
    def _explain_structure_validation(self, struct: HeadingStructureValidation) -> str:
        """Generate explanation for structure validation results."""
        parts = []
        
        # Overall status
        if struct.is_valid:
            parts.append("✓ 文档结构有效")
        else:
            parts.append("✗ 文档结构存在问题")
            
        # Missing levels
        if struct.missing_levels:
            parts.append("\n缺失的层级:")
            for level in struct.missing_levels:
                parts.append(f"  - 层级 {level}")
                
        # Level gaps
        if struct.level_gaps:
            parts.append("\n层级间断:")
            gap_desc = {
                HeadingLevelGapType.SKIP_LEVEL: "跳过层级",
                HeadingLevelGapType.WRONG_ORDER: "顺序错误",
                HeadingLevelGapType.MIXED_FORMAT: "格式混乱",
                HeadingLevelGapType.INVALID_NESTING: "嵌套无效"
            }
            for gap in struct.level_gaps:
                parts.append(f"  - {gap_desc[gap.type]}")
                parts.append(f"    从层级 {gap.start_level} 到 {gap.end_level}")
                parts.append(f"    在第 {gap.page} 页")
                
        # Cross-page issues
        if struct.cross_page_issues:
            parts.append("\n跨页问题:")
            issue_desc = {
                HeadingCrossPageIssueType.BREAK_HEADING: "标题跨页",
                HeadingCrossPageIssueType.LOST_CONTEXT: "上下文丢失"
            }
            for issue in struct.cross_page_issues:
                parts.append(f"  - {issue_desc[issue.type]}")
                parts.append(f"    从第 {issue.start_page} 页到第 {issue.end_page} 页")
                parts.append(f"    影响标题索引: {issue.heading_index}")
                
        return "\n".join(parts)
        
    def _explain_warnings(self, warnings: List[_HeadingWarningInfo]) -> str:
        """Generate explanation for warnings."""
        if not warnings:
            return "无警告信息"
            
        parts = ["警告信息:"]
        for warn in warnings:
            parts.append(f"\n- 类型: {'结构' if warn.type == 'structure' else '格式'}")
            parts.append(f"  页码: {warn.page}")
            parts.append(f"  行号: {', '.join(map(str, warn.lines))}")
            parts.append(f"  说明: {warn.message}")
            
        return "\n".join(parts)
        
    def _explain_context(self, ctx: HeadingContext) -> List[str]:
        """解释上下文信息"""
        parts = []
        if ctx.prev_heading_id:
            prev_heading = self._get_heading_by_id(ctx.prev_heading_id)
            if prev_heading:
                parts.append(f"上文标题: {prev_heading.content[:10]}...")
                parts.append(f"上文层级: {prev_heading.current_level}")
        if ctx.is_cross_page:
            parts.append("跨页相关")
        return parts

    def _get_heading_by_id(self, heading_id: str) -> Optional[HeadingInfo]:
        """根据ID获取标题信息"""
        for heading in self.doc_analysis.headings:
            if heading.heading_id == heading_id:
                return heading
        return None
        
    def explain(self) -> str:
        """Generate complete explanation for document analysis results."""
        parts = []
        
        # Document overview
        parts.append(f"文档概览:")
        parts.append(f"总页数: {self.doc_analysis.total_pages}")
        parts.append(f"标题数: {self.doc_analysis.total_headings}")
        
        # Headings
        if self.doc_analysis.headings:
            parts.append("\n标题分析:")
            for idx, heading in enumerate(self.doc_analysis.headings, 1):
                parts.append(f"\n标题 {idx}:")
                parts.append(f"页码: {heading.page}")
                parts.append(f"行号: {heading.line}")
                parts.append(f"内容: {heading.content}")
                if heading.current_level:
                    parts.append(f"当前层级: {heading.current_level}")
                if heading.expected_level:
                    parts.append(f"期望层级: {heading.expected_level}")
                parts.append(f"置信度: {self._format_confidence(heading.confidence)}")
                parts.append("\n验证结果:")
                parts.append(self._explain_heading_validation(heading.validation))
                
        # Remove actions
        if self.doc_analysis.remove_infos:
            parts.append("\n移除项分析:")
            for remove in self.doc_analysis.remove_infos:
                parts.append("\n" + self._explain_remove_info(remove))
                
        # Structure validation
        parts.append("\n结构分析:")
        parts.append(self._explain_structure_validation(self.doc_analysis.structure_validation))
        
        # Warnings
        parts.append("\n" + self._explain_warnings(self.doc_analysis.warnings))
        
        return "\n".join(parts) 