import os
import logging
import datetime
from urllib.parse import urlparse
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.document_transformers import Html2TextTransformer

def setup_logging():
    """Set up logging configuration
    
    Returns:
        str: The path to the log file
    """
    LOG_DIR = "logs"
    os.makedirs(LOG_DIR, exist_ok=True)
    log_filename = os.path.join(LOG_DIR, f"quiz_generator_agents_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return log_filename

def setup_directories(base_dir):
    """Set up necessary directories
    
    Args:
        base_dir (str): The base directory for the application
        
    Returns:
        tuple: A tuple containing the paths to the raw text, summary text, and JSON output directories
    """
    RAW_TEXT_DIR = os.path.join(base_dir, "raw_text")
    SUMMARY_TEXT_DIR = os.path.join(base_dir, "summarized_text")
    JSON_OUTPUT_DIR = os.path.join(base_dir, "json_question_answers")
    
    for directory in [RAW_TEXT_DIR, SUMMARY_TEXT_DIR, JSON_OUTPUT_DIR]:
        os.makedirs(directory, exist_ok=True)
        
    return RAW_TEXT_DIR, SUMMARY_TEXT_DIR, JSON_OUTPUT_DIR

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF
    
    Args:
        pdf_path (str): The path of the PDF file to extract text from

    Returns:
        str: The text extracted from the PDF
    """
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        return "\n".join([page.page_content for page in pages])
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def save_text_to_file(text: str, file_path: str) -> None:
    """Save text to file
    
    Args:
        text (str): The text to save
        file_path (str): The path of the file where to save the text
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        logging.error(f"Error saving text to file: {str(e)}")

def extract_text_from_url(url: str) -> str:
    """Extract text from URL
    
    Args:
        url (str): The URL to extract text from

    Returns:
        str: The text extracted from the URL
    """
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        
        # html to text
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        
        # combine pages into a single text
        return "\n".join([doc.page_content for doc in docs_transformed])
    except Exception as e:
        logging.error(f"Error extracting text from URL {url}: {str(e)}")
        return ""

def get_filename_from_url(url: str) -> str:
    """Extract filename from URL
    
    Args:
        url (str): The URL to extract filename from

    Returns:
        str: The filename extracted from the URL
    """
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path) or parsed.netloc
    # remove file extension
    filename = os.path.splitext(filename)[0]
    return filename 