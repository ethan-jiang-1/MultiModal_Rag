"""
Document Analysis Prompts

Core Principles:
1. Document Structure: Understand and reflect the logical organization
2. Hierarchy Validation: Ensure proper content relationships
3. Completeness: Capture all structural elements
4. Context Awareness: Consider document type and purpose
"""

SYSTEM_PROMPT_DOC_ANALYSIS_HEADING = """
Heading Identification Framework:

1. SEMANTIC ROLE EVALUATION (Primary Decision Layer)
   Question: "Does this content organize knowledge?"
   
   A. True Heading Characteristics:
      - Introduces new topic or concept
      - Creates clear knowledge boundary
      - Functions as section organizer
      - Enables document navigation
      - Belongs in a meaningful TOC
   
   B. Non-Heading Characteristics:
      - Describes rather than organizes
      - Continues previous content
      - Serves technical/administrative function
      - Contains detailed information
      - Functions as caption or attribution

2. CONTEXTUAL ANALYSIS (Secondary Decision Layer)
   Question: "How does it relate to document flow?"
   
   A. Context Indicators:
      Strong Heading Context:
      - Followed by new content section
      - Clear hierarchy with siblings
      - Independent of previous content
      - Creates natural content break
      
      Non-Heading Context:
      - Depends on previous content
      - Part of continuous paragraph
      - Subordinate to nearby content
      - Technical/supplementary role

3. IMMEDIATE REJECTION PATTERNS
   Automatically classify as non-heading if matches:
   
   A. Figure/Table Patterns:
      - Starts with: "Fig.", "Figure", "Table"
      - Contains: "shown in figure", "as illustrated"
   
   B. Reference Patterns:
      - Starts with: "Source:", "Reference:", "Cited from"
      - Contains: "et al.", "DOI:", "ISBN:"
   
   C. Metadata Patterns:
      - Copyright notices: "©", "All rights reserved"
      - Page numbers: "Page", "页码"
      - Author information: "Author:", "作者:"

4. CONFIDENCE SCORING SYSTEM
   Base Score (0.0-1.0) * Context Multiplier * Format Multiplier

   A. Base Score Assignment:
      1.0: Perfect structural heading
      - Major document sections
      - Clear numbering and formatting
      - Essential for navigation
      - Creates primary knowledge boundaries

      0.8: Strong heading
      - Clear subsections
      - Standard formatting
      - Strong organizational role
      - Clear structural significance

      0.6: Basic heading
      - Valid but simpler sections
      - Minor format variations
      - Clear but basic structure role

      0.4: Weak/Ambiguous
      - Mixed content type
      - Unclear structural role
      - Format inconsistencies
      - Questionable navigation value

      0.2: Non-heading content
      - Pure descriptive content
      - Technical specifications
      - Administrative text
      - Supplementary information

   B. Context Multipliers:
      - Clear section start: *1.2
      - Consistent hierarchy: *1.1
      - Mixed context: *0.8
      - Broken flow: *0.6

   C. Format Multipliers:
      - Standard format: *1.0
      - Minor issues: *0.9
      - Major issues: *0.7
      - Wrong format: *0.5

   D. Automatic Deductions:
      - Contains figure/table markers: -0.6
      - Contains references: -0.5
      - Contains metadata: -0.4
      - Excessive length: -0.3

5. VALIDATION REQUIREMENTS
   For each heading candidate:

   A. Basic Validation:
      - Verify semantic role first
      - Check context relationships
      - Evaluate format consistency
      - Assess structural importance

   B. Cross-Page Validation:
      - Check context continuation
      - Verify hierarchy maintenance
      - Evaluate reference resolution
      - Assess content flow

   C. Error Type Assignment:
      wrong_level: Incorrect heading level
      needs_level: Level needs to be specified
      not_heading: Not a heading
      missing: Missing heading
      wrong_format: Format error
      inconsistent: Inconsistent with context

6. OUTPUT GUIDELINES
   Strictly follow the schema defined in da_schemas_heading.py:
   
   A. HeadingInfo requirements:
      - Assign sequential heading_id (1, 2, 3...)
      - Set confidence based on scoring system
      - Include complete validation details
      - Provide context information

   B. RemoveInfo requirements:
      - Identify headers/footers accurately
      - Specify correct removal reason
      - Use appropriate pattern type
      - Maintain high confidence (>=0.8)

   C. Structure Validation:
      - Verify overall document structure
      - Identify missing levels
      - Report level gaps
      - Document cross-page issues

Remember: Always prioritize semantic role over formatting. A well-formatted line might not be a heading, while a less-formatted line with clear organizational function should be considered a heading.

Output Format Rules:
1. Validation scope must be one of: 'single_page', 'cross_page', or 'document'
2. All heading confidence scores must be >= 0.8
3. Remove info reasons must be one of: 'header', 'footer', 'duplicate', 'noise', or 'separator'
4. Remove info patterns must be one of: 'title_page', 'title_number', 'number_only', 'chapter_title', or 'custom'

Follow these rules strictly when formatting the output JSON, while applying the heading identification framework above."""

USER_PROMPT_DOC_ANALYSIS_HEADING = """Please analyze this document following the Heading Identification Framework. Focus on semantic role and context before considering format. Provide detailed validation for each heading candidate.

Document Content Format:
The `Document Content` will be presented in a structured XML format that clearly delineates pages and their relationships:

1. Document Structure:
   - Content is wrapped in <document> tags
   - Pages marked with "=== PAGE X ===" and "=== END PAGE X ==="
   - Each line has identifier "[PX-LY]" where:
     * X: Page number
     * Y: Line number within page

2. Content Organization:
   - Empty lines marked with "<empty>"
   - Page breaks clearly indicated
   - Special characters preserved
   - Cross-page relationships maintained

3. Example Structure:
<document>
=== PAGE 1 ===
[P1-L1] Title of Document
[P1-L2] <empty>
[P1-L3] First section heading
=== END PAGE 1 ===

=== PAGE 2 ===
[P2-L1] Continuation of content
=== END PAGE 2 ===
</document>

Document Content:
<document>
{marked_content_from_pages}
</document>

Required Output Format:
{
    "headings": [{
        "page": int,
        "line": int,
        "content": string,
        "heading_id": string,
        "current_level": int or null,
        "expected_level": int,
        "confidence": float,
        "validation": {
            "is_valid": boolean,
            "current_level": int or null,
            "expected_level": int,
            "error_type": string or null,
            "validation_scope": string,
            "confidence": float,
            "context": {
                "prev_heading_id": string or null,
                "is_cross_page": boolean
            }
        }
    }],
    
    "remove_infos": [{
        "page": int,
        "lines": [int],
        "reason": string,
        "confidence": float,
        "pattern": string
    }],
    
    "structure_validation": {
        "is_valid": boolean,
        "missing_levels": [int],
        "level_gaps": [{
            "type": string,
            "start_level": int,
            "end_level": int,
            "page": int
        }],
        "cross_page_issues": [{
            "type": string,
            "start_page": int,
            "end_page": int,
            "heading_index": int
        }]
    },
    
    "warnings": [{
        "type": string,
        "page": int,
        "lines": [int],
        "message": string
    }],
    
    "total_pages": int,
    "total_headings": int
}"""