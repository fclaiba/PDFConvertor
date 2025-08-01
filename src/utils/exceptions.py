"""
Excepciones personalizadas para el sistema de conversión.
"""


class ConversionError(Exception):
    """Excepción base para errores de conversión."""
    
    def __init__(self, message: str, file_path: str = None, details: str = None):
        self.message = message
        self.file_path = file_path
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        result = self.message
        if self.file_path:
            result += f" (Archivo: {self.file_path})"
        if self.details:
            result += f" - {self.details}"
        return result


class FileValidationError(ConversionError):
    """Excepción para errores de validación de archivos."""
    
    def __init__(self, message: str, file_path: str = None, validation_type: str = None):
        self.validation_type = validation_type
        super().__init__(message, file_path, f"Tipo de validación: {validation_type}")


class PDFGenerationError(ConversionError):
    """Excepción para errores de generación de PDF."""
    
    def __init__(self, message: str, file_path: str = None, pdf_error: str = None):
        self.pdf_error = pdf_error
        super().__init__(message, file_path, f"Error PDF: {pdf_error}")


class ConfigurationError(Exception):
    """Excepción para errores de configuración."""
    
    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(f"Error de configuración: {message}")


class ProcessingError(ConversionError):
    """Excepción para errores durante el procesamiento."""
    
    def __init__(self, message: str, file_path: str = None, processing_step: str = None):
        self.processing_step = processing_step
        super().__init__(message, file_path, f"Paso: {processing_step}")


class MemoryError(ConversionError):
    """Excepción para errores de memoria."""
    
    def __init__(self, message: str, file_path: str = None, memory_usage: str = None):
        self.memory_usage = memory_usage
        super().__init__(message, file_path, f"Uso de memoria: {memory_usage}")


class TimeoutError(ConversionError):
    """Excepción para errores de timeout."""
    
    def __init__(self, message: str, file_path: str = None, timeout_duration: int = None):
        self.timeout_duration = timeout_duration
        super().__init__(message, file_path, f"Timeout: {timeout_duration}s") 