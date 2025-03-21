from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
import streamlit as st
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_ollama import OllamaLLM
import os

st.title('Langchain Demo with Local LLAMA2 API')
st.header('Ask a question and get a response from the AI chatbot for the company!')
input_text = st.text_input("Enter your question:")

# Specify the directory containing PDFs
pdf_directory = r"C:\Users\Asus\OneDrive\Documents\gen_ai_project\company_chatbot\data_avizva"
chroma_persist_directory = "./chroma_db"  # Directory to store ChromaDB

# Initialize Embeddings
hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# **Check if ChromaDB Already Exists**
if os.path.exists(chroma_persist_directory):
    # Load existing vector database
    db = Chroma(persist_directory=chroma_persist_directory, embedding_function=hf_embeddings)
    print("Loaded existing ChromaDB")
else:
    # Load all PDFs from the directory
    loader = DirectoryLoader(pdf_directory, glob="*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents(docs)

    # Create a new ChromaDB vector store
    db = Chroma.from_documents(documents, hf_embeddings, persist_directory=chroma_persist_directory)
    print("Created new ChromaDB")

# **Define Prompt Template**
prompt = ChatPromptTemplate.from_template("""
Role: HR Assistant  

System Prompt:  
You are an HR assistant at a company, responsible for answering employee questions based on the company's policies and procedures. Your goal is to provide professional, clear, and concise responses strictly based on the given context.  

- **If the answer is found in the context, respond accurately and professionally.**  
- **If the answer is not available in the context, politely suggest contacting HR representative "Anukrit" for further assistance.**  

<context>  
{context}  
</context>  

Question: {input}  
""")

# Initialize Local Ollama Model
llm = OllamaLLM(model="llama3.2")
document_chain = create_stuff_documents_chain(llm, prompt)

# Define Retriever
retriever = db.as_retriever()

# Create a Retrieval Chain
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# Process user input
if input_text:
    response = retrieval_chain.invoke({"input": input_text})
    st.write(response['answer'])

# 6,7,8,9 vedio