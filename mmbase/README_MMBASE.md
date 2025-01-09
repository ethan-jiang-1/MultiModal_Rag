# mmbase

Base utilities for MultiModal RAG system, providing shared functionality for logging, LLM interactions, and other common operations.

## Project Structure

The MultiModal RAG system consists of several key components:
- `mmbase/`: Base utilities and shared functionality
- `ctn2md/`: Content to markdown conversion utilities
- `mrag_app/`: Main application implementation
- `mrag_vdb/`: Vector database related functionality
- `*_tests/`: Corresponding test directories for each component

## Installation

```bash
pip install -e .
```

For development, also install development dependencies:
```bash
pip install -r requirements-dev.txt
```

## Usage

### Logging

To use the logging system in your module:

```python
from mmbase.utils.logging import LoggingConfig, setup_logger_handlers

# Initialize with your module name
LoggingConfig.initialize("your_module_name")
setup_logger_handlers()

# Use logging as normal
import logging
logging.info("Your log message")
```

### LLM Utilities

The `utils_llm` package provides base classes and utilities for LLM interactions:
- Base LLM client implementations
- Monitoring and logging for LLM operations
- Message handling utilities
- OSS and TOS specific implementations

## Features

- Configurable logging with module-specific prefixes
- Rotating file handlers for different log types (main, error, LLM, progress)
- Colored console output
- Automatic log file management
- LLM interaction utilities
- Common base functionality for MultiModal RAG system 