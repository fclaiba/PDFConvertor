# REGLAMENTO DE DESARROLLO - CONVERSOR DOC/DOCX A PDF

## 1. ESTÁNDARES DE CÓDIGO

### 1.1 Convenciones de Nomenclatura

#### 1.1.1 Variables y Funciones
- **Variables**: snake_case (ej: `file_path`, `output_directory`)
- **Funciones**: snake_case (ej: `convert_document()`, `validate_file()`)
- **Constantes**: UPPER_SNAKE_CASE (ej: `MAX_FILE_SIZE`, `SUPPORTED_EXTENSIONS`)
- **Clases**: PascalCase (ej: `DocumentConverter`, `FileValidator`)

#### 1.1.2 Archivos y Directorios
- **Archivos Python**: snake_case (ej: `document_converter.py`, `file_validator.py`)
- **Directorios**: snake_case (ej: `src/`, `tests/`, `docs/`)
- **Archivos de configuración**: kebab-case (ej: `config.yaml`, `logging-config.json`)

### 1.2 Estructura de Código

#### 1.2.1 Imports
```python
# Imports de la biblioteca estándar
import os
import sys
from pathlib import Path

# Imports de terceros
import click
from docx import Document

# Imports locales
from .converters import DocumentConverter
from .validators import FileValidator
```

#### 1.2.2 Documentación de Funciones
```python
def convert_document(input_path: str, output_path: str) -> bool:
    """
    Convierte un documento Word a PDF.
    
    Args:
        input_path (str): Ruta del archivo de entrada
        output_path (str): Ruta del archivo de salida
        
    Returns:
        bool: True si la conversión fue exitosa, False en caso contrario
        
    Raises:
        FileNotFoundError: Si el archivo de entrada no existe
        PermissionError: Si no hay permisos para leer/escribir archivos
    """
    pass
```

### 1.3 Gestión de Errores

#### 1.3.1 Excepciones Personalizadas
```python
class ConversionError(Exception):
    """Excepción base para errores de conversión."""
    pass

class FileValidationError(ConversionError):
    """Excepción para errores de validación de archivos."""
    pass

class PDFGenerationError(ConversionError):
    """Excepción para errores de generación de PDF."""
    pass
```

#### 1.3.2 Manejo de Errores
```python
try:
    result = convert_document(input_file, output_file)
except FileNotFoundError as e:
    logger.error(f"Archivo no encontrado: {e}")
    return False
except PermissionError as e:
    logger.error(f"Error de permisos: {e}")
    return False
except ConversionError as e:
    logger.error(f"Error de conversión: {e}")
    return False
```

## 2. ARQUITECTURA DEL PROYECTO

### 2.1 Estructura de Directorios
```
doc_to_pdf_converter/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada principal
│   ├── cli.py                  # Interfaz de línea de comandos
│   ├── converters/             # Módulos de conversión
│   │   ├── __init__.py
│   │   ├── document_converter.py
│   │   └── pdf_generator.py
│   ├── validators/             # Módulos de validación
│   │   ├── __init__.py
│   │   └── file_validator.py
│   ├── utils/                  # Utilidades
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── progress.py
│   └── config/                 # Configuración
│       ├── __init__.py
│       └── settings.py
├── tests/                      # Tests unitarios y de integración
├── docs/                       # Documentación
├── logs/                       # Archivos de log
├── requirements.txt            # Dependencias
├── setup.py                   # Configuración de instalación
└── README.md                  # Documentación principal
```

### 2.2 Principios de Diseño

#### 2.2.1 Separación de Responsabilidades
- **Converters**: Solo lógica de conversión
- **Validators**: Solo validación de archivos
- **Utils**: Funciones auxiliares reutilizables
- **CLI**: Solo interfaz de usuario

#### 2.2.2 Inyección de Dependencias
```python
class DocumentConverter:
    def __init__(self, validator: FileValidator, logger: Logger):
        self.validator = validator
        self.logger = logger
```

## 3. ESTÁNDARES DE TESTING

### 3.1 Cobertura de Tests
- **Mínimo 80%** de cobertura de código
- Tests para todos los casos de uso principales
- Tests para manejo de errores
- Tests de integración para flujos completos

### 3.2 Estructura de Tests
```python
class TestDocumentConverter:
    def setup_method(self):
        """Configuración antes de cada test."""
        self.converter = DocumentConverter()
        self.test_file = "tests/fixtures/test_document.docx"
    
    def test_convert_valid_document(self):
        """Test de conversión de documento válido."""
        result = self.converter.convert(self.test_file, "output.pdf")
        assert result is True
        assert os.path.exists("output.pdf")
    
    def test_convert_invalid_file(self):
        """Test de conversión de archivo inválido."""
        with pytest.raises(FileValidationError):
            self.converter.convert("nonexistent.docx", "output.pdf")
```

### 3.3 Fixtures de Test
- Archivos de prueba reales en `tests/fixtures/`
- Mocks para dependencias externas
- Datos de prueba consistentes

## 4. GESTIÓN DE CONFIGURACIÓN

### 4.1 Archivos de Configuración
```yaml
# config.yaml
conversion:
  max_file_size: 104857600  # 100MB
  supported_extensions: [".doc", ".docx"]
  output_quality: "high"
  
processing:
  max_workers: 4
  timeout: 300  # 5 minutos
  
logging:
  level: "INFO"
  file: "logs/converter.log"
  max_size: 10485760  # 10MB
```

### 4.2 Variables de Entorno
```bash
# .env
CONVERTER_MAX_WORKERS=4
CONVERTER_LOG_LEVEL=INFO
CONVERTER_OUTPUT_DIR=./output
```

## 5. LOGGING Y MONITOREO

### 5.1 Estructura de Logs
```python
import logging

logger = logging.getLogger(__name__)

def convert_document(input_path: str, output_path: str) -> bool:
    logger.info(f"Iniciando conversión: {input_path} -> {output_path}")
    try:
        # Proceso de conversión
        logger.info(f"Conversión exitosa: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error en conversión: {e}")
        return False
```

### 5.2 Niveles de Log
- **DEBUG**: Información detallada para desarrollo
- **INFO**: Información general del proceso
- **WARNING**: Advertencias no críticas
- **ERROR**: Errores que afectan la funcionalidad
- **CRITICAL**: Errores que impiden continuar

## 6. GESTIÓN DE DEPENDENCIAS

### 6.1 Versionado
- Usar versiones específicas en `requirements.txt`
- Actualizar dependencias regularmente
- Verificar compatibilidad antes de actualizar

### 6.2 Dependencias de Desarrollo
```txt
# requirements-dev.txt
pytest==7.4.0
pytest-cov==4.1.0
black==23.7.0
flake8==6.0.0
mypy==1.5.1
```

## 7. ESTÁNDARES DE SEGURIDAD

### 7.1 Validación de Entrada
- Validar todas las rutas de archivo
- Sanitizar nombres de archivo
- Verificar permisos antes de operaciones

### 7.2 Manejo de Archivos
- Usar rutas absolutas cuando sea posible
- Verificar espacio en disco antes de escribir
- Limpiar archivos temporales

## 8. PROCESO DE DESARROLLO

### 8.1 Flujo de Trabajo Git
1. Crear rama feature: `git checkout -b feature/nombre-funcionalidad`
2. Desarrollar y testear
3. Commit con mensaje descriptivo: `git commit -m "feat: agregar validación de archivos"`
4. Push y crear Pull Request
5. Code review obligatorio
6. Merge a main

### 8.2 Mensajes de Commit
```
feat: nueva funcionalidad
fix: corrección de bug
docs: documentación
style: formato de código
refactor: refactorización
test: tests
chore: tareas de mantenimiento
```

### 8.3 Code Review
- Revisar lógica de negocio
- Verificar estándares de código
- Comprobar cobertura de tests
- Validar documentación 