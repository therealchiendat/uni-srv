# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Create a non-root user named 'python'
RUN useradd -ms /bin/bash python

# Set the working directory in the container
WORKDIR /home/python/workspace

# Install any dependencies
RUN apt-get update && apt-get install -y \
    vim \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install MongoDB Shell
RUN curl -fsSL https://pgp.mongodb.com/server-6.0.asc | tee /etc/apt/trusted.gpg.d/mongodb-server-6.0.asc
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
RUN apt-get update && apt-get install -y mongodb-mongosh

# Expose the port the app runs on
EXPOSE 8000

# Change to non-root user
USER python

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
