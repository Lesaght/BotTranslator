"""
OCR module for text extraction from images.
Uses Tesseract OCR for image recognition.
"""
import logging
import os
import pytesseract
from PIL import Image

# Logger for this module
logger = logging.getLogger(__name__)

def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text from the image, or empty string if extraction failed
    """
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return ""
    
    try:
        # Open the image using PIL
        logger.info(f"Opening image: {image_path}")
        image = Image.open(image_path)
        
        # Extract text from the image using pytesseract
        logger.info(f"Extracting text from image: {image_path}")
        extracted_text = pytesseract.image_to_string(image)
        
        # Clean up the text (remove extra whitespace)
        extracted_text = extracted_text.strip()
        
        logger.info(f"Extracted {len(extracted_text)} characters from image")
        return extracted_text
    
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        return ""
