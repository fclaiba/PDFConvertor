"""
Tests unitarios para el módulo de configuración.
"""

import pytest
import os
from unittest.mock import patch, mock_open
from pathlib import Path

from src.config.settings import Config, load_config


class TestConfig:
    """Tests para la clase Config."""
    
    def test_config_default_values(self):
        """Test que verifica los valores por defecto de la configuración."""
        config = Config()
        
        assert config.max_file_size == 104857600  # 100MB
        assert config.supported_extensions == [".doc", ".docx"]
        assert config.max_workers == 4
        assert config.timeout == 300
        assert config.log_level == "INFO"
        assert config.default_output_dir == "./output"
        assert config.output_quality == "high"
    
    def test_config_load_from_yaml(self):
        """Test que verifica la carga desde archivo YAML."""
        yaml_content = """
conversion:
  max_file_size: 209715200
  output_quality: "medium"
processing:
  max_workers: 8
  timeout: 600
logging:
  level: "DEBUG"
"""
        
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            with patch('pathlib.Path.exists', return_value=True):
                config = Config()
                
                assert config.max_file_size == 209715200
                assert config.output_quality == "medium"
                assert config.max_workers == 8
                assert config.timeout == 600
                assert config.log_level == "DEBUG"
    
    def test_config_load_from_env(self):
        """Test que verifica la carga desde variables de entorno."""
        env_vars = {
            'CONVERTER_MAX_WORKERS': '6',
            'CONVERTER_LOG_LEVEL': 'WARNING',
            'CONVERTER_OUTPUT_DIR': '/custom/output',
            'CONVERTER_MAX_FILE_SIZE': '209715200',
            'CONVERTER_TIMEOUT': '600'
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert config.max_workers == 6
            assert config.log_level == "WARNING"
            assert config.default_output_dir == "/custom/output"
            assert config.max_file_size == 209715200
            assert config.timeout == 600
    
    def test_config_validate_success(self):
        """Test que verifica la validación exitosa de configuración."""
        config = Config()
        errors = config.validate()
        
        assert len(errors) == 0
    
    def test_config_validate_errors(self):
        """Test que verifica la validación con errores."""
        config = Config()
        config.max_workers = 0
        config.max_file_size = 512
        config.timeout = 10
        config.supported_extensions = []
        
        errors = config.validate()
        
        assert len(errors) == 4
        assert "max_workers debe ser mayor a 0" in errors
        assert "max_file_size debe ser mayor a 1KB" in errors
        assert "timeout debe ser mayor a 30 segundos" in errors
        assert "Debe haber al menos una extensión soportada" in errors
    
    def test_config_is_supported_extension(self):
        """Test que verifica la validación de extensiones soportadas."""
        config = Config()
        
        assert config.is_supported_extension(".docx") is True
        assert config.is_supported_extension(".doc") is True
        assert config.is_supported_extension(".pdf") is False
        assert config.is_supported_extension(".txt") is False
    
    def test_config_get_output_path(self, temp_dir):
        """Test que verifica la generación de rutas de salida."""
        config = Config()
        config.default_output_dir = temp_dir
        
        input_path = "/path/to/document.docx"
        output_path = config.get_output_path(input_path)
        
        expected_path = Path(temp_dir) / "document.pdf"
        assert output_path == str(expected_path)
    
    def test_config_get_output_path_with_subdirs(self, temp_dir):
        """Test que verifica la generación de rutas con subdirectorios."""
        config = Config()
        config.default_output_dir = temp_dir
        config.create_subdirs = True
        
        input_path = "/path/to/subdir/document.docx"
        output_path = config.get_output_path(input_path)
        
        expected_path = Path(temp_dir) / "path" / "to" / "subdir" / "document.pdf"
        assert output_path == str(expected_path)


class TestLoadConfig:
    """Tests para la función load_config."""
    
    def test_load_config_success(self):
        """Test que verifica la carga exitosa de configuración."""
        config = load_config()
        
        assert isinstance(config, Config)
        assert config.max_file_size > 0
        assert len(config.supported_extensions) > 0
    
    def test_load_config_with_validation_errors(self):
        """Test que verifica la carga con errores de validación."""
        with patch('src.config.settings.Config') as mock_config_class:
            mock_config = mock_config_class.return_value
            mock_config.validate.return_value = ["Error 1", "Error 2"]
            
            config = load_config()
            
            assert isinstance(config, Config)
            mock_config.validate.assert_called_once()
    
    @patch('builtins.print')
    def test_load_config_prints_errors(self, mock_print):
        """Test que verifica que se imprimen los errores de validación."""
        with patch('src.config.settings.Config') as mock_config_class:
            mock_config = mock_config_class.return_value
            mock_config.validate.return_value = ["Error de configuración"]
            
            load_config()
            
            # Verificar que se imprimieron los errores
            mock_print.assert_called() 