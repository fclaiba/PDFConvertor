# Conversor de Documentos Word a PDF

Un conversor masivo de archivos Microsoft Word (.doc/.docx) a PDF con procesamiento paralelo, desarrollado en Python siguiendo metodología Scrum.

## 🚀 Características

- **Conversión Masiva**: Procesa +30 archivos simultáneamente
- **Procesamiento Paralelo**: Optimizado para máxima velocidad
- **Soporte Completo**: Archivos .doc y .docx (usando antiword para .doc)
- **Interfaz CLI**: Fácil de usar desde terminal
- **Validación Robusta**: Verificación completa de archivos
- **Logging Avanzado**: Seguimiento detallado del proceso
- **Configuración Flexible**: Personalizable via archivos y variables de entorno

## 📋 Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`
- **antiword** (para archivos .doc): `sudo apt install antiword`

## 🛠️ Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd doc_to_pdf_converter
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Conversión Individual

```bash
# Convertir un archivo
python src/main.py convert documento.docx

# Especificar ruta de salida
python src/main.py convert documento.docx -o /ruta/salida/documento.pdf

# Configurar calidad
python src/main.py convert documento.docx --quality high
```

### Conversión Masiva

```bash
# Convertir múltiples archivos
python src/main.py batch archivo1.docx archivo2.docx archivo3.docx

# Convertir todos los archivos de un directorio
python src/main.py batch directorio/

# Procesamiento recursivo
python src/main.py batch directorio/ --recursive

# Configurar workers paralelos
python src/main.py batch directorio/ --workers 8

# Especificar directorio de salida
python src/main.py batch directorio/ -o ./pdfs/
```

### Validación

```bash
# Validar un archivo
python src/main.py validate archivo.docx

# Validar un directorio
python src/main.py validate directorio/
```

### Información del Sistema

```bash
# Ver información de configuración
python src/main.py info

# Ejecutar tests básicos
python src/main.py test
```

## 📖 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `convert` | Convierte un archivo individual |
| `batch` | Convierte múltiples archivos en paralelo |
| `validate` | Valida archivos sin convertirlos |
| `info` | Muestra información del sistema |
| `test` | Ejecuta tests básicos |

### Opciones Globales

- `--verbose, -v`: Modo verbose (más información)
- `--quiet, -q`: Modo silencioso (solo errores)
- `--config, -c`: Archivo de configuración personalizado

### Opciones de Conversión

- `--output, -o`: Ruta de salida
- `--quality`: Calidad del PDF (low/medium/high)
- `--workers, -w`: Número de workers paralelos
- `--recursive, -r`: Procesar subdirectorios recursivamente

## ⚙️ Configuración

### Archivo de Configuración

Crear `config.yaml` en el directorio raíz:

```yaml
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

### Variables de Entorno

```bash
export CONVERTER_MAX_WORKERS=8
export CONVERTER_LOG_LEVEL=DEBUG
export CONVERTER_OUTPUT_DIR=./pdfs/
export CONVERTER_MAX_FILE_SIZE=209715200  # 200MB
```

## 📊 Rendimiento

- **Velocidad**: +30 archivos en <5 minutos
- **Memoria**: <2GB RAM por proceso
- **Tasa de Éxito**: >95% conversiones exitosas
- **Escalabilidad**: Optimizado para múltiples CPUs

## 🏗️ Arquitectura

```
doc_to_pdf_converter/
├── src/
│   ├── main.py                 # Punto de entrada
│   ├── cli.py                  # Interfaz de línea de comandos
│   ├── config/                 # Configuración del sistema
│   ├── converters/             # Módulos de conversión
│   ├── validators/             # Validación de archivos
│   └── utils/                  # Utilidades y logging
├── docs/                       # Documentación técnica
├── tests/                      # Tests unitarios y de integración
├── logs/                       # Archivos de log
└── requirements.txt            # Dependencias
```

## 🔧 Desarrollo

### Estructura Modular

- **Config**: Gestión centralizada de configuración
- **Validators**: Validación robusta de archivos y directorios
- **Converters**: Motor de conversión y procesamiento paralelo
- **Utils**: Logging, progreso y manejo de errores
- **CLI**: Interfaz de usuario intuitiva

### Estándares de Código

- **PEP 8**: Formato de código Python
- **Type Hints**: Tipado estático
- **Docstrings**: Documentación completa
- **Logging**: Sistema de logs estructurado
- **Testing**: Cobertura >80%

## 📈 Metodología Scrum

### Sprints Completados

1. **Sprint 1**: Infraestructura Base ✅
2. **Sprint 2**: Validación de Archivos ✅
3. **Sprint 3**: Conversión Básica ✅
4. **Sprint 4**: Conversión Avanzada ✅
5. **Sprint 5**: Procesamiento Paralelo ✅
6. **Sprint 6**: Interfaz CLI ✅

### Próximos Sprints

7. **Sprint 7**: Testing y Calidad
8. **Sprint 8**: Documentación y Entrega

## 🐛 Solución de Problemas

### Errores Comunes

1. **Archivo no encontrado**: Verificar ruta y permisos
2. **Formato no soportado**: Solo .doc y .docx
3. **Memoria insuficiente**: Reducir número de workers
4. **Timeout**: Aumentar límite de tiempo en configuración

### Logs

Los logs se guardan en `logs/converter.log` con rotación automática.

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'feat: agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles.

## 👥 Autores

- Equipo de Desarrollo
- Metodología Scrum implementada
- Documentación técnica completa

## 🎯 Roadmap

- [ ] Soporte para más formatos (PPT, XLS)
- [ ] Interfaz web opcional
- [ ] API REST
- [ ] Docker container
- [ ] Integración con servicios en la nube

---

**¡Convierte tus documentos de manera eficiente y profesional!** 🚀 