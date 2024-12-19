import logging
import pandas as pd
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def convert_csv_to_str(file):
    """Convert CSV file to JSON string"""
    logger.info(f"Converting CSV file: {file.filename}")
    raw = pd.read_csv(file).to_dict(orient='records')    
    logger.info(f"Converted {len(raw)} records")
    return str(raw).replace("'", '\"')

def convert_pdf_to_base64(file):
    """Convert PDF file to base64 string"""
    logger.info(f"Converting PDF file: {file.filename}")
    raw = base64.b64encode(file.read()).decode('utf-8')
    logger.info("PDF conversion successful")
    return f"data:application/pdf;base64,{raw}"
