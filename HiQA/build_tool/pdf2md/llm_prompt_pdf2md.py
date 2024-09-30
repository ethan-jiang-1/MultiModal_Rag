PROMPT_GET_CONTENT="""
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

PROMPT_MD_CORRECT = """
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

USER_PROMPT_MD_SELF_CORRECT = """
# Task Description  
Your task is to correct and restore Markdown content generated from a PDF file through a PDF-to-Markdown conversion tool. Due to the OCR (Optical Character Recognition) process involved, the Markdown content may exhibit various issues such as:  
- **Disrupted information flow**: Text order or structure might not match the original PDF.  
- **Formatting errors**: Markdown syntax may be broken or inconsistent.  
- **Semantic inaccuracies**: Words, phrases, or sentences may be misrecognized or misplaced.  
- **Redundant or irrelevant text**: Extraneous elements, such as page numbers or artifacts from the conversion, may be present.  

Your primary goal is to restore the content to accurately reflect the original PDF's intent, meaning, and structure while improving readability.

---

## Input Content  
Enclosed within ```:  
```
{markdown}
```

---

## Correction Guidelines  

1. **Analyze and Infer**  
   - Carefully read the input Markdown to understand the context and intent of the original document.  
   - Identify areas where the information flow or structure has been disrupted.  

2. **Restore Content**  
   - **Reconstruct Logical Flow**: Reorganize the content into a coherent structure that matches the likely intent of the original PDF.  
   - **Correct Markdown Syntax**: Fix any errors or inconsistencies in Markdown formatting.  
   - **Refine Text**: Address OCR misrecognitions, correct typos, and improve semantic clarity.  

3. **Eliminate Redundancies**  
   - Remove irrelevant artifacts, such as page number references, blank spaces, or conversion notes that do not belong in the final document.  

4. **Standardize Formatting for Contracts**  
   - If the document resembles a contract, rename generic terms like "Party A" and "Party B" to user-friendly terms such as "Party 1" and "Party 2."  

5. **Preserve Original Intent**  
   - Ensure the corrected content reflects the meaning, structure, and purpose of the original PDF without adding or omitting critical information.  

---

## Output Format  

Provide your response in the following JSON structure:  
```json  
{
    "reasoning": "<Explain the steps taken to restore the content, including how you addressed disrupted flow, errors, or redundancies.>",
    "content": "<Corrected Markdown content in valid Markdown syntax.>"
}
"""

SYSTEM_PROMPT_MD_SELF_CORRECT = """
You are an expert assistant skilled in processing Markdown content generated from OCR-converted PDF files. Your task is to:
1. **Restore Content**: Correct errors, rebuild logical flow, and fix disrupted information caused by OCR conversion.  
2. **Ensure Clarity**: Maintain readability and coherence while adhering to Markdown syntax.  
3. **Follow Instructions**: Adhere strictly to any guidelines provided in the User Prompt, such as removing irrelevant text or renaming contract parties.
Focus on restoring the original intent and structure of the document without unnecessary changes. Deliver accurate, well-organized Markdown content, along with reasoning for your corrections.
"""