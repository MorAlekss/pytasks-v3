#!/usr/bin/env python3
"""
tmux-pty-worker.py — Worker через PTY без tmux
Использует терминал (PTY) напрямую для обхода ARG_MAX
"""
import pty
import os
import select
import sys
import time
import shutil

class PTYWorker:
    """Worker с PTY для обхода ARG_MAX"""
    
    def __init__(self, worktree_path: str):
        self.worktree_path = worktree_path
        self.pid = None
        self.master_fd = None
        self.output = []
        
    def start(self, command: str = "hermes --worktree --yolo"):
        """Запускает worker через PTY"""
        
        # Проверяем, есть ли PTY support
        if not hasattr(pty, 'fork'):
            raise RuntimeError("PTY not supported on this platform")
        
        print(f"Starting PTY worker in: {self.worktree_path}")
        print(f"Command: {command}")
        print("-" * 60)
        
        # Создаём мастер-слейв пару
        self.pid, self.master_fd = pty.fork()
        
        if self.pid == 0:
            # Child process
            os.chdir(self.worktree_path)
            os.execvp("bash", ["bash", "-c", command])
        else:
            # Parent process
            self.master = os.fdopen(self.master_fd, 'r')
            self.master_fd = None
            return self
        
    def send(self, text: str):
        """Отправляет текст в PTY"""
        if self.master_fd is None:
            raise RuntimeError("PTY not started")
        
        # Отправляем строку с Enter
        os.write(self.master_fd, (text + "\n").encode('utf-8'))
        time.sleep(0.1)  # Небольшая задержка
        
    def read_output(self, timeout: float = 0.1) -> str:
        """Читает output из PTY с таймаутом"""
        output = ""
        
        if self.master_fd is None:
            return output
        
        # Используем select для non-blocking read
        try:
            ready, _, _ = select.select([self.master], [], [], timeout)
            if ready:
                chunk = os.read(self.master_fd, 4096).decode('utf-8', errors='replace')
                output = chunk
        except (IOError, OSError):
            pass
        
        return output
    
    def capture(self, duration: float = 5.0, interval: float = 0.1) -> str:
        """Захватывает output в течение указанного времени"""
        total_output = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            output = self.read_output(interval)
            if output:
                total_output.append(output)
                print(output, end='', flush=True)
            
            # Проверяем, завершился ли процесс
            try:
                pid, status = os.waitpid(self.pid, os.WNOHANG)
                if pid == self.pid:
                    print(f"\nWorker completed with status: {status}")
                    break
            except OSError:
                pass
        
        return ''.join(total_output)
    
    def close(self):
        """Закрывает PTY"""
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
        self.master_fd = None


def run_pty_worker(worktree_path: str, prompt: str) -> str:
    """Запускает worker с prompt через PTY"""
    
    print(f"\n=== PTY Worker Test ===\n")
    print(f"Worktree: {worktree_path}")
    print(f"Prompt size: {len(prompt)} bytes")
    print(f"Prompt preview: {prompt[:200]}...")
    print("-" * 60)
    
    # Проверяем наличие bash
    if not shutil.which('bash'):
        print("ERROR: bash not found")
        return ""
    
    # Запускаем worker
    worker = PTYWorker(worktree_path)
    
    try:
        worker.start()
        time.sleep(3)  # Ждём инициализацию hermes
        
        # Отправляем prompt построчно
        print("\nSending prompt...")
        lines = prompt.strip().split('\n')
        for i, line in enumerate(lines, 1):
            worker.send(line)
            if i % 10 == 0:
                print(f"  Sent {i}/{len(lines)} lines...")
        
        print(f"\nSent all {len(lines)} lines")
        
        # Захватываем output
        print("\nCapturing output (up to 30 seconds)...")
        output = worker.capture(duration=30.0, interval=0.5)
        
        return output
        
    except Exception as e:
        print(f"ERROR: {e}")
        return ""
    finally:
        worker.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 tmux-pty-worker.py <worktree_path> <prompt_file>")
        sys.exit(1)
    
    worktree_path = sys.argv[1]
    prompt_file = sys.argv[2]
    
    # Читаем prompt
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    # Запускаем worker
    output = run_pty_worker(worktree_path, prompt)
    
    # Сохраняем результат
    output_file = prompt_file.replace('.txt', '.output.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"\n=== Output saved to: {output_file} ===")
