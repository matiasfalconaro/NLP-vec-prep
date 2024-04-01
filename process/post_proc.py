import json
import os
import logging
import traceback

from typing import List

from database import ChromaHTTPClient
from utils import MockDocument

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama


def create_embeddings(all_splits: List[str],
                      temp_dir: str,
                      embed_dir: str,
                      oembed: OllamaEmbeddings,
                      logger: logging.Logger) -> None:
    """
    Create embeddings for the document chunks
    and store them in the embeddings directory.
    """
    texts = []
    for file_path in all_splits:
        try:
            with open(file_path, 'r') as file:
                texts.append(file.read())
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            continue

    try:
        embeddings = oembed.embed_documents(texts)
        for i, embedding in enumerate(embeddings, start=1):
            try:
                temp_embedding_file_path = os.path.join(
                    temp_dir, f"embedding_{i}.json")
                permanent_embedding_file_path = os.path.join(
                    embed_dir, f"embedding_{i}.json")
                for path in [temp_embedding_file_path,
                             permanent_embedding_file_path]:
                    with open(path, 'w') as f:
                        json.dump(embedding, f)
            except IOError as e:
                logger.error(f"Failed to save embedding to {path}: {e}")
    except Exception as e:
        logger.error(f"Failed to create embeddings: {e}")


def vector_database_storage(all_splits: List[str],
                            oembed: OllamaEmbeddings,
                            logger: logging.Logger,
                            chroma_client: ChromaHTTPClient,
                            collection_name: str):
    """
    Read the documents from the files, generate embeddings using Ollama,
    and store them in the Chroma vector database using the HTTP client.
    """
    # Metadata for collection creation
    metadata = {
        "description": " Backend DI document embeddings.",
        "createdBy": "Matias",
        "purpose": "Storing embeddings for RAG."
    }
    
    # Ensure the collection exists in Chroma
    try:
        collection_info = chroma_client.create_collection(collection_name, metadata=metadata)
        collection_id = collection_info.get("id") if collection_info and 'id' in collection_info else collection_name
    except Exception as e:
        logger.error(f"Failed to prepare the collection: {e}")
        return
    
    for file_path in all_splits:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                # Generate embeddings for the document using Ollama
                embeddings = oembed.embed_documents([content])[0]
                
                # Prepare the document along with its embedding to be sent to Chroma
                add_response = chroma_client.add_to_collection(
                    collection_id=collection_id,
                    embeddings=[embeddings],
                    documents=[content],
                    metadatas=[{}],
                    uris=[],
                    ids=[]
                )
                if add_response:
                    logger.info(f"Document added successfully: {file_path}")
                else:
                    logger.error(f"Failed to add document to the collection: {file_path}")
        except Exception as e:
            logger.error(f"Error processing file for vector database: {file_path}; {e}")

    logger.info("Completed storing embeddings in vector database.")


def retrieve_answer(vectorstore: Chroma,
                    question: str,
                    config: dict,
                    logger: logging.Logger) -> dict:
    """
    Retrieve the answer to the user's question.
    """
    try:
        retrieval_config = config["retrieval_model"]
        ollama = Ollama(base_url=retrieval_config["base_url"],
                        model=retrieval_config["model"])
        logger.info(f"Using model: {ollama.model} at {ollama.base_url}")
        qachain = RetrievalQA.from_chain_type(
            ollama, retriever=vectorstore.as_retriever())
        answer = qachain.invoke({"query": question})
        if 'result' in answer:
            logger.info(f"User query:\n{answer['query']}")
            logger.info(f"Retrieved answer:\n{answer['result']}")
        else:
            logger.error("No 'result' found in the response.")
    except Exception as e:
        logger.error(f"Failed to retrieve answer: {e}")
        return {}
    return answer
