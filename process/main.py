import os

from halo import Halo
from tempfile import TemporaryDirectory

from database import ChromaHTTPClient
from utils import (load_config, setup_logging, start_monitoring, FakeContextManager)
from pre_proc import extract_text, process_text
from post_proc import create_embeddings, vector_database_storage, retrieve_answer
from langchain_community.embeddings import OllamaEmbeddings

def main():
    spinner = Halo(text='Initializing...', spinner='dots')
    spinner.start()
    observer = None

    try:
        logger = setup_logging()
        config = load_config()

        data_path = config.get("data_path")
        if not data_path or not os.path.exists(data_path):
            logger.error(f"Data path is incorrect or does not exist: {data_path}")
            spinner.fail("Initialization failed. Check configuration.")
            return

        temp_dir_context_manager = (
            TemporaryDirectory() if config["directories"]["use_temp_dir"]
            else FakeContextManager(config["directories"]["temp_dir"])
        )

        with temp_dir_context_manager as temp_dir:
            chunk_dir = config["directories"]["chunk_dir"]
            os.makedirs(chunk_dir, exist_ok=True)
            embed_dir = config["directories"]["embed_dir"]
            os.makedirs(embed_dir, exist_ok=True)

            if config["monitoring"]["enabled"]:
                observer = start_monitoring(temp_dir)
                if not observer:
                    logger.error("Failed to start monitoring.")

            oembed_config = config["ollama_embeddings"]
            oembed = OllamaEmbeddings(base_url=oembed_config["base_url"], model=oembed_config["model"])

            all_splits = []
            chroma_client = ChromaHTTPClient(base_url=config["chroma"]["base_url"])
            collection_name = config["chroma"]["collection_name"]
            for filename in os.listdir(data_path):
                if filename.lower().endswith('.pdf'):
                    pdf_path = os.path.join(data_path, filename)
                    logger.info(f"Processing PDF: {pdf_path}")
                    text = extract_text(pdf_path, logger)
                    processed_paths = process_text(text, temp_dir, chunk_dir, filename, logger)
                    all_splits.extend(processed_paths)

            if all_splits:
                spinner.text = 'Creating embeddings...'
                create_embeddings(all_splits, temp_dir, embed_dir, oembed, logger)
                spinner.text = 'Storing embeddings in vector database...'
                vectorstore = vector_database_storage(all_splits, oembed, logger, chroma_client, collection_name)

                spinner.stop()
                question = input("Enter your question: ")
                spinner.start()

                spinner.text = 'Retrieving answer...'
                answer = retrieve_answer(vectorstore, question, config, logger)
                spinner.stop()
                print(f"Answer: {answer['result']}" if 'result' in answer else "No answer found.")
            else:
                logger.error("No documents were processed.")
                spinner.fail("No documents processed.")

            if observer and config["monitoring"]["enabled"]:
                observer.stop()
                observer.join()
                logger.info("Monitoring stopped for temporary directory.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        spinner.fail("Process failed. Check LogFile for details.")
    finally:
        if observer and observer.is_alive():
            observer.stop()
            observer.join()
        spinner.stop()
        logger.info("Process completed.")

if __name__ == "__main__":
    main()
