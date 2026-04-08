#!/bin/bash
# parallel-tmux-workers.sh — Параллельный запуск нескольких workers через tmux
# Все workers выполняются одновременно, каждый в своей tmux сессии

set -e

NUM_WORKERS="${1:-3}"
WORKTREE_BASE="${2:-.hermes/worktrees}"
PROMPT_PREFIX="${3:-prompt}"

echo "=== Starting ${NUM_WORKERS} parallel tmux workers ==="
echo "Base path: ${WORKTREE_BASE}"
echo "Prompt prefix: ${PROMPT_PREFIX}"
echo ""

SESSIONS=()
RESULTS=()

# Создаём workers
for i in $(seq 1 $NUM_WORKERS); do
    SESSION_NAME="worker-${i}-$(date +%s)"
    WORKTREE_PATH="${WORKTREE_BASE}/unit-${i}"
    PROMPT_FILE="${WORKTREE_PATH}/${PROMPT_PREFIX}.txt"
    OUTPUT_FILE="${WORKTREE_PATH}/output.log"
    
    echo "[$i/${NUM_WORKERS}] Creating ${SESSION_NAME}"
    
    if [ ! -f "$PROMPT_FILE" ]; then
        echo "  WARNING: Prompt file not found: $PROMPT_FILE"
        RESULTS+=("ERROR: Prompt file not found")
        continue
    fi
    
    PROMPT=$(cat "$PROMPT_FILE")
    PROMPT_ESCAPED=$(printf '%s\n' "$PROMPT" | sed 's/"/\\"/g; s/\$/\\$/g')
    
    # Создаём tmux сессию
    tmux new-session -d -s "$SESSION_NAME" -x 120 -y 40 \
        "cd ${WORKTREE_PATH} && hermes --worktree --yolo"
    
    SESSIONS+=("$SESSION_NAME")
    RESULTS+=("RUNNING")
    
    echo "  ${SESSION_NAME} created, waiting for initialization..."
done

# Ждём инициализацию всех workers
echo ""
echo "Waiting for all workers to initialize..."
sleep 20

# Отправляем промпты всем workers
echo ""
echo "Sending prompts to workers..."
for i in $(seq 1 ${#SESSIONS[@]}); do
    SESSION_NAME="${SESSIONS[$((i-1))]}"
    WORKTREE_PATH="${WORKTREE_BASE}/unit-$i"
    PROMPT_FILE="${WORKTREE_PATH}/${PROMPT_PREFIX}.txt"
    
    if [ ! -f "$PROMPT_FILE" ]; then
        continue
    fi
    
    echo "  Sending to ${SESSION_NAME}..."
    
    # Отправляем prompt построчно для лучшей совместимости
    line_num=0
    while IFS= read -r line; do
        tmux send-keys -t "$SESSION_NAME" "$line" Enter
        sleep 0.05  # Небольшая задержка между строками
        line_num=$((line_num + 1))
    done < "$PROMPT_FILE"
    
    echo "  Sent ${line_num} lines to ${SESSION_NAME}"
done

# Мониторинг выполнения
echo ""
echo "Monitoring workers (timeout: 5 minutes)..."
COMPLETED=0
FAILED=0
TIMEOUT=300

for tick in $(seq 1 $TIMEOUT); do
    sleep 1
    
    COMPLETED=0
    FAILED=0
    
    for i in $(seq 1 ${#SESSIONS[@]}); do
        SESSION_NAME="${SESSIONS[$((i-1))]}"
        WORKTREE_PATH="${WORKTREE_BASE}/unit-$i"
        OUTPUT_FILE="${WORKTREE_PATH}/output.log"
        
        # Проверяем результат
        OUTPUT=$(tmux capture-pane -p -t "$SESSION_NAME" 2>/dev/null || echo "")
        
        if echo "$OUTPUT" | grep -q "Resume this session"; then
            RESULTS[$((i-1))]="COMPLETED"
            COMPLETED=$((COMPLETED + 1))
            
            # Сохраняем output
            echo "$OUTPUT" > "$OUTPUT_FILE"
            
            # Извлекаем session ID
            SESSION_ID=$(echo "$OUTPUT" | grep -o "Session:[[:space:]]*[0-9_]*" | tail -1 | awk '{print $2}')
            RESULTS[$((i-1))]+=" (session: $SESSION_ID)"
        elif echo "$OUTPUT" | grep -qi "error\|exception\|failed\|traceback"; then
            RESULTS[$((i-1))]="FAILED"
            FAILED=$((FAILED + 1))
            
            echo "$OUTPUT" > "$OUTPUT_FILE"
        fi
    done
    
    TOTAL=${#SESSIONS[@]}
    echo "  Progress: ${COMPLETED}/${TOTAL} completed, ${FAILED} failed (${tick}/${TIMEOUT}s)"
    
    # Если все завершены или все упали — выходим
    if [ $COMPLETED -eq $TOTAL ] || [ $FAILED -eq $TOTAL ]; then
        echo "All workers completed!"
        break
    fi
    
    # Периодический прогресс
    if [ $((tick % 60)) -eq 0 ]; then
        echo "  ${tick}/${TIMEOUT}s elapsed..."
    fi
done

# Вывод результатов
echo ""
echo "=== Final Results ==="
for i in $(seq 1 ${#SESSIONS[@]}); do
    echo "Worker $i: ${RESULTS[$((i-1))]}"
done

# Собираем summary
echo ""
echo "=== Summary ==="
echo "Completed: ${COMPLETED}/${#SESSIONS[@]}"
echo "Failed: ${FAILED}/${#SESSIONS[@]}"
echo "Timeout: $((TIMEOUT - ${#SESSIONS[@]}))"

# Очищаем tmux сессии
echo ""
echo "Cleaning up tmux sessions..."
for SESSION_NAME in "${SESSIONS[@]}"; do
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
done

echo "Cleanup complete."
