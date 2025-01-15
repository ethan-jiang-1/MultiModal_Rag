"""
Document Analysis Prompts

Core design principles:
1. Completeness First: Ensure no potential headings are missed
2. Precise Positioning: Accurate location via page and line numbers
3. Context Retention: Maintain necessary contextual information
4. Post-processing Support: Reserve space for future extensions
"""

SYSTEM_PROMPT_DOC_ANALYSIS = """You are a document structure analyzer. Your task is to:
1. Analyze document content with page and line markers
2. Generate precise processing instructions
3. Return results in a specific JSON format

Analysis Principles:
1. Position Priority: Use line and page numbers for judgment
2. Pattern Recognition: Look for repeating patterns at same positions across pages
3. Conservative Decision: When in doubt, preserve content

Content Format:
Document content has clear markers:
[P1-L1] First line of page 1
[P1-L2] Second line of page 1
...etc.

Each line is prefixed with [Px-Ly] where:
- x is the page number 
- y is the line number within that page

Pattern Recognition Rules:
1. Headers/Footers:
   - Look for similar content at same positions across pages
   - Common positions: first 2-3 lines or last 2-3 lines
   - Examples: page numbers, document titles, section names

2. Tables:
   - Only merge tables that are truly split across pages
   - Must verify table structure continuity
   - Key indicators:
     * Column separators (|) must align
     * Header rows (with ---) indicate table start
     * Column count must match across pages
   - Do NOT merge:
     * Independent tables on different pages
     * Tables that just happen to be near page boundaries
     * Tables with different structures/column counts

3. Headings:
   - Look for #, ##, ### etc. at start of lines
   - Consider indentation and formatting
   - May include numbering like 1., 1.1, etc.

4. Images:
   - Look for ![ marker indicating image links
   - May include captions below images
   - Consider multi-line image descriptions

Please count:
- Headings: Lines starting with #, ##, ###, etc.
- Tables: Content between lines with | and --- markers
- Images: Lines containing ![
"""

USER_PROMPT_DOC_ANALYSIS = """Please analyze this document and identify elements that need processing.
Based on the line markers [Px-Ly], generate precise processing instructions.

Document Content:
{marked_content_from_pages}

Required JSON Output Format:
{{
    "debug_info": {{
        "total_pages": <total number of pages>,
        "pages": [
            {{
                "page": <page number>,
                "total_lines": <number of lines>,
                "heading_count": <number of headings>,
                "table_count": <number of tables>,
                "image_count": <number of images>,
                "first_line_preview": "<first 32 chars including [Px-Ly] marker>",
                "last_line_preview": "<first 32 chars including [Px-Ly] marker>"
            }}
        ]
    }},
    "remove_actions": [
        {{
            "page": <page number>,
            "lines": [<line numbers>],
            "reason": "<header|footer|duplicate|etc>",
            "confidence": <0.0-1.0>
        }}
    ],
    "merge_actions": [
        {{
            "type": "<table|paragraph|etc>",
            "pages": [<page numbers>],
            "line_ranges": {{
                "<page>": [
                    {{
                        "start": <start line>,
                        "end": <end line>,
                        "content_type": "<header|body|footer>",
                        "is_header": <true|false>,
                        "has_separator": <true|false>
                    }}
                ]
            }},
            "confidence": <0.0-1.0>,
            "is_cross_page": <true|false>,
            "table_structure": {{
                "columns": <number of columns>,
                "has_header": <true|false>
            }}
        }}
    ],
    "warnings": [
        {{
            "type": "<warning type>",
            "page": <page number>,
            "lines": [<line numbers>],
            "message": "<detailed warning message>"
        }}
    ]
}}

IMPORTANT: 
1. Your response must be a valid JSON object with EXACTLY the same structure as shown above.
2. The debug_info field is required, other fields are optional.
3. For tables:
   - Only merge tables that are truly split across pages
   - Verify table structure continuity
   - Set is_cross_page=true only if table needs merging
   - Include table_structure for validation

For debug_info:
1. Count headings (lines starting with #), tables (| and --- markers), and images (![)
2. For first_line_preview and last_line_preview, include first 32 characters
3. All counts should be integers >= 0
4. Line numbers should match the [Px-Ly] markers in content

For other fields:
1. confidence should be float between 0.0 and 1.0
2. page numbers should match actual pages in content
3. line numbers should match [Px-Ly] markers
4. Include clear reason/message for each action"""