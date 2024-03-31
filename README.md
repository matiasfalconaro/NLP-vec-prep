# NPL-vec-prep

## Description
The goal is to create a tool that can be used to:
- Create an AI-model trainning dataset. 
- Perform semantic research.
- Test AI models using embeddings context.

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
> - All files processing is made in-memory and in temporary directories.
> - Refer to the [Ollama documentation](https://ollama.com/library) for information on the available models and their requirements.

### Virtual environment
> [!WARNING]
1. Python 3.9 virtual environment is recommended.
Since anaconda seems to be causing issues with the installation of some packages, we recommend using a virtual environment.
```
python3 -m venv nlp-venv
```
```
source nlp-venv/bin/activate
```
```
pip install -r requirements.txt
```

> [!NOTE]
If the following error occurs: 

```
An error occurred: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0. Please visit https://docs.trychroma.com/troubleshooting#sqlite to learn how to upgrade.
```
It is ncessary to install the `pysqlite3` package in the virtual environment.
And then edit the `__init__.py` file in the `chromadb` package inside the virtual environment.
```
~/NLP-vec-prep/nlp-venv/lib/python3.9/site-packages/chromadb/__init__.py
```
These 3 lines should be added at the beginning of the file:
```
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```
These three lines swap the stdlib sqlite3 lib with the pysqlite3 package

### Configuration
Edit the `config_template.json` and save it as `config.json`.

- Data path:
    - Specifies the path to the `documents/` directory
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
 In this project, we use Chroma as an in-memory database to store and retrieve embeddings.
