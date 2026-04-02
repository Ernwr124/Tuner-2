class CPUEquationAgent:
    """ИИ-Агент для обучения без видеокарты (CPU Mode)"""
    def __init__(self):
        self.mode = "survival"

    def get_config(self, core_count):
        return {
            "backend": "transformers-cpu",
            "quantization": "int8",
            "threads": core_count,
            "lora_r": 4,
            "warning": "Обучение будет медленным. Рекомендуется только для очень маленьких датасетов."
        }
