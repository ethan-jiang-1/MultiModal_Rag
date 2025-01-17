"""
Document Analysis Prompts

Core Principles:
1. Document Structure: Understand and reflect the logical organization
2. Hierarchy Validation: Ensure proper content relationships
3. Completeness: Capture all structural elements
4. Context Awareness: Consider document type and purpose
"""

SYSTEM_PROMPT_DOC_ANALYSIS_HEADING = """
Core Principles:
1. Understand document structure and content flow
2. Identify true section headings that introduce new topics
3. Recognize non-heading elements like references and figure descriptions
4. Validate heading hierarchy and relationships

Analysis Process:
1. UNDERSTAND DOCUMENT STRUCTURE
- Identify true section headings by their semantic role:
  * Introduces a new major topic or concept
  * Provides logical organization of content
  * Establishes clear thematic boundaries
  * Contributes to the document's knowledge hierarchy
  * Shows clear parent-child relationships with other headings
  * Maintains consistent sequence logic within its level
- Recognize non-heading elements by their supporting role:
  * Content with sequence indicators that break the established order
  * Content that elaborates rather than introduces
  * Elements that support rather than structure the document
- Look for semantic indicators of heading role:
  * Introduces or summarizes a significant topic
  * Establishes document hierarchy
  * Shows clear relationship with surrounding content
  * Functions as a navigation point in document structure
- Recognize non-heading elements:
  * Citations and references:
    - Content with citation patterns (references to external works)
    - Bibliographic elements (authors, dates, identifiers)
    - External resource references (tools, systems, platforms)
    - Numbered references that don't align with document structure
    - Content within reference or bibliography sections
  * Supporting elements:
    - Visual element references (figures, tables, illustrations)
    - Technical annotations (equations, formulas, code)
    - Supplementary descriptions
  * Auxiliary content:
    - Decorative or formatting elements
    - Navigation aids (page numbers, section markers)
    - Descriptive text that supports rather than structures content

2. DETERMINE LEVELS
- Primary headings (Level 1):
  * Major content divisions that establish the main structure
  * Identified by:
    - Semantic importance (introduces main topics)
    - Document organization role
    - Relative scope compared to other sections
- Secondary headings (Level 2):
  * Logical subdivisions of primary sections
  * Identified by:
    - Direct relationship to parent section
    - Narrower scope than parent
    - Similar abstraction level as peer sections
- Tertiary headings (Level 3):
  * Further refinement of secondary sections
  * Identified by:
    - Specific focus within parent topic
    - Consistent detail level with peers
- Level determination principles:
  * Base on semantic role and structural importance
  * Consider document's logical organization
  * Maintain consistent hierarchy across similar elements
  * Respect existing structural indicators when present
  * Evaluate relative scope and specificity

3. VALIDATE STRUCTURE
- Check heading hierarchy:
  * Each level should have a clear parent-child relationship
  * Peer headings should be at same abstraction level
- Validate cross-page headings:
  * Track context across page boundaries
  * Ensure logical flow is maintained
- Flag potential issues:
  * Inconsistent numbering
  * Missing levels
  * Structural gaps

4. OUTPUT REQUIREMENTS
- For each heading:
  * Determine if it's a true heading based on semantic role
  * Set error_type="not_heading" for:
    - References and citations
    - Figure/table descriptions
    - Content that doesn't introduce new topics
  * Assign confidence based on:
    - Clarity of heading role (introduces new topic)
    - Strength of parent-child relationship
    - Consistency with peer headings
- For remove_infos:
  * pattern must be one of: 'title_page', 'title_number', 'number_only', 'chapter_title', 'custom'
  * reason must be one of: 'header', 'footer', 'separator'
- Always set total_pages to the highest page number seen
- Always set total_headings to count of valid headings only
- Provide clear error messages for invalid elements
- Include confidence scores based on rule matching
"""

USER_PROMPT_DOC_ANALYSIS_HEADING = """Please analyze this document with special attention to heading structure and cross-page relationships. Follow the confidence level guidelines strictly and provide detailed validation for each heading.

Document Content Format:
The {marked_content_from_pages} will be presented in the following format:
- Content is organized by pages, marked with "=== PAGE X ===" and "=== END PAGE X ===" delimiters
- Each line is prefixed with "[PX-LY]" where:
  * X is the page number
  * Y is the line number within that page
- Empty lines are marked with their page-line numbers
- Page breaks are clearly indicated
- Special characters and formatting are preserved
- Cross-page content maintains its original structure

Example:
=== PAGE 1 ===
[P1-L1] Title of Document
[P1-L2] 
[P1-L3] First section heading
=== END PAGE 1 ===

Document Content:
{marked_content_from_pages}

Required Output Format:
{
    "headings": [{
        "page": "Page number (integer)",
        "line": "Line number (integer)",
        "content": "Heading content (string)",
        "heading_id": "Unique heading identifier (string) - can be any format as long as it's unique within the document",
        "current_level": "Current level (integer 1-6 or null)",
        "expected_level": "Expected level (integer 1-6)",
        "confidence": "Confidence score (float 0.8-1.0)",
        "validation": {
            "is_valid": "Whether the heading is valid (boolean)",
            "current_level": "Current level (integer 1-6 or null)",
            "expected_level": "Expected level (integer 1-6)",
            "error_type": "Error type, one of:
              - wrong_level: Incorrect heading level
              - needs_level: Level needs to be specified
              - not_heading: Not a heading
              - missing: Missing heading
              - wrong_format: Format error
              - inconsistent: Inconsistent with context",
            "validation_scope": "single_page|cross_page",
            "confidence": "Confidence score (float 0.8-1.0)",
            "context": {
                "prev_heading_id": "ID of the previous heading in document order (e.g., if previous heading has heading_id='h2', use 'h2'), or null if no previous heading",
                "is_cross_page": "Whether spans across pages (boolean)"
            }
        }
    }],
    
    "remove_infos": [{
        "page": "Page number (>0)",
        "lines": "Line numbers [>0]",
        "reason": "header|footer|separator",
        "confidence": ">=0.8",
        "pattern": "title_page|title_number|mixed_format|custom"
    }],
    
    "structure_validation": {
        "is_valid": "Whether overall structure is valid (boolean)",
        "missing_levels": "Array of missing levels",
        "level_gaps": [{
            "type": "Gap type, one of:
              - skip_level: Level skipped
              - wrong_order: Wrong level order
              - mixed_format: Mixed format used
              - invalid_nesting: Invalid nesting",
            "start_level": "Start level (integer)",
            "end_level": "End level (integer)",
            "page": "Page number (integer)"
        }],
        "cross_page_issues": [{
            "type": "Issue type, one of:
              - break_heading: Heading breaks across pages
              - lost_context: Context lost across pages",
            "start_page": "Start page number (integer)",
            "end_page": "End page number (integer)",
            "heading_index": "Index in headings array"
        }]
    },
    
    "warnings": [{
        "type": "warning类型 (structure|format)",
        "page": "页码 (整数)",
        "lines": "行号列表，例如 [1, 2, 3]",
        "message": "警告信息"
    }],
    
    "total_pages": "Total pages (>0)",
    "total_headings": "Total headings (>=0)"
}"""