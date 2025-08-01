"""
Configuración centralizada del sistema de conversión de documentos.
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional


class Config:
    """Clase de configuración centralizada."""
    
    def __init__(self):
        # Configuración de conversión
        self.max_file_size = 104857600  # 100MB
        self.supported_extensions = [".doc", ".docx"]
        self.output_quality = "high"
        
        # Configuración de procesamiento
        self.max_workers = 4
        self.timeout = 300  # 5 minutos
        self.chunk_size = 10  # Archivos por lote
        
        # Configuración de logging
        self.log_level = "INFO"
        self.log_file = "logs/converter.log"
        self.log_max_size = 10485760  # 10MB
        self.log_backup_count = 5
        
        # Configuración de salida
        self.default_output_dir = "./output"
        self.overwrite_existing = False
        self.create_subdirs = True
        
        # Configuración de PDF
        self.pdf_compression = True
        self.pdf_quality = 95
        self.pdf_metadata = True
        
        # Cargar configuración desde archivo si existe
        self._load_from_file()
        self._load_from_env()
    
    def _load_from_file(self) -> None:
        """Carga configuración desde archivo YAML."""
        config_file = Path("config.yaml")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    self._update_from_dict(config_data)
            except Exception as e:
                print(f"Advertencia: No se pudo cargar config.yaml: {e}")
    
    def _load_from_env(self) -> None:
        """Carga configuración desde variables de entorno."""
        env_mappings = {
            'CONVERTER_MAX_WORKERS': 'max_workers',
            'CONVERTER_LOG_LEVEL': 'log_level',
            'CONVERTER_OUTPUT_DIR': 'default_output_dir',
            'CONVERTER_MAX_FILE_SIZE': 'max_file_size',
            'CONVERTER_TIMEOUT': 'timeout',
        }
        
        for env_var, attr_name in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # Convertir tipos según el atributo
                    if attr_name in ['max_workers', 'max_file_size', 'timeout']:
                        setattr(self, attr_name, int(value))
                    else:
                        setattr(self, attr_name, value)
                except ValueError:
                    print(f"Advertencia: Valor inválido para {env_var}: {value}")
    
    def _update_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Actualiza configuración desde diccionario."""
        if not isinstance(config_data, dict):
            return
            
        for section, values in config_data.items():
            if hasattr(self, section) and isinstance(values, dict):
                for key, value in values.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
    
    def get_supported_extensions(self) -> List[str]:
        """Retorna las extensiones soportadas."""
        return self.supported_extensions.copy()
    
    def is_supported_extension(self, extension: str) -> bool:
        """Verifica si una extensión es soportada."""
        return extension.lower() in [ext.lower() for ext in self.supported_extensions]
    
    def get_output_path(self, input_path: str) -> str:
        """Genera la ruta de salida para un archivo de entrada."""
        input_path = Path(input_path)
        output_dir = Path(self.default_output_dir)
        
        if self.create_subdirs:
            # Mantener estructura de directorios
            relative_path = input_path.parent
            output_dir = output_dir / relative_path
        
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir / f"{input_path.stem}.pdf")
    
    def validate(self) -> List[str]:
        """Valida la configuración y retorna lista de errores."""
        errors = []
        
        if self.max_workers < 1:
            errors.append("max_workers debe ser mayor a 0")
        
        if self.max_file_size < 1024:
            errors.append("max_file_size debe ser mayor a 1KB")
        
        if self.timeout < 30:
            errors.append("timeout debe ser mayor a 30 segundos")
        
        if not self.supported_extensions:
            errors.append("Debe haber al menos una extensión soportada")
        
        return errors


def load_config() -> Config:
    """Carga y retorna la configuración del sistema."""
    config = Config()
    errors = config.validate()
    
    if errors:
        print("Errores en la configuración:")
        for error in errors:
            print(f"  - {error}")
        print("Usando configuración por defecto.")
    
    return config


# Instancia global de configuración
config = load_config() 