"""
Sistema de logging para el conversor de documentos.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from colorama import Fore, Style, init

# Inicializar colorama para colores en terminal
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Formateador de logs con colores para terminal."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT,
    }
    
    def format(self, record):
        # Agregar color al nivel de log
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
        
        return super().format(record)


def setup_logger(
    name: str = "doc_converter",
    level: str = "INFO",
    log_file: str = "logs/converter.log",
    max_size: int = 10485760,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Configura y retorna un logger configurado.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging
        log_file: Ruta del archivo de log
        max_size: Tamaño máximo del archivo de log
        backup_count: Número de archivos de backup
        console_output: Si mostrar logs en consola
    
    Returns:
        Logger configurado
    """
    # Crear directorio de logs si no existe
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Formato para archivo
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # Formato para consola (con colores)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "doc_converter") -> logging.Logger:
    """
    Obtiene un logger existente o crea uno nuevo.
    
    Args:
        name: Nombre del logger
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Si el logger no tiene handlers, configurarlo
    if not logger.handlers:
        logger = setup_logger(name)
    
    return logger


class LoggerMixin:
    """Mixin para agregar logging a las clases."""
    
    def __init__(self, logger_name: Optional[str] = None):
        self.logger = get_logger(logger_name or self.__class__.__name__)
    
    def log_info(self, message: str) -> None:
        """Log de información."""
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """Log de advertencia."""
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """Log de error."""
        self.logger.error(message)
    
    def log_debug(self, message: str) -> None:
        """Log de debug."""
        self.logger.debug(message)
    
    def log_critical(self, message: str) -> None:
        """Log crítico."""
        self.logger.critical(message)


def log_function_call(func):
    """Decorador para loggear llamadas a funciones."""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Llamando función: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Función {func.__name__} completada exitosamente")
            return result
        except Exception as e:
            logger.error(f"Error en función {func.__name__}: {e}")
            raise
    return wrapper


def log_execution_time(func):
    """Decorador para loggear tiempo de ejecución."""
    import time
    
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        logger.debug(f"Iniciando ejecución de {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Función {func.__name__} completada en {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error en {func.__name__} después de {execution_time:.2f}s: {e}")
            raise
    
    return wrapper 