# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Upgrade pip and install build dependencies for bcrypt
RUN apt-get update && apt-get install -y build-essential libffi-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly ensure compatible bcrypt + passlib versions
RUN pip install --no-cache-dir bcrypt==4.0.1 passlib==1.7.4

# Copy the rest of the code
COPY app/ ./app

# Set the working directory to /app/app so Uvicorn can find main.py
WORKDIR /app/app

# Run FastAPI via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
