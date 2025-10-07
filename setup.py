"""
Setup script for Stock and Crypto Automated Analysis
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Stock and Crypto Automated Analysis Tool"

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="stock-crypto-analyzer",
    version="2.0.0",
    description="Comprehensive Stock and Crypto Analysis Tool with Technical and Fundamental Analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/stock-crypto-analyzer",
    packages=find_packages(),
    py_modules=["SC_Automated_Analysis"],
    install_requires=read_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    entry_points={
        "console_scripts": [
            "stock-crypto-analyzer=SC_Automated_Analysis:main",
        ],
    },
    keywords="stock, crypto, analysis, trading, finance, technical analysis, fundamental analysis",
    include_package_data=True,
)
