# NPL-vec-prep

## Description
The goal is to create a tool that can be used to create an AI-model trainning dataset. 

The tool is going to be used to extract text from a PDF file, create chunks of text, generate embeddings, and save the embeddings to a vector database. The tool will also be able to perform a semantic search.

## Collaborators
1. Assign yourself an issue
2. Create a branch from `main`, named `<issueNr_branch_name>`
3. Push changes to that branch. Once the functionality is complete, assign the label `ready-for-review`
4. The reviewer will indicate if changes need to be made (by removing the label) or not
5. Once the changes are finalized, the reviewer will merge into the `main` branch

IMPORTANT: the only commits to the main branch should be changes to the README

## Models
This tool works with 2 instances of the Ollama model locally:

- `llama2` (or other conversational model)
- `gnomic-embed-text` (or other open embedding model)

**NOTE: Further tests are needed to determine the best model for the task.**

## Copilot model choice
Table of models and their features
| Model Name       | Coding | Embedded | State-of-the-art | Open training datasets | LLM | Natural language | SQL | General use | Code completion | Multimodal | Large context window | Instructions | Conversational | Merged models |
|------------------|--------|----------|------------------|------------------------|-----|------------------|-----|-------------|-----------------|------------|----------------------|--------------|----------------|---------------|
| llama2           | x      |          | x                |                        | x   | x                |     | x           |                 |            |                      |              | x              |               |
| starling-lm      |        |          | x                |                        | x   | x                |     |             |                 |            |                      |              | x              |               |
| gnomic-embed-text|        | x        | x                | x                      |     |                  |     |             |                 |            | x                    |              |                |               |

## Usage
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
5. Run the models.
```
docker exec -it ollama ollama run nomic-embed-text
```
NOTE: If the message `Error: embedding models do not support chat` appears when pulling th model 'nomic-embed-text', disregard it and continue with the next step.
```
docker exec -it ollama ollama run llama2
```
6. Run de models.
```
docker run ollama
```
7. Run the tool.
```
python main.py
```

### Modelfile
The Modelfile is a configuration file that allows you to customize the behavior of the model.
If you want to create a Modelfile you can edit the `Modelfile_template.txt` and save it as `Modelfile`.

(First 4 steps are equal to the previous ones.)

Run the Ollama container
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
docker exec -it ollama  ollama list
```
9. Run the model.
```
ollama run <modelname>
```
9. Run the tool.
```
python main.py
```
## Output
Once the tool is running the user will be asked to make a question via terminal.

The tool will then return:
    - `logfile.log` (A log file with the files processing information).
    - `chunks_<chunk number>.txt` (Text chunks will be satored in `chunks/`).
    - `embedding_<embedding number>.json` (Embeddings will be satored in `embeddings/`)

The model answers via the terminal.

## Vector Database (VectorStore)
 This tool uses `chromadb`.
 Chroma is an AI-native open-source embedding database.

### Vector database docker installation (Not yet implemented)
Pull the base image installation as a container for the vector database.
```
docker pull chromadb/chroma
```
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
- [Embeddings Theory] (https://jalammar.github.io/illustrated-word2vec)

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
