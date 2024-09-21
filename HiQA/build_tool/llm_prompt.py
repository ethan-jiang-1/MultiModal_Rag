get_content_prompt="""
###You're an expert at getting content.You will receive a piece of text content that contains a watermark. 
###Content to be analyzed:
{Content}
###Your task is:
1. Remove all whitespace characters (including spaces, tabs etc.).Keep line wrapping preceded by a numeric header. For complete content, line wrapping is not possible.
2. Identify and remove the watermark, which is typically a specific character or string that repeats.
3. Return the processed text content.
<example>
###Content to be analyzed:A6667 A6667 A 6 6 6 7 
# 2.3 相关文件及在项目进行过程中需由甲方提供的其它文件，将被认为是正确、精确并在各方面满
足要求的。如果在接到相关文件及甲方提供的其他文件后 一周 内，乙方未提出书面异议的，
则视为甲方提供的全部文件满足要求。
#2.4 本合同工作地点为甲方指定工作场地，具体时间应结合项目需求按 附件1中第 4 条“项目进
度” （以下简称“时间计划”）执行。甲方有权依据项目进展和业务需求适时调整工作地点，
乙方应全力配合，并依据合同工作要求和甲方的正式通知在指定期限内指派合格专项人员至甲
###output:2.3 相关文件及在项目进行过程中需由甲方提供的其它文件，将被认为是正确、精确并在各方面满足要求的。如果在接到相关文件及甲方提供的其他文件后 一周 内，乙方未提出书面异议的，则视为甲方提供的全部文件满足要求。
2.4 本合同工作地点为甲方指定工作场地，具体时间应结合项目需求按 附件1中第 4 条“项目进度” （以下简称“时间计划”）执行。甲方有权依据项目进展和业务需求适时调整工作地点，乙方应全力配合，并依据合同工作要求和甲方的正式通知在指定期限内指派合格专项人员至甲
<example>
###instructions:
1.Watermarks may appear in different forms, such as:
    * Repeated words or phrases
    * Sequences of specific characters
    * Special characters hidden within the text
2.You need to identify the watermark based on the specific context and remove it.
3.Delete the line identifying the number of pages
4.The final returned text content should contain only the original information, without any watermarks or whitespace characters.
5.You can't delete any information except watermarks and whitespace characters
6.A line feed is required after each paragraph in the final content
Your answer should strictly follow the following json format:
{{
    "reasoning": "", // The reasoning steps for getting content.
    "content": "", // The format of the final content is text.
}}
"""

md_correct_prompt = """
### You are tasked with correcting the Markdown content based on the provided text content. The Markdown content may contain errors or inconsistencies that need to be corrected using the information from the text content.

### Content to be analyzed:
{text1}

### Markdown content to be corrected:
{markdown}

Please correct the Markdown content using the information from the text content and output the result.

instructions:
1. **Read the provided text content (`text1`).**
2. **Identify any errors or inconsistencies in the Markdown content (`markdown`).**
3. **Correct the Markdown content using the information from `text1`.**
4. **Ensure that the Markdown format is preserved and only the content is corrected.**
5. **Output the corrected Markdown content.**

**Note:**  
Ensure that the Markdown output is clean, readable, and maintains the original structure and intent of the text content. Do not change the Markdown syntax, only correct the content.

Your answer should strictly follow the following json format:
{{
    "reasoning": "", // The reasoning steps for correcting the content.
    "content": "", // The format of the final content is markdown.
}}
"""

md_self_correct_prompt = """
### Task Description
You are tasked with correcting the given Markdown content. The Markdown content may contain errors or inconsistencies, such as formatting errors, text errors, or irrelevant text. You need to correct these based on the context and semantics of the Markdown content.

### Input Content
{markdown}

### Correction Requirements
1. **Carefully read and analyze the given Markdown content.**
2. **Identify and correct any formatting errors, text errors, or irrelevant text.**
3. **Ensure that the corrected Markdown content maintains the original structure and intent.**
4. **Output the corrected Markdown content.**
5.**Delete the line identifying the number of pages
6.**If the document like a contract, please change the title of Party A and Party B to facilitate use
### Notes
- **Maintain the correctness of the Markdown syntax.**
- **Only correct the content, do not change the Markdown syntax structure.**
- **Ensure that the corrected Markdown content is clear, readable, and semantically correct.**

Your answer should strictly follow the following json format:
{{
    "reasoning": "", // The reasoning steps for correcting the content.
    "content": "", // The format of the final content is markdown.
}}
"""