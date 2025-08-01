#!/usr/bin/env python3
"""
Conversor de Documentos Word a PDF
==================================

Aplicación principal para convertir archivos .doc/.docx a PDF
con procesamiento paralelo y alta eficiencia.

Uso:
    python src/main.py convert archivo.docx
    python src/main.py batch directorio/ --workers 8
    python src/main.py validate archivo.docx
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from cli import main

if __name__ == '__main__':
    main() 