import os

from halo import Halo
from langchain_community.embeddings import OllamaEmbeddings
from tempfile import TemporaryDirectory

from process.utils import (load_config, setup_logging,
                           start_monitoring,
                           FakeContextManager)
from process.pre_proc import (extract_text,
                              process_text)
from process.post_proc import (create_embeddings,
                               vector_database_storage,
                               retrieve_answer)


def main():
    """
    Main function to run the process.
    """
    spinner = Halo(text='Initializing...', spinner='dots')
    spinner.start()

    try:
        logger = setup_logging()
        config = load_config()
        pdf_path = config["pdf_path"]
        text = extract_text(pdf_path, logger)

        temp_dir_context_manager = (
            TemporaryDirectory() if config["directories"]["use_temp_dir"]
            else FakeContextManager(config["directories"]["temp_dir"])
        )

        with temp_dir_context_manager as temp_dir:
            chunk_dir = config["directories"]["chunk_dir"]
            if not os.path.exists(chunk_dir):
                os.makedirs(chunk_dir)
            embed_dir = config["directories"]["embed_dir"]
            if not os.path.exists(embed_dir):
                os.makedirs(embed_dir)

            if config["monitoring"]["enabled"]:
                observer = start_monitoring(temp_dir)
                logger.info("Monitoring temporary directory.")

            oembed_config = config["ollama_embeddings"]
            oembed = OllamaEmbeddings(base_url=oembed_config["base_url"],
                                      model=oembed_config["model"])

            spinner.text = 'Processing text...'
            all_splits = process_text(text, temp_dir, chunk_dir, logger)
            create_embeddings(all_splits, temp_dir, embed_dir, oembed, logger)
            vectorstore = vector_database_storage(all_splits,
                                                  oembed,
                                                  logger)

            spinner.stop()
            question = input("Enter your question: ")
            spinner.start()

            spinner.text = 'Retrieving answer...'
            answer = retrieve_answer(vectorstore, question, config, logger)
            spinner.stop()
            print(f"Answer: {answer['result']}" if 'result' in answer
                  else "No answer found.")

            if config["monitoring"]["enabled"]:
                observer.stop()
                observer.join()
                logger.info("Monitoring stopped for temporary directory.")
            logger.info("Temporary directory and files deleted.")
            logger.info("Process completed.")
    finally:
        spinner.stop()


if __name__ == "__main__":
    main()
