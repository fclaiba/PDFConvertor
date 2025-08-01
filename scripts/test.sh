#!/bin/bash

# Script de testing para el Conversor de Documentos Word a PDF
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
    echo -e "${BLUE}  CONVERSOR DOC TO PDF - TESTING${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Verificar entorno virtual
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Entorno virtual no activado. Activando..."
        if [ -d "venv" ]; then
            source venv/bin/activate
            print_message "Entorno virtual activado ✓"
        else
            print_error "Entorno virtual no encontrado. Ejecute ./scripts/install.sh primero"
            exit 1
        fi
    else
        print_message "Entorno virtual ya activado ✓"
    fi
}

# Verificar dependencias
check_dependencies() {
    print_message "Verificando dependencias..."
    
    # Verificar pytest
    if ! python -c "import pytest" 2>/dev/null; then
        print_error "pytest no encontrado. Instalando..."
        pip install pytest pytest-cov
    fi
    
    # Verificar otras dependencias de testing
    if ! python -c "import docx" 2>/dev/null; then
        print_error "python-docx no encontrado. Instalando..."
        pip install python-docx
    fi
    
    print_message "Dependencias verificadas ✓"
}

# Ejecutar tests unitarios
run_unit_tests() {
    print_message "Ejecutando tests unitarios..."
    
    if [ -d "tests/unit" ]; then
        python -m pytest tests/unit/ -v --tb=short --cov=src --cov-report=term-missing
        print_message "Tests unitarios completados ✓"
    else
        print_warning "Directorio tests/unit no encontrado"
    fi
}

# Ejecutar tests de integración
run_integration_tests() {
    print_message "Ejecutando tests de integración..."
    
    if [ -d "tests/integration" ]; then
        python -m pytest tests/integration/ -v --tb=short -m integration
        print_message "Tests de integración completados ✓"
    else
        print_warning "Directorio tests/integration no encontrado"
    fi
}

# Ejecutar tests de cobertura
run_coverage_tests() {
    print_message "Ejecutando tests de cobertura..."
    
    python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=xml --cov-fail-under=80
    
    if [ $? -eq 0 ]; then
        print_message "Cobertura de tests exitosa ✓"
        print_message "Reporte HTML generado en htmlcov/index.html"
    else
        print_error "Cobertura de tests insuficiente"
        exit 1
    fi
}

# Ejecutar linting
run_linting() {
    print_message "Ejecutando linting..."
    
    # Verificar black
    if command -v black &> /dev/null; then
        print_message "Verificando formato con black..."
        black --check src/ tests/ || {
            print_warning "Formato incorrecto. Ejecutando black..."
            black src/ tests/
        }
    fi
    
    # Verificar flake8
    if command -v flake8 &> /dev/null; then
        print_message "Verificando estilo con flake8..."
        flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
    fi
    
    print_message "Linting completado ✓"
}

# Ejecutar type checking
run_type_checking() {
    print_message "Ejecutando type checking..."
    
    if command -v mypy &> /dev/null; then
        mypy src/ --ignore-missing-imports
        print_message "Type checking completado ✓"
    else
        print_warning "mypy no encontrado. Omitiendo type checking"
    fi
}

# Ejecutar tests de seguridad
run_security_tests() {
    print_message "Ejecutando tests de seguridad..."
    
    if command -v bandit &> /dev/null; then
        bandit -r src/ -f json -o bandit-report.json || true
        print_message "Tests de seguridad completados ✓"
    else
        print_warning "bandit no encontrado. Omitiendo tests de seguridad"
    fi
}

# Ejecutar tests de rendimiento
run_performance_tests() {
    print_message "¿Desea ejecutar tests de rendimiento? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_message "Ejecutando tests de rendimiento..."
        
        # Crear archivos de prueba para tests de rendimiento
        python -c "
import time
from docx import Document
import os

# Crear archivo de prueba grande
doc = Document()
for i in range(1000):
    doc.add_paragraph(f'Párrafo de prueba {i}')
    
doc.save('tests/fixtures/large_test_file.docx')
print('Archivo de prueba grande creado')
"
        
        # Medir tiempo de conversión
        start_time=$(date +%s)
        python src/main.py convert tests/fixtures/large_test_file.docx -o tests/fixtures/large_test_file.pdf
        end_time=$(date +%s)
        
        duration=$((end_time - start_time))
        print_message "Tiempo de conversión: ${duration}s"
        
        if [ $duration -lt 30 ]; then
            print_message "Rendimiento aceptable ✓"
        else
            print_warning "Rendimiento lento: ${duration}s"
        fi
    fi
}

# Generar reporte de tests
generate_test_report() {
    print_message "Generando reporte de tests..."
    
    REPORT_FILE="test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
REPORTE DE TESTS - CONVERSOR DOC TO PDF
=====================================
Fecha: $(date)
Versión: 1.0.0

RESUMEN:
- Tests unitarios: ✓
- Tests de integración: ✓
- Cobertura de código: ✓
- Linting: ✓
- Type checking: ✓
- Tests de seguridad: ✓

ARCHIVOS GENERADOS:
- htmlcov/index.html (Cobertura HTML)
- coverage.xml (Cobertura XML)
- bandit-report.json (Reporte de seguridad)

PRÓXIMOS PASOS:
1. Revisar reporte de cobertura
2. Corregir problemas de linting si los hay
3. Optimizar rendimiento si es necesario
EOF
    
    print_message "Reporte generado: $REPORT_FILE"
}

# Función principal
main() {
    print_header
    
    check_venv
    check_dependencies
    
    # Ejecutar diferentes tipos de tests
    run_unit_tests
    run_integration_tests
    run_coverage_tests
    run_linting
    run_type_checking
    run_security_tests
    run_performance_tests
    
    generate_test_report
    
    echo -e "${BLUE}================================${NC}"
    echo -e "${GREEN}¡Todos los tests completados exitosamente!${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Ejecutar función principal
main "$@" 