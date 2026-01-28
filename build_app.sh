#!/usr/bin/env bash
set -euo pipefail

# Usage: ./build_app.sh
# Requirements: macOS, python3 with tkinter, Homebrew (optional)
# This script creates a venv, installs py2app, copies exiftool (from brew) and builds the .app

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install py2app

# Obtain exiftool (from Homebrew). If you already have a local exiftool, copy it to ./exiftool
if command -v brew >/dev/null 2>&1; then
  echo "Installing exiftool (brew) if necessary..."
  brew install exiftool || true
  cp "$(which exiftool)" ./exiftool
  chmod +x ./exiftool
else
  echo "Homebrew not available. Ensure ./exiftool exists in the repo (executable binary)."
  if [ ! -f ./exiftool ]; then
    echo "No ./exiftool found. Install it and copy here:" >&2
    echo "  brew install exiftool" >&2
    echo "  cp \\$(which exiftool) ./exiftool" >&2
    exit 1
  fi
fi

python3 setup.py py2app

echo "Build finished. Check dist/LimpiadorMetadatos.app"
echo "Test with: open dist/LimpiadorMetadatos.app"