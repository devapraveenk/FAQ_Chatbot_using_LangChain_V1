from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os 
from dotenv import load_dotenv
load_dotenv()

db_file_path='FAISS_Index'
embeddings = HuggingFaceEmbeddings()

def creation_of_vectorDB_in_local(loader):
    data = loader.load()
    db =FAISS.from_documents(data, embeddings)
    db.save_local(db_file_path)

def creation_FAQ_chain():
    db=FAISS.load_local(db_file_path, embeddings)
    retriever =db.as_retriever(score_threshold=0.7)
    
    llm = ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.2)
    
    prompt_temp="""Given the following context and a question, generate an answer based on this context only.
    In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
    If the answer is not found in the context, kindly state "This Question not Present in My Database." Don't try to make up an answer.
    CONTEXT: {context}
    QUESTION: {question}"""

    PROMPT = PromptTemplate(template=prompt_temp, input_variables=["context", "question"])
    chain = RetrievalQA.from_chain_type(llm=llm,chain_type="stuff", 
                                        retriever=retriever, 
                                        input_key="query", 
                                        return_source_documents=False,
                                        chain_type_kwargs={"prompt" : PROMPT})
    return chain

