FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run both FastAPI and Streamlit (we'll use FastAPI only for App Runner)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]