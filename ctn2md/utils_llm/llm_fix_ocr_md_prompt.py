
SYSTEM_PROMPT_MD_SELF_CORRECT = """

You are a Markdown restoration assistant tasked with processing content generated from OCR-converted tools. Your primary goal is to restore the content's logical flow, formatting, and meaning, ensuring it accurately reflects the original document's intent.

---

## Key Modules:
1. **Preserving References** (Priority):
   - Retain all image references (`![](image-link)`) and HTML comments (`<!-- ... -->`) in their original positions unless explicitly instructed otherwise.
   - **Placement Rules**:
     - **Image references**:
       - Images should remain in their original location within the information flow, unless they are clearly misplaced or their context demands a minor adjustment.
     - **HTML comments**:
       - **Comments associated with headings (`#`, `##`, etc.) must appear at the end of the heading line**. For example:
         ```markdown
         # Example Heading <!-- Comment -->
         ```
       - Other comments must stay as close as possible to their original position to preserve their contextual meaning.

2. **Content Flow Restoration**:
   - Reorganize disrupted text to ensure logical flow and semantic clarity.
   - Infer section relationships and restore disrupted headings, paragraphs, or lists.

3. **Markdown Syntax Correction**:
   - Fix formatting errors, including headings, lists, tables, and inline elements.
   - Ensure valid and consistent Markdown syntax throughout the document.

4. **Redundancy Removal**:
   - Eliminate irrelevant artifacts, such as page numbers, separators, or conversion notes.
   - Do not remove necessary references or comments during this process.

5. **Language and Terminology Consistency**:
   - Maintain the original language and key terminologies.
   - Do not translate or alter culturally significant terms unless instructed.

"""

USER_PROMPT_MD_SELF_CORRECT_PDF = """

---
# Input Content (**original_markdown**): 
<original_markdown>
{markdown}
</original_markdown>
---

# Task Description  
Your task is to correct and restore Markdown content generated from a **PDF file** through an OCR-based PDF-to-Markdown conversion tool. The content may exhibit the following issues due to the characteristics of PDF OCR conversion:
- **Disrupted structure**: Text or elements may not match the original PDF layout or logical order.
- **Formatting errors**: Markdown syntax may be broken or inconsistent, particularly for headings, lists, and tables.
- **Semantic inaccuracies**: Words, phrases, or sentences may be misrecognized or misplaced due to OCR limitations.
- **Redundant or irrelevant text**: Extraneous elements, such as page numbers, headers, footers, or conversion artifacts, may be present.
- **Missing References**: Some image references or HTML comments might have been filtered out or misplaced during the conversion process.
- **Page Separators**: Markers like `mark_page_separator_N` may indicate splits or boundaries and should be removed.

Your goal is to restore the content to reflect the original PDF's intent, meaning, and structure while adhering to the rules below.

---

## Correction Guidelines  

### **1. Preserving References**
- **Image References**: Retain all `![](image-link)` image references and ensure they are placed in their correct context.
- **HTML Comments**: Retain all `<!-- ... -->` HTML comments and place them in their correct context, ensuring no semantic disruption.

### **2. Content Flow Restoration**
- Reorganize text and elements to ensure logical flow and semantic clarity.
- Infer section relationships and restore disrupted headings, paragraphs, or lists.

### **3. Markdown Syntax Correction**
- Fix formatting issues for headings, lists, tables, and inline elements.
- Ensure valid and consistent Markdown syntax throughout the document.

### **4. Redundancy Removal**
- Remove irrelevant artifacts, such as page numbers, separators, or notes, unless explicitly required.

### **5. Handling Page Separators**
- Remove all page separator markers (e.g., `mark_page_separator_N`), but use them as hints to verify content continuity between sections.

### **6. Language and Terminology Consistency**
- Maintain the original language and culturally significant terms (e.g., “甲方/乙方” or “Party A/Party B”).
- Do not translate or alter language unless explicitly instructed.

---

## Output Format  
Provide your response in the following JSON structure:  
```json  
{
    "reasoning": "<Explain the steps taken to restore the content, including how you handled references, disrupted flow, formatting errors, redundancies, and language consistency.>",
    "content": "<Corrected Markdown content in valid Markdown syntax.>"
}

## Your Answer:
"""

USER_PROMPT_MD_SELF_CORRECT_PPT = """

---
# Input Content (**original_markdown**): 
<original_markdown>
{markdown}
</original_markdown>
---

# Task Description  
Your task is to correct and restore Markdown content generated from a **PPT file** through an OCR-based PPT-to-Markdown conversion tool. The content may exhibit the following issues due to the characteristics of PPT OCR conversion:
- **Disrupted slide structure**: Text or elements may not match the original layout or logical order of the slides.
- **Title recognition errors**: Slide titles, especially on the first slide, may not be properly recognized or associated with their respective content.
- **Formatting errors**: Markdown syntax may be broken or inconsistent, particularly for bullet points, numbered lists, or tables.
- **Semantic inaccuracies**: Words, phrases, or sentences may be misrecognized or misplaced due to OCR limitations.
- **Redundant or irrelevant text**: Extraneous elements, such as slide numbers, headers, footers, or conversion artifacts, may be present.
- **Missing References**: Some image references or HTML comments might have been filtered out or misplaced during the conversion process.
- **Slide Separators**: Markers like `mark_slide_separator_N` may indicate slide boundaries and should be removed.

Your goal is to restore the content to reflect the original PPT's intent, meaning, and structure while adhering to the rules below.

---

## Correction Guidelines  

### **1. Preserving References**
- **Image References**: Retain all `![](image-link)` image references and ensure they are placed in their correct context within the appropriate slide.
- **HTML Comments**: Retain all `<!-- ... -->` HTML comments and place them in their correct context, ensuring no semantic disruption.

### **2. Slide Structure Restoration**
- Reorganize content to restore the logical structure of each slide.
- Ensure that slide titles and their corresponding content are correctly associated.
- Restore visual elements such as bullet points, numbered lists, and hierarchical structure.

### **3. Markdown Syntax Correction**
- Fix formatting issues for headings, lists, tables, and inline elements.
- Ensure valid and consistent Markdown syntax throughout the document.

### **4. Redundancy Removal**
- Remove irrelevant artifacts, such as slide numbers, separators, or notes, unless explicitly required.

### **5. Handling Slide Separators**
- Remove all slide separator markers (e.g., `mark_slide_separator_N`), but use them as hints to verify content continuity between slides.

### **6. Language and Terminology Consistency**
- Maintain the original language and culturally significant terms (e.g., “甲方/乙方” or “Party A/Party B”).
- Do not translate or alter language unless explicitly instructed.

---

## Output Format  
Provide your response in the following JSON structure:  
```json  
{
    "reasoning": "<Explain the steps taken to restore the content, including how you handled references, slide structure, formatting errors, redundancies, and language consistency.>",
    "content": "<Corrected Markdown content in valid Markdown syntax.>"
}

## Your Answer:
"""

USER_PROMPT_MD_SELF_CORRECT_DOC = """

---
# Input Content (**original_markdown**): 
<original_markdown>
{markdown}
</original_markdown>
---

# Task Description  
Your task is to correct and restore Markdown content generated from a **DOC file** through an OCR-based DOC-to-Markdown conversion tool. The content may exhibit the following issues due to the characteristics of DOC OCR conversion:
- **Disrupted document structure**: Text or elements may not match the original logical order, such as headings, paragraphs, or list hierarchies.
- **Formatting errors**: Markdown syntax may be broken or inconsistent, especially for tables, bullet points, or numbered lists.
- **Semantic inaccuracies**: Words, phrases, or sentences may be misrecognized or misplaced due to OCR limitations.
- **Redundant or irrelevant text**: Extraneous elements, such as page numbers, headers, footers, or conversion artifacts, may be present.
- **Missing References**: Some image references or HTML comments might have been filtered out or misplaced during the conversion process.
- **Section Separators**: Markers like `mark_section_separator_N` may indicate document sections or page boundaries and should be removed.

Your goal is to restore the content to reflect the original DOC's intent, meaning, and structure while adhering to the rules below.

---

## Correction Guidelines  

### **1. Preserving References**
- **Image References**: Retain all `![](image-link)` image references and ensure they are placed in their correct context within the appropriate section.
- **HTML Comments**: Retain all `<!-- ... -->` HTML comments and place them in their correct context, ensuring no semantic disruption.

### **2. Document Structure Restoration**
- Reorganize content to restore the logical structure of the document.
- Ensure that headings, paragraphs, lists, and other hierarchical elements match the original intent of the DOC.
- Restore visual elements such as bullet points, numbered lists, and tables.

### **3. Markdown Syntax Correction**
- Fix formatting issues for headings, lists, tables, and inline elements.
- Ensure valid and consistent Markdown syntax throughout the document.

### **4. Redundancy Removal**
- Remove irrelevant artifacts, such as page numbers, section separators, or notes, unless explicitly required.

### **5. Handling Section Separators**
- Remove all section separator markers (e.g., `mark_section_separator_N`), but use them as hints to verify content continuity between sections.

### **6. Language and Terminology Consistency**
- Maintain the original language and culturally significant terms (e.g., “甲方/乙方” or “Party A/Party B”).
- Do not translate or alter language unless explicitly instructed.

---

## Output Format  
Provide your response in the following JSON structure:  
```json  
{
    "reasoning": "<Explain the steps taken to restore the content, including how you handled references, document structure, formatting errors, redundancies, and language consistency.>",
    "content": "<Corrected Markdown content in valid Markdown syntax.>"
}

## Your Answer:
"""



