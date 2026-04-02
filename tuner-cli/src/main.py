import os
import sys
import json
import time
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

console = Console()

def ensure_alem_auth():
    """Агент-Пограничник: проверяет доступ к Alem AI Plus"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

    # 1. Пытаемся загрузить ключ из окружения или файла
    api_key = os.getenv("ALEM_AI_API_KEY")

    if not api_key and os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("ALEM_AI_API_KEY="):
                    api_key = line.split("=")[1].strip()
                    break

    # 2. Если ключа нет, запрашиваем его красиво
    if not api_key:
        console.print(Panel(
            "[bold yellow]Добро пожаловать в Tuner-2![/bold yellow]\n\n"
            "Для работы Агентов-Оркестраторов требуется подключение к [bold cyan]Alem AI Plus[/bold cyan].\n"
            "Получить ключ можно здесь: [blue underline]https://plus.alem.ai/services[/blue underline]",
            title="🔑 Авторизация", border_style="cyan"
        ))

        api_key = Prompt.ask("[bold green]Введите ваш Alem AI API Key[/bold green]")

        if api_key.startswith("sk-"):
            with open(env_path, "a" if os.path.exists(env_path) else "w") as f:
                f.write(f"\nALEM_AI_API_KEY={api_key}\n")
            console.print("[bold green]✅ Ключ успешно сохранен в .env![/bold green]\n")
        else:
            console.print("[bold red]❌ Неверный формат ключа. Попробуйте еще раз.[/bold red]")
            sys.exit(1)

    os.environ["ALEM_AI_API_KEY"] = api_key
    return api_key

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from hardware import scout_hardware
from orchestration import Orchestrator, HardwareEngineer, DataScientist, TrainingMaster
from chat_engine import ChatAgent
from validator import DependencyAgent

console = Console()

def run_chat_mode(hw):
    console.print("\n[bold cyan]=== РЕЖИМ ТЕСТИРОВАНИЯ (CHAT) ===[/bold cyan]")
    agent = ChatAgent(hw)
    models = agent.scan_models()

    if not models:
        console.print("[bold red]Ошибка:[/bold red] Обученные модели не найдены (проверьте папку 'tuner-model').")
        return

    console.print("[bold magenta]Доступные модели:[/bold magenta]")
    for i, m in enumerate(models, 1):
        console.print(f"{i}. {m}")

    choice = Prompt.ask("\nВыберите номер модели", choices=[str(i) for i in range(1, len(models)+1)])
    selected_model = models[int(choice)-1]

    script = agent.generate_inference_script(selected_model)
    agent.start_chat(script)

def get_logo():
    logo_text = """
 [bold cyan]████████╗██╗   ██╗███╗   ██╗███████╗██████╗ [/bold cyan]
 [bold cyan]╚══██╔══╝██║   ██║████╗  ██║██╔════╝██╔══██╗[/bold cyan]
 [bold cyan]   ██║   ██║   ██║██╔██╗ ██║█████╗  ██████╔╝[/bold cyan]
 [bold cyan]   ██║   ██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗[/bold cyan]
 [bold cyan]   ██║   ╚██████╔╝██║ ╚████║███████╗██║  ██║[/bold cyan]
 [bold cyan]   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝[/bold cyan]
    """
    return Panel(logo_text, subtitle="[bold white]v2.0 - ML? It's simple.[/bold white]", border_style="cyan")

def show_hardware_report(hw):
    table = Table(show_header=True, header_style="bold magenta", border_style="dim")
    table.add_column("Компонент", style="cyan")
    table.add_column("Характеристики", style="white")

    table.add_row("Операционная система", f"{hw['os']} ({hw['os_release']})")
    table.add_row("Оперативная память (RAM)", f"{hw['ram_gb']} GB")

    if hw['cuda']:
        table.add_row("GPU (NVIDIA)", f"{hw['cuda']['gpu']}")
        table.add_row("VRAM", f"{hw['cuda']['vram_gb']} GB")
        table.add_row("Движок обучения", "[bold green]UNSLOTH (Ultra Fast)[/bold green]")
    elif hw['apple_silicon']:
        table.add_row("Chip (Apple)", f"{hw['apple_silicon']['chip']}")
        table.add_row("Unified Memory", f"{hw['apple_silicon']['unified_memory_gb']} GB")
        table.add_row("Движок обучения", "[bold green]MLX-LM (Optimized for Mac)[/bold green]")
    else:
        table.add_row("Процессор (CPU)", f"Cores: {hw['cpu']['count']}")
        table.add_row("Движок обучения", "[bold yellow]Transformers (CPU Mode)[/bold yellow]")

    console.print(Panel(table, title="[bold green]Hardware Detected[/bold green]", border_style="green"))

def start_training_mission(hw):
    # Проверка библиотек перед началом (только если нужно)
    # Мы пропускаем импорты здесь, чтобы избежать RuntimeError
    console.print("\n[bold cyan]🔍 Агент-Инженер проверяет среду...[/bold cyan]")

    # Теперь мы не запускаем принудительную стабилизацию КАЖДЫЙ раз,
    # только если пользователь сам этого захочет или если обучение упадет.
    # Но для первого раза после фикса - запустим один раз.

    console.print("\n[bold cyan]=== ИНИЦИАЦИЯ МИССИИ ОБУЧЕНИЯ ===[/bold cyan]")

    purpose = Prompt.ask("[bold white]Какова цель обучения?[/bold white]", default="Abai Kazakh Expert")

    console.print("\n[bold cyan]Выберите базу для обучения:[/bold cyan]")
    console.print("1. [bold green]Qwen 2.5 (1.5B)[/bold green] - Рекомендуется (Умнее, лучше для каз. языка)")
    console.print("2. [bold yellow]Llama 3.2 (1B)[/bold yellow] - Быстрее (Самая легкая)")

    model_choice = Prompt.ask("Выберите модель", choices=["1", "2"], default="1")
    selected_model_id = "unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit" if model_choice == "1" else "unsloth/Llama-3.2-1B-Instruct-bnb-4bit"

    model_url = f"https://huggingface.co/{selected_model_id}"
    console.print(Panel(f"🚀 [bold cyan]Выбрана модель:[/bold cyan] {selected_model_id}\n🔗 [blue underline]{model_url}[/blue underline]",
                  title="[bold]Информация о модели[/bold]", border_style="blue"))

    dataset = Prompt.ask("[bold white]Путь к датасету[/bold white]", default="data/abai_train.jsonl")

    # ПРОВЕРКА И ЗАГРУЗКА МОДЕЛИ С ИНДИКАТОРОМ
    # 0. Агент-Инженер проверяет зависимости
    dep_agent = DependencyAgent()
    with console.status("[bold green]Агент-Инженер готовит среду...[/bold green]", spinner="dots"):
        dep_agent.check_and_install()

    console.print(f"\n[bold yellow]📡 Агент-Загрузчик: Проверка локальных весов модели...[/bold yellow]")
    try:
        import warnings
        # Игнорируем предупреждения о депрекейтах в HF Hub, чтобы не мусорить в консоли
        warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")

        from huggingface_hub import snapshot_download
        import os

        # Включаем быстрый режим скачивания
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

        # Скачиваем БЕЗ with console.status, чтобы видеть прогресс-бар tqdm
        snapshot_download(
            repo_id=selected_model_id,
            local_dir_use_symlinks=False,
            # Индикатор tqdm появится автоматически, если его не подавлять
        )
        console.print("[bold green]✅ Модель полностью готова к работе![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Ошибка при загрузке: {e}[/bold red]")
        if not Confirm.ask("Попробовать продолжить обучение без предварительной загрузки?"):
            return

    # 1. Вызов Оркестратора
    commander = Orchestrator(hw)
    plan = commander.create_mission_plan(purpose, dataset)
    console.print(Panel(Markdown(plan), title="[bold cyan]План Командора[/bold cyan]", border_style="cyan"))

    # 2. Вызов Инженера по железу
    engineer = HardwareEngineer(hw)
    optimization = engineer.optimize_params()
    console.print(Panel(Markdown(optimization), title="[bold magenta]Отчет Инженера (Железо)[/bold magenta]", border_style="magenta"))

    # 3. Вызов Data Scientist
    scientist = DataScientist(dataset)
    data_report = scientist.inspect_data()
    console.print(Panel(Markdown(data_report), title="[bold green]Анализ Данных[/bold green]", border_style="green"))

    if Confirm.ask("\n[bold yellow]Все агенты готовы. Начать генерацию кода и запуск?[/bold yellow]"):
        master = TrainingMaster(hw, purpose, selected_model_id)
        code = master.generate_training_script(optimization, data_report)

        # Очистка и сохранение кода
        clean_code = code.strip()
        if "```python" in clean_code:
            clean_code = clean_code.split("```python")[1].split("```")[0].strip()
        elif "```" in clean_code:
            clean_code = clean_code.split("```")[1].split("```")[0].strip()

        lines = clean_code.split('\n')
        final_lines = []
        code_started = False
        for line in lines:
            trimmed = line.strip()
            if not code_started:
                if trimmed.startswith(('import ', 'from ', '#', '@', 'def ', 'class ')):
                    code_started = True
                    final_lines.append(line)
            else:
                final_lines.append(line)

        with open("generated_train.py", "w", encoding="utf-8") as f:
            f.write('\n'.join(final_lines))

        console.print("[bold green]✅ Код обучения успешно сгенерирован![/bold green]")

        if Confirm.ask("[bold magenta]🚀 ЗАПУСТИТЬ ОБУЧЕНИЕ ПРЯМО СЕЙЧАС?[/bold magenta]"):
            # Создаем уникальное имя папки на основе цели
            safe_purpose = "".join([c if c.isalnum() else "_" for c in purpose[:20]]).lower()
            model_output_dir = f"models/{safe_purpose}_{int(time.time())}"
            os.makedirs("models", exist_ok=True)

            console.print(f"\n[bold yellow]ВНИМАНИЕ: Обучение начнется. Результат будет в {model_output_dir}[/bold yellow]")

            # Нам нужно передать путь сохранения в скрипт.
            # Самый простой способ - заменить его в сгенерированном файле
            try:
                with open("generated_train.py", "r", encoding="utf-8") as f:
                    train_code = f.read()

                train_code = train_code.replace('output_dir = "outputs"', f'output_dir = "{model_output_dir}"')
                train_code = train_code.replace('model.save_pretrained("tuner-model")', f'model.save_pretrained("{model_output_dir}")')
                train_code = train_code.replace('tokenizer.save_pretrained("tuner-model")', f'tokenizer.save_pretrained("{model_output_dir}")')
                train_code = train_code.replace('tuner-model/base_model.txt', f'{model_output_dir}/base_model.txt')

                # ИСПРАВЛЕНИЕ: Принудительно заменяем путь к датасету
                train_code = train_code.replace('DATASET_PATH = "newdataset/train.jsonl"', f'DATASET_PATH = "{dataset}"')
                train_code = train_code.replace('data_files=dataset_path', f'data_files="{dataset}"')

                with open("generated_train.py", "w", encoding="utf-8") as f:
                    f.write(train_code)

                # ИСПРАВЛЕНИЕ: Запускаем процесс ПЕРЕД использованием
                process = subprocess.Popen(
                    [sys.executable, "generated_train.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )

                # Вывод логов обучения в реальном времени
                for line in iter(process.stdout.readline, ""):
                    # Используем сырую строку чтобы избежать SyntaxWarning
                    console.print(rf"[dim white][TRAIN][/dim white] {line.strip()}")

                process.wait()

                if process.returncode == 0:
                    console.print("\n[bold green]🏆 ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО![/bold green]")
                    console.print(f"[bold cyan]Ваша модель сохранена в папку 'tuner-model'.[/bold cyan]")
                else:
                    console.print(f"\n[bold red]❌ Ошибка в процессе обучения (код {process.returncode}).[/bold red]")

            except KeyboardInterrupt:
                console.print("\n[bold red]🛑 Обучение остановлено пользователем.[/bold red]")
            except Exception as e:
                console.print(f"\n[bold red]Ошибка запуска процесса: {e}[/bold red]")

def main():
    console.clear()
    console.print(get_logo())

    # Проверка ключа Alem AI перед запуском
    ensure_alem_auth()

    with console.status("[bold green]Сканирую систему...[/bold green]", spinner="dots"):
        time.sleep(1) # Для эффекта
        hw = scout_hardware()

    show_hardware_report(hw)

    console.print("\n[bold yellow]Добро пожаловать в будущее обучения LLM![/bold yellow]")

    # Интерактивное меню
    options = [
        "1. [bold white]Train Model[/bold white] (Дообучить модель)",
        "2. [bold white]Chat[/bold white] (Протестировать веса)",
        "3. [bold white]Dataset Studio[/bold white] (Подготовить данные)",
        "4. [bold white]Settings[/bold white] (Настройки)",
        "5. [bold red]Exit[/bold red] (Выход)"
    ]

    for opt in options:
        console.print(opt)

    choice = Prompt.ask("\n[bold cyan]Что будем делать?[/bold cyan]", choices=["1", "2", "3", "4", "5"], default="1")

    if choice == "1":
        start_training_mission(hw)
    elif choice == "2":
        run_chat_mode(hw)
    elif choice == "5":
        console.print("[bold red]Увидимся в следующий раз! ML — это просто.[/bold red]")
        sys.exit(0)
    else:
        console.print(f"\n[bold green]Отлично! Вы выбрали режим {choice}.[/bold green]")
        console.print("[dim]Примечание: Этот функционал будет добавлен скоро...[/dim]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Операция прервана. Tuner-2 уходит в спящий режим.[/bold red]")
        sys.exit(0)
