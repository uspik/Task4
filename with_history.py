import json

from langchain_community.chat_models import GigaChat
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.document import Document
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.gigachat import GigaChatEmbeddings
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage
from langchain_core.load.dump import default, dumps, dumpd
from langchain_core.load.load import load, loads
import ast

async def send_with_doc(text, question, chat_history):
    """
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = [Document(page_content=x) for x in text_splitter.split_text(text)]"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_text(text)
    llm = GigaChat(credentials="NWFhZWZjOWItYzJiZS00OWEwLWJjNDgtN2EzZTA0ZWEyOWIxOjFjNzZiM2EzLWVmYTctNGFmZi1hMDNhLTY1NmIxZGYyMmQ4ZA==", verify_ssl_certs=False)


    embeddings = GigaChatEmbeddings(
        credentials="NWFhZWZjOWItYzJiZS00OWEwLWJjNDgtN2EzZTA0ZWEyOWIxOjFjNzZiM2EzLWVmYTctNGFmZi1hMDNhLTY1NmIxZGYyMmQ4ZA==", verify_ssl_certs=False
    )
    db = Chroma.from_texts(
        splits,
        embeddings,
        client_settings=Settings(anonymized_telemetry=False),
    )


    # Извлечение данных и генерация с помощью релевантных фрагментов блога.
    retriever = db.as_retriever()




    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )



    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Use three sentences maximum and keep the answer concise.\
    
    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    chat_history = ast.literal_eval(chat_history)

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    ai_msg = rag_chain.invoke({"input": question, "chat_history": chat_history})
    chat_history.extend([question, ai_msg["answer"]])
    return ai_msg["answer"], chat_history
"""
third_question = "Какая арендная плата по договору субаренды от 01.01.2014?"
ai_msg_3 = rag_chain1.invoke({"input": third_question, "chat_history": chat_history1})
chat_history1.extend([HumanMessage(content=third_question), ai_msg_3["answer"]])
print(ai_msg_3["answer"])

second_question = "Добавь 150 к этому числу"
ai_msg_2 = rag_chain.invoke({"input": second_question, "chat_history": chat_history})
chat_history.extend([HumanMessage(content=second_question), ai_msg_2["answer"]])
print(ai_msg_2["answer"])


forth_question = "Добавь 150 к этому числу"
ai_msg_4 = rag_chain1.invoke({"input": forth_question, "chat_history": chat_history1})
print(ai_msg_4["answer"])"""
