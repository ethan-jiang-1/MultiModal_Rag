
SYSTEM_PROMPT_MD_SELF_CORRECT = """You are a Markdown restoration assistant tasked with processing content generated from OCR-converted tool. Your primary responsibilities include:

1. **Restoring Content Flow**: Reorganize disrupted text and ensure logical flow and semantic clarity.  
2. **Fixing Markdown Syntax**: Correct formatting errors and maintain valid Markdown syntax.  
3. **Preserving Image References**: Ensure that all image references in the format `![](image-link)` are retained and placed in their appropriate context without breaking the flow of the content.  
4. **Following User Guidelines**: Adhere strictly to any specific instructions provided in the User Prompt, such as removing redundant text or renaming terms in contracts.  

Deliver accurate, readable, and logically structured Markdown content while maintaining the original intent of the document.
"""

USER_PROMPT_MD_SELF_CORRECT_PDF = """
---
# Input Content (**original_markdown**) 
Enclosed within ```:  
```
{markdown}
```
---

# Task Description  
Your task is to correct and restore Markdown content generated from a PDF file through a PDF-to-Markdown conversion tool. Due to the OCR (Optical Character Recognition) process involved, the Markdown content may exhibit various issues such as:  
- **Disrupted information flow**: Text order or structure might not match the original PDF.  
- **Formatting errors**: Markdown syntax may be broken or inconsistent.  
- **Semantic inaccuracies**: Words, phrases, or sentences may be misrecognized or misplaced.  
- **Redundant or irrelevant text**: Extraneous elements, such as page numbers or artifacts from the conversion, may be present.  
- **Missing Image References**: Some image references in the format `![](image-link)` might have been filtered out or misplaced during the conversion process.  
- **Page Separators**: Markdown may include markers like `mark_page_separator_N`, which indicate page splits and page numbers. These markers are for reference only and should be removed during restoration.

Your primary goal is to restore the content to accurately reflect the original PDF's intent, meaning, and structure while maintaining the original language and terminologies of the Markdown content.

## Correction Guidelines  

1. **Analyze and Infer**  
   - Carefully read the input Markdown to understand the context and intent of the original document.  
   - Identify areas where the information flow or structure has been disrupted.  

2. **Restore Content**  
   - **Reconstruct Logical Flow**: Reorganize the content into a coherent structure that matches the likely intent of the original PDF.  
   - **Correct Markdown Syntax**: Fix any errors or inconsistencies in Markdown formatting.  
   - **Refine Text**: Address OCR misrecognitions, correct typos, and improve semantic clarity.  

3. **Preserve Image References**  
   - Ensure all image references in the format `![](image-link)` are retained.  
   - Place each image reference in the most contextually appropriate position in the content, ensuring the logical flow is not disrupted.  
   - Do not delete or modify any image links unless explicitly instructed.

4. **Handle Page Separators**  
   - Remove all page separator markers such as `mark_page_separator_N`.  
   - Ensure that removing these markers does not disrupt the content's logical flow.  
   - Use the page separator as a hint to verify content continuity between sections.

5. **Maintain Original Language and Terminologies**  
   - Respect the original language (e.g., Chinese or English) of the Markdown content. Do not translate or alter the language.  
   - Retain culturally and contextually significant terms (e.g., “甲方/乙方” in Chinese or “Party A/Party B” in English). Do not replace such terms with generic alternatives (e.g., “Party 1/Party 2”) unless explicitly requested.

6. **Eliminate Redundancies**  
   - Remove irrelevant artifacts, such as page number references, blank spaces, or conversion notes that do not belong in the final document.  

7. **Preserve Original Intent**  
   - Ensure the corrected content reflects the meaning, structure, and purpose of the original PDF without adding or omitting critical information.  

---

## Output Format  

Provide your response in the following JSON structure:  
```json  
{
    "reasoning": "<Explain the steps taken to restore the content, including how you handled disrupted flow, errors, redundancies, image references, page separators, and language consistency.>",
    "content": "<Corrected Markdown content in valid Markdown syntax.>"
}
"""

USER_PROMPT_MD_SELF_CORRECT_PPT = """
---
# Input Content (**original_markdown**) 
Enclosed within ```:  
```
{markdown}
```
---

# Task Description  
Your task is to correct and restore Markdown content generated from a PPT file through a PPT-to-Markdown conversion tool. Due to the OCR (Optical Character Recognition) process and the unique structure of PPT slides, the Markdown content may exhibit various issues such as:  
- **Disrupted slide structure**: Text or elements may not match the original slide layout.  
- **Title recognition errors**: Slide titles, especially on the first slide, may not be properly recognized or associated with their respective content.  
- **Formatting errors**: Markdown syntax may be broken or inconsistent.  
- **Semantic inaccuracies**: Words, phrases, or sentences may be misrecognized or misplaced.  
- **Redundant or irrelevant text**: Extraneous elements, such as slide numbers, presentation notes, or conversion artifacts, may be present.  
- **Missing Image References**: Some image references in the format `![](image-link)` might have been filtered out or misplaced during the conversion process.  
- **Slide Separators**: Markdown may include markers like `mark_slide_separator_N`, which indicate slide splits and slide numbers. These markers are for reference only and should be removed during restoration.

Your primary goal is to restore the content to accurately reflect the original PPT's intent, structure, and visual hierarchy while maintaining the original language and terminologies of the Markdown content.

## Correction Guidelines  

1. **Analyze and Infer**  
   - Carefully read the input Markdown to understand the context, intent, and visual layout of the original slides.  
   - Identify areas where the slide structure or logical flow has been disrupted.  

2. **Restore Content**  
   - **Reconstruct Slide Structure**: Reorganize the content into a coherent structure that matches the likely layout and intent of the original slides. Ensure that slide titles and their corresponding content are properly associated.  
   - **Correct Markdown Syntax**: Fix any errors or inconsistencies in Markdown formatting.  
   - **Refine Text**: Address OCR misrecognitions, correct typos, and improve semantic clarity.  

3. **Preserve Image References**  
   - Ensure all image references in the format `![](image-link)` are retained.  
   - Place each image reference in the most contextually appropriate position within the respective slide's content, ensuring the logical flow is not disrupted.  
   - Do not delete or modify any image links unless explicitly instructed.

4. **Handle Slide Separators**  
   - Remove all slide separator markers such as `mark_slide_separator_N`.  
   - Use the slide separator as a hint to verify content continuity between slides.  
   - Ensure that removing these markers does not disrupt the reconstructed structure of the content.

5. **Title and Key Element Restoration**  
   - Pay special attention to the recognition and placement of slide titles, especially for the first slide, which often serves as the presentation's title page.  
   - Ensure visually significant elements such as headings, bullet points, and key terms are correctly structured and semantically meaningful.

6. **Maintain Original Language and Terminologies**  
   - Respect the original language (e.g., Chinese or English) of the Markdown content. Do not translate or alter the language.  
   - Retain culturally and contextually significant terms (e.g., “甲方/乙方” in Chinese or “Party A/Party B” in English). Do not replace such terms with generic alternatives (e.g., “Party 1/Party 2”) unless explicitly requested.

7. **Eliminate Redundancies**  
   - Remove irrelevant artifacts, such as slide numbers, blank spaces, or conversion notes that do not belong in the final document.  

8. **Preserve Original Intent**  
   - Ensure the corrected content reflects the meaning, structure, and purpose of the original slides without adding or omitting critical information.  

---

## Output Format  

Provide your response in the following JSON structure:  
```json  
{
    "reasoning": "<Explain the steps taken to restore the content, including how you handled disrupted structure, errors, redundancies, image references, slide separators, title recognition, and language consistency.>",
    "content": "<Corrected Markdown content in valid Markdown syntax.>"
}
"""

USER_PROMPT_MD_SELF_CORRECT_DOC = """
---
# Input Content (**original_markdown**) 
Enclosed within ```:  
```
{markdown}
```
---

# Task Description  
Your task is to correct and restore Markdown content generated from a DOC file through a DOC-to-Markdown conversion tool. Due to the OCR (Optical Character Recognition) or conversion process involved, the Markdown content may exhibit various issues such as:  
- **Disrupted document structure**: Text order or hierarchy (e.g., headings, paragraphs, and lists) might not match the original DOC.  
- **Formatting errors**: Markdown syntax may be broken or inconsistent, especially for tables, bullet points, and numbered lists.  
- **Semantic inaccuracies**: Words, phrases, or sentences may be misrecognized or misplaced.  
- **Redundant or irrelevant text**: Extraneous elements, such as page numbers, headers, footers, or conversion notes, may be present.  
- **Missing Image References**: Some image references in the format `![](image-link)` might have been filtered out or misplaced during the conversion process.  
- **Section Separators**: Markdown may include markers like `mark_section_separator_N`, which indicate section splits or page boundaries. These markers are for reference only and should be removed during restoration.  
- **Unordered or Ordered List Errors**: Lists may lose their hierarchy, indentation, or numbering sequence during conversion.

Your primary goal is to restore the content to accurately reflect the original DOC's intent, meaning, and structure while maintaining the original language and terminologies of the Markdown content.

## Correction Guidelines  

1. **Analyze and Infer**  
   - Carefully read the input Markdown to understand the context and intent of the original document.  
   - Identify areas where the document structure, such as headings, paragraphs, or lists, has been disrupted.  

2. **Restore Content**  
   - **Reconstruct Logical Structure**: Reorganize the content into a coherent structure that matches the likely intent of the original DOC. Pay special attention to:
     - Headings and subheadings (`#`, `##`, etc.).
     - Bullet points and numbered lists (`-`, `1.`, etc.).
     - Paragraph flow and section continuity.
   - **Correct Markdown Syntax**: Fix any errors or inconsistencies in Markdown formatting, particularly for tables, lists, and indentation.  
   - **Refine Text**: Address OCR misrecognitions, correct typos, and improve semantic clarity.  

3. **Preserve Image References**  
   - Ensure all image references in the format `![](image-link)` are retained.  
   - Place each image reference in the most contextually appropriate position in the content, ensuring the logical flow is not disrupted.  
   - Do not delete or modify any image links unless explicitly instructed.

4. **Handle Section Separators**  
   - Remove all section separator markers such as `mark_section_separator_N`.  
   - Use the section separator as a hint to verify content continuity between sections.  
   - Ensure that removing these markers does not disrupt the reconstructed structure of the content.

5. **Maintain Original Language and Terminologies**  
   - Respect the original language (e.g., Chinese or English) of the Markdown content. Do not translate or alter the language.  
   - Retain culturally and contextually significant terms (e.g., “甲方/乙方” in Chinese or “Party A/Party B” in English). Do not replace such terms with generic alternatives (e.g., “Party 1/Party 2”) unless explicitly requested.

6. **Handle Tables and Lists**  
   - Ensure all tables are correctly restored in Markdown table syntax, aligning rows and columns accurately.  
   - Correct any unordered or ordered lists to maintain proper indentation and numbering hierarchy.  

7. **Eliminate Redundancies**  
   - Remove irrelevant artifacts, such as page numbers, headers, footers, or conversion notes, that do not belong in the final document.  

8. **Preserve Original Intent**  
   - Ensure the corrected content reflects the meaning, structure, and purpose of the original DOC without adding or omitting critical information.  

---

## Output Format  

Provide your response in the following JSON structure:  
```json  
{
    "reasoning": "<Explain the steps taken to restore the content, including how you handled disrupted structure, errors, redundancies, image references, section separators, list hierarchies, and language consistency.>",
    "content": "<Corrected Markdown content in valid Markdown syntax.>"
}

"""



