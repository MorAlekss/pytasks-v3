#!/bin/bash
# setup-tmux.sh — Проверка и установка tmux если не установлено

set -e

echo "=== Checking tmux installation ==="

# Проверка наличия tmux
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Attempting to install..."
    
    case "$(uname -s)" in
        Darwin*)  # macOS
            echo "Detected macOS. Installing with Homebrew..."
            if command -v brew &> /dev/null; then
                brew install tmux
            else
                echo "ERROR: Homebrew not found. Please install tmux manually:"
                echo "  brew install tmux"
                exit 1
            fi
            ;;
        Linux*)
            echo "Detected Linux. Installing with apt..."
            if command -v apt &> /dev/null; then
                sudo apt-get update && sudo apt-get install -y tmux
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y tmux
            elif command -v yum &> /dev/null; then
                sudo yum install -y tmux
            else
                echo "ERROR: Package manager not found. Please install tmux manually."
                exit 1
            fi
            ;;
        *)
            echo "ERROR: Unknown OS: $(uname -s)"
            exit 1
            ;;
    esac
    
    echo "tmux installed successfully!"
else
    echo "tmux is already installed: $(tmux -V)"
fi

# Проверка версии
TMUX_VERSION=$(tmux -V)
echo "tmux version: $TMUX_VERSION"

# Проверяем, что tmux работает
echo ""
echo "Testing tmux..."
SESSION_TEST="test-$(date +%s)"
tmux new-session -d -s "$SESSION_TEST" echo "Hello"
sleep 1

if tmux has-session -t "$SESSION_TEST" 2>/dev/null; then
    echo "✓ tmux is working correctly"
    tmux kill-session -t "$SESSION_TEST"
else
    echo "✗ tmux test failed"
    exit 1
fi

echo ""
echo "=== tmux setup complete ==="
