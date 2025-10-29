"""
Setup configuration for MPSA package
Allows installation via: pip install -e .
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mpsa",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Amazon Market Sentiment Analysis - Analyze customer reviews using FinBERT and LDA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mpsa",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-cov>=4.1.0",
            "pytest-xdist>=3.5.0",
            "black>=23.12.0",
            "isort>=5.13.0",
            "flake8>=6.1.0",
            "pylint>=3.0.0",
            "mypy>=1.7.0",
        ],
        "api": [
            "fastapi>=0.109.0",
            "uvicorn>=0.27.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mpsa=main:main",
            "mpsa-api=api_server:main",
        ],
    },
)