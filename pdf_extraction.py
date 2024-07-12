import pdfplumber
import logging

logging.basicConfig(level=logging.DEBUG)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise e
    return text
