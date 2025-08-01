"""
Procesador paralelo para conversión masiva de documentos.
"""

import os
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

from utils import LoggerMixin, ConversionError, create_multi_progress_tracker
from config.settings import config
from validators import FileValidator
from .document_converter import DocumentConverter


class ParallelProcessor(LoggerMixin):
    """Procesador paralelo para conversión masiva."""
    
    def __init__(self, max_workers: Optional[int] = None):
        super().__init__("ParallelProcessor")
        self.max_workers = max_workers or config.max_workers
        self.file_validator = FileValidator()
        self.progress_tracker = None
        
        # Estadísticas de procesamiento
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'start_time': None,
            'end_time': None
        }
    
    def process_files(self, input_files: List[str], output_dir: str) -> Dict[str, Any]:
        """
        Procesa múltiples archivos en paralelo.
        
        Args:
            input_files: Lista de rutas de archivos de entrada
            output_dir: Directorio de salida para los PDFs
            
        Returns:
            Dict[str, Any]: Resultados del procesamiento
        """
        try:
            self.log_info(f"Iniciando procesamiento paralelo de {len(input_files)} archivos")
            self.stats['total_files'] = len(input_files)
            self.stats['start_time'] = time.time()
            
            # Inicializar progreso
            self.progress_tracker = create_multi_progress_tracker(
                len(input_files), 
                self.max_workers
            )
            
            # Validar archivos antes del procesamiento
            valid_files = self._validate_input_files(input_files)
            if not valid_files:
                return self._create_error_result("No hay archivos válidos para procesar")
            
            # Procesar archivos en paralelo
            results = self._process_parallel(valid_files, output_dir)
            
            # Finalizar estadísticas
            self.stats['end_time'] = time.time()
            self.stats['processed_files'] = len(valid_files)
            
            self.log_info(f"Procesamiento completado: {self.stats['successful_conversions']} exitosos, "
                         f"{self.stats['failed_conversions']} fallidos")
            
            return results
            
        except Exception as e:
            self.log_error(f"Error en procesamiento paralelo: {e}")
            self.stats['end_time'] = time.time()
            return self._create_error_result(f"Error de procesamiento: {str(e)}")
    
    def _validate_input_files(self, input_files: List[str]) -> List[str]:
        """
        Valida los archivos de entrada.
        
        Args:
            input_files: Lista de archivos a validar
            
        Returns:
            List[str]: Lista de archivos válidos
        """
        valid_files = []
        
        for file_path in input_files:
            is_valid, error_msg = self.file_validator.validate_file(file_path)
            if is_valid:
                valid_files.append(file_path)
            else:
                self.log_warning(f"Archivo inválido {file_path}: {error_msg}")
        
        self.log_info(f"Archivos válidos: {len(valid_files)}/{len(input_files)}")
        return valid_files
    
    def _process_parallel(self, input_files: List[str], output_dir: str) -> Dict[str, Any]:
        """
        Procesa archivos usando un pool de procesos.
        
        Args:
            input_files: Lista de archivos válidos
            output_dir: Directorio de salida
            
        Returns:
            Dict[str, Any]: Resultados del procesamiento
        """
        results = {
            'successful': [],
            'failed': [],
            'errors': [],
            'stats': {}
        }
        
        # Crear directorio de salida
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Procesar archivos en paralelo
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Crear tareas de conversión
            future_to_file = {}
            for file_path in input_files:
                output_path = self._get_output_path(file_path, output_dir)
                future = executor.submit(self._convert_single_file, file_path, output_path)
                future_to_file[future] = file_path
            
            # Procesar resultados
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    success, output_path, error_msg = future.result()
                    
                    if success:
                        results['successful'].append({
                            'input': file_path,
                            'output': output_path
                        })
                        self.stats['successful_conversions'] += 1
                        self.log_info(f"Conversión exitosa: {file_path}")
                    else:
                        results['failed'].append({
                            'input': file_path,
                            'error': error_msg
                        })
                        results['errors'].append(f"{file_path}: {error_msg}")
                        self.stats['failed_conversions'] += 1
                        self.log_error(f"Conversión fallida: {file_path} - {error_msg}")
                        
                except Exception as e:
                    results['failed'].append({
                        'input': file_path,
                        'error': str(e)
                    })
                    results['errors'].append(f"{file_path}: Error inesperado - {str(e)}")
                    self.stats['failed_conversions'] += 1
                    self.log_error(f"Error procesando {file_path}: {e}")
        
        # Calcular estadísticas finales
        results['stats'] = self._calculate_final_stats()
        
        return results
    
    def _convert_single_file(self, input_path: str, output_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Convierte un archivo individual (ejecutado en proceso separado).
        
        Args:
            input_path: Ruta del archivo de entrada
            output_path: Ruta del archivo de salida
            
        Returns:
            Tuple[bool, str, Optional[str]]: (éxito, ruta_salida, mensaje_error)
        """
        try:
            converter = DocumentConverter()
            success = converter.convert_document(input_path, output_path)
            
            if success:
                return True, output_path, None
            else:
                return False, output_path, "Error en conversión"
                
        except Exception as e:
            return False, output_path, str(e)
    
    def _get_output_path(self, input_path: str, output_dir: str) -> str:
        """
        Genera la ruta de salida para un archivo de entrada.
        
        Args:
            input_path: Ruta del archivo de entrada
            output_dir: Directorio de salida
            
        Returns:
            str: Ruta del archivo de salida
        """
        input_file = Path(input_path)
        output_file = Path(output_dir) / f"{input_file.stem}.pdf"
        return str(output_file)
    
    def _calculate_final_stats(self) -> Dict[str, Any]:
        """
        Calcula estadísticas finales del procesamiento.
        
        Returns:
            Dict[str, Any]: Estadísticas finales
        """
        # Verificar que los tiempos estén disponibles
        if self.stats['start_time'] is None or self.stats['end_time'] is None:
            total_time = 0.0
        else:
            total_time = self.stats['end_time'] - self.stats['start_time']
        
        success_rate = (self.stats['successful_conversions'] / self.stats['processed_files'] * 100) if self.stats['processed_files'] > 0 else 0
        
        return {
            'total_files': self.stats['total_files'],
            'processed_files': self.stats['processed_files'],
            'successful_conversions': self.stats['successful_conversions'],
            'failed_conversions': self.stats['failed_conversions'],
            'success_rate': success_rate,
            'total_time': total_time,
            'average_time_per_file': total_time / self.stats['processed_files'] if self.stats['processed_files'] > 0 else 0,
            'files_per_minute': (self.stats['processed_files'] / total_time * 60) if total_time > 0 else 0
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        Crea un resultado de error.
        
        Args:
            error_message: Mensaje de error
            
        Returns:
            Dict[str, Any]: Resultado de error
        """
        return {
            'successful': [],
            'failed': [],
            'errors': [error_message],
            'stats': {
                'total_files': self.stats['total_files'],
                'processed_files': 0,
                'successful_conversions': 0,
                'failed_conversions': 0,
                'success_rate': 0.0,
                'total_time': 0.0,
                'average_time_per_file': 0.0,
                'files_per_minute': 0.0
            }
        }
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """
        Imprime los resultados del procesamiento.
        
        Args:
            results: Resultados del procesamiento
        """
        stats = results['stats']
        
        print(f"\n{'='*60}")
        print(f"RESULTADOS DEL PROCESAMIENTO")
        print(f"{'='*60}")
        print(f"Total de archivos: {stats['total_files']}")
        print(f"Archivos procesados: {stats['processed_files']}")
        print(f"Conversiones exitosas: {stats['successful_conversions']}")
        print(f"Conversiones fallidas: {stats['failed_conversions']}")
        print(f"Tasa de éxito: {stats['success_rate']:.1f}%")
        print(f"Tiempo total: {stats['total_time']:.2f}s")
        print(f"Tiempo promedio por archivo: {stats['average_time_per_file']:.2f}s")
        print(f"Archivos por minuto: {stats['files_per_minute']:.1f}")
        
        if results['errors']:
            print(f"\nErrores encontrados:")
            for error in results['errors'][:10]:  # Mostrar solo los primeros 10
                print(f"  - {error}")
            
            if len(results['errors']) > 10:
                print(f"  ... y {len(results['errors']) - 10} errores más")
        
        print(f"{'='*60}")
    
    def get_optimal_worker_count(self, file_count: int) -> int:
        """
        Calcula el número óptimo de workers basado en el número de archivos.
        
        Args:
            file_count: Número de archivos a procesar
            
        Returns:
            int: Número óptimo de workers
        """
        cpu_count = mp.cpu_count()
        
        # Para pocos archivos, usar menos workers
        if file_count <= 5:
            return min(2, cpu_count)
        elif file_count <= 20:
            return min(4, cpu_count)
        else:
            return min(self.max_workers, cpu_count)
    
    def set_max_workers(self, max_workers: int) -> None:
        """
        Establece el número máximo de workers.
        
        Args:
            max_workers: Número máximo de workers
        """
        self.max_workers = max_workers
        self.log_info(f"Número de workers establecido en: {max_workers}")
    
    def reset_stats(self) -> None:
        """Reinicia las estadísticas de procesamiento."""
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'start_time': None,
            'end_time': None
        } 