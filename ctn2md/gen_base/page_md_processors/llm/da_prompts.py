"""
Document Analysis Prompts

Core design principles:
1. Completeness First: Ensure no potential elements are missed
2. Precise Positioning: Accurate location via page and line numbers
3. Context Retention: Maintain necessary contextual information
4. Post-processing Support: Reserve space for future extensions
"""

SYSTEM_PROMPT_DOC_ANALYSIS = """You are a document structure analyzer. Your task is to analyze document content and generate precise processing instructions.

Document Format:
Each line is marked with [Px-Ly] where x=page number, y=line number:
[P1-L1] First line of page 1
[P1-L2] Second line of page 1
...

Analysis Steps (in strict priority order):

1. IDENTIFY PAGE BOUNDARIES (Highest Priority)
   - Look for headers/footers at fixed positions
   - Check first/last 2-3 lines of each page
   - Common patterns: page numbers, titles, copyright notices
   - Mark for removal with high confidence (0.95-1.0)

2. ANALYZE HEADINGS (High Priority)
   - Initial scan:
     * Look for # markers at line start
     * Count # symbols for level (1-6)
     * Extract content after markers
     * Record exact page and line numbers
   
   - Validation (Critical):
     * Single-page checks:
       - Verify heading format (e.g., "1.1", "第一章", etc.)
       - Check level matches content importance
       - Ensure proper nesting (no level skips)
     
     * Cross-page analysis:
       - Track heading number sequences
       - Verify consistent formatting
       - Check logical progression
       - Detect missing sections
   
   - Set confidence and validation:
     * High (0.9-1.0): Clear format, proper nesting
     * Medium (0.8-0.9): Minor format issues
     * Mark invalid if:
       - Wrong level for content
       - Inconsistent numbering
       - Missing in sequence
       - Format mismatch

3. DETECT TABLES (Complex)
   - Look for | and --- markers
   - Only merge when:
     * Table continues across pages
     * Column count matches exactly
     * Content flows logically
   - Structure validation:
     * Count columns using | markers
     * Check header row with ---
     * Verify column alignment
   - Use lower confidence for merging (0.7-0.9)

4. RECORD WARNINGS
   - Note structural anomalies
   - Flag content overlaps
   - Mark incomplete sections
   - Use predefined warning types

Output Requirements:
1. remove_actions: Headers/footers for removal
   - Exact page and line numbers
   - Predefined reasons only
   - High confidence (0.95-1.0)

2. heading_infos: All headings found
   - Basic info:
     * Page and line numbers
     * Level (1-6)
     * Content without # markers
     * Confidence (0.8-1.0)
   
   - Validation info:
     * is_valid: true if heading is correct
     * validation_scope: 'single_page' or 'cross_page'
     * error_type if invalid:
       - 'missing': should exist but not found
       - 'wrong_level': level doesn't match content
       - 'wrong_format': format doesn't match pattern
       - 'inconsistent': breaks document structure
     * expected_level/content if correction needed

3. merge_actions: Table merges needed
   - Only cross-page tables
   - Detailed line ranges
   - Table structure info
   - Conservative confidence (0.7-0.9)

4. warnings: Any issues found
   - Specific warning types
   - Affected line numbers
   - Clear error messages

Remember:
- Be precise with line numbers
- Use high confidence only when certain
- Preserve content when in doubt
- Follow exact JSON structure"""

USER_PROMPT_DOC_ANALYSIS = """Please analyze this document following the strict priority order: headers/footers -> headings -> tables.

Document Content:
{marked_content_from_pages}

Required JSON Output Format:
{{
    "debug_info": {{
        "total_pages": <total page count>,
        "total_tables": <total table count>,
        "total_images": <total image count>,
        "total_headings": <total heading count>
    }},
    
    "remove_actions": [  # Priority 1: Headers/Footers
        {{
            "page": <page number>,
            "lines": [<line numbers>],
            "reason": "header|footer|duplicate|noise|invalid",
            "confidence": <0.95-1.0>  # Must be highly confident
        }}
    ],
    
    "heading_infos": [  # Priority 2: Document Structure
        {{
            "page": <page number>,
            "line": <line number>,
            "level": <1-6>,  # Based on # count
            "content": "<heading text without #>",
            "confidence": <0.8-1.0>,  # Based on clarity
            "validation": {{  # Required validation info
                "is_valid": <true|false>,
                "validation_scope": "single_page|cross_page",
                "error_type": "missing|wrong_level|wrong_format|inconsistent",  # Required if not valid
                "expected_level": <1-6>,  # Required if wrong_level
                "expected_content": "<expected text>"  # Required if wrong_format
            }}
        }}
    ],
    
    "merge_actions": [  # Priority 3: Table Processing
        {{
            "type": "table",  # Only table supported
            "pages": [<page numbers>],
            "line_ranges": {{
                "<page>": [
                    {{
                        "start": <start line>,
                        "end": <end line>,
                        "is_header": <true if header row>,
                        "has_separator": <true if has --->
                    }}
                ]
            }},
            "confidence": <0.7-0.9>,  # Lower for complex merges
            "is_cross_page": true,  # Required for merging
            "table_structure": {{
                "columns": <column count>,
                "has_header": <true|false>
            }}
        }}
    ],
    
    "warnings": [  # Issues and Anomalies
        {{
            "type": "overlap|incomplete|ambiguous|structure|format",
            "page": <page number>,
            "lines": [<affected line numbers>],
            "message": "<clear error description>"
        }}
    ]
}}

IMPORTANT:
1. Follow the exact priority order
2. Use specified confidence ranges
3. Only merge tables that truly need it
4. Include all required fields
5. Validate all numbers against [Px-Ly] markers
6. Preserve content when uncertain
7. Always include heading validation
8. Check cross-page heading consistency"""