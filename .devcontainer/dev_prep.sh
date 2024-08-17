DB_HOST=${DB_HOST:-mongodb}
DB_PORT=${DB_PORT:-27017}

# Install any additional Python dependencies
pip install -r .devcontainer/requirements.txt
