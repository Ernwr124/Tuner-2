#!/bin/bash

# Инсталлятор Tuner-2: Vibe & Train
echo "🚀 Начинаю установку Tuner-2..."

# 1. Определяем пути
PROJECT_DIR=$(pwd)/tuner-cli
VENV_DIR="$PROJECT_DIR/tuner_env"

# 2. Создание виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Создаю виртуальное окружение..."
    python3 -m venv "$VENV_DIR"
fi

# 3. Установка базовых зависимостей
echo "🛠 Установка необходимых библиотек (это быстро)..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install rich huggingface_hub requests psutil

# 4. Создание глобальной команды 'tuner'
echo "🔗 Создаю системную команду 'tuner'..."
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

cat << EOF > "$BIN_DIR/tuner"
#!/bin/bash
"$VENV_DIR/bin/python" "$PROJECT_DIR/src/main.py" "\$@"
EOF

chmod +x "$BIN_DIR/tuner"

# 5. Проверка PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "⚠️ Внимание: Добавьте $BIN_DIR в ваш PATH или перезапустите терминал."
    echo "Команда для добавления: export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo "✅ Установка завершена! Теперь вы можете использовать команду 'tuner'."
