import os
import json
import subprocess
from rich.console import Console
from rich.panel import Panel
from ai_agent import TunerAI, AGENTS

console = Console()

class Orchestrator:
    def __init__(self, hw_info):
        self.ai = TunerAI()
        self.hw = hw_info
        self.agents = AGENTS
        self.plan = None

    def create_mission_plan(self, user_purpose, dataset_path):
        """Главный агент анализирует запрос и создает план миссии."""
        system_prompt = self.agents["orchestrator"]
        user_input = f"""
        ЦЕЛЬ ПОЛЬЗОВАТЕЛЯ: {user_purpose}
        ДАТАСЕТ: {dataset_path}
        ЖЕЛЕЗО: {json.dumps(self.hw, indent=2)}

        Создай краткий план действий. Кого из агентов (Data, Hardware, Training, Validator) ты задействуешь и какая у них будет задача?
        Ответь в стиле военного командира.
        """

        with console.status("[bold cyan]Командор анализирует ситуацию...[/bold cyan]"):
            response = self.ai.ask(system_prompt, user_input)

        return response

class HardwareEngineer:
    def __init__(self, hw_info):
        self.ai = TunerAI()
        self.hw = hw_info
        self.agent_prompt = AGENTS["hardware_agent"]

    def optimize_params(self):
        """Анализирует железо и выдает гиперпараметры для обучения."""
        user_input = f"Мое железо: {json.dumps(self.hw, indent=2)}. Какие параметры LoRA (r, alpha), Batch Size и тип квантования использовать, чтобы не вылетело по памяти?"

        with console.status("[bold magenta]Инженер по железу рассчитывает нагрузку...[/bold magenta]"):
            response = self.ai.ask(self.agent_prompt, user_input)
        return response

class DataScientist:
    def __init__(self, dataset_path):
        self.ai = TunerAI()
        self.dataset_path = dataset_path
        self.agent_prompt = AGENTS["data_agent"]

    def inspect_data(self):
        """Проверяет файл датасета (первые несколько строк)."""
        if not os.path.exists(self.dataset_path):
            return "ОШИБКА: Файл не найден."

        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                head = [next(f) for _ in range(5)]

            user_input = f"Проверь структуру данных: {head}. Все ли ок для fine-tuning?"
            with console.status("[bold green]Data Scientist изучает образцы данных...[/bold green]"):
                response = self.ai.ask(self.agent_prompt, user_input)
            return response
        except Exception as e:
            return f"Ошибка при чтении данных: {e}"

class TrainingMaster:
    def __init__(self, hw_info, purpose, model_id="unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit"):
        self.ai = TunerAI()
        self.hw = hw_info
        self.purpose = purpose
        self.model_id = model_id
        self.agent_prompt = AGENTS["trainer_agent"]

    def generate_training_script(self, optimization_tips, data_status):
        """Возвращает рабочий шаблон с подставленными данными."""
        template_path = os.path.join(os.path.dirname(__file__), "template.py")
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                code = f.read()

            # Динамически подставляем модель и датасет в шаблон
            # Вытягиваем путь к датасету из data_status (там обычно есть путь)
            # Если не находим, используем дефолт
            dataset_path = "newdataset/train.jsonl" # Дефолт
            if "newdataset/train.jsonl" in data_status:
                dataset_path = "newdataset/train.jsonl"

            # Используем модель, выбранную пользователем в интерфейсе
            model_name = self.model_id

            # Заменяем дефолтные переменные внизу шаблона
            code = code.replace('MODEL_NAME = "unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit"', f'MODEL_NAME = "{model_name}"')
            code = code.replace('DATASET_PATH = "newdataset/train.jsonl"', f'DATASET_PATH = "{dataset_path}"')

            return code

        # Если шаблона нет (что странно), возвращаем старую логику как запасной вариант
        instruction = f"""
        ЦЕЛЬ: {self.purpose}
        ЖЕЛЕЗО: RTX 2050 4GB.
        ДАТАСЕТ: 'newdataset/train.jsonl'
        ...
        """
        response = self.ai.ask(self.agent_prompt, instruction)
        return response
