# GUÍA DE USUARIO - CONVERSOR DOC TO PDF

## 🚀 Inicio Rápido

### Instalación
```bash
# Clonar el repositorio
git clone <repository-url>
cd doc_to_pdf_converter

# Ejecutar instalación automática
./scripts/install.sh
```

### Uso Básico
```bash
# Activar entorno virtual
source venv/bin/activate

# Convertir un archivo
python src/main.py convert documento.docx

# Convertir múltiples archivos
python src/main.py batch directorio/ --workers 4
```

## 📖 Comandos Disponibles

### 1. Conversión Individual
```bash
python src/main.py convert <archivo> [opciones]
```

**Ejemplos:**
```bash
# Conversión básica
python src/main.py convert documento.docx

# Especificar ruta de salida
python src/main.py convert documento.docx -o /ruta/salida/documento.pdf

# Configurar calidad
python src/main.py convert documento.docx --quality high
```

**Opciones:**
- `--output, -o`: Ruta del archivo PDF de salida
- `--quality`: Calidad del PDF (low/medium/high)

### 2. Conversión Masiva
```bash
python src/main.py batch <archivos_o_directorios> [opciones]
```

**Ejemplos:**
```bash
# Convertir archivos específicos
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

**Opciones:**
- `--output-dir, -o`: Directorio de salida para PDFs
- `--workers, -w`: Número de workers paralelos (default: 4)
- `--quality`: Calidad del PDF (low/medium/high)
- `--recursive, -r`: Procesar subdirectorios recursivamente

### 3. Validación
```bash
python src/main.py validate <archivo_o_directorio>
```

**Ejemplos:**
```bash
# Validar un archivo
python src/main.py validate archivo.docx

# Validar un directorio
python src/main.py validate directorio/
```

### 4. Información del Sistema
```bash
python src/main.py info
```

Muestra información sobre:
- Configuración actual
- Recursos del sistema
- Extensiones soportadas
- Configuración de logging

### 5. Tests del Sistema
```bash
python src/main.py test [opciones]
```

**Ejemplos:**
```bash
# Tests básicos
python src/main.py test

# Especificar directorio de salida
python src/main.py test --output-dir ./test_output/
```

## ⚙️ Configuración

### Archivo de Configuración (config.yaml)
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
# Configurar workers
export CONVERTER_MAX_WORKERS=8

# Configurar nivel de logging
export CONVERTER_LOG_LEVEL=DEBUG

# Configurar directorio de salida
export CONVERTER_OUTPUT_DIR=./pdfs/

# Configurar tamaño máximo de archivo
export CONVERTER_MAX_FILE_SIZE=209715200  # 200MB

# Configurar timeout
export CONVERTER_TIMEOUT=600  # 10 minutos
```

## 🔧 Opciones Avanzadas

### Opciones Globales
```bash
# Modo verbose (más información)
python src/main.py --verbose convert archivo.docx

# Modo silencioso (solo errores)
python src/main.py --quiet batch directorio/

# Archivo de configuración personalizado
python src/main.py --config mi_config.yaml convert archivo.docx
```

### Optimización de Rendimiento

#### Para Archivos Grandes
```bash
# Reducir workers para archivos grandes
python src/main.py batch directorio/ --workers 2

# Usar calidad media para mayor velocidad
python src/main.py batch directorio/ --quality medium
```

#### Para Muchos Archivos
```bash
# Aumentar workers para procesamiento paralelo
python src/main.py batch directorio/ --workers 8

# Usar calidad alta para mejor resultado
python src/main.py batch directorio/ --quality high
```

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real
```bash
# Ver logs en tiempo real
tail -f logs/converter.log

# Ver solo errores
grep "ERROR" logs/converter.log

# Ver logs de una conversión específica
grep "documento.docx" logs/converter.log
```

### Niveles de Log
- **DEBUG**: Información detallada para desarrollo
- **INFO**: Información general del proceso
- **WARNING**: Advertencias no críticas
- **ERROR**: Errores que afectan la funcionalidad
- **CRITICAL**: Errores que impiden continuar

## 🐛 Solución de Problemas

### Problemas Comunes

#### 1. "Archivo no encontrado"
```bash
# Verificar que el archivo existe
ls -la archivo.docx

# Verificar permisos
chmod +r archivo.docx
```

#### 2. "Extensión no soportada"
- Solo se soportan archivos .doc y .docx
- Verificar la extensión del archivo
- Renombrar si es necesario

#### 3. "Archivo demasiado grande"
```bash
# Verificar tamaño del archivo
ls -lh archivo.docx

# Aumentar límite en configuración
export CONVERTER_MAX_FILE_SIZE=209715200  # 200MB
```

#### 4. "Memoria insuficiente"
```bash
# Reducir número de workers
python src/main.py batch directorio/ --workers 2

# Procesar archivos en lotes más pequeños
```

#### 5. "Timeout"
```bash
# Aumentar timeout
export CONVERTER_TIMEOUT=600  # 10 minutos

# Usar calidad más baja
python src/main.py convert archivo.docx --quality low
```

### Verificación del Sistema
```bash
# Verificar instalación
python src/main.py test

# Verificar información del sistema
python src/main.py info

# Verificar dependencias
pip list | grep -E "(docx|reportlab|click)"
```

## 📈 Mejores Prácticas

### 1. Organización de Archivos
```bash
# Estructura recomendada
proyectos/
├── documentos_originales/
│   ├── proyecto1/
│   └── proyecto2/
├── documentos_pdf/
│   ├── proyecto1/
│   └── proyecto2/
└── logs/
```

### 2. Procesamiento Eficiente
```bash
# Procesar por lotes
python src/main.py batch proyecto1/ -o pdfs/proyecto1/

# Usar workers apropiados
python src/main.py batch proyecto2/ --workers 4 -o pdfs/proyecto2/
```

### 3. Monitoreo
```bash
# Ver progreso en tiempo real
python src/main.py batch directorio/ --verbose

# Revisar logs después del procesamiento
tail -n 50 logs/converter.log
```

### 4. Backup
```bash
# Hacer backup antes de procesar
cp -r documentos_originales/ backup/

# Verificar archivos procesados
ls -la documentos_pdf/
```

## 🔄 Automatización

### Script de Procesamiento Automático
```bash
#!/bin/bash
# procesar_documentos.sh

echo "Iniciando procesamiento de documentos..."

# Procesar directorio 1
python src/main.py batch documentos/proyecto1/ -o pdfs/proyecto1/ --workers 4

# Procesar directorio 2
python src/main.py batch documentos/proyecto2/ -o pdfs/proyecto2/ --workers 4

# Generar reporte
echo "Procesamiento completado. Revisar logs en logs/converter.log"
```

### Cron Job (Linux/Mac)
```bash
# Editar crontab
crontab -e

# Ejecutar diariamente a las 2 AM
0 2 * * * /ruta/completa/a/procesar_documentos.sh
```

## 📞 Soporte

### Información de Contacto
- **Email**: soporte@doc-to-pdf-converter.com
- **Documentación**: https://github.com/example/doc-to-pdf-converter/docs
- **Issues**: https://github.com/example/doc-to-pdf-converter/issues

### Información para Reportes de Error
Al reportar un error, incluir:
1. Comando ejecutado
2. Mensaje de error completo
3. Versión del sistema
4. Contenido de logs/converter.log
5. Información del archivo (tamaño, extensión)

### Ejemplo de Reporte
```
Comando: python src/main.py convert documento.docx
Error: FileNotFoundError: [Errno 2] No such file or directory: 'documento.docx'
Sistema: Ubuntu 20.04, Python 3.8.10
Archivo: documento.docx (2.5MB, .docx)
Logs: [adjuntar contenido relevante]
```

---

**¡Disfruta convirtiendo tus documentos de manera eficiente!** 🚀 