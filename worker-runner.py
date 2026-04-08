#!/usr/bin/env python3
"""
worker-runner.py - Запуск hermes worker с prompt из файла
Использует subprocess для надёжного запуска
"""
import subprocess
import sys
import os

def run_worker(prompt_file, worktree_path=None):
    """Запускает hermes worker с prompt из файла"""
    
    # Читаем prompt
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    # Определяем рабочую директорию
    if worktree_path:
        os.chdir(worktree_path)
    
    # Запускаем hermes
    cmd = ['hermes', 'chat', '-q', prompt, '--yolo']
    
    print(f"Running: {' '.join(cmd)}")
    print(f"Working directory: {os.getcwd()}")
    print("-" * 80)
    
    result = subprocess.run(cmd, text=True, capture_output=False)
    
    return result.returncode

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: worker-runner.py <prompt_file> [worktree_path]")
        sys.exit(1)
    
    prompt_file = sys.argv[1]
    worktree_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    exit_code = run_worker(prompt_file, worktree_path)
    sys.exit(exit_code)
