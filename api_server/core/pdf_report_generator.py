from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    Image, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from io import BytesIO


class PDFReportGenerator:
    """
    Professional PDF report generator for all 7 StockaDoodle reports
    with company branding and proper formatting
    """
    
    # Company branding
    BRANCH_NAME = "Quezon Branch"
    COMPANY_NAME = "StockaDoodle Inventory Management System"
    LOGO_PATH = "desktop_app/assets/icons/stockadoodle-logo.png"
    
    # Color scheme
    PRIMARY_COLOR = colors.HexColor('#6C5CE7')
    SECONDARY_COLOR = colors.HexColor('#00B894')
    ACCENT_COLOR = colors.HexColor('#D63031')
    HEADER_BG = colors.HexColor('#2C3E50')
    ROW_ALT_BG = colors.HexColor('#ECF0F1')
    
    def __init__(self):
        """Initialize PDF generator with custom styles"""
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.HEADER_BG,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=10,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    def _add_header(self, elements):
        """Add company header with logo and branch info"""
        # Add logo if exists
        if os.path.exists(self.LOGO_PATH):
            try:
                logo = Image(self.LOGO_PATH, width=1.5*inch, height=1.5*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.2*inch))
            except:
                pass
        
        # Company name
        elements.append(Paragraph(self.COMPANY_NAME, self.styles['CustomTitle']))
        
        # Branch name
        branch_text = f"<b>{self.BRANCH_NAME}</b>"
        elements.append(Paragraph(branch_text, self.styles['CustomSubtitle']))
        
        elements.append(Spacer(1, 0.3*inch))
    
    def _add_footer(self, elements):
        """Add report footer"""
        elements.append(Spacer(1, 0.3*inch))
        
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        elements.append(Paragraph(footer_text, self.styles['Footer']))
        
        footer_text2 = f"{self.COMPANY_NAME} | {self.BRANCH_NAME}"
        elements.append(Paragraph(footer_text2, self.styles['Footer']))
    
    def _create_table(self, data, col_widths=None, has_header=True):
        """Create a styled table"""
        table = Table(data, colWidths=col_widths)
        
        # Base style
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), self.HEADER_BG) if has_header else None,
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke) if has_header else None,
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold') if has_header else None,
            ('FONTSIZE', (0, 0), (-1, 0), 12) if has_header else None,
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12) if has_header else None,
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.ROW_ALT_BG]),
        ]
        
        # Remove None values
        style = [s for s in style if s is not None]
        table.setStyle(TableStyle(style))
        
        return table
    
    # ================================================================
    # REPORT 1: Sales Performance Report
    # ================================================================
    def generate_sales_performance_report(self, report_data):
        """Generate Report 1: Sales Performance Report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        elements = []
        
        # Header
        self._add_header(elements)
        
        # Report title
        title = Paragraph("Sales Performance Report", self.styles['CustomTitle'])
        elements.append(title)
        
        # Date range
        date_range = f"Report Period: {report_data['date_range']['start']} to {report_data['date_range']['end']}"
        elements.append(Paragraph(date_range, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary section
        elements.append(Paragraph("Summary", self.styles['SectionHeader']))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Revenue', f"${report_data['summary']['total_income']:,.2f}"],
            ['Total Quantity Sold', f"{report_data['summary']['total_quantity_sold']:,}"],
            ['Total Transactions', f"{report_data['summary']['total_transactions']:,}"]
        ]
        
        summary_table = self._create_table(summary_data, col_widths=[3*inch, 3*inch])
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Sales details
        if report_data['sales']:
            elements.append(Paragraph("Sales Details", self.styles['SectionHeader']))
            
            sales_data = [['Sale ID', 'Date', 'Product', 'Qty', 'Price', 'Retailer']]
            
            for sale in report_data['sales'][:50]:  # Limit to 50 for PDF
                sales_data.append([
                    str(sale['sale_id']),
                    sale['date'][:10],
                    sale['product_name'][:25],
                    str(sale['quantity_sold']),
                    f"${sale['total_price']:,.2f}",
                    sale['retailer_name'][:20]
                ])
            
            sales_table = self._create_table(
                sales_data, 
                col_widths=[0.7*inch, 1*inch, 2*inch, 0.6*inch, 1*inch, 1.5*inch]
            )
            elements.append(sales_table)
        
        # Footer
        self._add_footer(elements)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    # ================================================================
    # REPORT 2: Category Distribution Report
    # ================================================================
    def generate_category_distribution_report(self, report_data):
        """Generate Report 2: Category Distribution Report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        elements = []
        
        # Header
        self._add_header(elements)
        
        # Report title
        title = Paragraph("Category Distribution Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_text = f"Total Categories: {report_data['summary']['total_categories']} | Total Stock: {report_data['summary']['total_stock']:,} units"
        elements.append(Paragraph(summary_text, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Category table
        cat_data = [['Category', 'Products', 'Stock Quantity', 'Percentage']]
        
        for cat in report_data['categories']:
            cat_data.append([
                cat['category_name'],
                str(cat['number_of_products']),
                f"{cat['total_stock_quantity']:,}",
                f"{cat['percentage_share']:.1f}%"
            ])
        
        cat_table = self._create_table(
            cat_data,
            col_widths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch]
        )
        elements.append(cat_table)
        
        # Footer
        self._add_footer(elements)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    # ================================================================
    # REPORT 3: Retailer Performance Report
    # ================================================================
    def generate_retailer_performance_report(self, report_data):
        """Generate Report 3: Retailer Performance Report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        elements = []
        
        # Header
        self._add_header(elements)
        
        # Report title
        title = Paragraph("Retailer Performance Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_text = f"Total Retailers: {report_data['summary']['total_retailers']} | Active Today: {report_data['summary']['active_today']}"
        elements.append(Paragraph(summary_text, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Retailer table
        ret_data = [['Retailer', 'Daily Quota', 'Today\'s Sales', 'Progress', 'Streak', 'Total Sales']]
        
        for ret in report_data['retailers']:
            ret_data.append([
                ret['retailer_name'][:25],
                f"${ret['daily_quota']:,.2f}",
                f"${ret['current_sales']:,.2f}",
                f"{ret['quota_progress']:.1f}%",
                str(ret['streak_count']),
                f"${ret['total_sales']:,.2f}"
            ])
        
        ret_table = self._create_table(
            ret_data,
            col_widths=[2*inch, 1*inch, 1*inch, 0.8*inch, 0.7*inch, 1*inch]
        )
        elements.append(ret_table)
        
        # Footer
        self._add_footer(elements)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    # ================================================================
    # REPORT 4: Low-Stock and Expiration Alert Report
    # ================================================================
    def generate_alerts_report(self, report_data):
        """Generate Report 4: Low-Stock and Expiration Alert Report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        elements = []
        
        # Header
        self._add_header(elements)
        
        # Report title
        title = Paragraph("Low-Stock & Expiration Alert Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_text = f"Total Alerts: {report_data['summary']['total_alerts']} | Critical: {report_data['summary']['critical_alerts']} | Warning: {report_data['summary']['warning_alerts']}"
        elements.append(Paragraph(summary_text, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Alerts table
        alert_data = [['Product', 'Current Stock', 'Min Level', 'Expiration', 'Status', 'Severity']]
        
        for alert in report_data['alerts']:
            # Color code severity
            alert_data.append([
                alert['product_name'][:30],
                str(alert['current_stock']),
                str(alert['min_stock_level']),
                alert['expiration_date'] or 'N/A',
                alert['alert_status'],
                alert['severity']
            ])
        
        alert_table = self._create_table(
            alert_data,
            col_widths=[2*inch, 1*inch, 0.9*inch, 1*inch, 1.5*inch, 0.8*inch]
        )
        
        # Apply color coding for severity
        table_style = alert_table._cellStyles
        for i, alert in enumerate(report_data['alerts'], start=1):
            if alert['severity'] == 'CRITICAL':
                alert_table.setStyle(TableStyle([
                    ('BACKGROUND', (5, i), (5, i), colors.HexColor('#FFCCCC')),
                    ('TEXTCOLOR', (5, i), (5, i), self.ACCENT_COLOR)
                ]))
        
        elements.append(alert_table)
        
        # Footer
        self._add_footer(elements)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    # ================================================================
    # REPORT 5: Managerial Activity Log Report
    # ================================================================
    def generate_managerial_activity_report(self, report_data):
        """Generate Report 5: Managerial Activity Log Report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        elements = []
        
        # Header
        self._add_header(elements)
        
        # Report title
        title = Paragraph("Managerial Activity Log Report", self.styles['CustomTitle'])
        elements.append(title)
        
        # Date range
        date_range = f"Report Period: {report_data['date_range']['start']} to {report_data['date_range']['end']}"
        elements.append(Paragraph(date_range, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_text = f"Total Actions: {report_data['summary']['total_actions']} | Unique Managers: {report_data['summary']['unique_managers']}"
        elements.append(Paragraph(summary_text, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Activity table
        log_data = [['Log ID', 'Product', 'Action', 'Manager', 'Date/Time']]
        
        for log in report_data['logs'][:100]:  # Limit to 100
            log_data.append([
                str(log['log_id']),
                log['product_name'][:25],
                log['action_performed'],
                log['manager_name'][:20],
                log['date_time'][:16]
            ])
        
        log_table = self._create_table(
            log_data,
            col_widths=[0.7*inch, 2*inch, 1.3*inch, 1.5*inch, 1.5*inch]
        )
        elements.append(log_table)
        
        # Footer
        self._add_footer(elements)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    # ================================================================
    # REPORT 6: Detailed Sales Transaction Report
    # ================================================================
    def generate_transactions_report(self, report_data):
        """Generate Report 6: Detailed Sales Transaction Report (same as Report 1)"""
        return self.generate_sales_performance_report(report_data)
    
    # ================================================================
    # REPORT 7: User Accounts Report
    # ================================================================
    def generate_user_accounts_report(self, report_data):
        """Generate Report 7: User Accounts Report"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        elements = []
        
        # Header
        self._add_header(elements)
        
        # Report title
        title = Paragraph("User Accounts Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary = report_data['summary']
        summary_text = f"Total Users: {summary['total_users']} | Admins: {summary['admins']} | Managers: {summary['managers']} | Retailers: {summary['retailers']}"
        elements.append(Paragraph(summary_text, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # User table
        user_data = [['User ID', 'Username', 'Full Name', 'Role', 'Status']]
        
        for user in report_data['users']:
            user_data.append([
                str(user['user_id']),
                user['username'][:20],
                user['full_name'][:25],
                user['role'].capitalize(),
                user['account_status']
            ])
        
        user_table = self._create_table(
            user_data,
            col_widths=[0.8*inch, 1.5*inch, 2*inch, 1.2*inch, 1.2*inch]
        )
        elements.append(user_table)
        
        # Footer
        self._add_footer(elements)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer