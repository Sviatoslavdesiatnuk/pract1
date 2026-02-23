import os
import re
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def main():
    print("🚀 Запуск RAG-архітектора (генерація PlantUML)...")

    # --- ЕТАП 1: Завантаження ---
    loader = DirectoryLoader('./', glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    try:
        docs = loader.load()
    except Exception as e:
        return print(f"⚠️ Помилка при читанні файлів: {e}")
    if not docs:
        return print("⚠️ Помилка: .md файли не знайдені!")

    # --- ЕТАП 2: Розбиття тексту (Chunking) ---
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(docs)

    # --- ЕТАП 3: Векторизація та База даних ---
    print("🧮 Індексація знань...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # --- ЕТАП 4: Налаштування ШІ ---
    llm = OllamaLLM(model="llama3.2", temperature=0.1)

    # --- ЕТАП 5: Промпт ---
    template = """Ти — системний архітектор. Твоє завдання: на основі наданого контексту розробити State Diagram у PlantUML.
    
    КОНТЕКСТ:
    {context}
    
    ЗАДАЧА: {question}
    
    ТИ ПОВИНЕН СТВОРИТИ ДІАГРАМУ СУВОРО ЗА ЦИМ ШАБЛОНОМ (підстав свої дані з контексту):
    @startuml
    [*] --> Idle
    Idle --> MovingUp : startMotorUp
    ... (додай інші переходи ТІЛЬКИ з контексту)
    @enduml
    
    ЖОДНИХ participant, ЖОДНИХ компонентів. Тільки стани (-->) та події (:).
    Після @enduml напиши 2 речення українською про логіку системи.
    """
    prompt = ChatPromptTemplate.from_template(template)
    generation_chain = prompt | llm | StrOutputParser()

    # --- ЕТАП 6: Виконання запиту ---
    query = "Реалізуй безпечне закриття вікна (Car Power Window). Система має переходити в SafeState при виявленні перешкоди."
    print(f"\n🤖 Аналізую задачу: '{query}'")

    try:
        # 6.1: Пошук інформації
        retrieved_docs = retriever.invoke(query)
        print("\n📂 ЗНАЙДЕНИЙ КОНТЕКСТ З ФАЙЛІВ:")
        
        # Проходимося по кожному знайденому шматку тексту і виводимо його
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.metadata.get('source', 'Невідомо')
            print(f"\n--- Уривок {i} (Джерело: {source}) ---")
            print(doc.page_content) # Ось тут ми друкуємо сам текст
            
        print("\n" + "="*50) # Візуальний роздільник

        # 6.2: Генерація відповіді
        context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        print("\n⏳ Генерую PlantUML діаграму...")
        response = generation_chain.invoke({"context": context_text, "question": query})
        
        print("\n📝 ВІДПОВІДЬ ШІ:")
        print("-" * 40)
        print(response)
        print("-" * 40)

        # 6.3: Екстракція та збереження коду
        puml_match = re.search(r'(@startuml.*?@enduml)', response, re.DOTALL)
        if puml_match:
            with open("diagram.puml", "w", encoding="utf-8") as f:
                f.write(puml_match.group(1))
            print("\n✅ УСПІХ: Діаграму автоматично збережено у файл 'diagram.puml'!")
        else:
            print("\n⚠️ Модель не згенерувала валідний блок @startuml ... @enduml")

    except Exception as e:
        print(f"\n⚠️ Помилка: {e}")

if __name__ == "__main__":
    main()