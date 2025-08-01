"""
Validador de lotes para procesamiento masivo de archivos.
"""

from typing import List, Dict, Tuple, Optional
from pathlib import Path
from .file_validator import FileValidator
from utils import LoggerMixin, FileValidationError
from config.settings import config


class BatchValidator(LoggerMixin):
    """Validador para lotes de archivos."""
    
    def __init__(self):
        super().__init__("BatchValidator")
        self.file_validator = FileValidator()
        self.max_files_per_batch = 100  # Límite de seguridad
    
    def validate_batch(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Valida un lote de archivos.
        
        Args:
            file_paths: Lista de rutas de archivos a validar
            
        Returns:
            Dict[str, List[str]]: {'valid': [...], 'invalid': [...], 'errors': [...]}
        """
        self.log_info(f"Validando lote de {len(file_paths)} archivos")
        
        valid_files = []
        invalid_files = []
        errors = []
        
        # Verificar límite de archivos
        if len(file_paths) > self.max_files_per_batch:
            error_msg = f"Demasiados archivos ({len(file_paths)}). Máximo: {self.max_files_per_batch}"
            self.log_warning(error_msg)
            errors.append(error_msg)
            return {'valid': [], 'invalid': file_paths, 'errors': errors}
        
        # Validar cada archivo
        for file_path in file_paths:
            try:
                is_valid, error_msg = self.file_validator.validate_file(file_path)
                
                if is_valid:
                    valid_files.append(file_path)
                else:
                    invalid_files.append(file_path)
                    errors.append(f"{file_path}: {error_msg}")
                    
            except Exception as e:
                invalid_files.append(file_path)
                errors.append(f"{file_path}: Error inesperado - {str(e)}")
                self.log_error(f"Error validando {file_path}: {e}")
        
        self.log_info(f"Validación completada: {len(valid_files)} válidos, {len(invalid_files)} inválidos")
        
        return {
            'valid': valid_files,
            'invalid': invalid_files,
            'errors': errors
        }
    
    def validate_directory_batch(self, dir_path: str) -> Dict[str, List[str]]:
        """
        Valida todos los archivos válidos en un directorio.
        
        Args:
            dir_path: Ruta del directorio
            
        Returns:
            Dict[str, List[str]]: {'valid': [...], 'invalid': [...], 'errors': [...]}
        """
        self.log_info(f"Validando directorio: {dir_path}")
        
        # Primero validar el directorio
        is_valid, error_msg = self.file_validator.validate_directory(dir_path)
        if not is_valid:
            return {
                'valid': [],
                'invalid': [],
                'errors': [f"Directorio inválido: {error_msg}"]
            }
        
        # Obtener archivos válidos del directorio
        valid_files = self.file_validator.get_valid_files_in_directory(dir_path)
        
        if not valid_files:
            return {
                'valid': [],
                'invalid': [],
                'errors': [f"No se encontraron archivos válidos en {dir_path}"]
            }
        
        # Validar el lote de archivos encontrados
        return self.validate_batch(valid_files)
    
    def validate_mixed_input(self, inputs: List[str]) -> Dict[str, List[str]]:
        """
        Valida una mezcla de archivos y directorios.
        
        Args:
            inputs: Lista de rutas (archivos y/o directorios)
            
        Returns:
            Dict[str, List[str]]: {'valid': [...], 'invalid': [...], 'errors': [...]}
        """
        self.log_info(f"Validando entrada mixta: {len(inputs)} elementos")
        
        all_valid_files = []
        all_invalid_files = []
        all_errors = []
        
        for input_path in inputs:
            path = Path(input_path)
            
            if path.is_file():
                # Es un archivo individual
                is_valid, error_msg = self.file_validator.validate_file(input_path)
                if is_valid:
                    all_valid_files.append(input_path)
                else:
                    all_invalid_files.append(input_path)
                    all_errors.append(f"{input_path}: {error_msg}")
                    
            elif path.is_dir():
                # Es un directorio
                batch_result = self.validate_directory_batch(input_path)
                all_valid_files.extend(batch_result['valid'])
                all_invalid_files.extend(batch_result['invalid'])
                all_errors.extend(batch_result['errors'])
                
            else:
                # No existe
                all_invalid_files.append(input_path)
                all_errors.append(f"{input_path}: No existe")
        
        self.log_info(f"Validación mixta completada: {len(all_valid_files)} válidos, {len(all_invalid_files)} inválidos")
        
        return {
            'valid': all_valid_files,
            'invalid': all_invalid_files,
            'errors': all_errors
        }
    
    def get_batch_statistics(self, validation_result: Dict[str, List[str]]) -> Dict[str, any]:
        """
        Obtiene estadísticas del lote validado.
        
        Args:
            validation_result: Resultado de validación
            
        Returns:
            Dict[str, any]: Estadísticas del lote
        """
        total_files = len(validation_result['valid']) + len(validation_result['invalid'])
        valid_count = len(validation_result['valid'])
        invalid_count = len(validation_result['invalid'])
        
        success_rate = (valid_count / total_files * 100) if total_files > 0 else 0
        
        return {
            'total_files': total_files,
            'valid_files': valid_count,
            'invalid_files': invalid_count,
            'success_rate': success_rate,
            'error_count': len(validation_result['errors'])
        }
    
    def print_validation_report(self, validation_result: Dict[str, List[str]]) -> None:
        """
        Imprime un reporte de validación.
        
        Args:
            validation_result: Resultado de validación
        """
        stats = self.get_batch_statistics(validation_result)
        
        print(f"\n{'='*60}")
        print(f"REPORTE DE VALIDACIÓN")
        print(f"{'='*60}")
        print(f"Total de archivos: {stats['total_files']}")
        print(f"Archivos válidos: {stats['valid_files']}")
        print(f"Archivos inválidos: {stats['invalid_files']}")
        print(f"Tasa de éxito: {stats['success_rate']:.1f}%")
        
        if validation_result['errors']:
            print(f"\nErrores encontrados:")
            for error in validation_result['errors'][:10]:  # Mostrar solo los primeros 10
                print(f"  - {error}")
            
            if len(validation_result['errors']) > 10:
                print(f"  ... y {len(validation_result['errors']) - 10} errores más")
        
        print(f"{'='*60}")
    
    def filter_by_size(self, file_paths: List[str], max_size_mb: Optional[float] = None) -> List[str]:
        """
        Filtra archivos por tamaño.
        
        Args:
            file_paths: Lista de rutas de archivos
            max_size_mb: Tamaño máximo en MB (None = usar configuración)
            
        Returns:
            List[str]: Archivos que cumplen el criterio de tamaño
        """
        if max_size_mb is None:
            max_size_mb = config.max_file_size / (1024 * 1024)
        
        max_size_bytes = max_size_mb * 1024 * 1024
        filtered_files = []
        
        for file_path in file_paths:
            try:
                file_size = Path(file_path).stat().st_size
                if file_size <= max_size_bytes:
                    filtered_files.append(file_path)
            except OSError:
                continue
        
        self.log_info(f"Filtrado por tamaño: {len(filtered_files)}/{len(file_paths)} archivos")
        return filtered_files
    
    def sort_by_size(self, file_paths: List[str], reverse: bool = False) -> List[str]:
        """
        Ordena archivos por tamaño.
        
        Args:
            file_paths: Lista de rutas de archivos
            reverse: True para orden descendente (más grandes primero)
            
        Returns:
            List[str]: Archivos ordenados por tamaño
        """
        def get_file_size(file_path):
            try:
                return Path(file_path).stat().st_size
            except OSError:
                return 0
        
        sorted_files = sorted(file_paths, key=get_file_size, reverse=reverse)
        self.log_debug(f"Archivos ordenados por tamaño (reverse={reverse})")
        return sorted_files 