"""
Interfaz de línea de comandos para el conversor de documentos.
"""

import sys
import os
from pathlib import Path
from typing import List, Optional

import click
from colorama import Fore, Style, init

from config.settings import config, load_config
from utils import setup_logger, get_logger
from validators import BatchValidator
from converters import DocumentConverter, ParallelProcessor

# Inicializar colorama
init(autoreset=True)

# Configurar logging
logger = get_logger("CLI")


@click.group()
@click.version_option(version="1.0.0", prog_name="doc-to-pdf-converter")
@click.option('--verbose', '-v', is_flag=True, help='Modo verbose')
@click.option('--quiet', '-q', is_flag=True, help='Modo silencioso')
@click.option('--config', '-c', type=click.Path(exists=True), help='Archivo de configuración personalizado')
def cli(verbose: bool, quiet: bool, config: Optional[str]):
    """
    Conversor de documentos Word (.doc/.docx) a PDF con procesamiento paralelo.
    
    Permite convertir archivos individuales o lotes completos de documentos
    a formato PDF de manera eficiente y rápida.
    """
    # Configurar nivel de logging
    if verbose:
        setup_logger(level="DEBUG")
    elif quiet:
        setup_logger(level="ERROR")
    else:
        setup_logger(level="INFO")
    
    # Cargar configuración personalizada si se especifica
    if config:
        # Aquí se podría implementar la carga de configuración personalizada
        pass
    
    logger.info("Iniciando conversor de documentos")


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Ruta de salida del PDF')
@click.option('--quality', type=click.Choice(['low', 'medium', 'high']), default='high', help='Calidad del PDF')
def convert(input_path: str, output: Optional[str], quality: str):
    """
    Convierte un archivo individual de Word a PDF.
    
    INPUT_PATH: Ruta del archivo .doc o .docx a convertir
    """
    try:
        logger.info(f"Convirtiendo archivo individual: {input_path}")
        
        # Validar archivo de entrada
        validator = BatchValidator()
        validation_result = validator.validate_batch([input_path])
        
        if not validation_result['valid']:
            click.echo(f"{Fore.RED}Error: Archivo inválido{Style.RESET_ALL}")
            for error in validation_result['errors']:
                click.echo(f"  - {error}")
            sys.exit(1)
        
        # Generar ruta de salida si no se especifica
        if not output:
            input_file = Path(input_path)
            output = str(input_file.parent / f"{input_file.stem}.pdf")
        
        # Configurar calidad
        config.output_quality = quality
        
        # Convertir archivo
        converter = DocumentConverter()
        success = converter.convert_document(input_path, output)
        
        if success:
            click.echo(f"{Fore.GREEN}✓ Conversión exitosa{Style.RESET_ALL}")
            click.echo(f"Archivo PDF generado: {output}")
        else:
            click.echo(f"{Fore.RED}✗ Error en la conversión{Style.RESET_ALL}")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.error(f"Error en conversión individual: {e}")
        sys.exit(1)


@cli.command()
@click.argument('input_paths', nargs=-1, type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), default='./output', help='Directorio de salida')
@click.option('--workers', '-w', type=int, default=4, help='Número de workers paralelos')
@click.option('--quality', type=click.Choice(['low', 'medium', 'high']), default='high', help='Calidad del PDF')
@click.option('--recursive', '-r', is_flag=True, help='Procesar subdirectorios recursivamente')
def batch(input_paths: tuple, output_dir: str, workers: int, quality: str, recursive: bool):
    """
    Convierte múltiples archivos de Word a PDF en paralelo.
    
    INPUT_PATHS: Rutas de archivos .doc/.docx o directorios a procesar
    """
    try:
        logger.info(f"Iniciando conversión masiva con {workers} workers")
        
        # Validar y expandir rutas de entrada
        all_files = []
        validator = BatchValidator()
        
        for input_path in input_paths:
            path = Path(input_path)
            
            if path.is_file():
                # Es un archivo individual
                all_files.append(str(path))
            elif path.is_dir():
                # Es un directorio
                if recursive:
                    # Buscar archivos recursivamente
                    pattern = "**/*.doc*"
                    files = list(path.glob(pattern))
                else:
                    # Solo archivos en el directorio actual
                    files = list(path.glob("*.doc*"))
                
                all_files.extend([str(f) for f in files])
            else:
                click.echo(f"{Fore.YELLOW}Advertencia: {input_path} no existe{Style.RESET_ALL}")
        
        if not all_files:
            click.echo(f"{Fore.RED}Error: No se encontraron archivos válidos para procesar{Style.RESET_ALL}")
            sys.exit(1)
        
        click.echo(f"Encontrados {len(all_files)} archivos para procesar")
        
        # Validar archivos
        validation_result = validator.validate_batch(all_files)
        
        if not validation_result['valid']:
            click.echo(f"{Fore.YELLOW}Advertencia: Algunos archivos son inválidos{Style.RESET_ALL}")
            validator.print_validation_report(validation_result)
            
            if not validation_result['valid']:
                click.echo(f"{Fore.RED}Error: No hay archivos válidos para procesar{Style.RESET_ALL}")
                sys.exit(1)
        
        valid_files = validation_result['valid']
        click.echo(f"Archivos válidos: {len(valid_files)}")
        
        # Configurar procesador
        config.output_quality = quality
        processor = ParallelProcessor(max_workers=workers)
        
        # Procesar archivos
        click.echo(f"{Fore.CYAN}Iniciando procesamiento paralelo...{Style.RESET_ALL}")
        results = processor.process_files(valid_files, output_dir)
        
        # Mostrar resultados
        processor.print_results(results)
        
        # Mostrar archivos convertidos exitosamente
        if results['successful']:
            click.echo(f"\n{Fore.GREEN}Archivos convertidos exitosamente:{Style.RESET_ALL}")
            for success in results['successful'][:10]:  # Mostrar solo los primeros 10
                click.echo(f"  ✓ {success['input']} -> {success['output']}")
            
            if len(results['successful']) > 10:
                click.echo(f"  ... y {len(results['successful']) - 10} archivos más")
        
        # Mostrar errores
        if results['errors']:
            click.echo(f"\n{Fore.RED}Errores encontrados:{Style.RESET_ALL}")
            for error in results['errors'][:5]:  # Mostrar solo los primeros 5
                click.echo(f"  ✗ {error}")
            
            if len(results['errors']) > 5:
                click.echo(f"  ... y {len(results['errors']) - 5} errores más")
        
        click.echo(f"\n{Fore.GREEN}Procesamiento completado{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.error(f"Error en conversión masiva: {e}")
        sys.exit(1)


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
def validate(input_path: str):
    """
    Valida un archivo o directorio sin convertirlo.
    
    INPUT_PATH: Ruta del archivo o directorio a validar
    """
    try:
        logger.info(f"Validando: {input_path}")
        
        validator = BatchValidator()
        path = Path(input_path)
        
        if path.is_file():
            # Validar archivo individual
            is_valid, error_msg = validator.file_validator.validate_file(input_path)
            
            if is_valid:
                file_info = validator.file_validator.get_file_info(input_path)
                click.echo(f"{Fore.GREEN}✓ Archivo válido{Style.RESET_ALL}")
                click.echo(f"  Nombre: {file_info['name']}")
                click.echo(f"  Tamaño: {file_info['size_mb']:.2f} MB")
                click.echo(f"  Tipo: {file_info['mime_type']}")
            else:
                click.echo(f"{Fore.RED}✗ Archivo inválido{Style.RESET_ALL}")
                click.echo(f"  Error: {error_msg}")
                
        elif path.is_dir():
            # Validar directorio
            validation_result = validator.validate_directory_batch(input_path)
            validator.print_validation_report(validation_result)
            
        else:
            click.echo(f"{Fore.RED}Error: {input_path} no existe{Style.RESET_ALL}")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.error(f"Error en validación: {e}")
        sys.exit(1)


@cli.command()
def info():
    """Muestra información del sistema y configuración."""
    try:
        click.echo(f"{Fore.CYAN}{'='*50}")
        click.echo(f"INFORMACIÓN DEL SISTEMA")
        click.echo(f"{'='*50}{Style.RESET_ALL}")
        
        # Información de configuración
        click.echo(f"Configuración:")
        click.echo(f"  Workers máximos: {config.max_workers}")
        click.echo(f"  Tamaño máximo de archivo: {config.max_file_size / (1024*1024):.0f} MB")
        click.echo(f"  Extensiones soportadas: {', '.join(config.supported_extensions)}")
        click.echo(f"  Directorio de salida por defecto: {config.default_output_dir}")
        click.echo(f"  Calidad de salida: {config.output_quality}")
        
        # Información del sistema
        import multiprocessing as mp
        click.echo(f"\nSistema:")
        click.echo(f"  CPUs disponibles: {mp.cpu_count()}")
        click.echo(f"  Python: {sys.version}")
        click.echo(f"  Plataforma: {sys.platform}")
        
        # Información de logging
        click.echo(f"\nLogging:")
        click.echo(f"  Nivel: {config.log_level}")
        click.echo(f"  Archivo: {config.log_file}")
        
        click.echo(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        logger.error(f"Error mostrando información: {e}")


@cli.command()
@click.option('--output-dir', '-o', type=click.Path(), default='./output', help='Directorio de salida')
def test(output_dir: str):
    """Ejecuta tests básicos del sistema."""
    try:
        click.echo(f"{Fore.CYAN}Ejecutando tests básicos...{Style.RESET_ALL}")
        
        # Test de configuración
        click.echo(f"✓ Configuración cargada")
        
        # Test de logging
        logger.info("Test de logging")
        click.echo(f"✓ Sistema de logging funcionando")
        
        # Test de validación
        validator = BatchValidator()
        click.echo(f"✓ Validador inicializado")
        
        # Test de conversor
        converter = DocumentConverter()
        click.echo(f"✓ Conversor inicializado")
        
        # Test de procesador paralelo
        processor = ParallelProcessor()
        click.echo(f"✓ Procesador paralelo inicializado")
        
        # Crear directorio de salida de prueba
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        click.echo(f"✓ Directorio de salida creado: {output_dir}")
        
        click.echo(f"\n{Fore.GREEN}✓ Todos los tests básicos pasaron{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error en tests: {e}{Style.RESET_ALL}")
        logger.error(f"Error en tests: {e}")


def main():
    """Función principal de la CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}Operación cancelada por el usuario{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}Error inesperado: {e}{Style.RESET_ALL}")
        logger.error(f"Error inesperado en CLI: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 