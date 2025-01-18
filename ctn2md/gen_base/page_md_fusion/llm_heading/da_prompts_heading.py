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
1. Headings are cognitive anchors that:
   - Create mental models of document structure
   - Enable efficient knowledge navigation
   - Define conceptual boundaries
   - Establish information hierarchy

2. True headings serve as:
   - Knowledge Organizers: Like a library's classification system
   - Navigation Points: Like landmarks in a city
   - Scope Definers: Like chapter titles in a book
   - Relationship Builders: Like family trees

3. Non-headings are supporting elements that:
   - Provide details (like footnotes)
   - Attribute content (like citations)
   - Describe visuals (like captions)
   - Manage metadata (like page numbers)

Analysis Process:
1. EVALUATE HEADING ESSENCE
- Consider how the content functions:
  * Does it help build a mental map of the document?
  * Would it appear in a meaningful table of contents?
  * Does it create a natural pause in reading flow?
  * Could it stand alone as a section identifier?

2. CONFIDENCE SCORING GUIDELINES
- Score based on heading essence (10-point scale):
  1.0: Perfect structural heading
    * Major document sections (e.g. "1. Introduction", "2. Methods")
    * Clear numbering and perfect formatting
    * Essential for document navigation
    * Creates primary knowledge boundaries

  0.9: Strong heading
    * Subsections with clear hierarchy (e.g. "1.1", "2.3")
    * Standard formatting
    * Clear organizational role
    * Strong structural significance

  0.8: Basic heading
    * Valid sections without numbering (e.g. "Conclusion", "References")
    * May have minor format variations
    * Clear but simpler structural role

  0.5: Weak/Ambiguous content
    * Mixed organizational/detail content
    * Unclear structural role
    * Format inconsistencies
    * Questionable navigation value

  0.3 or lower: Non-heading content
    * Figure/table titles (-0.6 deduction)
    * Author/attribution information (-0.6 deduction)
    * Technical specifications (-0.5 deduction)
    * Running text, footnotes, page numbers
    * Pure descriptive or administrative content

- Key indicators for non-headings (should score ≤0.5):
  * Describes rather than organizes
  * Part of content flow
  * No meaningful structural role
  * Serves technical/administrative function

- Context Deductions:
  * -0.6: Clear figure/table caption patterns
  * -0.6: Pure attribution/metadata content
  * -0.5: Technical specifications
  * -0.3: Format inconsistencies
  * -0.2: Minor numbering variations

- Key indicators for non-headings (should score <0.5):
  * Describes rather than organizes
  * Part of content flow
  * Serves technical/administrative function
  * No structural significance

- Common non-heading patterns (should score <0.6):
  * Figure/table titles (should score 0.4-0.5)
  * Technical specifications (should score 0.3-0.4)
  * Author/citation information (should score <0.3)
  * Running text headings (should score 0.4-0.5)
  * Metadata entries (should score <0.3)

3. ASSESS STRUCTURAL ROLE
- Key considerations:
  - Position in document hierarchy
  - Relationship to other headings
  - Scope of content organized
  - Contribution to document navigation

4. VALIDATE RELATIONSHIPS
- Critical checks:
  - Logical progression of ideas
  - Consistent hierarchical structure
  - Clear parent-child connections
  - Coherent cross-page links

5. OUTPUT REQUIREMENTS
- For each heading:
  * Determine if it's a true heading based on semantic role
  * Set error_type to one of:
    - wrong_level: Incorrect heading level
    - wrong_format: Format error (for headings without proper markers)
    - not_heading: Not a heading
    - missing: Missing heading
    - inconsistent: Inconsistent with context
  * Assign confidence based on:
    - Clarity of heading role (introduces new topic)
    - Strength of parent-child relationship
    - Consistency with peer headings
  * Assign heading_id as a simple numeric string:
    - Use "1" for first heading, "2" for second, etc.
    - Must be sequential and unique within the document
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
The `marked_content_from_pages` will be presented in the following format:
- Content is organized by pages, marked with "=== PAGE X ===" and "=== END PAGE X ===" delimiters
- Each line is prefixed with "[PX-LY]" where:
  * X is the page number
  * Y is the line number within that page
- Empty lines are explicitly marked with "<empty>"
- Page breaks are clearly indicated
- Special characters and formatting are preserved
- Cross-page content maintains its original structure

Example:
=== PAGE 1 ===
[P1-L1] Title of Document
[P1-L2] <empty>
[P1-L3] First section heading
=== END PAGE 1 ===

Document Content:
<document>
{marked_content_from_pages}
</document>

Required Output Format:
{
    "headings": [{
        "page": "Page number (integer)",
        "line": "Line number (integer)",
        "content": "Heading content (string)",
        "heading_id": "Sequential numeric string starting from '1' (e.g., '1', '2', '3')",
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
                "prev_heading_id": "ID of the previous heading (e.g., if previous heading has heading_id='2', use '2'), or null if no previous heading",
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