import os
import subprocess
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from ai_agent import TunerAI

console = Console()

class ChatAgent:
    def __init__(self, hw_info):
        self.ai = TunerAI()
        self.hw = hw_info
        self.models_dir = "models"
        self.tuner_model_dir = "tuner-model"

    def scan_models(self):
        """Сканирует папки на наличие обученных моделей."""
        found = []
        # Проверяем стандартную папку вывода
        if os.path.exists(self.tuner_model_dir):
            found.append(self.tuner_model_dir)

        # Проверяем папку models если она есть
        if os.path.exists(self.models_dir):
            for d in os.listdir(self.models_dir):
                path = os.path.join(self.models_dir, d)
                if os.path.isdir(path):
                    found.append(path)
        return found

    def generate_inference_script(self, model_path):
        """Просто использует эталонный шаблон чата."""
        template_path = os.path.join(os.path.dirname(__file__), "chat_template.py")

        with open(template_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Подставляем реальный путь к модели в шаблон
        final_code = code.replace('MODEL_PATH = "tuner-model"', f'MODEL_PATH = "{model_path}"')

        with open("inference_temp.py", "w", encoding="utf-8") as f:
            f.write(final_code)

        return "inference_temp.py"

    def start_chat(self, script_path):
        """Запускает сгенерированный скрипт чата."""
        console.print(f"[bold green]🚀 Запуск инференса...[/bold green]")
        try:
            python_exe = sys.executable
            # Подавляем KeyboardInterrupt внутри подпроцесса, чтобы main.py сам его обработал
            subprocess.run([python_exe, script_path], check=True)
        except KeyboardInterrupt:
            # Текст уже выведется в основном цикле
            pass
        except Exception as e:
            console.print(f"[bold red]Ошибка при запуске чата: {e}[/bold red]")
