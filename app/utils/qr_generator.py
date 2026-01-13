"""
QR Code Generator for ScooterShare Pro
"""

import qrcode
import io
import base64
from flask import url_for

def generate_qr_code_image(qr_code_text: str, size: int = 200) -> str:
    """
    Generate QR code image and return as base64 data URL
    
    Args:
        qr_code_text: The text to encode in QR code
        size: Size of the QR code image
        
    Returns:
        Base64 data URL for QR code image
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data and optimize
    qr.add_data(qr_code_text)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize to desired size
    img = img.resize((size, size))
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Return as data URL
    return f"data:image/png;base64,{img_str}"
