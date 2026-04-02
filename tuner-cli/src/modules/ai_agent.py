import requests
import json
import os

class TunerAI:
    def __init__(self, api_key="sk-q-rZTaq5btkySCqGHIccbg"):
        self.api_url = "https://llm.alem.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.model = "gpt-oss"
        self.knowledge_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge_base.txt")
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self):
        try:
            with open(self.knowledge_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not load knowledge base: {e}")
            return ""

    def ask(self, system_prompt, user_input):
        # Добавляем базу знаний в системный промпт
        full_system_prompt = f"ЗНАНИЯ О ПРОЕКТЕ:\n{self.knowledge}\n\nИНСТРУКЦИЯ РОЛИ:\n{system_prompt}"

        # Добавляем жесткую инструкцию по формату вывода кода
        formatting_instruction = "\n\nВАЖНО: Твой ответ должен содержать ТОЛЬКО чистый Python код, без каких-либо пояснений, заголовков или Markdown-разметки (никаких ```python). Начни сразу с импортов. Если ты добавишь лишний текст, скрипт не запустится и миссия будет провалена. Используй только стандартные символы ASCII, избегай специальных тире или кавычек. НЕ ИСПОЛЬЗУЙ Markdown в ответах для плана и отчетов, пиши обычным текстом."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": full_system_prompt + formatting_instruction},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.1 # Еще ниже для максимальной точности
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error connecting to AI: {e}"

# Агенты (Промпты)
AGENTS = {
    "orchestrator": "Ты — Главный Командор системы Tuner-2. Твоя задача — получить запрос пользователя на обучение модели, проанализировать его и распределить задачи между специализированными агентами (Data, Hardware, Training, Validator).",

    "data_agent": "Ты — Эксперт по данным. Твоя задача — анализировать датасеты (.jsonl, .csv), предлагать способы их очистки, расширения (синтетические данные) и проверки на качество перед обучением.",

    "hardware_agent": "Ты — Инженер по железу. Ты анализируешь отчеты о системе (RAM, VRAM, OS) и выбираешь оптимальные гиперпараметры (batch size, r/alpha для LoRA, квантование), чтобы обучение не вылетело с ошибкой Memory Error.",

    "trainer_agent": "Ты — Мастер Обучения. Ты пишешь финальный код на Python (используя Unsloth или MLX) на основе данных от других агентов. Твой код должен быть стабильным и эффективным.",

    "validator_agent": "Ты — Офицер по качеству. После обучения ты тестируешь модель, сравниваешь ответы 'до' и 'после' и выносишь вердикт: стало ли лучше."
}
