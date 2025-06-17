## MultiModal_Rag

> A complete multimodal RAG (Retrieval-Augmented Generation) system, including document conversion, vector database storage, and a Gradio interactive interface.

> The purpose of this project is to provide an end-to-end solution for building intelligent question-answering systems over complex, multimodal documents. It supports various document formats, leverages advanced AI models for content understanding and generation, and offers a user-friendly web interface for interaction.

> The project is in an active development state.

> Team information is not specified.

> The project is primarily built using Python 3.12+. Key frameworks and libraries include Gradio for the web interface, and various LLM/VLM integrations (OpenAI, Qwen, Ark). It uses vector databases for retrieval augmentation.



## Dependencies (init from programming language specification like package.json, requirements.txt, etc.)

* acres==0.2.0: A library for asynchronous cross-origin resource sharing.
* aiofiles==23.2.1: Asynchronous file operations.
* aiohttp==3.11.10: Asynchronous HTTP client/server for asyncio.
* aliyun-python-sdk-core==2.16.0: Alibaba Cloud SDK for Python - Core.
* aliyun-python-sdk-kms==2.16.5: Alibaba Cloud SDK for Python - KMS.
* anyio==4.7.0: High-level asynchronous compatibility layer.
* beautifulsoup4==4.12.3: For parsing HTML and XML documents.
* gradio==5.9.1: A fast way to build and share ML apps.
* llama-index==0.12.8: A data framework for LLM applications.
* llama-parse==0.5.17: A library for parsing complex documents for LLMs.
* mammoth==1.9.0: Converts .docx documents to simple HTML.
* matplotlib==3.10.0: Plotting with Python.
* mmbase: Local multimodal base utilities for this project.
* numpy==2.2.1: Fundamental package for scientific computing with Python.
* openai==1.58.1: Official Python library for the OpenAI API.
* opencv-python==4.10.0.84: Computer vision library.
* openpyxl==3.1.5: A Python library to read/write Excel 2010 xlsx/xlsm files.
* pandas==2.2.3: Data analysis and manipulation tool.
* pdfminer.six==20240706: A tool for extracting information from PDF documents.
* pillow==10.4.0: Python Imaging Library (Fork).
* pptx2md==2.0.6: A library to convert PowerPoint files to Markdown.
* PyMuPDF==1.25.1: A high-performance Python library for data extraction and manipulation of PDF documents.
* pytest==8.3.4: A framework for writing tests in Python.
* python-pptx==1.0.2: A library for creating and updating PowerPoint (.pptx) files.
* qdrant-client==1.12.1: The client for Qdrant, a vector similarity search engine.
* rank-bm25==0.2.2: A library for BM25 ranking.
* requests==2.32.3: HTTP for Humans.
* tiktoken==0.8.0: A fast BPE tokenizer for use with OpenAI's models.
* ... (and other dependencies listed in requirements.txt)


## Development Environment

To run this project, you need:
1.  **Python 3.12+**.
2.  An environment where you can install packages from `requirements.txt` and `requirements-dev.txt`.
3.  A `.env` file configured with necessary API keys (OpenAI, Qwen, Ark, etc.) and `PYTHONPATH=.`.
4.  Docker and Docker Compose for running services like Milvus or Qdrant if used.
5.  To install the local `mmbase` package by running `pip install -e ./mmbase` in the root directory.


## Structure (init from project tree)

```
root
- .cursor/ # Cursor IDE specific files
- .env # Environment variables
- .gitignore # Git ignore file
- README_MRAG.md # Main project README
- _ds_ref/ # Directory for data source references
- _ds_vdb/ # Directory for vector database storage
- _test/ # General testing directory
- clearn_prj.sh # Script to clean the project
- ctn2md/ # Content to Markdown: Core module for converting various document formats to Markdown.
    - converters/ # Specific converter implementations
    - gen_base/ # Base utilities for generation
    - gen_llamaparse/ # Generation using LlamaParse engine
    - gen_lvlm/ # Generation using Large Vision Language Models
    - gen_markitdown/ # Generation using Markitdown
    - gen_plain/ # Plain text to Markdown conversion
    - gen_pptx2md/ # PPTX to Markdown conversion
    - gen_textin/ # Generation using TextIn OCR
    - src/ # Source for post-processing and structuring Markdown
    - requirements.txt # Python dependencies for this module
- ctn2md_tests/ # Tests for the ctn2md module
- datasrc/ # Source data for the project, like raw documents and questions
    - test/
        - raw_docs/ # Raw documents for testing
        - raw_questions/ # Questions for testing
- docs/ # Project documentation
    - diagrams/ # Mermaid diagrams for architecture
    - images/ # Images used in documentation
- exams/ # Experimental scripts and explorations for various libraries and services
- logs/ # Log files
- mmbase/ # MultiModal Base: Shared core functionalities like logging, LLM interaction, etc.
    - utils/ # Utility functions
    - utils_llm/ # LLM related utilities
- mmbase_tests/ # Tests for the mmbase module
- mrag_app/ # MultiModal RAG Application: The Gradio web interface and application logic.
    - core/ # Core logic for QA and RAG
    - resources/ # CSS and other resources for the app
    - responses/ # Response generation logic
    - ui/ # UI components
- mrag_app_tests/ # Tests for the mrag_app module
- mrag_vdb/ # MultiModal RAG Vector Database: Handles document chunking, embedding, and storing in a vector DB.
    - common/ # Common data structures and utilities
    - dto/ # Data Transfer Objects
    - knowledge/ # Knowledge extraction and representation
    - query/ # Query processing and retrieval logic
    - rerank/ # Reranking logic for search results
    - utils/ # Utility functions
    - utils_llm/ # LLM utilities for VDB operations
- mrag_vdb_tests/ # Tests for the mrag_vdb module
- requirements.txt # Main project dependencies
- requirements-dev.txt # Development dependencies
- start_gradio.sh # Script to start the Gradio app
- stop_gradio.sh # Script to stop the Gradio app
- TODO.md # To-do list for the project
```