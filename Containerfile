FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code (uses .containerignore)
COPY . .

# Entrypoint
CMD ["python", "server.py"]
