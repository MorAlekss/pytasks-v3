# Параллельное выполнение workers с большими промптами

## Проблема
`hermes -q` не поддерживает stdin и лимитирован ARG_MAX (~1MB).
Это делает параллельный запуск workers с большими промптами проблематичным.

## Доступные паттерны

### Паттерн 1: Последовательный запуск через Python subprocess (БЕЗОПАСНЫЙ)

```python
import subprocess
from pathlib import Path

def run_worker_sequential(prompt_file: str, worktree_path: str):
    """Запуск workers по очереди — надёжно, но медленно"""
    prompt = Path(prompt_file).read_text(encoding='utf-8')
    result = subprocess.run(
        ['hermes', 'chat', '-q', prompt, '--yolo'],
        cwd=worktree_path,
        capture_output=True,
        text=True
    )
    return result.stdout
```

**Плюсы**: Гарантированно работает, простой код  
**Минусы**: Последовательно, долго для 10+ workers

---

### Паттерн 2: Параллельный запуск через `asyncio` + `subprocess`

```python
import asyncio
from pathlib import Path

async def run_worker_async(prompt_file: str, worktree_path: str):
    """Параллельный запуск с ограничением concurrency"""
    prompt = Path(prompt_file).read_text(encoding='utf-8')
    
    proc = await asyncio.create_subprocess_exec(
        'hermes', 'chat', '-q', prompt, '--yolo',
        cwd=worktree_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode()

async def run_parallel(workers: list, max_concurrent: int = 3):
    """
    workers = [
        (prompt_file, worktree_path),
        (prompt_file, worktree_path),
    ]
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def worker_with_limit(item):
        async with semaphore:
            return await run_worker_async(item[0], item[1])
    
    return await asyncio.gather(*[worker_with_limit(w) for w in workers])
```

**Плюсы**: Параллельно, контролируемый concurrency  
**Минусы**: Всё ещё ограничено ARG_MAX (~200KB эффективный лимит)

---

### Паттерн 3: Через MCP Server Mode (РЕКОМЕНДУЕТСЯ ТЕКНИУМУ)

```bash
# В терминале 1: Запускаем MCP сервер
hermes mcp serve --port 5000

# В терминале 2: Отправляем запросы через stdin pipe
cat prompt1.txt | nc localhost 5000
cat prompt2.txt | nc localhost 5000
```

**Плюсы**: Нет ARG_MAX, stdin support, настоящий IPC  
**Минусы**: Нужно реализовать серверный режим

---

### Паттерн 4: Через Python API (РЕКОМЕНДУЕТСЯ ТЕКНИУМУ)

```python
# Предполагаемый API (нужно реализовать):
from hermes import Agent

async def run_worker():
    agent = Agent(worktree_path="/path/to/worktree", profile="worker")
    result = await agent.run(prompt_file.read_text())
    return result

# Параллельно:
results = await asyncio.gather(
    run_worker(),
    run_worker(),
    run_worker(),
)
```

**Плюсы**: Полный контроль, нет ARG_MAX, native Python  
**Минусы**: Нужно реализовать Python API

---

### Паттерн 5: Через tmux PTY (ОБХОДНОЕ РЕШЕНИЕ)

```bash
# Создаём tmux сессии для каждого worker
tmux new-session -d -s worker1 -x 120 -y 40 'hermes -w'
tmux new-session -d -s worker2 -x 120 -y 40 'hermes -w'

# Отправляем команды через PTY
sleep 5  # Ждём инициализацию
tmux send-keys -t worker1 "hermes chat -q \"$PROMPT\"" Enter
tmux send-keys -t worker2 "hermes chat -q \"$PROMPT\"" Enter

# Читаем результат
tmux capture-pane -t worker1 -p | grep "Resume this session"
```

**Плюсы**: Настоящая PTY изоляция, работает с большими промптами  
**Минусы**: Нужно tmux, сложно с экранированием, медленная отправка

---

### Паттерн 6: Через Profiles + Cron Jobs (ПОСТОЯННАЯ РЕШАЮЩАЯ)

```bash
# Создаём profile для каждого worker
hermes profile create worker1
hermes profile create worker2

# Создаём cron jobs с промптами в prompt файле
hermes cron create "0 * * * *" --profile worker1 --script "read prompt.txt | hermes -q"

# Запускаем cron
hermes cron run <job_id>
```

**Плюсы**: Не зависит от ARG_MAX, persistent jobs  
**Минусы**: Овершейд для разовых задач

---

## Сравнение паттернов

| Паттерн |并行性 | Большие промпты | Сложность | Рекомендация |
|---------|----------|-----------------|-----------|--------------|
| 1. Sequential | ❌ | ✅ | Низкая | ⭐️ Базовый выбор |
| 2. Asyncio | ✅ (3-5) | ⚠️ (~200KB) | Средняя | Для быстрых задач |
| 3. MCP Server | ✅ (10+) | ✅ Без лимитов | Высокая | 🎯 **Лучший вариант** |
| 4. Python API | ✅ (10+) | ✅ Без лимитов | Средняя | 🎯 **Оптимально** |
| 5. tmux PTY | ✅ (3-5) | ✅ Без лимитов | Высокая | Для экспериментов |
| 6. Cron+Profiles | ❌ (послед.) | ✅ Без лимитов | Средняя | Для планирования |

---

## Рекомендации для batch-migration навыка

### Текущее состояние:
- Работает только для небольших миграций (<200KB промптов)
- Требует ручного управления workers
- Не масштабируется для больших кодовых баз

### Краткосрочное решение (сейчас):
```bash
# Паттерн 1: Последовательный запуск для малых миграций
for worker_dir in .hermes/worktrees/*; do
    python3 worker-runner.py "$worker_dir/prompt.txt" "$worker_dir"
done
```

### Долгосрочное решение (нужна реализация в hermes):

**Option A: Добавить `--stdin` флаг к `hermes chat -q`**
```bash
hermes chat -q --stdin << 'EOF'
prompt here
EOF
```

**Option B: Реализовать Python API**
```python
from hermes import spawn_worker

results = await asyncio.gather(
    spawn_worker(prompt="migrate users.py", worktree="..."),
    spawn_worker(prompt="migrate products.py", worktree="..."),
)
```

**Option C: Улучшить MCP server mode**
```bash
# Встроенный IPC для parallel workers
hermes worker spawn batch/001 --prompt-file prompt.txt
hermes worker spawn batch/002 --prompt-file prompt.txt
hermes worker wait --all
```

---

## Вывод

На текущий момент **нет идеального решения** для параллельного запуска workers с большими промптами. 

**Рекомендуемые действия**:
1. Для малых задач (<100KB) — паттерн 1 (sequential) или 2 (asyncio)
2. Для больших задач — ждать реализации MCP/Python API
3. Обновить batch-migration skill с предупреждением об ограничениях
4. Предложить teknium реализовать `--stdin` или Python API

---

## Пример работыющего кода (паттерн 2)

```python
import asyncio
from pathlib import Path
from subprocess import run

async def run_worker(prompt_file, worktree, max_chars=180000):
    """Worker с обрезкой промпта до безопасного размера"""
    prompt = Path(prompt_file).read_text(encoding='utf-8')
    
    # Обрезаем до безопасного размера
    if len(prompt) > max_chars:
        prompt = prompt[:max_chars] + "\n... (truncated)"
    
    result = await asyncio.create_subprocess_exec(
        'hermes', 'chat', '-q', prompt, '--yolo',
        cwd=worktree,
        stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await result.communicate()
    return stdout.decode()

# Использование
workers = [
    ("prompt1.txt", "worktrees/unit-01"),
    ("prompt2.txt", "worktrees/unit-02"),
]

results = asyncio.run(asyncio.gather(
    *[run_worker(p, w) for p, w in workers]
))
```
