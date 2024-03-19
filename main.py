import fitz # PyMuPDF

from tempfile import TemporaryDirectory
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.agent_toolkits.file_management.toolkit import FileManagementToolkit
from langchain_community.tools.file_management.read import ReadFileTool
from langchain_community.tools.file_management.write import WriteFileTool
from langchain_community.tools.file_management.list_dir import ListDirectoryTool


pdf_path = "documents/Tkinter_expense_manager.pdf"

# Read the PDF file and extract text
text = ""
with fitz.open(pdf_path) as doc:
    for page_num in doc:
        text += page_num.get_text()

# At this point, `text` contains the textual content of the PDF file.
with TemporaryDirectory() as temp_dir:
    toolkit = FileManagementToolkit(root_dir=str(temp_dir))
    tools = toolkit.get_tools()

    # Initialize placeholders for the tools we need
    read_tool = None
    write_tool = None
    list_tool = None

    # Figuring out if each tool can be identified by a specific attribute or type
    for tool in tools:
        if isinstance(tool, ReadFileTool):
            read_tool = tool
        elif isinstance(tool, WriteFileTool):
            write_tool = tool
        elif isinstance(tool, ListDirectoryTool):
            list_tool = tool

    if read_tool is None or write_tool is None or list_tool is None:
        exit(1)
    
    # Process the extracted PDF text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    
    # Create a mock class to wrap text in the expected format
    class MockDocument:
        def __init__(self, text, metadata=None):
            self.page_content = text
            self.metadata = metadata if metadata is not None else {}

    # String containing the PDF text you extracted earlier
    mock_docs = [MockDocument(text)]

    # Now, try splitting the documents again
    all_splits = text_splitter.split_documents(mock_docs)

    # Create the embeddings using nomic-embed-text model and store then in the Chroma vectorstore 
    oembed = OllamaEmbeddings(base_url="http://localhost:11434", model="nomic-embed-text")
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=oembed)

    # Use the vectorstore to perform similarity searches
    question = "¿Como puedo modificar un registro?"
    print(f"Question: {question}")
    docs = vectorstore.similarity_search(question)

    # Use the llama2 model to perform a QA search 
    ollama = Ollama(base_url='http://localhost:11434', model="llama2")
    qachain = RetrievalQA.from_chain_type(ollama, retriever=vectorstore.as_retriever())
    answer = qachain.invoke({"query": question})
    print(f"Answer: {answer}")