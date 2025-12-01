"""
Professional PDF Report Styling Utilities for StockaDoodle IMS
Corporate luxury design with navy blue, purple, and gold accents
"""

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import PageBreak, Spacer
from reportlab.lib.units import inch


class PDFColors:
    """Corporate color palette"""
    # Primary colors
    NAVY_DARK = colors.HexColor('#2C3E50')
    PURPLE_RICH = colors.HexColor('#6C5CE7')
    GOLD_ACCENT = colors.HexColor('#FDCB6E')
    
    # Secondary colors
    WHITE = colors.white
    LIGHT_GRAY = colors.HexColor('#ECF0F1')
    MEDIUM_GRAY = colors.HexColor('#95A5A6')
    DARK_GRAY = colors.HexColor('#34495E')
    
    # Status colors
    SUCCESS_GREEN = colors.HexColor('#00B894')
    WARNING_ORANGE = colors.HexColor('#FDCB6E')
    CRITICAL_RED = colors.HexColor('#D63031')
    
    # Table colors
    HEADER_BG = NAVY_DARK
    ROW_ALT_BG = LIGHT_GRAY
    BORDER_COLOR = MEDIUM_GRAY


class PDFStyles:
    """Reusable paragraph styles"""
    
    @staticmethod
    def get_title_style():
        """Main report title - large, centered, navy"""
        return ParagraphStyle(
            name='ReportTitle',
            fontName='Helvetica-Bold',
            fontSize=26,
            textColor=PDFColors.NAVY_DARK,
            alignment=TA_CENTER,
            spaceAfter=16,
            spaceBefore=12
        )
    
    @staticmethod
    def get_subtitle_style():
        """Report subtitle - medium, centered, purple"""
        return ParagraphStyle(
            name='ReportSubtitle',
            fontName='Helvetica',
            fontSize=14,
            textColor=PDFColors.PURPLE_RICH,
            alignment=TA_CENTER,
            spaceAfter=12,
            spaceBefore=6
        )
    
    @staticmethod
    def get_section_header_style():
        """Section headers - bold, left-aligned"""
        return ParagraphStyle(
            name='SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=PDFColors.NAVY_DARK,
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=20,
            borderPadding=(0, 0, 4, 0),
            borderColor=PDFColors.GOLD_ACCENT,
            borderWidth=2
        )
    
    @staticmethod
    def get_body_style():
        """Normal body text"""
        return ParagraphStyle(
            name='BodyText',
            fontName='Helvetica',
            fontSize=11,
            textColor=PDFColors.DARK_GRAY,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        )
    
    @staticmethod
    def get_footer_style():
        """Footer text - small, centered, gray"""
        return ParagraphStyle(
            name='FooterText',
            fontName='Helvetica',
            fontSize=9,
            textColor=PDFColors.MEDIUM_GRAY,
            alignment=TA_CENTER,
            spaceAfter=4
        )
    
    @staticmethod
    def get_metric_label_style():
        """Metric labels in summary boxes"""
        return ParagraphStyle(
            name='MetricLabel',
            fontName='Helvetica',
            fontSize=10,
            textColor=PDFColors.MEDIUM_GRAY,
            alignment=TA_LEFT
        )
    
    @staticmethod
    def get_metric_value_style():
        """Metric values in summary boxes"""
        return ParagraphStyle(
            name='MetricValue',
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=PDFColors.NAVY_DARK,
            alignment=TA_LEFT
        )


class PDFTableStyles:
    """Reusable table styling configurations"""
    
    @staticmethod
    def get_standard_table_style():
        """Standard data table style with alternating rows"""
        from reportlab.platypus import TableStyle
        
        return TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), PDFColors.HEADER_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), PDFColors.WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), PDFColors.WHITE),
            ('TEXTCOLOR', (0, 1), (-1, -1), PDFColors.DARK_GRAY),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [PDFColors.WHITE, PDFColors.ROW_ALT_BG]),
            
            # Grid lines
            ('GRID', (0, 0), (-1, -1), 0.5, PDFColors.BORDER_COLOR),
            ('LINEBELOW', (0, 0), (-1, 0), 2, PDFColors.GOLD_ACCENT),
        ])
    
    @staticmethod
    def get_summary_table_style():
        """Summary metrics table style"""
        from reportlab.platypus import TableStyle
        
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PDFColors.LIGHT_GRAY),
            ('TEXTCOLOR', (0, 0), (-1, -1), PDFColors.DARK_GRAY),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('GRID', (0, 0), (-1, -1), 1, PDFColors.WHITE),
        ])


class PDFLayoutHelpers:
    """Helper functions for consistent layout"""
    
    @staticmethod
    def create_spacer(height_inches=0.2):
        """Create a spacer of specified height"""
        return Spacer(1, height_inches * inch)
    
    @staticmethod
    def create_section_divider():
        """Create a decorative section divider"""
        from reportlab.platypus import HRFlowable
        return HRFlowable(
            width="100%",
            thickness=1,
            color=PDFColors.GOLD_ACCENT,
            spaceBefore=15,
            spaceAfter=15
        )
    
    @staticmethod
    def create_gold_border_line():
        """Create thin gold border line"""
        from reportlab.platypus import HRFlowable
        return HRFlowable(
            width="100%",
            thickness=0.5,
            color=PDFColors.GOLD_ACCENT,
            spaceBefore=5,
            spaceAfter=5
        )


class PDFBranding:
    """Company branding constants"""
    COMPANY_NAME = "StockaDoodle Inventory Management System"
    BRANCH_NAME = "QuickMart – Quezon Branch"
    LOGO_PATH = "desktop_app/assets/icons/stockadoodle-transparent.png"