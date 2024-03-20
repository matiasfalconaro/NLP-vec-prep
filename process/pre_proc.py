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
    with fitz.open(pdf_path) as doc:
        for page_num in doc:
            text += page_num.get_text()
            logger.info(f"Extracted text from page {page_num.number}")
    return text


def process_text(text: str,
                 temp_dir: str,
                 chunk_dir: str,
                 logger: logging.Logger) -> List[str]:
    """
    Process the text into chunks and store them in the temporary directory.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                                   chunk_overlap=20)
    mock_docs = [MockDocument(text)]
    splits = text_splitter.split_documents(mock_docs)

    saved_chunk_paths = []
    for i, chunk in enumerate(splits, start=1):
        chunk_filename = f"chunk_{i}.txt"
        temp_path = os.path.join(temp_dir, chunk_filename)
        perm_path = os.path.join(chunk_dir, chunk_filename)
        logger.info(f"Saving chunk {i} to {temp_path} and {perm_path}")
        for path in [temp_path, perm_path]:
            with open(path, 'w') as file:
                file.write(chunk.page_content)
            if path == temp_path:
                saved_chunk_paths.append(temp_path)
            logger.info(f"Saved chunk {i} to {path}")

    return saved_chunk_paths
