#!/usr/bin/env python3

import fitz  # PyMuPDF
import logging
import os
import json

from tempfile import TemporaryDirectory
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.agent_toolkits.file_management.toolkit import FileManagementToolkit
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


# Setup logging
def setup_logging():
    logging.basicConfig(filename='logfile.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    return logging.getLogger(__name__)


# Function to start monitoring TemporaryDirectory
def start_monitoring(path):
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer


# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    logger.info("""Starting PDF file extraction.""")
    text = ""
    with fitz.open(pdf_path) as doc:
        for page_num in doc:
            text += page_num.get_text()
            logger.info(f"Extracted text from {page_num}")
    return text


class MockDocument:
    def __init__(self, text, metadata=None):
        self.page_content = text
        self.metadata = metadata if metadata is not None else {}

            
# Process text into chunks
def process_text_into_chunks(text, temp_dir):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    mock_docs = [MockDocument(text)]
    all_splits = text_splitter.split_documents(mock_docs)
    logger.info(f"Total text chunks created: {len(all_splits)}")
    
    for i, chunk in enumerate(all_splits, start=1):
        logger.info(f"Processing chunk {i}/{len(all_splits)}")
        
    # If the process involves creating or modifying files, add respective logs here.
    # This part is for demonstration; adjust according to actual usage:
    for filename in os.listdir(temp_dir):
        logger.info(f"Modified directory: {temp_dir}, File: {filename}")
        
    return all_splits


# Create embeddings and store in vector database
def create_embeddings_and_store(all_splits, temp_dir):
    oembed = OllamaEmbeddings(base_url="http://localhost:11434", model="nomic-embed-text")
    logger.info(f"Initialized OllamaEmbeddings with model: nomic-embed-text at {oembed.base_url}")
    
    texts = [doc.page_content for doc in all_splits]
    logger.info("Starting to create embeddings for document chunks.")
    
    try:
        embeddings = oembed.embed_documents(texts)
        logger.info("Embeddings created successfully.")
        
        for i, embedding in enumerate(embeddings, start=1):
            embedding_file_path = os.path.join(temp_dir, f"embedding_{i}.json")
            with open(embedding_file_path, 'w') as f:
                json.dump(embedding, f)
            logger.info(f"Saved embedding for chunk {i} to {embedding_file_path}")
            
    except Exception as e:
        logger.error(f"Failed to create embeddings: {e}")
        
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=oembed)
    logger.info("Completed storing embeddings in vector database.")
    return vectorstore

 
# Retrieve answer using chain
def retrieve_answer(vectorstore, question):
    ollama = Ollama(base_url='http://localhost:11434', model="llama2")
    qachain = RetrievalQA.from_chain_type(ollama, retriever=vectorstore.as_retriever())
    answer = qachain.invoke({"query": question})
    if 'result' in answer:
        logger.info(f"User query:\n{answer['query']}")
        logger.info(f"Retrieved answer:\n{answer['result']}")
        print(answer['result'])
    else:
        logger.error("No 'result' found in the response.")
    return answer


# Main function to coordinate the steps
def main():
    global logger
    answer = ""
    logger = setup_logging()
    pdf_path = "documents/Tkinter_expense_manager.pdf"
    text = extract_text_from_pdf(pdf_path)
    
    with TemporaryDirectory() as temp_dir:
        observer = start_monitoring(temp_dir)
        logger.info(f"Monitoring started for temporary directory at {temp_dir}")
        
        # Pass temp_dir as an argument to process_text_into_chunks
        all_splits = process_text_into_chunks(text, temp_dir)  # Fixed here
        
        vectorstore = create_embeddings_and_store(all_splits, temp_dir)
        
        question = input("Enter your question: ")
        logger.info(f"Performing similarity search for the question: {question}")
        
        retrieve_answer(vectorstore, question)

        observer.stop()
        observer.join()
        logger.info("Monitoring stopped for temporary directory.")
        
        final_temp_dir_contents = os.listdir(temp_dir)
        logger.info(f"Final contents of the temporary directory before cleanup: {final_temp_dir_contents}")


if __name__ == "__main__":
    main()

