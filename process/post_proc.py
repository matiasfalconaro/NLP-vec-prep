import json
import os
import logging

from typing import List

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
                temp_embedding_file_path = os.path.join(temp_dir, f"embedding_{i}.json")
                permanent_embedding_file_path = os.path.join(embed_dir, f"embedding_{i}.json")
                for path in [temp_embedding_file_path, permanent_embedding_file_path]:
                    with open(path, 'w') as f:
                        json.dump(embedding, f)
            except IOError as e:
                logger.error(f"Failed to save embedding to {path}: {e}")
    except Exception as e:
        logger.error(f"Failed to create embeddings: {e}")

def vector_database_storage(all_splits: List[str],
                            oembed: OllamaEmbeddings,
                            logger: logging.Logger) -> Chroma:
    """
    Read the embeddings from the files and store them in the vector database.
    """
    document_objects = []
    for file_path in all_splits:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                document_objects.append(MockDocument(text=content))
        except Exception as e:
            logger.error(f"Error reading file for vector database: {e}")
            continue

    try:
        vectorstore = Chroma.from_documents(documents=document_objects, embedding=oembed)
    except Exception as e:
        logger.error(f"Failed to create vector database: {e}")
        # Depending on your error handling policy, you might want to return None or raise
        raise
    logger.info("Completed storing embeddings in vector database.")
    return vectorstore

def retrieve_answer(vectorstore: Chroma,
                    question: str,
                    config: dict,
                    logger: logging.Logger) -> dict:
    """
    Retrieve the answer to the user's question.
    """
    try:
        retrieval_config = config["retrieval_model"]
        ollama = Ollama(base_url=retrieval_config["base_url"], model=retrieval_config["model"])
        logger.info(f"Using model: {ollama.model} at {ollama.base_url}")
        qachain = RetrievalQA.from_chain_type(ollama, retriever=vectorstore.as_retriever())
        answer = qachain.invoke({"query": question})
        if 'result' in answer:
            logger.info(f"User query:\n{answer['query']}")
            logger.info(f"Retrieved answer:\n{answer['result']}")
        else:
            logger.error("No 'result' found in the response.")
    except Exception as e:
        logger.error(f"Failed to retrieve answer: {e}")
        # Depending on how critical this failure is, you might want to return an empty dict or raise
        return {}
    return answer
