#!/usr/bin/env python3
"""Setup script for Therefore Configuration Processor."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README if it exists
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="theconfiguration-processor",
    version="1.0.0",
    description="Generate HTML documentation from Therefore configuration exports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Configuration Processor Team",
    python_requires=">=3.9",
    packages=find_packages(include=["src", "src.*"]),
    entry_points={
        "console_scripts": [
            "theconfiguration-processor=src.main:main",
        ],
        "gui_scripts": [
            "theconfiguration-processor-gui=src.gui:main",
        ],
    },
    install_requires=[],  # No external dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "build": [
            "pyinstaller>=5.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
