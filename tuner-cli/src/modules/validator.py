import subprocess
import sys
import os
from rich.console import Console

console = Console()

class DependencyAgent:
    def __init__(self):
        self.required_libs = [
            "torch", "torchvision", "torchaudio", "transformers", "peft",
            "accelerate", "bitsandbytes", "datasets", "rich", "psutil", "unsloth", "trl"
        ]

    def check_and_install(self):
        console.print("\n[bold cyan]🔍 Агент-Инженер: ПРИНУДИТЕЛЬНАЯ ОПЕРАЦИЯ НА ОТКРЫТОМ КОДЕ...[/bold cyan]")
        try:
            # 1. Жесткий снос всего
            console.print("[bold yellow]⚠️ Полная зачистка...[/bold yellow]")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio", "unsloth", "unsloth-zoo", "xformers"], check=False)

            # 2. Установка стабильного ядра
            console.print("[cyan]📦 Установка Torch 2.4.0...[/cyan]")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "torch==2.4.0", "torchvision==0.19.0", "--index-url", "https://download.pytorch.org/whl/cu121"])

            # 3. Установка Unsloth
            console.print("[cyan]🦥 Установка Unsloth...[/cyan]")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "unsloth"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "trl", "peft", "accelerate", "bitsandbytes"])

            # 4. ХАКЕРСКИЙ ПАТЧ (Удаляем битую строку из библиотеки физически)
            console.print("[bold magenta]🛠️ ПРИМЕНЯЮ СИЛОВОЙ ПАТЧ К БИБЛИОТЕКЕ...[/bold magenta]")

            # Находим путь к папке site-packages
            import site
            packages_path = site.getsitepackages()[0]
            common_py_path = os.path.join(packages_path, "unsloth_zoo", "temporary_patches", "common.py")

            if os.path.exists(common_py_path):
                with open(common_py_path, 'r') as f:
                    content = f.read()

                # Заменяем проблемную строку на пустышку
                new_content = content.replace(
                    "inductor_config_source = inspect.getsource(torch._inductor.config)",
                    "inductor_config_source = \"\""
                )

                with open(common_py_path, 'w') as f:
                    f.write(new_content)
                console.print("[green]✅ Патч применен успешно![/green]")
            else:
                console.print("[yellow]⚠️ Файл для патча не найден, возможно он в другом месте...[/yellow]")

            console.print("[bold green]✅ ОПЕРАЦИЯ ЗАВЕРШЕНА. БАГ УНИЧТОЖЕН.[/bold green]")
            return True
        except Exception as e:
            console.print(f"[bold red]❌ Ошибка: {e}[/bold red]")
            return False
