"""
Validador de archivos para el conversor de documentos.
"""

import os
import magic
from pathlib import Path
from typing import List, Tuple, Optional
from utils import FileValidationError, LoggerMixin
from config.settings import config


class FileValidator(LoggerMixin):
    """Validador de archivos de entrada."""
    
    def __init__(self):
        super().__init__("FileValidator")
        self.supported_extensions = config.get_supported_extensions()
        self.max_file_size = config.max_file_size
    
    def validate_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un archivo individual.
        
        Args:
            file_path: Ruta del archivo a validar
            
        Returns:
            Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
        """
        try:
            # Validar existencia
            if not self._file_exists(file_path):
                return False, f"Archivo no encontrado: {file_path}"
            
            # Validar permisos de lectura
            if not self._is_readable(file_path):
                return False, f"Sin permisos de lectura: {file_path}"
            
            # Validar extensión
            if not self._has_valid_extension(file_path):
                return False, f"Extensión no soportada: {Path(file_path).suffix}"
            
            # Validar tamaño
            if not self._has_valid_size(file_path):
                return False, f"Archivo demasiado grande: {self._get_file_size_mb(file_path)}MB"
            
            # Validar integridad
            if not self._is_valid_file(file_path):
                return False, f"Archivo corrupto o no válido: {file_path}"
            
            self.log_debug(f"Archivo válido: {file_path}")
            return True, None
            
        except Exception as e:
            self.log_error(f"Error validando archivo {file_path}: {e}")
            return False, f"Error de validación: {str(e)}"
    
    def validate_directory(self, dir_path: str) -> Tuple[bool, Optional[str]]:
        """
        Valida un directorio.
        
        Args:
            dir_path: Ruta del directorio a validar
            
        Returns:
            Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
        """
        try:
            path = Path(dir_path)
            
            # Verificar existencia
            if not path.exists():
                return False, f"Directorio no encontrado: {dir_path}"
            
            # Verificar que sea un directorio
            if not path.is_dir():
                return False, f"No es un directorio: {dir_path}"
            
            # Verificar permisos de lectura
            if not os.access(path, os.R_OK):
                return False, f"Sin permisos de lectura en directorio: {dir_path}"
            
            # Verificar que contenga archivos válidos
            valid_files = self.get_valid_files_in_directory(dir_path)
            if not valid_files:
                return False, f"No se encontraron archivos válidos en: {dir_path}"
            
            self.log_debug(f"Directorio válido: {dir_path} con {len(valid_files)} archivos")
            return True, None
            
        except Exception as e:
            self.log_error(f"Error validando directorio {dir_path}: {e}")
            return False, f"Error de validación: {str(e)}"
    
    def get_valid_files_in_directory(self, dir_path: str) -> List[str]:
        """
        Obtiene lista de archivos válidos en un directorio.
        
        Args:
            dir_path: Ruta del directorio
            
        Returns:
            List[str]: Lista de rutas de archivos válidos
        """
        valid_files = []
        path = Path(dir_path)
        
        try:
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    is_valid, _ = self.validate_file(str(file_path))
                    if is_valid:
                        valid_files.append(str(file_path))
            
            self.log_info(f"Encontrados {len(valid_files)} archivos válidos en {dir_path}")
            return valid_files
            
        except Exception as e:
            self.log_error(f"Error escaneando directorio {dir_path}: {e}")
            return []
    
    def _file_exists(self, file_path: str) -> bool:
        """Verifica si el archivo existe."""
        return Path(file_path).exists()
    
    def _is_readable(self, file_path: str) -> bool:
        """Verifica si el archivo es legible."""
        return os.access(file_path, os.R_OK)
    
    def _has_valid_extension(self, file_path: str) -> bool:
        """Verifica si el archivo tiene una extensión válida."""
        extension = Path(file_path).suffix.lower()
        return config.is_supported_extension(extension)
    
    def _has_valid_size(self, file_path: str) -> bool:
        """Verifica si el archivo tiene un tamaño válido."""
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= self.max_file_size
        except OSError:
            return False
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Obtiene el tamaño del archivo en MB."""
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except OSError:
            return 0.0
    
    def _is_valid_file(self, file_path: str) -> bool:
        """Verifica la integridad del archivo usando magic numbers."""
        try:
            # Verificar magic numbers para archivos .docx
            if file_path.lower().endswith('.docx'):
                mime_type = magic.from_file(file_path, mime=True)
                return mime_type in [
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/zip'  # .docx es básicamente un ZIP
                ]
            
            # Verificar magic numbers para archivos .doc
            elif file_path.lower().endswith('.doc'):
                mime_type = magic.from_file(file_path, mime=True)
                return mime_type in [
                    'application/msword',
                    'application/vnd.ms-word'
                ]
            
            return True
            
        except Exception as e:
            self.log_warning(f"No se pudo verificar magic number para {file_path}: {e}")
            # Si no se puede verificar magic number, asumir que es válido
            return True
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Obtiene información detallada de un archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            dict: Información del archivo
        """
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                'name': path.name,
                'extension': path.suffix.lower(),
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'modified': stat.st_mtime,
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
                'mime_type': magic.from_file(file_path, mime=True) if path.exists() else None
            }
        except Exception as e:
            self.log_error(f"Error obteniendo información de {file_path}: {e}")
            return {}


def validate_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Función de conveniencia para validar un archivo.
    
    Args:
        file_path: Ruta del archivo a validar
        
    Returns:
        Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
    """
    validator = FileValidator()
    return validator.validate_file(file_path)


def validate_directory(dir_path: str) -> Tuple[bool, Optional[str]]:
    """
    Función de conveniencia para validar un directorio.
    
    Args:
        dir_path: Ruta del directorio a validar
        
    Returns:
        Tuple[bool, Optional[str]]: (es_válido, mensaje_error)
    """
    validator = FileValidator()
    return validator.validate_directory(dir_path) 