#!/bin/bash
set -e

echo "Installing LucaCli..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 could not be found."
    exit 1
fi

# Install the package in editable mode
pip3 install -e .

# Get the installation path for scripts
# This usually defaults to ~/.local/bin or similar on Linux/Mac when doing user installs,
# but with 'pip install -e .', it might put binaries in a specific location.
# We'll try to find where 'luca' is.

LUCA_PATH=$(which luca 2>/dev/null || echo "")

if [ -z "$LUCA_PATH" ]; then
    # It seems it's not in PATH yet. Let's try to guess where pip puts it.
    # Typically ~/.local/bin for --user, or /usr/local/bin for system.
    # Since we didn't use --user explicitly, it might be in the venv or system path.
    # If the user is running this, they probably want it accessible.
    
    # Let's check typical user bin paths
    USER_BASE=$(python3 -m site --user-base)
    USER_BIN="$USER_BASE/bin"
    
    if [ -d "$USER_BIN" ]; then
        echo "Detected user bin directory: $USER_BIN"
        if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
            echo "Adding $USER_BIN to PATH..."
            
            # Detect shell
            SHELL_NAME=$(basename "$SHELL")
            RC_FILE=""
            
            if [ "$SHELL_NAME" = "bash" ]; then
                RC_FILE="$HOME/.bashrc"
            elif [ "$SHELL_NAME" = "zsh" ]; then
                RC_FILE="$HOME/.zshrc"
            fi
            
            if [ -n "$RC_FILE" ]; then
                echo "export PATH=\"\$PATH:$USER_BIN\"" >> "$RC_FILE"
                echo "Added to $RC_FILE. Please restart your terminal or run 'source $RC_FILE'."
            else
                echo "Could not detect shell configuration file. Please add $USER_BIN to your PATH manually."
            fi
        else
            echo "Path is already configured."
        fi
    else
        echo "Could not locate the installation bin directory. Please ensure pip installs executables to a directory in your PATH."
    fi
else
    echo "LucaCli is successfully installed at: $LUCA_PATH"
fi

echo "Installation Complete!"
echo "Run 'luca --setup' to configure."
