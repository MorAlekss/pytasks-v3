#!/bin/bash
# parallel-workers.sh — Пример параллельного запуска workers
# Работает через process background без tmux

set -e

NUM_WORKERS="${1:-2}"
WORKTREE_BASE="${2:-.hermes/worktrees}"
PROMPT_FILE="${3:-prompt.txt}"

echo "=== Parallel Workers Test ==="
echo "Workers: $NUM_WORKERS"
echo "Base path: $WORKTREE_BASE"
echo "Prompt file: $PROMPT_FILE"
echo ""

# Создаём workers
PIDS=()
SESSIONS=()

for i in $(seq 1 $NUM_WORKERS); do
    WORKTREE_PATH="${WORKTREE_BASE}/unit-$i"
    OUTPUT_FILE="${WORKTREE_PATH}/output.log"
    SESSION_FILE="${WORKTREE_PATH}/session.txt"
    
    echo "[$i/$NUM_WORKERS] Starting worker in $WORKTREE_PATH"
    
    # Проверяем prompt file
    if [ ! -f "$WORKTREE_PATH/$PROMPT_FILE" ]; then
        echo "  ERROR: Prompt file not found: $WORKTREE_PATH/$PROMPT_FILE"
        continue
    fi
    
    # Создаём shell script для worker
    WORKER_SCRIPT="${WORKTREE_PATH}/run-worker.sh"
    
    cat > "$WORKER_SCRIPT" << 'WORKER_EOF'
#!/bin/bash
cd "$(dirname "$0")"
hermes --worktree --yolo -q "$(cat prompt.txt)" 2>&1 | tee output.log
echo "Done" > status.txt
WORKER_EOF
    
    chmod +x "$WORKER_SCRIPT"
    
    # Запускаем worker в фоне
    (
        cd "$WORKTREE_PATH"
        bash run-worker.sh > "$OUTPUT_FILE" 2>&1 &
        echo $! > pid.txt
    ) &
    
    PIDS+=($!)
    SESSIONS+=("$WORKTREE_PATH")
    
    echo "  PID: ${PIDS[-1]}"
done

# Ждём завершения всех workers
echo ""
echo "Waiting for workers to complete (up to 5 minutes)..."

for i in "${!PIDS[@]}"; do
    WORKTREE_PATH="${SESSIONS[$i]}"
    PID="${PIDS[$i]}"
    OUTPUT_FILE="${WORKTREE_PATH}/output.log"
    
    # Ждём с таймаутом
    TIMEOUT=300
    COUNT=0
    
    while [ $COUNT -lt $TIMEOUT ]; do
        sleep 1
        COUNT=$((COUNT + 1))
        
        # Проверяем, завершился ли процесс
        if ! kill -0 $PID 2>/dev/null; then
            echo "  [$i+1] Worker ${COUNT}s: COMPLETED"
            
            # Сохраняем session ID
            SESSION_ID=$(grep -o "Session:[[:space:]]*[0-9_]*" "$OUTPUT_FILE" | tail -1 | awk '{print $2}')
            echo "Session: ${SESSION_ID:-none}" > "${WORKTREE_PATH}/session.txt"
            
            break
        fi
        
        if [ $((COUNT % 30)) -eq 0 ]; then
            echo "  [$i+1] Worker: Still running... (${COUNT}s)"
        fi
        
        # Проверяем timeout
        if [ $COUNT -ge $TIMEOUT ]; then
            echo "  [$i+1] Worker: TIMEOUT after ${COUNT}s"
            kill $PID 2>/dev/null || true
        fi
    done
done

# Сбор результатов
echo ""
echo "=== Results ==="
for i in "${!PIDS[@]}"; do
    WORKTREE_PATH="${SESSIONS[$i]}"
    OUTPUT_FILE="${WORKTREE_PATH}/output.log"
    SESSION_FILE="${WORKTREE_PATH}/session.txt"
    
    if [ -f "$OUTPUT_FILE" ]; then
        echo ""
        echo "[$i+1] Output:"
        echo "---"
        tail -20 "$OUTPUT_FILE"
        echo "---"
        
        if [ -f "$SESSION_FILE" ]; then
            SESSION_ID=$(cat "$SESSION_FILE")
            echo "Session ID: $SESSION_ID"
        fi
    fi
done

echo ""
echo "=== Summary ==="
echo "All workers completed or timed out"
echo "Check output files in each worktree directory"
