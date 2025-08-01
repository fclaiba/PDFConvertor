"""
Tests unitarios para los módulos de validación.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, Mock

from src.validators.file_validator import FileValidator, validate_file, validate_directory
from src.validators.batch_validator import BatchValidator


class TestFileValidator:
    """Tests para la clase FileValidator."""
    
    def test_file_validator_init(self):
        """Test que verifica la inicialización del validador."""
        validator = FileValidator()
        
        assert validator.supported_extensions == [".doc", ".docx"]
        assert validator.max_file_size == 104857600
    
    def test_validate_file_success(self, sample_docx_file, mock_magic):
        """Test que verifica la validación exitosa de un archivo."""
        validator = FileValidator()
        is_valid, error_msg = validator.validate_file(sample_docx_file)
        
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_file_not_found(self):
        """Test que verifica la validación de archivo inexistente."""
        validator = FileValidator()
        is_valid, error_msg = validator.validate_file("nonexistent.docx")
        
        assert is_valid is False
        assert "Archivo no encontrado" in error_msg
    
    def test_validate_file_invalid_extension(self, temp_dir):
        """Test que verifica la validación de extensión inválida."""
        # Crear archivo con extensión inválida
        file_path = Path(temp_dir) / "test.txt"
        file_path.write_text("Contenido de prueba")
        
        validator = FileValidator()
        is_valid, error_msg = validator.validate_file(str(file_path))
        
        assert is_valid is False
        assert "Extensión no soportada" in error_msg
    
    def test_validate_file_too_large(self, large_file):
        """Test que verifica la validación de archivo demasiado grande."""
        validator = FileValidator()
        is_valid, error_msg = validator.validate_file(large_file)
        
        assert is_valid is False
        assert "Archivo demasiado grande" in error_msg
    
    def test_validate_directory_success(self, temp_dir, sample_files_list):
        """Test que verifica la validación exitosa de un directorio."""
        validator = FileValidator()
        is_valid, error_msg = validator.validate_directory(temp_dir)
        
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_directory_not_found(self):
        """Test que verifica la validación de directorio inexistente."""
        validator = FileValidator()
        is_valid, error_msg = validator.validate_directory("/nonexistent/dir")
        
        assert is_valid is False
        assert "Directorio no encontrado" in error_msg
    
    def test_validate_directory_no_valid_files(self, temp_dir):
        """Test que verifica la validación de directorio sin archivos válidos."""
        # Crear directorio vacío
        empty_dir = Path(temp_dir) / "empty"
        empty_dir.mkdir()
        
        validator = FileValidator()
        is_valid, error_msg = validator.validate_directory(str(empty_dir))
        
        assert is_valid is False
        assert "No se encontraron archivos válidos" in error_msg
    
    def test_get_valid_files_in_directory(self, temp_dir, sample_files_list):
        """Test que verifica la obtención de archivos válidos en directorio."""
        validator = FileValidator()
        valid_files = validator.get_valid_files_in_directory(temp_dir)
        
        assert len(valid_files) == 5
        assert all(f.endswith('.docx') for f in valid_files)
    
    def test_get_file_info(self, sample_docx_file):
        """Test que verifica la obtención de información de archivo."""
        validator = FileValidator()
        file_info = validator.get_file_info(sample_docx_file)
        
        assert file_info['name'] == 'test_document.docx'
        assert file_info['extension'] == '.docx'
        assert file_info['size_bytes'] > 0
        assert file_info['is_readable'] is True


class TestBatchValidator:
    """Tests para la clase BatchValidator."""
    
    def test_batch_validator_init(self):
        """Test que verifica la inicialización del validador de lotes."""
        validator = BatchValidator()
        
        assert validator.max_files_per_batch == 100
        assert isinstance(validator.file_validator, FileValidator)
    
    def test_validate_batch_success(self, sample_files_list):
        """Test que verifica la validación exitosa de un lote."""
        validator = BatchValidator()
        result = validator.validate_batch(sample_files_list)
        
        assert len(result['valid']) == 5
        assert len(result['invalid']) == 0
        assert len(result['errors']) == 0
    
    def test_validate_batch_with_invalid_files(self, sample_files_list, invalid_file):
        """Test que verifica la validación de lote con archivos inválidos."""
        files = sample_files_list + [invalid_file]
        validator = BatchValidator()
        result = validator.validate_batch(files)
        
        assert len(result['valid']) == 5
        assert len(result['invalid']) == 1
        assert len(result['errors']) == 1
    
    def test_validate_batch_too_many_files(self):
        """Test que verifica el límite de archivos por lote."""
        # Crear lista con más de 100 archivos
        many_files = [f"file_{i}.docx" for i in range(150)]
        
        validator = BatchValidator()
        result = validator.validate_batch(many_files)
        
        assert len(result['valid']) == 0
        assert len(result['invalid']) == 150
        assert "Demasiados archivos" in result['errors'][0]
    
    def test_validate_directory_batch(self, temp_dir, sample_files_list):
        """Test que verifica la validación de directorio en lote."""
        validator = BatchValidator()
        result = validator.validate_directory_batch(temp_dir)
        
        assert len(result['valid']) == 5
        assert len(result['invalid']) == 0
    
    def test_validate_mixed_input(self, temp_dir, sample_files_list, invalid_file):
        """Test que verifica la validación de entrada mixta."""
        # Crear subdirectorio con archivos
        subdir = Path(temp_dir) / "subdir"
        subdir.mkdir()
        
        # Mover algunos archivos al subdirectorio
        for i, file_path in enumerate(sample_files_list[:2]):
            Path(file_path).rename(subdir / f"moved_{i}.docx")
        
        mixed_input = [
            temp_dir,  # directorio
            sample_files_list[2],  # archivo individual
            invalid_file  # archivo inválido
        ]
        
        validator = BatchValidator()
        result = validator.validate_mixed_input(mixed_input)
        
        assert len(result['valid']) >= 3  # 2 del subdir + 1 individual
        assert len(result['invalid']) >= 1  # archivo inválido
    
    def test_get_batch_statistics(self):
        """Test que verifica el cálculo de estadísticas del lote."""
        validator = BatchValidator()
        
        validation_result = {
            'valid': ['file1.docx', 'file2.docx', 'file3.docx'],
            'invalid': ['file4.txt'],
            'errors': ['file4.txt: Extensión no soportada']
        }
        
        stats = validator.get_batch_statistics(validation_result)
        
        assert stats['total_files'] == 4
        assert stats['valid_files'] == 3
        assert stats['invalid_files'] == 1
        assert stats['success_rate'] == 75.0
        assert stats['error_count'] == 1
    
    def test_filter_by_size(self, sample_files_list):
        """Test que verifica el filtrado por tamaño."""
        validator = BatchValidator()
        
        # Filtrar con límite pequeño
        filtered = validator.filter_by_size(sample_files_list, max_size_mb=0.001)
        
        assert len(filtered) == 0  # Todos los archivos son más grandes
    
    def test_sort_by_size(self, sample_files_list):
        """Test que verifica el ordenamiento por tamaño."""
        validator = BatchValidator()
        
        # Ordenar por tamaño ascendente
        sorted_files = validator.sort_by_size(sample_files_list, reverse=False)
        
        assert len(sorted_files) == len(sample_files_list)
        # Verificar que están ordenados (todos tienen tamaño similar en este caso)


class TestValidationFunctions:
    """Tests para las funciones de conveniencia."""
    
    def test_validate_file_function(self, sample_docx_file, mock_magic):
        """Test que verifica la función validate_file."""
        is_valid, error_msg = validate_file(sample_docx_file)
        
        assert is_valid is True
        assert error_msg is None
    
    def test_validate_directory_function(self, temp_dir, sample_files_list):
        """Test que verifica la función validate_directory."""
        is_valid, error_msg = validate_directory(temp_dir)
        
        assert is_valid is True
        assert error_msg is None 