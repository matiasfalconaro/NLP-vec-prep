import fitz  # PyMuPDF
import json
import os
import re

from typing import List


def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)


def extract_text(pdf_path: str, skip_pages: List[int]) -> str:
    """
    Extract text from the PDF file, skipping specified pages.
    """
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc, start=1):
                if i in skip_pages:
                    continue
                page_text = page.get_text()
                # Remove standalone numbers
                page_text = re.sub(r'^\s*\d+\s*$',
                                   '',
                                   page_text,
                                   flags=re.MULTILINE)
                # Reduce multiple newlines to a single one
                page_text = re.sub(r'\n\s*\n',
                                   '\n',
                                   page_text)
                text += page_text
    except Exception as e:
        print(f"Failed to process {pdf_path}: {str(e)}")
        return ""
    return text


def split_text(text: str, max_size: int) -> List[str]:
    """
    Split the given text into chunks,
    ending each chunk with an empty line.
    """
    chunks = []
    current_chunk = ""
    for line in text.split('\n'):
        # +1 for the newline character
        if len(current_chunk) + len(line) + 1 > max_size:
            # Check if the current chunk ends appropriately.
            # Add newline if it doesn't.
            if not current_chunk.endswith('\n'):
                current_chunk += '\n'
            chunks.append(current_chunk)
            # Start a new chunk with the current line
            current_chunk = line + '\n'
        else:
            current_chunk += line + '\n'

    if current_chunk:
        # Ensure the final chunk is properly terminated with a newline
        if not current_chunk.endswith('\n'):
            current_chunk += '\n'
        chunks.append(current_chunk)
    return chunks


def save_chunks(chunks: List[str],
                base_directory: str,
                document_name: str) -> None:
    """
    Save each chunk to a separate file
    in a dedicated directory for the document.
    """
    directory = os.path.join(base_directory, document_name)
    if not os.path.exists(directory):
        os.makedirs(directory)

    for i, chunk in enumerate(chunks):
        file_path = os.path.join(directory,
                                 f"{document_name}_chunk_{i+1}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(chunk)


def process_pdfs(config: dict) -> None:
    """
    Process all PDF files based on the configuration settings.
    """
    pdf_directory = config.get('documents_directory', 'documents')
    chunks_directory = config.get('chunks_directory', 'chunks')
    
    for pdf_filename in os.listdir(pdf_directory):
        if pdf_filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_directory, pdf_filename)
            settings = config['documents'].get(pdf_filename, {})
            skip_pages = settings.get('skip_pages', [])
            max_chunk_size = settings.get('max_chunk_size', 500)
            print(f"Processing {pdf_filename}")
            text = extract_text(pdf_path, skip_pages)
            chunks = split_text(text, max_chunk_size)
            save_chunks(chunks,
                        chunks_directory,
                        os.path.splitext(pdf_filename)[0])


config = load_config()
process_pdfs(config)
