cat > fix.sh <<'EOF'
#!/usr/bin/env bash

set -e

echo
echo "========================================"
echo " JARVIS - PYTHON 3.11 SETUP"
echo "========================================"
echo

# Go to Jarvis directory
cd "$HOME/OneDrive/Desktop/new code/Jarvis"

echo "[1/6] Current directory:"
pwd
echo

# Deactivate old environment if active
if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo "[2/6] Deactivating old virtual environment..."
    deactivate 2>/dev/null || true
else
    echo "[2/6] No active virtual environment."
fi

# Remove old environment
echo
echo "Removing old .venv..."
rm -rf .venv

# Find Windows Python launcher
echo
echo "[3/6] Looking for Windows Python launcher..."

PYLAUNCHER=""

if command -v py.exe >/dev/null 2>&1; then
    PYLAUNCHER="py.exe"
elif command -v py >/dev/null 2>&1; then
    PYLAUNCHER="py"
fi

if [ -z "$PYLAUNCHER" ]; then
    echo
    echo "ERROR: Python launcher (py.exe) was not found."
    echo
    echo "Install the Python Install Manager from:"
    echo "https://www.python.org/downloads/"
    echo
    exit 1
fi

echo "Found: $PYLAUNCHER"
echo

# Install Python 3.11
echo "[4/6] Installing/updating Python 3.11..."
echo

"$PYLAUNCHER" install 3.11 --update

echo
echo "Checking Python 3.11..."
"$PYLAUNCHER" -3.11 --version

# Create virtual environment
echo
echo "[5/6] Creating .venv using Python 3.11..."

"$PYLAUNCHER" -3.11 -m venv .venv

# IMPORTANT:
# Use the venv's Python directly instead of relying on activation.
VENV_PYTHON="./.venv/Scripts/python.exe"

if [ ! -f "$VENV_PYTHON" ]; then
    echo
    echo "ERROR: .venv was not created correctly."
    exit 1
fi

echo
echo "Virtual environment Python:"
"$VENV_PYTHON" --version

echo
echo "Python executable:"
"$VENV_PYTHON" -c "import sys; print(sys.executable)"

# Upgrade pip
echo
echo "Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

# Install requirements
echo
echo "[6/6] Setup complete."

echo
echo "========================================"
echo " SUCCESS"
echo "========================================"
echo

echo "Python version:"
"$VENV_PYTHON" --version

echo
echo "Python executable:"
"$VENV_PYTHON" -c "import sys; print(sys.executable)"

echo
echo "========================================"
echo " Activating Python 3.11 environment..."
echo "========================================"
echo

# Activate in this script's shell
source .venv/Scripts/activate

echo
echo "FINAL CHECK:"
python --version
echo

echo "Python executable:"
python -c "import sys; print(sys.executable)"

echo
echo "========================================"
echo " JARVIS IS READY"
echo "========================================"
echo
echo "Run:"
echo "python main.py"
echo
EOF

chmod +x fix.sh

bash fix.sh

# IMPORTANT:
# bash runs fix.sh in a child shell, so activate again
# in the current Git Bash terminal.
source .venv/Scripts/activate

echo
echo "========================================"
echo " FINAL PROJECT PYTHON VERSION"
echo "========================================"
python --version
python -c "import sys; print(sys.executable)"
echo
