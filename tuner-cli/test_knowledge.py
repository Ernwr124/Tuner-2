from src.modules.ai_agent import TunerAI
import os

def test_model():
    # Инициализируем нашего агента, который теперь умеет читать knowledge_base.txt
    ai = TunerAI()

    print("\n" + "="*50)
    print("🧪 ТЕСТ СИСТЕМЫ С БАЗОЙ ЗНАНИЙ (БЕЗ ПОРЧИ ВЕСОВ)")
    print("="*50)

    questions = [
        "Что такое стол?",
        "Что такое Tuner-2?",
        "Кто такой Оркестратор в вашей системе?",
        "Что такое город?"
    ]

    for q in questions:
        print(f"\n👤 ВОПРОС: {q}")
        # Используем промпт оркестратора для теста
        response = ai.ask("Ты — помощник Tuner-2. Отвечай кратко и по делу.", q)
        print(f"🤖 ОТВЕТ: {response}")

if __name__ == "__main__":
    test_model()
