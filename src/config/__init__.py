"""
Módulo de configuración del sistema.

Gestiona la configuración centralizada del conversor de documentos.
"""

from .settings import Config, load_config

__all__ = ["Config", "load_config"] 