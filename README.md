# NPL-vec-prep

## Description
The goal is to create a tool that can be used to create an AI-model trainning dataset. 

The tool is going to be used to extract text from a PDF file, create chunks of text, generate embeddings, and save the embeddings to a vector database. The tool will also be able to perform a semantic search.

![Architecture](assets/Architecture.drawio.svg)

## Collaborators
1. Assign yourself an issue
2. Create a branch from `main`, named `<issueNr_branch_name>`
3. Push changes to that branch. Once the functionality is complete, assign the label `ready-for-review`
4. The reviewer will indicate if changes need to be made (by removing the label) or not
5. Once the changes are finalized, the reviewer will merge into the `main` branch

IMPORTANT: the only commits to the main branch should be changes to the README

## Models
This tool works with 2 instances of the Ollama model locally:

- `llama2` / `falcon` (or other conversational model)
- `gnomic-embed-text` (or other open embedding model)

**NOTE: Further tests are needed to determine the best model for the task.**

### Copilot model choice
Table of models and their features
| Model Name       | Coding | Embedded | State-of-the-art | Open training datasets | LLM | Natural language | SQL | General use | Code completion | Multimodal | Large context window | Instructions | Conversational | Merged models |
|------------------|--------|----------|------------------|------------------------|-----|------------------|-----|-------------|-----------------|------------|----------------------|--------------|----------------|---------------|
| llama2           | x      |          | x                |                        | x   | x                |     | x           |                 |            |                      |              | x              |               |
| falcon           | x      |          | x                |                        | x   | x                |     | x           |                 |            | x                    | x            | x              |               |
| gnomic-embed-text|        | x        | x                | x                      |     |                  |     |             |                 |            | x                    |              |                |               |

## Usage

> [!CAUTION]
> Computational resources and storage space should be considered when using this tool.
>
> Refer to the [Ollama documentation](https://ollama.com/library) for information on the available models and their requirements.

> [!WARNING]
> The tool is computationally intensive, so users should expect potentially long processing times depending on PDF size and local machine resources.
>
> Since the tool runs in a temporary directory, logging and monitoring can be enabled to track the process, but users should be aware that log files may become large.
>
> Sub-process products, like chunked data and embeddings, can be stored in permanent directories to avoid data loss, but users should be aware that these directories may also become large.

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

### Linux
For linux the tool can be run using the `init.sh` script. 

The script will automate most of the steps to run the tool and will guide the user through the process. 

Run the script with the following command:
```
chmod +x init.sh && ./init.sh
```

### Installation
1. Create the `documents` directory in `NLP-vec-prep/` and place the PDF file to be processed in the documents folder.
2. Dependencies.
```
pip install -r requirements.txt
```
3. Pull the base image installation wich is a container for the models.
```
docker pull ollama/ollama
```
4. Run the image and the container.
```
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```
5. (optional) Run the models and interact directly via terminal to verify that the conversational/chat model selected is working correctly.  
```
docker exec -it ollama ollama run <conversational/chat model name>
```
6. Run the tool.
```
python main.py
```

### Modelfile
The Modelfile is a configuration file that allows you to customize the behavior of the model.
If you want to create a Modelfile you can edit the `Modelfile_template.txt` and save it as `Modelfile`.

(First 4 steps are equal to the previous ones.)

5. Create the directory where the Modelfile will be stored.
```
docker exec ollama mkdir -p /files
```
6. Copy the Modelfile to the container.
```
docker cp ./Modelfile ollama:/files/Modelfile
```
7. Create the model using the modelfile.
```
docker exec -it ollama ollama create <modelname> -f /files/Modelfile
```
8. List the models to verify that the model was created.
```
docker exec -it ollama ollama list
```
9. (optional) Run the models and interact directly via terminal to verify that the conversational/chat model selected is working correctly.  
```
docker exec -it ollama ollama run <modelname>
```
10. Run the tool.
```
python main.py
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
