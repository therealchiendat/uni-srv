#!/usr/bin/env bash

git config --local core.hooksPath ./githooks
chmod +x .githooks/*

# Python environment setup
if [ ! -d "venv" ]; then
  python -m venv venv
fi

source venv/bin/activate

# Install Python dependencies
pip install -r .devcontainer/requirements.txt

git config --global --replace-all safe.directory /home/python/workspace
