# Python Project Rules and Best Practices

## Core Principles
### KISS Principle (Keep It Simple Stupid)
- Write the simplest possible code
- Maintain easy-to-understand and maintainable code
- Ensure code is easily comprehensible for both humans and AI

### Single Responsibility
- One module per file
- Each module performs the simplest possible functionality
- Clear responsibilities for each class/function

### Progressive Development
- Iterate in small steps, avoid large changes
- Build framework first, then refine details
- Maintain code testability

## Project Structure
### Directory Organization
- Separate source code, tests, documentation, and configuration
- Include README.md for functionality explanation
- Store architecture diagrams in diagrams/
- Avoid excessive directory nesting

### Dependency Management
- Use venv for virtual environment management (.venv directory)
- Use .env for configuration and secrets
- Use .gitignore for version control
- Follow dependency injection principles

## Coding Standards
### Code Quality
- Type annotations required for all files
- Documentation strings required for all functions/classes (PEP 257)
- Use Ruff for code style consistency
- Preserve existing comments

### Data Processing
- Use dataclass for data structure definitions
- Use pydantic for data validation
- Use lru_cache for computation result caching

### Async and Error Handling
- Use async/await for asynchronous operations
- Implement consistent logging practices
- Implement appropriate error handling and context management

## Testing Standards
### Test Organization
- Name test directories as ./xxx_tests
- Organize test files by module name
- Create necessary __init__.py files

### Test Writing
- Use pytest and its plugins exclusively
- Include type annotations and documentation for all tests
- Use fixtures for resource reuse
- Use parametrize for test parameterization
- Use mock for external dependency simulation

### Test Entry Points
- Place simple tests in __main__
- Place complex tests in pytest
- Provide quick validation through __main__

## Design Patterns
### Processor Pattern
- Business logic layer handles only flow orchestration
- Complex logic delegated to processors
- Base-level processors independently testable

### Workspace
- Share context through md_info
- Ensure workspace isolation for security
- Avoid direct original file modifications

### Common Patterns
- Factory pattern for object creation
- Strategy pattern for algorithm variants
- Observer pattern for event handling
- Decorator pattern for functionality extension

## Best Practices
### Code Optimization
- Use async for performance improvement
- Use caching appropriately
- Monitor performance and memory usage

### Code Maintenance
- Conduct regular code reviews
- Perform continuous refactoring
- Maintain code testability

### AI-Friendly Development
- Use reasonable but not excessive type annotations
- Maintain clear code structure
- Optimize code for AI-assisted development

## Module Import Rules
### Core Rules
1. **Environment Initialization Priority**
   - Execute `load_env()` at file top
   - Ensure correct project root directory identification
   - Base all subsequent module imports on root directory

2. **Module Independence**
   - Each core module should have a `__main__` test entry
   - Depend on environment initialization from rule 1
   - Enable direct test execution from project root
   - Focus on making models independently debuggable for AI understanding

3. **Absolute Path Imports**
   - Use complete import paths from project root
   - Avoid relative imports with `.` or `..`
   - Prevent import errors from module relocations

## Progressive Modification Principles
### Step-by-Step Approach
1. **Incremental Changes**
   - Modify one key point at a time
   - Verify effects after each modification
   - Maintain stability in other components

2. **Modification Strategy**
   - Progress from abstract to concrete
   - Move from general to specific
   - Prefer augmentation over replacement

3. **Verification Process**
   - Run tests after each modification
   - Compare behavior before and after changes
   - Confirm no unintended side effects

4. **Best Practices**
   - Find appropriate locations within existing structure
   - Maintain current abstraction levels
   - Ensure new content matches contextual expression

5. **Common Pitfalls to Avoid**
   - Modifying too much at once
   - Altering existing abstraction levels
   - Skipping modification effect verification 