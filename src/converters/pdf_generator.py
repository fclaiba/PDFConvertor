"""
Generador de PDF para el conversor de documentos.
"""

import io
from pathlib import Path
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white, gray
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

from utils import LoggerMixin, PDFGenerationError


class PDFGenerator(LoggerMixin):
    """Generador de PDF a partir de contenido extraído."""
    
    def __init__(self):
        super().__init__("PDFGenerator")
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF."""
        # Estilo para títulos
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=black
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=black
        ))
        
        # Estilo para párrafos normales
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            textColor=black
        ))
    
    def generate_pdf(self, content: Dict[str, Any], output_path: str) -> bool:
        """
        Genera un PDF a partir del contenido extraído.
        
        Args:
            content: Contenido extraído del documento Word
            output_path: Ruta del archivo PDF de salida
            
        Returns:
            bool: True si la generación fue exitosa
        """
        try:
            self.log_info(f"Generando PDF: {output_path}")
            
            # Crear documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Construir contenido del PDF
            story = self._build_pdf_content(content)
            
            # Generar PDF
            doc.build(story)
            
            self.log_info(f"PDF generado exitosamente: {output_path}")
            return True
            
        except Exception as e:
            self.log_error(f"Error generando PDF {output_path}: {e}")
            raise PDFGenerationError(f"Error generando PDF: {str(e)}", output_path)
    
    def _build_pdf_content(self, content: Dict[str, Any]) -> List:
        """
        Construye el contenido del PDF.
        
        Args:
            content: Contenido extraído
            
        Returns:
            List: Lista de elementos del PDF
        """
        story = []
        
        # Agregar título
        if content.get('title'):
            title_para = Paragraph(content['title'], self.styles['CustomTitle'])
            story.append(title_para)
            story.append(Spacer(1, 20))
        
        # Agregar párrafos
        for para_data in content.get('paragraphs', []):
            para_element = self._create_paragraph_element(para_data)
            if para_element:
                story.append(para_element)
                story.append(Spacer(1, 6))
        
        # Agregar tablas
        for table_data in content.get('tables', []):
            table_element = self._create_table_element(table_data)
            if table_element:
                story.append(table_element)
                story.append(Spacer(1, 12))
        
        # Agregar imágenes
        for image_data in content.get('images', []):
            image_element = self._create_image_element(image_data)
            if image_element:
                story.append(image_element)
                story.append(Spacer(1, 12))
        
        return story
    
    def _create_paragraph_element(self, para_data: Dict[str, Any]) -> Optional[Paragraph]:
        """
        Crea un elemento de párrafo para el PDF.
        
        Args:
            para_data: Datos del párrafo
            
        Returns:
            Optional[Paragraph]: Elemento de párrafo o None
        """
        try:
            text = para_data.get('text', '').strip()
            if not text:
                return None
            
            # Determinar estilo basado en el estilo del documento
            style_name = para_data.get('style', 'Normal')
            if 'Heading' in style_name or 'Title' in style_name:
                pdf_style = self.styles['CustomHeading']
            else:
                pdf_style = self.styles['CustomNormal']
            
            # Aplicar formato de texto basado en runs
            formatted_text = self._apply_text_formatting(para_data)
            
            # Crear párrafo
            para = Paragraph(formatted_text, pdf_style)
            return para
            
        except Exception as e:
            self.log_warning(f"Error creando párrafo: {e}")
            return None
    
    def _apply_text_formatting(self, para_data: Dict[str, Any]) -> str:
        """
        Aplica formato de texto basado en los runs del párrafo.
        
        Args:
            para_data: Datos del párrafo
            
        Returns:
            str: Texto con formato HTML para ReportLab
        """
        if not para_data.get('runs'):
            return para_data.get('text', '')
        
        formatted_parts = []
        
        for run in para_data['runs']:
            text = run.get('text', '')
            if not text:
                continue
            
            # Aplicar formato
            if run.get('bold'):
                text = f"<b>{text}</b>"
            if run.get('italic'):
                text = f"<i>{text}</i>"
            if run.get('underline'):
                text = f"<u>{text}</u>"
            
            # Aplicar color si está definido
            if run.get('color'):
                color = run['color']
                text = f'<font color="{color}">{text}</font>'
            
            formatted_parts.append(text)
        
        return ''.join(formatted_parts)
    
    def _create_table_element(self, table_data: Dict[str, Any]) -> Optional[Table]:
        """
        Crea un elemento de tabla para el PDF.
        
        Args:
            table_data: Datos de la tabla
            
        Returns:
            Optional[Table]: Elemento de tabla o None
        """
        try:
            rows = table_data.get('rows', [])
            if not rows:
                return None
            
            # Preparar datos de la tabla
            table_content = []
            for row in rows:
                row_data = []
                for cell in row:
                    cell_text = cell.get('text', '')
                    # Si hay párrafos en la celda, usar el texto del primer párrafo
                    if cell.get('paragraphs'):
                        cell_text = cell['paragraphs'][0].get('text', cell_text)
                    row_data.append(cell_text)
                table_content.append(row_data)
            
            if not table_content:
                return None
            
            # Crear tabla
            table = Table(table_content)
            
            # Aplicar estilo a la tabla
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), gray),
                ('TEXTCOLOR', (0, 0), (-1, 0), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), white),
                ('TEXTCOLOR', (0, 1), (-1, -1), black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            return table
            
        except Exception as e:
            self.log_warning(f"Error creando tabla: {e}")
            return None
    
    def _create_image_element(self, image_data: Dict[str, Any]) -> Optional[Image]:
        """
        Crea un elemento de imagen para el PDF.
        
        Args:
            image_data: Datos de la imagen
            
        Returns:
            Optional[Image]: Elemento de imagen o None
        """
        try:
            image_bytes = image_data.get('data')
            if not image_bytes:
                return None
            
            # Crear imagen desde bytes
            pil_image = PILImage.open(io.BytesIO(image_bytes))
            
            # Convertir a RGB si es necesario
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                pil_image = pil_image.convert('RGB')
            
            # Guardar temporalmente para ReportLab
            temp_path = f"/tmp/temp_image_{hash(image_bytes)}.jpg"
            pil_image.save(temp_path, 'JPEG', quality=85)
            
            # Crear elemento de imagen
            img = Image(temp_path, width=4*inch, height=3*inch, keepAspectRatio=True)
            
            # Limpiar archivo temporal
            try:
                Path(temp_path).unlink()
            except:
                pass
            
            return img
            
        except Exception as e:
            self.log_warning(f"Error creando imagen: {e}")
            return None
    
    def add_metadata(self, doc: SimpleDocTemplate, metadata: Dict[str, Any]):
        """
        Agrega metadatos al PDF.
        
        Args:
            doc: Documento PDF
            metadata: Metadatos del documento original
        """
        try:
            if metadata.get('title'):
                doc.setTitle(metadata['title'])
            if metadata.get('author'):
                doc.setAuthor(metadata['author'])
            if metadata.get('subject'):
                doc.setSubject(metadata['subject'])
            if metadata.get('keywords'):
                doc.setKeywords(metadata['keywords'])
        except Exception as e:
            self.log_warning(f"Error agregando metadatos: {e}")
    
    def create_simple_pdf(self, text_content: str, output_path: str, title: str = None) -> bool:
        """
        Crea un PDF simple con solo texto.
        
        Args:
            text_content: Contenido de texto
            output_path: Ruta del archivo PDF
            title: Título del documento
            
        Returns:
            bool: True si la generación fue exitosa
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            if title:
                title_para = Paragraph(title, self.styles['CustomTitle'])
                story.append(title_para)
                story.append(Spacer(1, 20))
            
            # Dividir texto en párrafos
            paragraphs = text_content.split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    para = Paragraph(para_text.strip(), self.styles['CustomNormal'])
                    story.append(para)
                    story.append(Spacer(1, 6))
            
            doc.build(story)
            return True
            
        except Exception as e:
            self.log_error(f"Error creando PDF simple: {e}")
            return False 