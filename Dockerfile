FROM python:3.11-slim

WORKDIR /app

# Copy ml module
COPY ./ml /app/ml
COPY ./backend /app/backend

# Install dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Expose port
EXPOSE 8000

# Run the app
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
