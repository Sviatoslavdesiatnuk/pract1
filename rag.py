import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def main():
    print("🚀 Запуск ЛОКАЛЬНОГО RAG-аналітика (Ollama)...")

    # 1. Завантаження документів (виправляємо проблему з Unicode)
    loader = DirectoryLoader(
        './', 
        glob="**/*.md", 
        loader_cls=TextLoader,
        loader_kwargs={'encoding': 'utf-8'}
    )
    
    try:
        docs = loader.load()
    except Exception as e:
        print(f"⚠️ Помилка при читанні файлів: {e}")
        return

    if not docs:
        print("⚠️ Помилка: .md файли не знайдені в поточній папці!")
        return
    print(f"📄 Завантажено документів: {len(docs)}")

    # 2. Розбиття тексту на частини
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(docs)

    # 3. Створення векторної бази (повністю локально)
    print("🧮 Індексація знань (це може зайняти кілька секунд)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = Chroma.from_documents(
        documents=texts, 
        embedding=embeddings
    )

    # 4. Підключення до моделі Llama 3.2
    llm = OllamaLLM(model="llama3.2")

    # 5. Шаблон запиту (Prompt)
    template = """Використовуй наступний контекст, щоб відповісти на питання. 
    Відповідай українською мовою.
    
    Контекст:
    {context}
    
    Питання: {question}
    
    Відповідь:"""
    prompt = ChatPromptTemplate.from_template(template)

    # 6. Ланцюжок RAG
    rag_chain = (
        {"context": vectorstore.as_retriever(), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # мій запит
    query = "Проаналізуй CarPowerWindow.md. Які основні проблеми та рішення описані в цьому документі?"
    print(f"🤖 Запит до локального AI...")
    
    try:
        response = rag_chain.invoke(query)
        print("\n📝 ВІДПОВІДЬ:")
        print("-" * 30)
        print(response)
        print("-" * 30)
    except Exception as e:
        print(f"\n⚠️ Помилка під час генерації: {e}")

if __name__ == "__main__":
    main()