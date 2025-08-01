"""
Setup script para el conversor de documentos Word a PDF.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Leer requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name="doc-to-pdf-converter",
    version="1.0.0",
    author="Equipo de Desarrollo",
    author_email="dev@example.com",
    description="Conversor masivo de documentos Word (.doc/.docx) a PDF con procesamiento paralelo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/doc-to-pdf-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "doc2pdf=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    keywords="word doc docx pdf converter batch parallel processing",
    project_urls={
        "Bug Reports": "https://github.com/example/doc-to-pdf-converter/issues",
        "Source": "https://github.com/example/doc-to-pdf-converter",
        "Documentation": "https://github.com/example/doc-to-pdf-converter/docs",
    },
) 