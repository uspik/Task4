from langchain_community.chat_models import GigaChat
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
from langchain_community.callbacks import get_openai_callback
import ast
from promts import contextualize_q_system_prompt, qa_system_prompt, qa_system_prompt_practic
import re

contextualize_q_system_prompt = contextualize_q_system_prompt
qa_system_prompt = qa_system_prompt
qa_system_prompt_practic = qa_system_prompt_practic

def send_with_doc(text, question, chat_history, analysis):
    global  contextualize_q_system_prompt, qa_system_prompt, qa_system_prompt_practic
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
        #persist_directory = "C:/Users/User1/PycharmProjects/Task4/Chroma",
    )
    """db = Chroma(
        persist_directory="C:/Users/User1/PycharmProjects/Task4/Chroma",
        embedding_function=embeddings
    )"""
    #print(llm.tokens_count(mas))
    tok = 0
    for i in llm.tokens_count(splits):
        tok += int(re.search(r"tokens=\d*", str(i)).group(0)[7:])
    # Извлечение данных и генерация с помощью релевантных фрагментов блога.
    retriever = db.as_retriever()




    contextualize_q_system_prompt = contextualize_q_system_prompt
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


    if not analysis:
        qa_system_prompt = qa_system_prompt
    else:
        qa_system_prompt = qa_system_prompt_practic
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    all_message = 0
    all_message += tok
    mas = [f'("system", {qa_system_prompt}),MessagesPlaceholder("chat_history"),("human", "{input}")']
    all_message += llm.tokens_count(mas)
    mas = [f'("system", {contextualize_q_system_prompt}),MessagesPlaceholder("chat_history"),("human", "{input}")']
    all_message += llm.tokens_count(mas)
    mas = [str(question)]
    all_message += llm.tokens_count(mas)

    chat_history = ast.literal_eval(chat_history)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    ai_msg = rag_chain.invoke({"input": question, "chat_history": chat_history})
    #print(rag_chain.invoke({"input": question, "chat_history": chat_history}))
    chat_history.extend([question, ai_msg["answer"]])
    return ai_msg["answer"], chat_history, tok, all_message

