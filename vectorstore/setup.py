"""
Setup script for vectorstore package.
"""

from setuptools import setup, find_packages

setup(
    name="vectorstore",
    version="1.0.0",
    description="ChromaDB-based vector storage and retrieval for RAG systems",
    author="AskMyDoc Team",
    packages=find_packages(),
    install_requires=[
        "chromadb>=0.5.0",
        "langchain-text-splitters>=0.3.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
