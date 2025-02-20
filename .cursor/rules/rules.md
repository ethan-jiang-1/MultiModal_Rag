# Project Rules

## Code Style & Structure
- Use type hints for all function parameters and return values
- Follow PEP 257 for docstrings with clear descriptions
- Use Ruff for code formatting and linting
- Keep functions focused and under 50 lines where possible
- One class/module per file following single responsibility principle
- Use absolute imports from project root, avoid relative imports
- Place imports at the top of file after `load_env()`

## Testing Requirements
- All new code must have corresponding tests in ./xxx_tests directories
- Use pytest as the primary testing framework
- Write test functions with clear type hints and docstrings
- Use fixtures for resource reuse and setup
- Use parametrize for testing multiple scenarios
- Mock external dependencies appropriately
- Include `__main__` test entry points for quick validation

## Documentation Standards
- All modules must have comprehensive docstrings
- README.md required for each major component
- Document complex algorithms and design decisions
- Keep documentation synchronized with code changes
- Use diagrams/ directory for architecture and flow diagrams
- Include usage examples in documentation
- Document environment variables and configuration options

## Data & Error Handling
- Use dataclass for data structure definitions
- Use pydantic for data validation and serialization
- Implement proper error handling with specific exceptions
- Use async/await for asynchronous operations
- Implement consistent logging throughout the codebase
- Use lru_cache for computation result caching where appropriate
- Handle edge cases and validate inputs explicitly

## AI Assistant Guidelines
- Prefer simple, readable solutions over clever ones
- Make incremental changes, one modification at a time
- Follow existing project patterns and conventions
- Add comprehensive type hints and docstrings
- Implement proper error handling and logging
- Write testable code with clear dependencies
- Optimize for maintainability over premature optimization
- Keep code structure clear and AI-friendly
- Use established design patterns appropriately
- Document complex logic and important decisions

## Development Workflow
- Use venv for virtual environment management
- Store secrets and configuration in .env files
- Follow dependency injection principles
- Conduct code reviews for all significant changes
- Run tests before committing changes
- Keep dependencies up to date
- Monitor performance and memory usage
- Refactor code when complexity increases 