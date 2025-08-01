"""
Sistema de barras de progreso para el conversor de documentos.
"""

import time
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from colorama import Fore, Style


class ProgressBar:
    """Barra de progreso personalizada para conversiones."""
    
    def __init__(self, total: int, description: str = "Procesando"):
        self.total = total
        self.description = description
        self.current = 0
        self.start_time = time.time()
        self.pbar = None
    
    def __enter__(self):
        """Context manager entry."""
        self.pbar = tqdm(
            total=self.total,
            desc=self.description,
            unit="archivos",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.pbar:
            self.pbar.close()
    
    def update(self, n: int = 1, description: str = None):
        """Actualiza el progreso."""
        if self.pbar:
            if description:
                self.pbar.set_description(description)
            self.pbar.update(n)
            self.current += n
    
    def set_description(self, description: str):
        """Establece la descripción de la barra."""
        if self.pbar:
            self.pbar.set_description(description)


class ProgressTracker:
    """Rastreador de progreso para múltiples archivos."""
    
    def __init__(self, total_files: int):
        self.total_files = total_files
        self.completed_files = 0
        self.failed_files = 0
        self.current_file = ""
        self.start_time = time.time()
        self.file_times: Dict[str, float] = {}
        self.errors: List[Dict[str, Any]] = []
    
    def start_file(self, filename: str):
        """Inicia el procesamiento de un archivo."""
        self.current_file = filename
        self.file_times[filename] = time.time()
    
    def complete_file(self, filename: str, success: bool = True, error: str = None):
        """Marca un archivo como completado."""
        if success:
            self.completed_files += 1
            elapsed = time.time() - self.file_times.get(filename, time.time())
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {filename} completado en {elapsed:.2f}s")
        else:
            self.failed_files += 1
            self.errors.append({
                'file': filename,
                'error': error,
                'time': time.time()
            })
            print(f"{Fore.RED}✗{Style.RESET_ALL} {filename} falló: {error}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Retorna el progreso actual."""
        elapsed = time.time() - self.start_time
        success_rate = (self.completed_files / self.total_files * 100) if self.total_files > 0 else 0
        
        return {
            'total': self.total_files,
            'completed': self.completed_files,
            'failed': self.failed_files,
            'current': self.current_file,
            'elapsed': elapsed,
            'success_rate': success_rate,
            'errors': self.errors.copy()
        }
    
    def print_summary(self):
        """Imprime un resumen del procesamiento."""
        progress = self.get_progress()
        
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"RESUMEN DE CONVERSIÓN")
        print(f"{'='*50}{Style.RESET_ALL}")
        print(f"Total de archivos: {progress['total']}")
        print(f"Completados: {Fore.GREEN}{progress['completed']}{Style.RESET_ALL}")
        print(f"Fallidos: {Fore.RED}{progress['failed']}{Style.RESET_ALL}")
        print(f"Tasa de éxito: {Fore.BLUE}{progress['success_rate']:.1f}%{Style.RESET_ALL}")
        print(f"Tiempo total: {Fore.YELLOW}{progress['elapsed']:.2f}s{Style.RESET_ALL}")
        
        if progress['errors']:
            print(f"\n{Fore.RED}Errores encontrados:{Style.RESET_ALL}")
            for error in progress['errors']:
                print(f"  - {error['file']}: {error['error']}")


class MultiProgressTracker:
    """Rastreador de progreso para múltiples workers."""
    
    def __init__(self, total_files: int, num_workers: int):
        self.total_files = total_files
        self.num_workers = num_workers
        self.worker_progress: Dict[int, Dict[str, Any]] = {}
        self.global_progress = ProgressTracker(total_files)
        self.start_time = time.time()
        
        # Inicializar progreso por worker
        for i in range(num_workers):
            self.worker_progress[i] = {
                'files_assigned': 0,
                'files_completed': 0,
                'current_file': None,
                'status': 'idle'
            }
    
    def assign_file_to_worker(self, worker_id: int, filename: str):
        """Asigna un archivo a un worker."""
        if worker_id in self.worker_progress:
            self.worker_progress[worker_id]['files_assigned'] += 1
            self.worker_progress[worker_id]['current_file'] = filename
            self.worker_progress[worker_id]['status'] = 'processing'
    
    def complete_file_in_worker(self, worker_id: int, filename: str, success: bool, error: str = None):
        """Marca un archivo como completado en un worker específico."""
        if worker_id in self.worker_progress:
            self.worker_progress[worker_id]['files_completed'] += 1
            self.worker_progress[worker_id]['current_file'] = None
            self.worker_progress[worker_id]['status'] = 'idle'
            
            # Actualizar progreso global
            self.global_progress.complete_file(filename, success, error)
    
    def get_worker_status(self, worker_id: int) -> Dict[str, Any]:
        """Obtiene el estado de un worker específico."""
        return self.worker_progress.get(worker_id, {}).copy()
    
    def get_all_workers_status(self) -> Dict[int, Dict[str, Any]]:
        """Obtiene el estado de todos los workers."""
        return self.worker_progress.copy()
    
    def print_workers_status(self):
        """Imprime el estado de todos los workers."""
        print(f"\n{Fore.CYAN}Estado de Workers:{Style.RESET_ALL}")
        for worker_id, status in self.worker_progress.items():
            status_color = Fore.GREEN if status['status'] == 'idle' else Fore.YELLOW
            current_file = status['current_file'] or 'N/A'
            print(f"Worker {worker_id}: {status_color}{status['status']}{Style.RESET_ALL} "
                  f"(Completados: {status['files_completed']}/{status['files_assigned']}) "
                  f"Archivo actual: {current_file}")
    
    def is_complete(self) -> bool:
        """Verifica si todos los archivos han sido procesados."""
        total_completed = sum(w['files_completed'] for w in self.worker_progress.values())
        return total_completed >= self.total_files


def create_progress_bar(total: int, description: str = "Procesando") -> ProgressBar:
    """Factory function para crear barras de progreso."""
    return ProgressBar(total, description)


def create_progress_tracker(total_files: int) -> ProgressTracker:
    """Factory function para crear rastreadores de progreso."""
    return ProgressTracker(total_files)


def create_multi_progress_tracker(total_files: int, num_workers: int) -> MultiProgressTracker:
    """Factory function para crear rastreadores de progreso multi-worker."""
    return MultiProgressTracker(total_files, num_workers) 