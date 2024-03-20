#!/usr/bin/env python3

import fitz  # PyMuPDF
import logging
import os
import json

from typing import Any
from tempfile import TemporaryDirectory
from logging import Logger

from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


def setup_logging() -> Logger:
    """
    Setup logging configuration and return a logger object.
    """
    logging.basicConfig(filename='logfile.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    return logging.getLogger(__name__)


def start_monitoring(path: str) -> Any:
    """
    Monitor the given path for file system events.
    """
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from the PDF file.
    """
    logger.info("Starting PDF file extraction.")
    text = ""
    with fitz.open(pdf_path) as doc:
        for page_num in doc:
            text += page_num.get_text()
            logger.info(f"Extracted text from {page_num}")
    return text


class MockDocument:
    """
    A mock document class to hold the text and metadata.
    """
    def __init__(self, text, metadata=None):
        self.page_content = text
        self.metadata = metadata if metadata is not None else {}


def process_text_into_chunks(text: str, temp_dir: str, permanent_dir: str) -> list:
    """
    Process the text into chunks and store them in the temporary directory.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    mock_docs = [MockDocument(text)]
    splits = text_splitter.split_documents(mock_docs)
    logger.info(f"Total text chunks created: {len(splits)}")
    
    saved_chunk_paths = [] 

    for i, chunk in enumerate(splits, start=1):
        chunk_filename = f"chunk_{i}.txt"
        temp_path = os.path.join(temp_dir, chunk_filename)
        perm_path = os.path.join(permanent_dir, chunk_filename)

        for path in [temp_path, perm_path]:
            with open(path, 'w') as file:
                file.write(chunk.page_content)
            if path == temp_path:
                saved_chunk_paths.append(temp_path)

        logger.info(f"Processed and saved chunk {i}/{len(splits)}")

    return saved_chunk_paths


def create_and_store_embeddings(all_splits: list, temp_dir: str, embed_dir: str, oembed: OllamaEmbeddings):
    """
    Create embeddings for the document chunks and store them in the embeddings directory.
    """
    logger.info(f"Initializing nomic-embed-text at {oembed.base_url}")

    texts = []
    for file_path in all_splits:
        with open(file_path, 'r') as file:
            texts.append(file.read())
    logger.info("Starting to create embeddings for document chunks.")

    try:
        embeddings = oembed.embed_documents(texts)
        logger.info("Embeddings created successfully.")

        for i, embedding in enumerate(embeddings, start=1):
            temp_embedding_file_path = os.path.join(temp_dir, f"embedding_{i}.json")
            permanent_embedding_file_path = os.path.join(embed_dir, f"embedding_{i}.json")
            
            for path in [temp_embedding_file_path, permanent_embedding_file_path]:
                with open(path, 'w') as f:
                    json.dump(embedding, f)
                logger.info(f"Saved embedding for chunk {i} to {path}")

    except Exception as e:
        logger.error(f"Failed to create embeddings: {e}")


def read_files_and_store_in_db(all_splits: list, oembed: OllamaEmbeddings, embed_dir: str) -> Chroma:
    """
    Read the embeddings from the files and store them in the vector database.
    """
    document_objects = []
    for file_path in all_splits:
        with open(file_path, 'r') as file:
            content = file.read()
            document_objects.append(MockDocument(text=content))

    vectorstore = Chroma.from_documents(documents=document_objects, embedding=oembed)
    logger.info("Completed storing embeddings in vector database.")
    return vectorstore


def retrieve_answer(vectorstore: Chroma, question: str) -> dict:
    """
    Retrieve the answer to the user's question.
    """
    ollama = Ollama(base_url='http://localhost:11434', model="<modelname>") # Replace with actual model name
    logger.info(f"Using model:{ollama.model} at {ollama.base_url}")
    qachain = RetrievalQA.from_chain_type(
        ollama, retriever=vectorstore.as_retriever())
    answer = qachain.invoke({"query": question})
    if 'result' in answer:
        logger.info(f"User query:\n{answer['query']}")
        logger.info(f"Retrieved answer:\n{answer['result']}")
        print(f"Answer: {answer['result']}")
    else:
        logger.error("No 'result' found in the response.")
    return answer


def main():
    """
    Main function to perform the NLP tasks.
    """
    global logger
    logger = setup_logging()
    pdf_path = "<documentname.pdf>"
    text = extract_text_from_pdf(pdf_path)

    with TemporaryDirectory() as temp_dir:
        permanent_dir = "chunks"
        if not os.path.exists(permanent_dir):
            os.makedirs(permanent_dir)
        embed_dir = "embeddings/"
        observer = start_monitoring(temp_dir)
        logger.info(f"Monitoring temporary directory at {temp_dir}")

        oembed = OllamaEmbeddings(base_url="http://localhost:11434", model="nomic-embed-text")
        all_splits = process_text_into_chunks(text, temp_dir, permanent_dir)
        create_and_store_embeddings(all_splits, temp_dir, embed_dir, oembed)
        vectorstore = read_files_and_store_in_db(all_splits, oembed, embed_dir)

        question = input("Enter your question: ")
        logger.info(f"Performing search for the question: {question}")

        retrieve_answer(vectorstore, question)

        observer.stop()
        observer.join()
        logger.info("Monitoring stopped for temporary directory.")

    logger.info("Temp directory cleanup complete.")


if __name__ == "__main__":
    main()
