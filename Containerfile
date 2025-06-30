FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code (uses .containerignore)
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Entrypoint
CMD ["python", "server.py"] 