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
    print("🚀 Запуск RAG-архітектора (генерація PlantUML) для систем з вимогами...")

    # --- ЕТАП 1: Завантаження ---
    # glob="**/*.md" автоматично знайде knowledge_library.md ТА файли у папці requirements/ (напр., req_cond.md)
    loader = DirectoryLoader('./', glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    try:
        docs = loader.load()
    except Exception as e:
        return print(f"⚠️ Помилка при читанні файлів: {e}")
    if not docs:
        return print("⚠️ Помилка: .md файли не знайдені! Переконайтеся, що файли існують у поточній директорії або вкладених папках.")

    # --- ЕТАП 2: Розбиття тексту (Chunking) ---
    text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=150) # Трохи зменшив, щоб точніше знаходити дрібні вимоги
    texts = text_splitter.split_documents(docs)

    # --- ЕТАП 3: Векторизація та База даних ---
    print("🧮 Індексація знань (правил ISO та системних вимог)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings)
    
    # Збільшуємо 'k' до 4, щоб база гарантовано захопила і загальні правила безпеки, і вимоги до кондиціонера
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # --- ЕТАП 4: Налаштування ШІ ---
    llm = OllamaLLM(model="llama3.2", temperature=0.1)

    # --- ЕТАП 5: Промпт ---
    template = """Ти — системний архітектор. Твоє завдання: на основі наданого контексту розробити State Diagram у PlantUML для конкретної системи.
    
    КОНТЕКСТ (містить як загальні правила безпеки, так і специфічні вимоги до системи):
    {context}
    
    ЗАДАЧА: {question}
    
    ІНСТРУКЦІЯ:
    1. Уважно вивчи знайдені специфічні стани системи (наприклад, Cooling, Heating для кондиціонера).
    2. Обов'язково застосуй загальні правила безпеки (додай перехід у SafeState при критичних помилках, описаних у вимогах).
    3. Створи діаграму СУВОРО ЗА ЦИМ ШАБЛОНОМ:
    @startuml
    [*] --> Standby
    Standby --> Cooling : TargetTemp < CabinTemp
    ... (додай інші переходи з контексту, включаючи SafeState)
    @enduml
    
    ЖОДНИХ participant, ЖОДНИХ компонентів. Тільки стани (-->) та події (:).
    Після @enduml напиши 2 речення українською про логіку системи та її безпеку.
    """
    prompt = ChatPromptTemplate.from_template(template)
    
    # Сучасний LCEL пайплайн (без старих chains)
    generation_chain = prompt | llm | StrOutputParser()

    # --- ЕТАП 6: Виконання запиту ---
    # Змінюємо запит на кондиціонер, щоб перевірити файл req_cond.md
    query = "Згенеруй PlantUML Statechart для автомобільного кондиціонера (HVAC). Врахуй стани та тригери безпеки (наприклад, PressureFault) з файлу вимог."
    print(f"\n🤖 Аналізую задачу: '{query}'")

    try:
        # 6.1: Пошук інформації
        retrieved_docs = retriever.invoke(query)
        print("\n📂 ЗНАЙДЕНИЙ КОНТЕКСТ З ФАЙЛІВ (Правила + Вимоги):")
        
        # Проходимося по кожному знайденому шматку тексту і виводимо його
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.metadata.get('source', 'Невідомо')
            print(f"\n--- Уривок {i} (Джерело: {source}) ---")
            print(doc.page_content) 
            
        print("\n" + "="*50)

        # 6.2: Генерація відповіді
        context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        print("\n⏳ Об'єдную вимоги і генерую PlantUML діаграму...")
        
        # Викликаємо ланцюг
        response = generation_chain.invoke({"context": context_text, "question": query})
        
        print("\n📝 ВІДПОВІДЬ ШІ:")
        print("-" * 40)
        print(response)
        print("-" * 40)

        # 6.3: Екстракція та збереження коду
        puml_match = re.search(r'(@startuml.*?@enduml)', response, re.DOTALL)
        if puml_match:
            # Зберігаємо у новий файл для кондиціонера
            with open("diagram_hvac.puml", "w", encoding="utf-8") as f:
                f.write(puml_match.group(1))
            print("\n✅ УСПІХ: Діаграму автоматично збережено у файл 'diagram_hvac.puml'!")
        else:
            print("\n⚠️ Модель не згенерувала валідний блок @startuml ... @enduml")

    except Exception as e:
        print(f"\n⚠️ Помилка: {e}")

if __name__ == "__main__":
    main()