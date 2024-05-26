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
import ast
from promts import contextualize_q_system_prompt, qa_system_prompt, qa_system_prompt_practic

contextualize_q_system_prompt = contextualize_q_system_prompt
qa_system_prompt = qa_system_prompt
qa_system_prompt_practic = qa_system_prompt_practic

async def send_with_doc(text, question, chat_history, analysis):
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
    )


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

    chat_history = ast.literal_eval(chat_history)

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    ai_msg = rag_chain.invoke({"input": question, "chat_history": chat_history})
    chat_history.extend([question, ai_msg["answer"]])
    return ai_msg["answer"], chat_history
