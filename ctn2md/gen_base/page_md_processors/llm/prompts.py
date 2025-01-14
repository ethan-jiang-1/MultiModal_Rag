"""
LLM提示词管理
"""

def get_document_analysis_prompt(marked_content: str) -> str:
    """生成文档分析提示词
    
    Args:
        marked_content: 带标记的文档内容
        
    Returns:
        完整的提示词
    """
    return f"""请分析这份文档，识别需要处理的内容。
需要输出可执行的动作指令，每个动作都需要精确的页号和行号。

文档内容：
{marked_content}

请识别以下内容并按格式返回：
1. 需要删除的页眉页脚
2. 需要合并的跨页表格

返回格式：
{{
    "remove_actions": [
        {{
            "page": 1,                    # 具体页号
            "lines": [1, 2],              # 具体需要删除的行号
            "reason": "页眉"              # 删除原因：页眉/页脚
        }}
    ],
    "merge_actions": [
        {{
            "type": "table",              # 合并类型：表格/段落
            "pages": [1, 2],              # 涉及的具体页面
            "line_ranges": {{             # 每页需要合并的具体行范围
                "1": [
                    {{
                        "start": 15,
                        "end": 20
                    }}
                ],
                "2": [
                    {{
                        "start": 1,
                        "end": 5
                    }}
                ]
            }}
        }}
    ]
}}

注意：
1. 所有行号必须是实际的行号（参考每行前的 [Px-Lx] 标记）
2. 页号必须是实际的页号（参考 <<<< 第x页 >>>> 标记）
3. 返回的JSON必须符合上述格式，以便程序处理
""" 