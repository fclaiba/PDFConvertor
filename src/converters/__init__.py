"""
Módulo de conversión de documentos.

Contiene los conversores de Word a PDF y el procesador paralelo.
"""

from .document_converter import DocumentConverter
from .pdf_generator import PDFGenerator
from .parallel_processor import ParallelProcessor

__all__ = ["DocumentConverter", "PDFGenerator", "ParallelProcessor"] 