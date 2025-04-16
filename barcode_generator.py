import os
import barcode
from barcode.writer import ImageWriter

# Folder to save barcode images
BARCODE_FOLDER = 'static/barcodes'

# Ensure folder exists
os.makedirs(BARCODE_FOLDER, exist_ok=True)

def generate_barcode_image(barcode_text):
    code128 = barcode.get('code128', barcode_text, writer=ImageWriter())
    file_path = os.path.join(BARCODE_FOLDER, barcode_text)
    filename = code128.save(file_path)  # Automatically adds .png
    return f"{filename}.png"  # Return path to saved image
