import os
import datetime
import random
import string
import logging
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from flask import current_app

# ========== CONFIGURATION ==========
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Changed to a Linux path
LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "logo.png")
BARCODE_DIR = os.path.join(os.path.dirname(__file__), "static", "barcodes")
LEFT_MARGIN = 50
TOP_MARGIN = 750
LINE_HEIGHT = 18

# Ensure barcode directory exists
os.makedirs(BARCODE_DIR, exist_ok=True)

# Register font
try:
    pdfmetrics.registerFont(TTFont("Arial", FONT_PATH))
    logging.info(f"Successfully registered font from {FONT_PATH}")
except Exception as e:
    logging.warning(f"Could not register Arial font: {e}")

# ========== UTILITY FUNCTIONS ==========

def generate_invoice_number():
    return f"INV{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

def generate_unique_barcode(length=5):
    from models import Product  # Import Product model here to avoid circular imports
    with current_app.app_context():
        while True:
            barcode_val = ''.join(random.choices(string.digits, k=length))
            if not Product.query.filter_by(barcode=barcode_val).first():
                return barcode_val

def generate_barcode_image_for_invoice(barcode_number):
    barcode_path = os.path.join(BARCODE_DIR, f"{barcode_number}.png")
    # Using get_barcode_class instead of directly importing Code128
    code128 = barcode.get_barcode_class('code128')
    barcode_image = code128(barcode_number, writer=ImageWriter())
    barcode_image.save(barcode_path)
    return barcode_path

# ========== PDF INVOICE GENERATOR ==========

def generate_invoice_pdf(filename, customer_info, items, total_amount, payment_amount, balance_amount, store_info):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Draw watermark/logo
    _draw_watermark(c, width, height)

    # Draw header
    _draw_header(c, store_info, customer_info)

    # Draw item table
    _draw_items_table(c, items)

    # Totals
    _draw_totals(c, total_amount, payment_amount, balance_amount)

    c.save()

    with open(filename, "wb") as f:
        f.write(buffer.getvalue())

def _draw_watermark(c, width, height):
    try:
        c.drawImage(LOGO_PATH, width / 2 - 100, height / 2, width=200, height=200, mask="auto")
    except:
        c.setFont("Helvetica", 50)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, "INVOICE")
        c.restoreState()

def _draw_header(c, store_info, customer_info):
    y = TOP_MARGIN
    c.setFont("Helvetica-Bold", 14)
    c.drawString(LEFT_MARGIN, y, store_info.get("name", "Store Name"))
    c.setFont("Helvetica", 10)
    y -= 15
    c.drawString(LEFT_MARGIN, y, f"Address: {store_info.get('address', '-')}")
    y -= 15
    c.drawString(LEFT_MARGIN, y, f"Phone: {store_info.get('phone', '-')}")
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(LEFT_MARGIN, y, "Customer Info:")
    c.setFont("Helvetica", 10)
    y -= 15
    c.drawString(LEFT_MARGIN, y, f"Name: {customer_info.get('name', '-')}")
    y -= 15
    c.drawString(LEFT_MARGIN, y, f"Contact: {customer_info.get('contact', '-')}")
    y -= 15
    c.drawString(LEFT_MARGIN, y, f"Address: {customer_info.get('address', '-')}")
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(LEFT_MARGIN, y, f"Invoice No: {generate_invoice_number()}")
    y -= 15
    c.drawString(LEFT_MARGIN, y, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def _draw_items_table(c, items):
    y = 520
    c.setFont("Helvetica-Bold", 10)
    headers = ["Item", "Weight (g)", "Rate", "Amount"]
    x_positions = [LEFT_MARGIN, 250, 350, 450]
    for i, header in enumerate(headers):
        c.drawString(x_positions[i], y, header)
    y -= LINE_HEIGHT
    c.setFont("Helvetica", 10)
    for item in items:
        c.drawString(x_positions[0], y, item.get("name", "-"))
        c.drawString(x_positions[1], y, str(item.get("weight", "-")))
        c.drawString(x_positions[2], y, str(item.get("rate", "-")))
        c.drawString(x_positions[3], y, str(item.get("amount", "-")))
        y -= LINE_HEIGHT

def _draw_totals(c, total_amount, payment_amount, balance_amount):
    y = 300
    c.setFont("Helvetica-Bold", 11)
    c.drawString(LEFT_MARGIN, y, f"Total Amount: ₹ {total_amount:.2f}")
    y -= 20
    c.drawString(LEFT_MARGIN, y, f"Payment Received: ₹ {payment_amount:.2f}")
    y -= 20
    c.drawString(LEFT_MARGIN, y, f"Balance: ₹ {balance_amount:.2f}")
