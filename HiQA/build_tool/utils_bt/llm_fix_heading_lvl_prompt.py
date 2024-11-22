
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
根据用户提供的原始标题数据 (fhl_org)，生成修正后的结构化映射（fhl_map）。分析标题含义及层级关系，以生成专业、清晰、结构合理的 TOC，便于后续替换和使用。

### fhl_org 结构说明
输入数据 (fhl_org) 包括以下内容：
- `org_doc_title` (string): 文档来源文件名，通常从文件名提取， 不要参与TOC 的标题。
- `org_first_line` (string): 文档正文的第一行，可是标题，也可能是正文内容，酌情考虑。
- `org_heading_lines` (list of turples: string as heading and count of word under the heading ): 提取的标题列表和这标题下字符数，需根据内容生成合理的层级映射。

**现有用户的原始标题数据 (fhl_org) (JSON格式)如下**:
{fhl_headings_json_str}

---

## 生成填写指南

### fhl_map 生成要求

1. **文档标题和标题行映射**：
   - `org_heading_lines`: 必须逐行生成映射，确保每行都被清晰映射，映射结果不多不少。
   - `org_doc_title`: 不要参与做标题，只是一个辅助构造TOC的参考内容而已。
   - 顶部内容用 heading 1， 即 `# `开始为第一层。 

2. **first_line_map**：
   - 如果 `org_first_line` 是有意义的标题，应生成映射，映射可以是 Markdown 标题或 ** ** 粗体（适用于不占据 TOC 的情况）。
   - 映射需包含以下字段：
     - `original_line`: org_first_line
     - `mapped_line`: 修正后的标题行。
     - `level`: 标题层级，或 `null` 如果映射为非标题格式（如 ** **）。
     - `reasoning`: 修正思路。

3. **heading_lines_map**：
   - 为 `org_heading_lines` 的每一行生成映射，格式同 `first_line_map`。 映射格式类似如下
   - 映射需包含以下字段：
     - `original_line`: org_heading_line
     - `mapped_line`: 修正后的标题行。
     - `level`: 标题层级，或 `null` 如果映射为非标题格式（如 ** **）。
     - `reasoning`: 修正思路。
   - 支持映射为 Markdown 标题或 ** ** 粗体，便于生成合理的 TOC。

4. **全局修正逻辑**：
   - 提供 `reasoning` 字段，说明修正逻辑及生成结果的整体思考。

5. **new_heading_lines**:
   - 和 ** org_heading_lines ** 数量一摸一样多，完全从org_heading_lines逐一能从旧的映射到新的。
   - 提供最后整理好的heading来容易看出新的TOC。

### 注意事项
A. 所有映射需逐行生成，确保 `org_heading_lines` 和 `org_first_line` 的内容不多不少。

B. `org_first_line` 可映射为 Markdown 标题或 ** ** 粗体，依据其内容的重要性。

C. `org_doc_title` 可映射为文档最高级标题，或保留为背景信息。

D. 映射结果需符合 TOC 目标，确保层级清晰、结构合理，支持直接替换原文。

---

**最终 JSON 输出格式**：
{
  "org_doc_title": "string",  // 原始文档的标题。
  "org_first_line": "string",  // Markdown 文档的第一行内容。
  "org_heading_lines": [  // 文档中的所有标题行。
    "string",  // 第一个标题行。
    "string",  // 第二个标题行。
    "... (更多标题行)"  // 其他标题行。
  ],
  "mapped_heading_lines": [  // 带编号的新标题行列表。
    "string",  // 编号后的第一个标题行。
    "string",  // 编号后的第二个标题行。
    "... (更多标题行)"  // 更多编号后的标题行。
  ]，
  "first_line_map": {  // 第一行的映射信息。
    "original_line": "string (original_first_line)",  // 原始标题行。
    "mapped_line": "string",  // 第一行内容的映射结果。
    "level": "integer or null",  // 层级，若不是标题则为 null。
    "reasoning": "string"  // 对映射结果的解释。
  },
  "heading_lines_map": [  // 所有标题的映射信息列表。
    {
      "original_line": "string (original_line)",  // 原始标题行。
      "mapped_line": "string",  // 标题映射后的内容。
      "level": "integer or null",  // 标题层级，例如 1 表示 `#`，2 表示 `##`，依此类推。
      "reasoning": "string"  // 映射结果的推理解释。
    },
    {
      "original_line": "string (original_line)",  // 第二个标题行。
      "mapped_line": "string",  // 第二个标题行的映射结果。
      "level": "integer or null",  // 第二个标题行的层级。
      "reasoning": "string"  // 映射结果的推理解释。
    },
    "... (更多映射)"  // 更多标题的映射信息。
  ],
  "reasoning": "string",  // 全局推理逻辑，用于解释如何映射标题和内容。
}


## Your Answer:
"""