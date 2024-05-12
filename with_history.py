from langchain import hub
from langchain.vectorstores import Chroma
from langchain_community.chat_models import GigaChat
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import GigaChatEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)

llm = GigaChat(credentials="NWFhZWZjOWItYzJiZS00OWEwLWJjNDgtN2EzZTA0ZWEyOWIxOjFjNzZiM2EzLWVmYTctNGFmZi1hMDNhLTY1NmIxZGYyMmQ4ZA==", verify_ssl_certs=False)


loader = TextLoader("Text.txt", "utf-8")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
documents = text_splitter.split_documents(documents)


from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain_community.embeddings.gigachat import GigaChatEmbeddings

embeddings = GigaChatEmbeddings(
    credentials="NWFhZWZjOWItYzJiZS00OWEwLWJjNDgtN2EzZTA0ZWEyOWIxOjFjNzZiM2EzLWVmYTctNGFmZi1hMDNhLTY1NmIxZGYyMmQ4ZA==", verify_ssl_certs=False
)
db = Chroma.from_documents(
    documents,
    embeddings,
    client_settings=Settings(anonymized_telemetry=False),
)

print(db)
# Извлечение данных и генерация с помощью релевантных фрагментов блога.
retriever = db.as_retriever()


from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

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


question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
rag_chain1 = create_retrieval_chain(history_aware_retriever, question_answer_chain)

from langchain_core.messages import HumanMessage
chat_history = []
chat_history1 = []

question = "Какие расходы по утилизации бортового питания?"
ai_msg_1 = rag_chain.invoke({"input": question, "chat_history": chat_history})
print(ai_msg_1["answer"])
chat_history.extend([HumanMessage(content=question), ai_msg_1["answer"]])

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
print(ai_msg_4["answer"])