from typing import Optional

def _strip_ocr_and_triplequotes(content: str) -> str:
    content = content.replace("[ocr_end]", " ")
    content = content.replace("```", "")
    content = content.replace("```", "")
    return content.strip()

def strip_llm_format_markers(content: Optional[str]) -> str:
    """移除 LLM 输出中的外层 markdown 格式标记，保留核心内容。"""
    if not isinstance(content, str):
        return content
    
    content = content.strip()
    if not content:
        return ""
    
    # 处理无换行的情况
    if content.startswith("```") and content.endswith("```"):
        if content.startswith("```markdown"):
            content = content[len("```markdown"):-3].strip()
        else:
            content = content[3:-3].strip()
        return _strip_ocr_and_triplequotes(content)
    
    # 处理有换行的情况
    lines = [line.strip() for line in content.splitlines()]
    
    # 处理开头的标记
    if lines and (lines[0] == "```" or lines[0] == "```markdown"):
        lines.pop(0)
    
    # 处理结尾的标记
    if lines and lines[-1] == "```":
        lines.pop()
    
    content = "\n".join(lines)
    content = content.replace("[ocr_end]", " ")
    
    return _strip_ocr_and_triplequotes(content)

if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "```markdown\nHello World\n```",
        "```\nTest Content\n```",
        "```markdown\nLine 1\nLine 2[ocr_end]\n```",
        "Plain text without markers",
        None
    ]
    
    for test in test_cases:
        result = strip_llm_format_markers(test)
        print(f"\nInput:\n{test}\n\nOutput:\n{result}\n{'-'*50}")
