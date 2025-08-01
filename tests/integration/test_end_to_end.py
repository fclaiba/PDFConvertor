"""
Tests de integración end-to-end para el conversor de documentos.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch

from src.cli import cli
from src.converters import DocumentConverter, ParallelProcessor
from src.validators import BatchValidator


class TestEndToEnd:
    """Tests de integración end-to-end."""
    
    @pytest.mark.integration
    def test_convert_single_file_end_to_end(self, sample_docx_file, output_directory):
        """Test de conversión individual end-to-end."""
        output_path = Path(output_directory) / "test_output.pdf"
        
        # Usar el conversor directamente
        converter = DocumentConverter()
        success = converter.convert_document(sample_docx_file, str(output_path))
        
        assert success is True
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    
    @pytest.mark.integration
    def test_batch_conversion_end_to_end(self, sample_files_list, output_directory):
        """Test de conversión masiva end-to-end."""
        # Usar el procesador paralelo
        processor = ParallelProcessor(max_workers=2)
        results = processor.process_files(sample_files_list, output_directory)
        
        assert len(results['successful']) == 5
        assert len(results['failed']) == 0
        assert results['stats']['success_rate'] == 100.0
        
        # Verificar que se crearon los archivos PDF
        for success in results['successful']:
            pdf_path = Path(success['output'])
            assert pdf_path.exists()
            assert pdf_path.stat().st_size > 0
    
    @pytest.mark.integration
    def test_validation_pipeline_end_to_end(self, sample_files_list, invalid_file):
        """Test del pipeline de validación end-to-end."""
        # Usar el validador de lotes
        validator = BatchValidator()
        validation_result = validator.validate_batch(sample_files_list + [invalid_file])
        
        assert len(validation_result['valid']) == 5
        assert len(validation_result['invalid']) == 1
        assert len(validation_result['errors']) == 1
        
        # Verificar estadísticas
        stats = validator.get_batch_statistics(validation_result)
        assert stats['total_files'] == 6
        assert stats['valid_files'] == 5
        assert stats['invalid_files'] == 1
        assert stats['success_rate'] == 83.33
    
    @pytest.mark.integration
    def test_full_workflow_end_to_end(self, sample_files_list, output_directory):
        """Test del flujo completo end-to-end."""
        # 1. Validar archivos
        validator = BatchValidator()
        validation_result = validator.validate_batch(sample_files_list)
        
        assert len(validation_result['valid']) == 5
        
        # 2. Convertir archivos
        processor = ParallelProcessor(max_workers=2)
        conversion_results = processor.process_files(
            validation_result['valid'], 
            output_directory
        )
        
        assert len(conversion_results['successful']) == 5
        assert conversion_results['stats']['success_rate'] == 100.0
        
        # 3. Verificar archivos de salida
        output_files = list(Path(output_directory).glob("*.pdf"))
        assert len(output_files) == 5
        
        for pdf_file in output_files:
            assert pdf_file.stat().st_size > 0
    
    @pytest.mark.integration
    def test_error_handling_end_to_end(self, temp_dir):
        """Test del manejo de errores end-to-end."""
        # Crear archivo inválido
        invalid_file = Path(temp_dir) / "invalid.txt"
        invalid_file.write_text("No es un archivo Word")
        
        # Intentar convertir archivo inválido
        converter = DocumentConverter()
        output_path = Path(temp_dir) / "output.pdf"
        
        with pytest.raises(Exception):
            converter.convert_document(str(invalid_file), str(output_path))
        
        # Verificar que no se creó el archivo de salida
        assert not output_path.exists()
    
    @pytest.mark.integration
    def test_configuration_integration(self, sample_docx_file, output_directory):
        """Test de integración con configuración."""
        from src.config import config
        
        # Modificar configuración temporalmente
        original_quality = config.output_quality
        config.output_quality = "medium"
        
        try:
            # Convertir con configuración modificada
            converter = DocumentConverter()
            output_path = Path(output_directory) / "config_test.pdf"
            success = converter.convert_document(sample_docx_file, str(output_path))
            
            assert success is True
            assert output_path.exists()
        finally:
            # Restaurar configuración original
            config.output_quality = original_quality
    
    @pytest.mark.integration
    def test_logging_integration(self, sample_docx_file, output_directory):
        """Test de integración del sistema de logging."""
        from src.utils import setup_logger, get_logger
        
        # Configurar logging para test
        log_file = Path(output_directory) / "test.log"
        setup_logger(log_file=str(log_file), console_output=False)
        
        logger = get_logger("test_integration")
        logger.info("Test de logging")
        
        # Convertir archivo
        converter = DocumentConverter()
        output_path = Path(output_directory) / "logging_test.pdf"
        success = converter.convert_document(sample_docx_file, str(output_path))
        
        assert success is True
        assert log_file.exists()
        assert log_file.stat().st_size > 0
        
        # Verificar que hay logs
        log_content = log_file.read_text()
        assert "Test de logging" in log_content
        assert "Conversión exitosa" in log_content


class TestCLIIntegration:
    """Tests de integración de la interfaz CLI."""
    
    @pytest.mark.integration
    def test_cli_info_command(self, runner):
        """Test del comando info de la CLI."""
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(cli, ['info'])
        
        assert result.exit_code == 0
        assert "INFORMACIÓN DEL SISTEMA" in result.output
        assert "Workers máximos" in result.output
    
    @pytest.mark.integration
    def test_cli_test_command(self, output_directory):
        """Test del comando test de la CLI."""
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(cli, ['test', '--output-dir', output_directory])
        
        assert result.exit_code == 0
        assert "✓ Todos los tests básicos pasaron" in result.output
    
    @pytest.mark.integration
    def test_cli_validate_command(self, sample_docx_file):
        """Test del comando validate de la CLI."""
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(cli, ['validate', sample_docx_file])
        
        assert result.exit_code == 0
        assert "✓ Archivo válido" in result.output
    
    @pytest.mark.integration
    def test_cli_convert_command(self, sample_docx_file, output_directory):
        """Test del comando convert de la CLI."""
        from click.testing import CliRunner
        
        output_path = Path(output_directory) / "cli_test.pdf"
        runner = CliRunner()
        result = runner.invoke(cli, [
            'convert', 
            sample_docx_file, 
            '--output', str(output_path)
        ])
        
        assert result.exit_code == 0
        assert "✓ Conversión exitosa" in result.output
        assert output_path.exists()
    
    @pytest.mark.integration
    def test_cli_batch_command(self, sample_files_list, output_directory):
        """Test del comando batch de la CLI."""
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'batch',
            *sample_files_list,
            '--output-dir', output_directory,
            '--workers', '2'
        ])
        
        assert result.exit_code == 0
        assert "RESULTADOS DEL PROCESAMIENTO" in result.output
        assert "Tasa de éxito: 100.0%" in result.output
        
        # Verificar archivos de salida
        output_files = list(Path(output_directory).glob("*.pdf"))
        assert len(output_files) == 5


@pytest.fixture
def runner():
    """Fixture para CliRunner."""
    from click.testing import CliRunner
    return CliRunner() 