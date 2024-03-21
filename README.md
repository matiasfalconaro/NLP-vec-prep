# NPL-vec-prep

## Description
The goal is to create a tool that can be used to:
- Create an AI-model trainning dataset. 
- Perform semantic research.
- Test AI models using embeddings context.

![Architecture](assets/Architecture.drawio.svg)

## Collaborators
1. Assign yourself an issue
2. Create a branch from `main`, named `<issueNr_branch_name>`
3. Push changes to that branch. Once the functionality is complete, assign the label `ready-for-review`
4. The reviewer will indicate if changes need to be made (by removing the label) or not
5. Once the changes are finalized, the reviewer will merge into the `main` branch

IMPORTANT: the only commits to the main branch should be changes to the README

## Models
This tool use 2 instances of the Ollama model:

- `llama2` / `falcon` (or other conversational model)
- `gnomic-embed-text` (or other embedding model)

## Usage

> [!CAUTION]
> - Computational resources and storage space should be considered when using this tool.
> - Refer to the [Ollama documentation](https://ollama.com/library) for information on the available models and their requirements.

> [!NOTE]
> Python 3.9.5

### Configuration
Edit the `config_template.json` and save it as `config.json`.

- PDF Path:
    - Specifies the path to the PDF file to be processed.
- Logging:
    - Enabled: Indicates whether logging is enabled or not. If enabled, logs will be generated.
    - Log File: Specifies the name of the log file.
    - Level: Sets the logging level (e.g., INFO, DEBUG, ERROR).
    - Format: Defines the format of log entries.
    - Date Format: Specifies the format for timestamps in log entries.
- Directories:
    - Chunk Directory: Specifies the directory where chunked data will be stored.
    - Embed Directory: Specifies the directory where embeddings will be stored.
    - Use Temp Directory: Indicates whether the tool should use a temporary directory.
    - Temp Directory: Specifies the path to a custom temporary directory, if enabled.
- Ollama Embeddings:
    - Base URL: Specifies the base URL for accessing Ollama embeddings model running in the `ollama` container.
    - Model: Specifies the specific Ollama embedding model to be used.
- Monitoring:
    - Enabled: Indicates whether monitoring is enabled. If enabled, progress or status updates could logged into an `logfile`.
- Retrieval Model:
    - Base URL: Specifies the base URL for accessing a retrieval model running in the `ollama` container.
    - Model: Specifies the specific retrieval model to be used.

### Linux installation
For linux the tool can be run using the `init.sh` script. 

The script will automate most of the steps to run the tool and will guide the user through the process. 

Run the script from the project directory with the following command:
```
chmod +x init.sh && ./init.sh
```

## Output
Once the tool is running the user will be asked to make a question and the tool will return the answer via terminal.

## Vector Database (VectorStore)
 This tool uses `chromadb`.
 
 Chroma is an AI-native open-source embedding database.

## Resources:
Ollama
- [Ollama Llama2 model](https://ollama.com/library/llama2)
- [Ollama Nomic-Embed-Text model](https://ollama.com/library/nomic-embed-text)
- [Ollama Docker Image](https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Ollama Model File](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)

Langchain
- [Langchain GitHub](https://github.com/langchain-ai/langchain)
- [Langchainpy Tutorial](https://github.com/ollama/ollama/blob/main/docs/tutorials/langchainpy.md)
- [Langchain Ollama](https://python.langchain.com/docs/integrations/llms/ollama)
- [Langchain Chains](https://python.langchain.com/docs/modules/chains)
- [Langchain Chroma](https://python.langchain.com/docs/integrations/vectorstores/chroma)
- [Langchain Filesystem](https://python.langchain.com/docs/integrations/tools/filesystem)
- [Langchain RetrievalQA](https://api.python.langchain.com/en/latest/chains/langchain.chains.retrieval_qa.base.RetrievalQA.html#langchain.chains.retrieval_qa.base.RetrievalQA)
- [Embeddings Theory](https://jalammar.github.io/illustrated-word2vec)

Chroma
- [Chroma GitHub](https://github.com/chroma-core/chroma)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Chroma Client](https://docs.trychroma.com/reference/Client)
- [Chroma Collection](https://docs.trychroma.com/reference/Collection)

PyMuPDF
- [PyMuPDF GitHub](https://github.com/pymupdf/PyMuPDF)

WatchDog (optional, for file system monitoring)
- [WatchDog GitHub](https://github.com/gorakhargosh/watchdog)

PythonDotEnv
- [PythonDotEnv GitHub](https://github.com/theskumar/python-dotenv)
