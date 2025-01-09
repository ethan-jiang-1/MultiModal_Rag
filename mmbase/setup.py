from setuptools import setup, find_packages

setup(
    name="mmbase",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "colorlog",
        "psutil",
    ],
    extras_require={
        'test': [
            'freezegun',
            'pytest',
            'pytest-cov',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Base utilities for MultiModal RAG system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/MultiModal_Rag",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 