# 1. Base Image: Official lightweight Python runtime
FROM python:3.11-slim

# 2. Set the working directory
WORKDIR /app

# 3. Environment flags for instant logging and clean builds
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 4. Copy and install dependencies first (Optimizes layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Expose the standard FastAPI port
EXPOSE 8000

# 7. Start Uvicorn listening on all network interfaces (0.0.0.0)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]