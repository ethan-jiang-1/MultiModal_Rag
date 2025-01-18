# TOC Recovery from PDF-converted Markdown Files

## Core Understanding

### The Essence of TOC
- TOC is not just a list of formatted text, but a **knowledge organization framework**
- It serves as a cognitive map helping readers navigate through the document
- It reflects the author's logical structuring of knowledge
- It enables both quick overview and targeted reading
- It reveals the natural boundaries between different topics and concepts
- It functions as a cognitive framework for document comprehension
- It mirrors how humans naturally organize and process information

### Why Headings Matter
1. **Knowledge Organization**
   - Headings form the skeleton of document structure
   - They create clear hierarchical relationships between topics
   - They guide progressive understanding of content
   - They establish the scope and domain of content sections
   - They represent logical boundaries in the knowledge flow

2. **Reader Navigation**
   - Help readers quickly grasp document scope
   - Enable efficient location of specific information
   - Show relationships between different parts of content
   - Create natural breaks in content flow
   - Serve as mental anchors for information processing

3. **Structural Significance**
   - Stand above the content they organize
   - Create consistent patterns with peer sections
   - Impact document navigability when present or absent
   - Maintain coherence across document sections
   - Bridge gaps between high-level concepts and detailed content

4. **Cognitive Anchoring**
   - Act as mental landmarks in the knowledge landscape
   - Create natural cognitive boundaries between concepts
   - Enable efficient mental model construction
   - Support progressive knowledge building
   - Facilitate information chunking and recall

### Understanding Through Analogies
1. **Knowledge Architecture**
   - Headings as Library Classification System
     * Organize information into logical categories
     * Enable efficient content location
     * Create clear hierarchical relationships
   
   - Headings as City Landmarks
     * Provide navigation reference points
     * Create memorable mental maps
     * Enable intuitive wayfinding

2. **Content Flow**
   - Headings as Chapter Titles in Books
     * Define clear thematic boundaries
     * Set reader expectations
     * Create natural reading pauses
   
   - Headings as Family Trees
     * Show clear parent-child relationships
     * Maintain generational hierarchy
     * Represent logical inheritance

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

### Cognitive-First Approach
1. **Mental Model Alignment**
   - Evaluate content based on its role in understanding
   - Consider how it contributes to document mental map
   - Assess its function in knowledge organization

2. **Natural Information Processing**
   - Mirror how humans naturally parse documents
   - Support intuitive navigation patterns
   - Enable progressive understanding

## Prompt Engineering Insights

### Core Principles
1. **Focus on Semantic Role**
   - Ask "Does this organize knowledge?" not "Does this look like a heading?"
   - Consider how content contributes to document navigation
   - Evaluate relationship with surrounding content
   - Assess impact on document's cognitive map
   - Consider content's role in establishing topic boundaries

2. **Context Awareness**
   - Consider document type and purpose
   - Understand typical structure patterns
   - Recognize special sections (references, appendices)
   - Evaluate content's relationship with document flow
   - Consider impact on reader's mental model

3. **Validation Depth**
   - Check both individual headings and overall structure
   - Validate hierarchical relationships
   - Ensure navigation effectiveness

4. **Cognitive Processing Perspective**
   - Consider how content supports mental model building
   - Evaluate contribution to document understanding
   - Assess role in knowledge structure formation
   - Focus on natural information organization
   - Support intuitive document navigation

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