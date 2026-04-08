#!/bin/bash
# worker-runner.sh - Запуск hermes worker с prompt из файла
PROMPT_FILE="$1"
cd "$(dirname "$0")"

if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: Prompt file not found: $PROMPT_FILE"
    exit 1
fi

# Читаем prompt и передаём в hermes
PROMPT=$(cat "$PROMPT_FILE")
hermes chat -q "$PROMPT" --yolo
