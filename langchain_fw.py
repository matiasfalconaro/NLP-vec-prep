# According to https://github.com/ollama/ollama/blob/main/docs/tutorials/langchainpy.md

'pip install langchain'

# Then we can create a model and ask the question:
from langchain.llms import Ollama
ollama = Ollama(base_url='http://localhost:11434',
model="llama2")
print(ollama("why is the sky blue"))

# pip install bs4

from langchain.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://www.gutenberg.org/files/1727/1727-h/1727-h.htm")
data = loader.load()

# Split the text into chunks

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)

# Find the relevant splits and then submit those to the model. 

'pip install chromadb'

from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
oembed = OllamaEmbeddings(base_url="http://localhost:11434", model="nomic-embed-text")
vectorstore = Chroma.from_documents(documents=all_splits, embedding=oembed)

# Let's ask a question from the document
# This will output the number of matches for chunks of data similar to the search.

question="Who is Neleus and who is in Neleus' family?"
docs = vectorstore.similarity_search(question)
len(docs)

# Send the question and the relevant parts of the docs to the model to see if we can get a good answer.

from langchain.chains import RetrievalQA
qachain=RetrievalQA.from_chain_type(ollama, retriever=vectorstore.as_retriever())
qachain.invoke({"query": question})

