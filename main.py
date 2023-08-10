
from langchain import PromptTemplate, HuggingFaceHub, LLMChain
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from huggingface_hub import hf_hub_download
import textwrap
import glob
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5173",  # Add your React frontend URL
    # Add other allowed origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HUGGING_FACE_API_KEY = "YOUR-KEY-HERE"

import os
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "YOUR-KEY-HERE"

model = HuggingFaceHub(repo_id="google/flan-t5-large" ,model_kwargs={"temperature": 0.7, "max_length":64} ,huggingfacehub_api_token=HUGGING_FACE_API_KEY)

hf_embeddings = HuggingFaceEmbeddings(model_name='google/flan-t5-large')

# pass the text and embeddings to FAISS
vectorstore = FAISS.load_local("faiss_index", hf_embeddings)


# from langchain.memory import ConversationBufferMemory
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

my_chain = load_qa_with_sources_chain(model, chain_type="refine")

def ans_retrieve(query):
  documents = vectorstore.similarity_search(query)
  result = my_chain.run({"input_documents": documents, "question": query})
  return result


import sqlite3

# Function to insert the query and chatbot response into the database
def insert_into_database(query, response):
    # Connecting to the database
    database_path = "C:\\Users\\Talha Nadeem\\Desktop\\FE\\ReactChatGPTChatbot\\chatbot_db.db"
    conn = sqlite3.connect(database_path)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    # print("Hello")
    cursor.execute('INSERT INTO chatbot_history (query, chatbot_response) VALUES (?, ?)', (query, response))
    conn.commit()
    # print("hello")


from typing import List
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

# Endpoint to handle incoming chatbot queries
@app.post("/chatbot")
def chatbot_endpoint(user_query: str):
    # Getting the answer from chatbot

    chatbot_response = ans_retrieve(user_query)

    # Log the response before sending it
    #print("Chatbot Response:", chatbot_response)
    
    insert_into_database(user_query, chatbot_response)

    return {"response": chatbot_response}


@app.get("/", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("temp.html", {"request": request})

 
