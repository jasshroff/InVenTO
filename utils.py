import io
import os
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Frame, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas

# Set up logging
logger = logging.getLogger(__name__)

# Try to register fonts, but don't fail if we can't
try:
    font_paths = [
        'DejaVuSans.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'C:/Windows/Fonts/arial.ttf',
        'static/fonts/DejaVuSans.ttf'
    ]
    
    fonts_registered = False
    for path in font_paths:
        try:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont('CustomFont', path))
                logger.info(f"Successfully registered font from {path}")
                fonts_registered = True
                break
        except Exception as e:
            logger.warning(f"Failed to register font from {path}: {str(e)}")
except Exception as e:
    logger.warning(f"Font registration error: {str(e)}")

def generate_invoice_number():
    """Generate a unique invoice number based on timestamp"""
    now = datetime.now()
    return f"INV-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"

# Watermark class to add logo as a background
class Watermark(Flowable):
    def __init__(self, width=None, height=None):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.setFillColorRGB(0.95, 0.95, 0.95)  # Very light gray, almost white
        
        # Try to use the logo image as watermark
        try:
            # Check for logo file in multiple possible locations
            logo_paths = [
                'static/images/logo.png',
                'static/img/logo.png',
                'static/logo.png',
                'logo.png'
            ]
            
            logo_file = None
            for path in logo_paths:
                if os.path.exists(path):
                    logo_file = path
                    break
            
            if logo_file:
                # Calculate center position and scale
                page_width, page_height = A4
                img = canvas.drawImage(
                    logo_file, 
                    x=(page_width - 150) / 2,  # Center horizontally
                    y=(page_height - 150) / 2,  # Center vertically
                    width=150,
                    height=150,
                    mask='auto',
                    preserveAspectRatio=True
                )
                
                # Set transparency
                canvas.setFillAlpha(0.1)  # 10% opacity
            else:
                # If no logo file, draw text as watermark
                canvas.setFont('Helvetica-Bold', 60)
                canvas.setFillAlpha(0.1)  # 10% opacity
                page_width, page_height = A4
                text = "InVenTO"
                canvas.drawCentredString(page_width/2, page_height/2, text)
                
        except Exception as e:
            logger.warning(f"Could not add watermark: {str(e)}")
        
        canvas.restoreState()

class WatermarkDocTemplate(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        SimpleDocTemplate.__init__(self, *args, **kwargs)
            
    def build(self, flowables, **kwargs):
        # Add watermark to each page
        self._calc()  # Calculate the document layout
        frame = Frame(self.leftMargin, self.bottomMargin,
                      self.width, self.height, id='normal')
        
        template = []
        
        def add_watermark(canvas, doc):
            canvas.saveState()
            # Try to use the logo image as watermark
            try:
                # Check for logo file in multiple possible locations
                logo_paths = [
                    'static/images/logo.png',
                    'static/img/logo.png',
                    'static/logo.png',
                    'logo.png'
                ]
                
                logo_file = None
                for path in logo_paths:
                    if os.path.exists(path):
                        logger.info(f"Found logo file at: {path}")
                        logo_file = path
                        break
                    else:
                        logger.info(f"Logo file not found at: {path}")
                
                if logo_file:
                    # Get page dimensions
                    page_width, page_height = A4
                    
                    # First, we'll draw the image with proper opacity
                    # Without the additional white overlay
                    canvas.saveState()
                    
                    # Set the blend mode for the entire canvas
                    # This makes everything drawn on top blend with what's underneath
                    canvas.setFillAlpha(0.25)  # Make the watermark 25% opaque (more visible)
                    
                    # Draw the logo larger for better visibility
                    canvas.drawImage(
                        logo_file, 
                        x=(page_width - 450) / 2,  # Center horizontally
                        y=(page_height - 450) / 2,  # Center vertically
                        width=450,                 # Larger size
                        height=450,
                        mask='auto',
                        preserveAspectRatio=True
                    )
                    
                    canvas.restoreState()
                else:
                    # Fallback to text watermark
                    canvas.setFont('Helvetica-Bold', 90)
                    canvas.setFillColorRGB(0.8, 0.8, 0.8)  # Medium gray
                    canvas.setFillAlpha(0.2)  # 20% opacity (more visible)
                    text = "SGV Jewellers"
                    canvas.drawCentredString(page_width/2, page_height/2, text)
            except Exception as e:
                logger.warning(f"Could not add watermark: {str(e)}")
                logger.exception(e)
            
            canvas.restoreState()
            
        template.append(frame)
        SimpleDocTemplate.build(self, flowables, onFirstPage=add_watermark, onLaterPages=add_watermark, **kwargs)

def generate_invoice_pdf(invoice):
    """Generate a PDF for the given invoice"""
    buffer = io.BytesIO()
    
    # Use A4 size which is more standard for invoices
    doc = WatermarkDocTemplate(buffer, pagesize=A4, 
                           leftMargin=20*mm, rightMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    
    # Create custom styles with better font settings
    font_name = 'Helvetica'
    bold_font = 'Helvetica-Bold'
    
    # Cleaner, more modern styling
    styles.add(ParagraphStyle(
        name='CompanyName',
        parent=styles['Heading3'],
        fontSize=14,
        fontName=bold_font,
        textColor=colors.black,
        leading=16
    ))
    
    styles.add(ParagraphStyle(
        name='SystemName',
        parent=styles['Normal'],
        fontSize=10,
        fontName=font_name,
        textColor=colors.gray,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='InvoiceNumber',
        parent=styles['Heading3'],
        fontSize=12,
        alignment=2,  # Right aligned
        fontName=bold_font,
        textColor=colors.black
    ))
    
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading3'],
        fontSize=10,
        fontName=bold_font,
        textColor=colors.black
    ))
    
    styles.add(ParagraphStyle(
        name='RegularText',
        parent=styles['Normal'],
        fontSize=9,
        fontName=font_name,
        textColor=colors.black,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='PaidStatus',
        parent=styles['Normal'],
        fontSize=12,
        alignment=2,  # Right aligned
        fontName=bold_font,
        textColor=colors.green
    ))
    
    # Add content
    elements = []
    
    # Header with company name and invoice number
    logo_text = Paragraph("Shree Gopaldas Vallabhdas Jewellers", styles['CompanyName'])
    company_text = Paragraph("Trusted Jewellery Store Since 1938", styles['SystemName'])
    invoice_num_text = Paragraph(f"GST-INVOICE #{invoice.invoice_number}", styles['InvoiceNumber'])
    
    # Create a table for the header with logo and invoice number
    header_data = [
        [logo_text, invoice_num_text],
        [company_text, ""]
    ]
    
    header_table = Table(header_data, colWidths=[doc.width/2, doc.width/2])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    
    elements.append(header_table)
    
    # Add status indicator (PAID, PENDING, etc.)
    status_data = [['', Paragraph(invoice.status.upper(), styles['PaidStatus'])]]
    status_table = Table(status_data, colWidths=[doc.width/2, doc.width/2])
    status_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(status_table)
    
    # Add a horizontal line
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, 
                            spaceBefore=3, spaceAfter=6))
    
    # From and To section
    from_title = Paragraph("From:", styles['SectionTitle'])
    to_title = Paragraph("To:", styles['SectionTitle'])
    
    # Company info with clean styling
    company_name = Paragraph("Shree Gopaldas Vallabhdas Jewellers", styles['RegularText'])
    company_address1 = Paragraph("17, Shreenath Sadan", styles['RegularText'])
    company_address2 = Paragraph("Pandumal Chouraha, Burhanpur (M.P.)-450331", styles['RegularText'])
    company_phone = Paragraph("Phone: 7806034035", styles['RegularText'])
    company_email = Paragraph("Email: sgvjewellers1938@gmail.com", styles['RegularText'])
    company_gstin = Paragraph("GSTIN: 23ARPPS1329A1Z1", styles['RegularText'])
    
    # Customer info with clean styling
    customer_name = Paragraph(f"Name: {invoice.customer.name}" if invoice.customer.name else "", styles['RegularText'])
    customer_email = Paragraph(f"Email: {invoice.customer.email}" if invoice.customer.email else "", styles['RegularText'])
    customer_phone = Paragraph(f"Phone: {invoice.customer.phone}" if invoice.customer.phone else "", styles['RegularText'])
    customer_address = Paragraph(f"Address: {invoice.customer.address}" if invoice.customer.address else "", styles['RegularText'])
    customer_gstin = Paragraph(f"GSTIN: {getattr(invoice.customer, 'gstin', '')}" if hasattr(invoice.customer, 'gstin') and invoice.customer.gstin else "", styles['RegularText'])
    
    # Create a table for From/To section with better spacing
    address_data = [
        [from_title, to_title],
        [company_name, customer_name],
        [company_address1, customer_email],
        [company_address2, customer_phone],
        [company_phone, customer_address],
        [company_email, customer_gstin],
        [company_gstin, '']
    ]
    
    address_table = Table(address_data, colWidths=[doc.width/2, doc.width/2])
    address_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 1),
    ]))
    
    elements.append(address_table)
    elements.append(Spacer(1, 5*mm))
    
    # Invoice dates section with better alignment
    issue_date = Paragraph(f"Issue Date: {invoice.issue_date.strftime('%Y-%m-%d')}", styles['RegularText'])
    if invoice.due_date:
        due_date = Paragraph(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}", styles['RegularText'])
    else:
        due_date = Paragraph("", styles['RegularText'])
    
    created_by = Paragraph(f"Created By: {getattr(invoice, 'created_by', '2')}", styles['RegularText'])
    created_on = Paragraph(f"Created On: {invoice.created_at.strftime('%Y-%m-%d %H:%M')}", styles['RegularText'])
    
    dates_data = [
        [issue_date, created_by],
        [due_date, created_on]
    ]
    
    dates_table = Table(dates_data, colWidths=[doc.width/2, doc.width/2])
    dates_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    
    elements.append(dates_table)
    elements.append(Spacer(1, 10*mm))
    
    # Items table with improved styling
    header = ["#", "Item", "Type", "Quantity", "Unit Price", "Total"]
    
    # Set column widths for the items table
    col_widths = [10*mm, 60*mm, 25*mm, 20*mm, 25*mm, 25*mm]
    
    data = [header]
    
    # Use 'Rs.' instead of the rupee symbol to ensure compatibility
    rupee_symbol = "Rs."
    
    for idx, item in enumerate(invoice.items, 1):
        item_name = item.product.name if hasattr(item, 'product') and item.product else (
                   item.service.name if hasattr(item, 'service') and item.service else "Unknown")
        
        item_type = "Service" if getattr(item, 'is_service', False) else "Product"
        
        data.append([
            str(idx),
            item_name,
            item_type,
            str(item.quantity),
            f"{rupee_symbol} {item.unit_price:.2f}",
            f"{rupee_symbol} {item.total_price:.2f}"
        ])
    
    # Create the table with cleaner styling
    items_table = Table(data, colWidths=col_widths)
    
    # Style the table to match the screenshot (light gray header, clean lines)
    header_bg = colors.Color(0.9, 0.9, 0.9)  # Light gray for header
    items_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ])
    
    items_table.setStyle(items_style)
    elements.append(items_table)
    
    # Totals section with right alignment
    elements.append(Spacer(1, 3*mm))
    
    # Calculate GST components (assuming half CGST, half SGST)
    gst_rate = 3  # 3% is standard for gold jewelry in India
    cgst = invoice.tax_amount / 2
    sgst = invoice.tax_amount / 2
    
    totals_data = [
        ["", "", "", "", "Subtotal:", f"{rupee_symbol} {invoice.total_amount:.2f}"],
        ["", "", "", "", f"CGST ({gst_rate/2}%):", f"{rupee_symbol} {cgst:.2f}"],
        ["", "", "", "", f"SGST ({gst_rate/2}%):", f"{rupee_symbol} {sgst:.2f}"]
    ]
    
    if float(invoice.discount) > 0:
        totals_data.append(["", "", "", "", "Discount:", f"{rupee_symbol} {invoice.discount:.2f}"])
    
    totals_data.append(["", "", "", "", "Total:", f"{rupee_symbol} {invoice.final_amount:.2f}"])
    
    totals_table = Table(totals_data, colWidths=col_widths)
    
    # Style totals to match the screenshot
    totals_style = TableStyle([
        ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
        ('LINEABOVE', (-2, -1), (-1, -1), 1, colors.black),
        ('FONTNAME', (-2, -1), (-1, -1), bold_font),
    ])
    
    totals_table.setStyle(totals_style)
    elements.append(totals_table)
    
    # Thank you message
    elements.append(Spacer(1, 20*mm))
    thank_you = Paragraph("Thank you for your business!", styles['RegularText'])
    thank_you_table = Table([[thank_you]], colWidths=[doc.width])
    thank_you_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.gray),
    ]))
    elements.append(thank_you_table)
    
    # Add signature section
    elements.append(Spacer(1, 25*mm))
    signature_data = [
        ["", "______________________"],
        ["", "Authorized Signature"]
    ]
    signature_table = Table(signature_data, colWidths=[doc.width/2, doc.width/2])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 1), 'CENTER'),
        ('FONTNAME', (1, 1), (1, 1), font_name),
        ('FONTSIZE', (1, 1), (1, 1), 8),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.gray),
    ]))
    elements.append(signature_table)
    
    # Add footer with developer info
    elements.append(Spacer(1, 20*mm))
    dev_info = Paragraph("Developed by Team InVenTO - The Inventory Management Systems", 
                      ParagraphStyle(
                          name='Footer',
                          parent=styles['Normal'],
                          fontSize=7,
                          textColor=colors.gray,
                          alignment=1  # Center alignment
                      ))
    elements.append(dev_info)
    
    # Build the document
    try:
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return None
