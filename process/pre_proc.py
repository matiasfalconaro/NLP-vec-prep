import fitz  # PyMuPDF
import logging
import os

from typing import List

from process.utils import MockDocument

from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text(pdf_path: str, logger: logging.Logger) -> str:
    """
    Extract text from the PDF file.
    """
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page_num in doc:
                text += page_num.get_text()
                logger.info(f"Extracted text from page {page_num.number}")
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path}: {e}")
        raise
    return text

def process_text(text: str, temp_dir: str, chunk_dir: str, logger: logging.Logger) -> List[str]:
    """
    Process the text into chunks and store them in the temporary directory.
    """
    saved_chunk_paths = []
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        mock_docs = [MockDocument(text)]
        splits = text_splitter.split_documents(mock_docs)

        for i, chunk in enumerate(splits, start=1):
            chunk_filename = f"chunk_{i}.txt"
            temp_path = os.path.join(temp_dir, chunk_filename)
            perm_path = os.path.join(chunk_dir, chunk_filename)
            logger.info(f"Saving chunk {i} to {temp_path} and {perm_path}")
            for path in [temp_path, perm_path]:
                try:
                    with open(path, 'w') as file:
                        file.write(chunk.page_content)
                    if path == temp_path:
                        saved_chunk_paths.append(temp_path)
                    logger.info(f"Saved chunk {i} to {path}")
                except IOError as e:
                    logger.error(f"Failed to save chunk {i} to {path}: {e}")
    except Exception as e:
        logger.error(f"Failed during text processing: {e}")
        raise

    return saved_chunk_paths
