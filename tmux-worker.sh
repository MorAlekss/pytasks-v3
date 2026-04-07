#!/bin/bash
# tmux-worker.sh — Запуск hermes workers через tmux PTY
# Обходит ARG_MAX через прямое управление терминалом

set -e

WORKTREE_PATH="${1:-.}"
PROMPT_FILE="${2:-prompt.txt}"
WORKER_NAME="${3:-worker}"

if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: Prompt file not found: $PROMPT_FILE"
    exit 1
fi

# Читаем prompt
PROMPT=$(cat "$PROMPT_FILE")
PROMPT_ESCAPED=$(printf '%s\n' "$PROMPT" | sed 's/"/\\"/g; s/\$/\\$/g; s/`/\\`/g')

# Создаём tmux сессию
SESSION_NAME="${WORKER_NAME}-$(date +%s)"

echo "=== Starting ${SESSION_NAME} ==="
echo "Working directory: ${WORKTREE_PATH}"
echo "Prompt size: $(wc -c < "$PROMPT_FILE") bytes"
echo ""

# Создаём tmux сессию в фоновом режиме
tmux new-session -d -s "$SESSION_NAME" -x 120 -y 40 \
    "cd ${WORKTREE_PATH} && hermes --worktree --yolo"

# Ждём инициализацию hermes (нужно время для загрузки)
echo "Waiting for hermes to initialize..."
sleep 15

# Отправляем prompt через tmux send-keys
# Используем -l для точного управления вводом
echo "Sending prompt..."

# Разбиваем prompt на строки и отправляем по одной
echo "$PROMPT" | while IFS= read -r line; do
    tmux send-keys -t "$SESSION_NAME" "$line" Enter
    sleep 0.1
done

# Ждём выполнения
echo "Waiting for worker to complete (up to 5 minutes)..."
for i in {1..300}; do
    sleep 1
    
    # Проверяем, завершился ли worker
    if tmux capture-pane -p -t "$SESSION_NAME" 2>/dev/null | grep -q "Resume this session"; then
        echo ""
        echo "=== Worker completed ==="
        break
    fi
    
    # Проверяем на ошибки
    if tmux capture-pane -p -t "$SESSION_NAME" 2>/dev/null | grep -qi "error\|exception\|failed"; then
        echo ""
        echo "=== Worker encountered an error ==="
        break
    fi
    
    if [ $((i % 60)) -eq 0 ]; then
        echo "Still running... ($i/300)"
    fi
done

# Сохраняем сессию для анализа
echo ""
echo "=== Capturing output ==="
OUTPUT_FILE="${SESSION_NAME}.log"
tmux capture-pane -p -t "$SESSION_NAME" > "$OUTPUT_FILE"

# Извлекаем session ID
SESSION_ID=$(grep -o "Session:[[:space:]]*[0-9_]*" "$OUTPUT_FILE" | tail -1 | awk '{print $2}')
echo "Session ID: $SESSION_ID"

# Показываем краткий результат
echo ""
echo "=== Brief output ==="
tail -50 "$OUTPUT_FILE"

# Очищаем tmux сессию
echo ""
echo "Cleaning up session..."
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

echo ""
echo "=== Done ==="
echo "Output saved to: $OUTPUT_FILE"
echo "To resume: hermes --resume $SESSION_ID"
