# TOC Recovery from PDF-converted Markdown Files

## Core Understanding

### The Essence of TOC
- TOC is not just a list of formatted text, but a **knowledge organization framework**
- It serves as a cognitive map helping readers navigate through the document
- It reflects the author's logical structuring of knowledge
- It enables both quick overview and targeted reading

### Why Headings Matter
1. **Knowledge Organization**
   - Headings form the skeleton of document structure
   - They create clear hierarchical relationships between topics
   - They guide progressive understanding of content

2. **Reader Navigation**
   - Help readers quickly grasp document scope
   - Enable efficient location of specific information
   - Show relationships between different parts of content

## Technical Implementation

### Data Requirements
1. **Input Format**
   ```
   === PAGE X ===
   [PX-LY] Content line
   === END PAGE X ===
   ```
   - Each line prefixed with page and line numbers
   - Clear page delimiters
   - Preserved formatting and special characters
   - Cross-page content maintains structure

2. **Output Schema**
   - Structured JSON format
   - Detailed heading information (page, line, content, level)
   - Validation results and confidence scores
   - Structure analysis and warnings

### Key Challenges
1. **Distinguishing True Headings**
   - Not all formatted text are headings
   - References and figure captions may look like headings
   - Headers/footers need special handling

2. **Cross-page Relationships**
   - Maintaining context across pages
   - Handling split headings
   - Preserving structural continuity

3. **Level Determination**
   - Based on knowledge organization role
   - Considering topic relationships
   - Maintaining consistent hierarchy

## Prompt Engineering Insights

### Core Principles
1. **Focus on Semantic Role**
   - Ask "Does this organize knowledge?" not "Does this look like a heading?"
   - Consider how content contributes to document navigation
   - Evaluate relationship with surrounding content

2. **Context Awareness**
   - Consider document type and purpose
   - Understand typical structure patterns
   - Recognize special sections (references, appendices)

3. **Validation Depth**
   - Check both individual headings and overall structure
   - Validate hierarchical relationships
   - Ensure navigation effectiveness

### Common Pitfalls
1. **Over-reliance on Formatting**
   - Don't judge solely by appearance
   - Formatting is a hint, not a determinant
   - Consider semantic role first

2. **Rule Complexity**
   - Avoid endless specific rules
   - Focus on fundamental principles
   - Maintain generalizability

3. **Losing Sight of Purpose**
   - Remember TOC is for navigation
   - Keep focus on knowledge organization
   - Prioritize reader understanding

## Engineering Considerations

### Performance
- Balance between accuracy and processing speed
- Efficient handling of large documents
- Smart caching of context information

### Maintainability
- Clear separation of concerns
- Well-documented prompt structure
- Modular validation rules

### Extensibility
- Support for different document types
- Adaptable confidence scoring
- Flexible output formats

## Best Practices

### Prompt Design
1. **Clear Core Principles**
   - State fundamental understanding upfront
   - Focus on essential purpose
   - Avoid over-specification

2. **Structured Analysis Process**
   - Break down into logical steps
   - Clear criteria for each decision
   - Consistent evaluation framework

3. **Comprehensive Output Requirements**
   - Detailed schema specification
   - Clear validation rules
   - Useful error messages

### Validation Strategy
1. **Multi-level Checking**
   - Individual heading validation
   - Structural relationship validation
   - Cross-page consistency checks

2. **Confidence Scoring**
   - Based on multiple factors
   - Clear scoring criteria
   - Useful for downstream processing

3. **Error Handling**
   - Descriptive error types
   - Actionable warning messages
   - Clear validation scope

## Future Improvements
- Enhanced semantic understanding
- Better handling of special cases
- More sophisticated confidence scoring
- Improved cross-page analysis
- Support for more document types 