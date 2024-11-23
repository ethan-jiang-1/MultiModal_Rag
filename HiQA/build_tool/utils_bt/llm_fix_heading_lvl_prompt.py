
SYSTEM_PROMPT_FIX_HEADING_LVL = """
你是一位Markdown结构优化助手，专注于解析和修正Markdown标题层级。
根据用户提供的原始标题数据 (fhl_org)，生成一个修正后的结构化映射（fhl_map）。你的目标是通过分析文档标题含义和层级关系，生成一个清晰、结构合理的 TOC（目录）。

### 你的任务
1. **修正层级**：分析 `org_doc_title`、`org_first_line` 和 `org_heading_lines`，修正层级缺陷，生成专业的 Markdown 标题层次结构。
2. **映射生成**：
   - `first_line_map`：映射文档第一行，可选择作为标题，或以非标题格式（如粗体等）。
   - `heading_lines_map`：逐行映射标题列表，生成合理的 Markdown 标题或非标题格式（如粗体等）。
3. **生成逻辑**：所有映射需清晰描述原始标题与修正后结果的关系，并提供生成理由（reasoning）。
4. **最终目标**：生成的 fhl_map 应用于替换不规范内容，构建符合文档逻辑和专业标准的 TOC。

确保映射灵活且准确，支持直接替换原始内容，同时满足 Markdown 层级规范。
"""

USER_PROMPT_FIX_HEADING_LVL = """
## 指令
根据用户提供的原始标题数据 (fhl_org)，生成修正后的结构化映射（fhl_map）。分析标题含义及层级关系，修正 Markdown 标题层级缺陷，生成专业、清晰、结构合理的 TOC，便于直接替换原始内容并用于文档结构优化。

---

### fhl_org 结构说明
输入数据 (fhl_org) 包括以下内容：
- `org_doc_title` (string): 文档来源文件名，通常从文件名提取，不参与 TOC 的标题，仅用于参考。
- `org_doc_type` (string): 文档来源类型（如 PDF、PPT、DOC），不同类型的文档可能有不同的标题规则。
- `org_first_line` (string): 文档正文的第一行，可能是标题，也可能是正文内容，需根据其重要性判断是否映射为标题。
- `org_heading_lines` (list of tuples): 提取的标题列表，每个标题包含以下两部分：
  - `heading` (string): 标题内容。
  - `count_of_word` (integer): 该标题下的字符数，用于判断标题是否为装饰性或占位性标题（如字符数为 0）。

**现有用户的原始标题数据 (fhl_org) (JSON格式)如下**:
{fhl_headings_json_str}

---

### fhl_map 生成要求

1. **文档标题和标题行映射**：
   - `org_heading_lines`: 必须逐行生成映射，确保每行都被清晰映射，映射结果与原始行数一致。
   - `org_doc_title`: 不映射为标题，仅作为辅助参考内容，用于构造 TOC。
   - 顶部内容映射为 Heading 1（以 `# ` 开始），作为文档的第一层。

2. **first_line_map**：
   - 映射 `org_first_line`，如果其内容有重要性，应映射为 Markdown 标题或 ** ** 粗体（适用于不占据 TOC 的情况）。
   - 映射字段：
     - `original_line`: `org_first_line` 的原始内容。
     - `mapped_line`: 修正后的标题行。
     - `level`: 标题层级，或 `null`（非标题格式）。
     - `reasoning`: 修正理由和逻辑。

3. **heading_lines_map**：
   - 逐行分析 `org_heading_lines` 的每一行标题，生成对应的映射，映射需结合标题内容、层级含义及 `count_of_word` 的值。
   - 映射需包含以下字段：
     - `original_line`: 对应 `org_heading_lines` 中的原始标题内容。
     - `mapped_line`: 修正后的标题行，需基于标题内容、层级关系和文档逻辑，生成合理的 Markdown 标题或非标题格式（如 ** **）。
     - `level`: 标题层级，或 `null`（若映射为非标题格式，如 ** **）。
     - `reasoning`: 对该标题的修正思路，说明为何选择当前层级或非标题格式。
   - 支持映射为 Markdown 标题（用于 TOC 中的层级结构）或 ** ** 粗体（适用于不占据 TOC 的情况，但需保留内容的场景）。

   **count_of_word 的特殊处理**：
   1. **保留父标题**：
      - 如果某行标题的 `count_of_word` 为 0，但其后续标题的层级低于该标题（即它有子标题），则必须保留该标题在 TOC 中的地位，作为子标题的引导。
   2. **降级为非标题格式**：
      - 如果某行标题的 `count_of_word` 为 0，并且满足以下条件之一：
        - 该标题既不是父标题，也没有后续子标题与之关联。
        - 该标题的同级兄弟标题也有 `count_of_word` 为 0，且它们共同构成装饰性标题。
      - 在以上情况下，可将该标题降级为非标题格式（如 ** **），避免占据 TOC 层级。
   3. **修正理由**：
      - 降级时，需在 `reasoning` 字段中明确指出该标题为何被降级（如它是装饰性标题或无实际内容）。

4. **全局修正逻辑**：
   - 提供 `reasoning` 字段，说明修正逻辑及生成结果的整体思考。

5. **new_heading_lines**：
   - 与 `org_heading_lines` 数量完全一致，逐一从原始标题映射到修正后的标题。
   - 提供整理好的最终标题，方便直观查看新的 TOC。

---

### 注意事项
A. 所有映射需逐行生成，确保 `org_heading_lines` 和 `org_first_line` 的内容不多不少。

B. `org_first_line` 可映射为 Markdown 标题或 ** ** 粗体，依据其内容的重要性。

C. `org_doc_title` 不作为标题映射，只用于提供参考。

D. 映射结果需符合 TOC 目标，确保层级清晰、结构合理，支持直接替换原文。


---

**最终 JSON 输出格式**：
```json
{
  "org_doc_title": "string",  // Original document title, used as a reference but not part of the TOC.
  "org_first_line": "string",  // The first line of the document, possibly a title or introductory content.
  "org_heading_lines": [  // List of all original heading lines extracted from the document.
    "string",  // First original heading line.
    "string",  // Second original heading line.
    "... (additional original heading lines)"  // More heading lines as extracted.
  ],
  "mapped_heading_lines": [  // List of newly processed headings ready for TOC.
    "string",  // Processed version of the first heading line.
    "string",  // Processed version of the second heading line.
    "... (additional processed heading lines)"  // More processed headings.
  ],
  "first_line_map": {  // Mapping information for the document's first line.
    "original_line": "string (original_first_line)",  // The original first line content.
    "mapped_line": "string",  // Processed or mapped version of the first line.
    "level": "integer or null",  // Heading level; null if it is not a heading.
    "reasoning": "string"  // Explanation for the mapping decision.
  },
  "heading_lines_map": [  // List of mappings for all original headings.
    {
      "original_line": "string (original_heading_line)",  // Original heading line content.
      "mapped_line": "string",  // Processed version of the heading line.
      "level": "integer or null",  // Heading level; null for non-heading formats (e.g., bold text).
      "reasoning": "string"  // Explanation for the mapping decision.
    },
    {
      "original_line": "string (original_heading_line)",  // Second original heading line.
      "mapped_line": "string",  // Processed version of the second heading line.
      "level": "integer or null",  // Heading level for the second line.
      "reasoning": "string"  // Explanation for the second line mapping.
    },
    "... (more heading mappings)"  // Additional mappings for remaining headings.
  ],
  "reasoning": "string"  // Global reasoning that explains the overall mapping strategy and document-specific logic.
}


## Your Answer:
"""