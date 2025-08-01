# GUÍA PARA DESARROLLADORES - CONVERSOR DOC TO PDF

## 🏗️ Arquitectura del Sistema

### Estructura Modular
```
src/
├── main.py                 # Punto de entrada principal
├── cli.py                  # Interfaz de línea de comandos
├── config/                 # Gestión de configuración
│   ├── __init__.py
│   └── settings.py
├── converters/             # Motor de conversión
│   ├── __init__.py
│   ├── document_converter.py
│   ├── pdf_generator.py
│   └── parallel_processor.py
├── validators/             # Validación de archivos
│   ├── __init__.py
│   ├── file_validator.py
│   └── batch_validator.py
└── utils/                  # Utilidades comunes
    ├── __init__.py
    ├── exceptions.py
    ├── logger.py
    └── progress.py
```

### Principios de Diseño

#### 1. Separación de Responsabilidades
- **Converters**: Solo lógica de conversión
- **Validators**: Solo validación de archivos
- **Utils**: Funciones auxiliares reutilizables
- **CLI**: Solo interfaz de usuario

#### 2. Inyección de Dependencias
```python
class DocumentConverter:
    def __init__(self, validator: FileValidator, logger: Logger):
        self.validator = validator
        self.logger = logger
```

#### 3. Configuración Centralizada
```python
from src.config import config

# Usar configuración global
max_workers = config.max_workers
```

## 🔧 Configuración del Entorno de Desarrollo

### Requisitos
- Python 3.8+
- Git
- Virtual environment

### Instalación para Desarrollo
```bash
# Clonar repositorio
git clone <repository-url>
cd doc_to_pdf_converter

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install pytest pytest-cov black flake8 mypy pre-commit

# Configurar pre-commit hooks
pre-commit install
```

### Configuración de IDE

#### VS Code
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm
1. Configurar interpreter: `venv/bin/python`
2. Habilitar linting con flake8
3. Configurar formatter: Black
4. Configurar tests: pytest

## 🧪 Testing

### Estructura de Tests
```
tests/
├── conftest.py            # Configuración y fixtures
├── unit/                  # Tests unitarios
│   ├── test_config.py
│   └── test_validators.py
├── integration/           # Tests de integración
│   └── test_end_to_end.py
└── fixtures/              # Archivos de prueba
```

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Tests unitarios
pytest tests/unit/

# Tests de integración
pytest tests/integration/

# Con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/unit/test_config.py::TestConfig::test_config_default_values
```

### Escribir Tests

#### Test Unitario
```python
def test_validate_file_success(self, sample_docx_file, mock_magic):
    """Test que verifica la validación exitosa de un archivo."""
    validator = FileValidator()
    is_valid, error_msg = validator.validate_file(sample_docx_file)
    
    assert is_valid is True
    assert error_msg is None
```

#### Test de Integración
```python
@pytest.mark.integration
def test_convert_single_file_end_to_end(self, sample_docx_file, output_directory):
    """Test de conversión individual end-to-end."""
    output_path = Path(output_directory) / "test_output.pdf"
    
    converter = DocumentConverter()
    success = converter.convert_document(sample_docx_file, str(output_path))
    
    assert success is True
    assert output_path.exists()
    assert output_path.stat().st_size > 0
```

### Fixtures Comunes
```python
@pytest.fixture
def sample_docx_file(temp_dir):
    """Fixture que crea un archivo .docx de prueba."""
    from docx import Document
    
    doc = Document()
    doc.add_heading('Documento de Prueba', 0)
    doc.add_paragraph('Este es un párrafo de prueba.')
    
    file_path = Path(temp_dir) / "test_document.docx"
    doc.save(str(file_path))
    
    return str(file_path)
```

## 📝 Estándares de Código

### Formato
```bash
# Formatear código
black src/ tests/

# Verificar formato
black --check src/ tests/
```

### Linting
```bash
# Verificar estilo
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503

# Verificar tipos
mypy src/ --ignore-missing-imports
```

### Pre-commit Hooks
```bash
# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

### Convenciones de Nomenclatura

#### Variables y Funciones
```python
# Variables: snake_case
file_path = "/path/to/file.docx"
output_directory = "./output"

# Funciones: snake_case
def convert_document(input_path: str, output_path: str) -> bool:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 104857600
SUPPORTED_EXTENSIONS = [".doc", ".docx"]
```

#### Clases
```python
# Clases: PascalCase
class DocumentConverter:
    pass

class FileValidator:
    pass
```

#### Archivos y Directorios
```python
# Archivos Python: snake_case
document_converter.py
file_validator.py

# Directorios: snake_case
src/
tests/
docs/
```

### Documentación

#### Docstrings
```python
def convert_document(input_path: str, output_path: str) -> bool:
    """
    Convierte un documento Word a PDF.
    
    Args:
        input_path (str): Ruta del archivo de entrada
        output_path (str): Ruta del archivo de salida
        
    Returns:
        bool: True si la conversión fue exitosa
        
    Raises:
        ConversionError: Si hay un error en la conversión
        FileNotFoundError: Si el archivo de entrada no existe
    """
    pass
```

#### Type Hints
```python
from typing import List, Dict, Any, Optional

def process_files(
    file_paths: List[str], 
    output_dir: str,
    max_workers: Optional[int] = None
) -> Dict[str, Any]:
    pass
```

## 🔄 Flujo de Desarrollo

### 1. Crear Rama
```bash
git checkout -b feature/nueva-funcionalidad
```

### 2. Desarrollar
```bash
# Hacer cambios en el código
# Ejecutar tests
pytest

# Verificar calidad
pre-commit run --all-files
```

### 3. Commit
```bash
git add .
git commit -m "feat: agregar nueva funcionalidad

- Implementar validación de archivos grandes
- Agregar tests unitarios
- Actualizar documentación"
```

### 4. Push y Pull Request
```bash
git push origin feature/nueva-funcionalidad
# Crear Pull Request en GitHub
```

### Mensajes de Commit
```
feat: nueva funcionalidad
fix: corrección de bug
docs: documentación
style: formato de código
refactor: refactorización
test: tests
chore: tareas de mantenimiento
```

## 🐛 Debugging

### Logging
```python
import logging

logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("Información de debug")
    logger.info("Información general")
    logger.warning("Advertencia")
    logger.error("Error")
```

### Debug con pdb
```python
import pdb

def problematic_function():
    # ... código ...
    pdb.set_trace()  # Breakpoint
    # ... más código ...
```

### Debug con IDE
- **VS Code**: Configurar launch.json
- **PyCharm**: Configurar debug configuration

## 📊 Métricas y Monitoreo

### Cobertura de Código
```bash
# Generar reporte de cobertura
pytest --cov=src --cov-report=html --cov-report=xml

# Ver reporte
open htmlcov/index.html
```

### Análisis de Código
```bash
# Análisis de seguridad
bandit -r src/ -f json -o bandit-report.json

# Complejidad ciclomática
radon cc src/ -a

# Mantenibilidad
radon mi src/
```

## 🚀 Despliegue

### Build del Paquete
```bash
# Instalar build tools
pip install build twine

# Construir paquete
python -m build

# Verificar paquete
twine check dist/*
```

### Publicar en PyPI
```bash
# Subir a PyPI
twine upload dist/*

# Subir a TestPyPI (pruebas)
twine upload --repository testpypi dist/*
```

### Docker
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

ENTRYPOINT ["python", "src/main.py"]
```

## 🔧 Configuración Avanzada

### Configuración de Logging
```python
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/converter.log',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Configuración de Tests
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    manual: Manual tests
```

## 📚 Recursos Adicionales

### Documentación
- [Python Documentation](https://docs.python.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Click Documentation](https://click.palletsprojects.com/)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)

### Herramientas
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linter](https://flake8.pycqa.org/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)
- [Pre-commit Hooks](https://pre-commit.com/)

### Patrones de Diseño
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Design Patterns](https://refactoring.guru/design-patterns)
- [Clean Code](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350884)

---

**¡Contribuye al proyecto siguiendo estos estándares!** 🚀 