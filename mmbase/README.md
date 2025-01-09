# mmbase

Base utilities for MultiModal RAG system, providing shared functionality for logging, LLM interactions, and other common operations.

## Installation

```bash
pip install -e .
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

## Features

- Configurable logging with module-specific prefixes
- Rotating file handlers for different log types (main, error, LLM, progress)
- Colored console output
- Automatic log file management 