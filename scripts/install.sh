#!/bin/bash

# Script de instalación para el Conversor de Documentos Word a PDF
# Versión: 1.0.0

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  CONVERSOR DOC TO PDF - INSTALACIÓN${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Verificar Python
check_python() {
    print_message "Verificando Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_message "Python encontrado: $PYTHON_VERSION"
        
        # Verificar versión mínima (3.8)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_message "Versión de Python compatible ✓"
        else
            print_error "Se requiere Python 3.8 o superior"
            exit 1
        fi
    else
        print_error "Python 3 no encontrado. Por favor instale Python 3.8+"
        exit 1
    fi
}

# Verificar antiword
check_antiword() {
    print_message "Verificando antiword..."
    
    if command -v antiword &> /dev/null; then
        print_message "antiword encontrado ✓"
    else
        print_warning "antiword no encontrado. Instalando..."
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y antiword
            print_message "antiword instalado ✓"
        else
            print_error "No se pudo instalar antiword automáticamente. Por favor instálelo manualmente:"
            print_error "  Ubuntu/Debian: sudo apt install antiword"
            print_error "  CentOS/RHEL: sudo yum install antiword"
            print_error "  macOS: brew install antiword"
        fi
    fi
}

# Crear entorno virtual
create_venv() {
    print_message "Creando entorno virtual..."
    
    if [ -d "venv" ]; then
        print_warning "El entorno virtual ya existe. ¿Desea recrearlo? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            print_message "Usando entorno virtual existente"
            return
        fi
    fi
    
    python3 -m venv venv
    print_message "Entorno virtual creado ✓"
}

# Activar entorno virtual
activate_venv() {
    print_message "Activando entorno virtual..."
    source venv/bin/activate
    print_message "Entorno virtual activado ✓"
}

# Instalar dependencias
install_dependencies() {
    print_message "Instalando dependencias..."
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias principales
    pip install -r requirements.txt
    
    print_message "Dependencias principales instaladas ✓"
}

# Instalar dependencias de desarrollo (opcional)
install_dev_dependencies() {
    print_message "¿Desea instalar dependencias de desarrollo? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_message "Instalando dependencias de desarrollo..."
        pip install pytest pytest-cov black flake8 mypy pre-commit
        print_message "Dependencias de desarrollo instaladas ✓"
    fi
}

# Configurar pre-commit hooks
setup_pre_commit() {
    if command -v pre-commit &> /dev/null; then
        print_message "¿Desea configurar pre-commit hooks? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_message "Configurando pre-commit hooks..."
            pre-commit install
            print_message "Pre-commit hooks configurados ✓"
        fi
    fi
}

# Crear directorios necesarios
create_directories() {
    print_message "Creando directorios necesarios..."
    
    mkdir -p logs
    mkdir -p output
    mkdir -p tests/fixtures
    
    print_message "Directorios creados ✓"
}

# Ejecutar tests básicos
run_tests() {
    print_message "¿Desea ejecutar tests básicos? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_message "Ejecutando tests básicos..."
        
        if command -v pytest &> /dev/null; then
            python -m pytest tests/unit/ -v --tb=short
            print_message "Tests básicos completados ✓"
        else
            print_warning "pytest no encontrado. Omitiendo tests."
        fi
    fi
}

# Crear archivo de configuración
create_config() {
    print_message "¿Desea crear un archivo de configuración personalizado? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_message "Creando archivo de configuración..."
        
        cat > config.yaml << EOF
# Configuración del Conversor de Documentos Word a PDF
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
EOF
        
        print_message "Archivo config.yaml creado ✓"
    fi
}

# Mostrar información de uso
show_usage() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  INFORMACIÓN DE USO${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo -e "${GREEN}Para activar el entorno virtual:${NC}"
    echo "  source venv/bin/activate"
    echo ""
    echo -e "${GREEN}Para convertir un archivo:${NC}"
    echo "  python src/main.py convert archivo.docx"
    echo ""
    echo -e "${GREEN}Para convertir múltiples archivos:${NC}"
    echo "  python src/main.py batch directorio/ --workers 4"
    echo ""
    echo -e "${GREEN}Para validar archivos:${NC}"
    echo "  python src/main.py validate archivo.docx"
    echo ""
    echo -e "${GREEN}Para ver información del sistema:${NC}"
    echo "  python src/main.py info"
    echo ""
    echo -e "${GREEN}Para ejecutar tests:${NC}"
    echo "  python -m pytest tests/ -v"
    echo ""
    echo -e "${GREEN}Para formatear código:${NC}"
    echo "  black src/ tests/"
    echo ""
    echo -e "${BLUE}¡Instalación completada exitosamente!${NC}"
}

# Función principal
main() {
    print_header
    
    check_python
    check_antiword
    create_venv
    activate_venv
    install_dependencies
    install_dev_dependencies
    setup_pre_commit
    create_directories
    create_config
    run_tests
    
    show_usage
}

# Ejecutar función principal
main "$@" 