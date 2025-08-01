# FLUJOGRAMA - CONVERSOR DOC/DOCX A PDF

## DIAGRAMA DE FLUJO PRINCIPAL

```
INICIO
  ↓
[Usuario ejecuta comando]
  ↓
[Validar argumentos CLI]
  ↓
¿Argumentos válidos?
  ├─ NO → [Mostrar ayuda] → FIN
  └─ SÍ → [Configurar parámetros]
  ↓
[Detectar tipo de entrada]
  ↓
¿Es archivo individual?
  ├─ SÍ → [Procesar archivo único]
  └─ NO → [Procesar directorio]
  ↓
[Validar archivos de entrada]
  ↓
¿Archivos válidos encontrados?
  ├─ NO → [Mostrar error] → FIN
  └─ SÍ → [Crear directorio de salida]
  ↓
[Inicializar procesamiento paralelo]
  ↓
[Iniciar conversión de archivos]
  ↓
[Mostrar barra de progreso]
  ↓
¿Todos los archivos procesados?
  ├─ NO → [Continuar procesamiento]
  └─ SÍ → [Generar reporte final]
  ↓
[Mostrar estadísticas]
  ↓
FIN
```

## DIAGRAMA DE FLUJO - CONVERSIÓN DE ARCHIVO

```
INICIO CONVERSIÓN
  ↓
[Cargar documento Word]
  ↓
¿Archivo cargado correctamente?
  ├─ NO → [Registrar error] → FIN
  └─ SÍ → [Extraer contenido]
  ↓
[Procesar texto]
  ↓
[Procesar imágenes]
  ↓
[Procesar tablas]
  ↓
[Procesar estilos y formato]
  ↓
[Generar PDF]
  ↓
¿PDF generado correctamente?
  ├─ NO → [Registrar error] → FIN
  └─ SÍ → [Guardar archivo]
  ↓
[Validar archivo PDF]
  ↓
¿Archivo válido?
  ├─ NO → [Registrar error] → FIN
  └─ SÍ → [Marcar como exitoso]
  ↓
FIN CONVERSIÓN
```

## DIAGRAMA DE FLUJO - VALIDACIÓN DE ARCHIVOS

```
INICIO VALIDACIÓN
  ↓
[Verificar existencia del archivo]
  ↓
¿Archivo existe?
  ├─ NO → [Error: Archivo no encontrado]
  └─ SÍ → [Verificar permisos de lectura]
  ↓
¿Archivo es legible?
  ├─ NO → [Error: Sin permisos de lectura]
  └─ SÍ → [Verificar extensión]
  ↓
¿Extensión válida (.doc/.docx)?
  ├─ NO → [Error: Formato no soportado]
  └─ SÍ → [Verificar tamaño del archivo]
  ↓
¿Tamaño < 100MB?
  ├─ NO → [Error: Archivo demasiado grande]
  └─ SÍ → [Verificar integridad del archivo]
  ↓
¿Archivo no corrupto?
  ├─ NO → [Error: Archivo corrupto]
  └─ SÍ → [Archivo válido]
  ↓
FIN VALIDACIÓN
```

## DIAGRAMA DE FLUJO - GESTIÓN DE ERRORES

```
ERROR DETECTADO
  ↓
[Clasificar tipo de error]
  ↓
¿Error crítico?
  ├─ SÍ → [Detener procesamiento] → [Mostrar error] → FIN
  └─ NO → [Registrar error en log]
  ↓
[Continuar con siguiente archivo]
  ↓
[Actualizar contador de errores]
  ↓
¿Máximo de errores alcanzado?
  ├─ SÍ → [Detener procesamiento] → [Mostrar advertencia]
  └─ NO → [Continuar procesamiento]
  ↓
[Actualizar barra de progreso]
```

## DIAGRAMA DE FLUJO - PROCESAMIENTO PARALELO

```
INICIO PROCESAMIENTO PARALELO
  ↓
[Calcular número de workers]
  ↓
[Crear pool de procesos]
  ↓
[Distribuir archivos entre workers]
  ↓
[Iniciar workers en paralelo]
  ↓
[Monitorear progreso]
  ↓
¿Todos los workers completados?
  ├─ NO → [Esperar y actualizar progreso]
  └─ SÍ → [Recopilar resultados]
  ↓
[Consolidar estadísticas]
  ↓
[Limpiar recursos]
  ↓
FIN PROCESAMIENTO PARALELO
```

## DIAGRAMA DE FLUJO - GENERACIÓN DE REPORTE

```
INICIO REPORTE
  ↓
[Recopilar estadísticas]
  ↓
[Calcular métricas]
  ├─ Total de archivos procesados
  ├─ Archivos convertidos exitosamente
  ├─ Archivos con errores
  ├─ Tiempo total de procesamiento
  └─ Tasa de éxito
  ↓
[Generar reporte detallado]
  ↓
[Mostrar resumen en consola]
  ↓
[Guardar log detallado]
  ↓
[Mostrar ubicación de archivos PDF]
  ↓
FIN REPORTE
```

## LEGENDA DE SÍMBOLOS

- **Óvalo**: Inicio/Fin
- **Rectángulo**: Proceso
- **Rombo**: Decisión
- **Paralelogramo**: Entrada/Salida
- **Flecha**: Flujo de control
- **Línea punteada**: Flujo de datos 