FROM python:3.10-slim

WORKDIR /app

# Copy shared packages and backend
COPY packages/ packages/
COPY backend/ backend/

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Set Python path for shared packages
ENV PYTHONPATH=/app/backend:/app/packages

# Default port
ENV PORT=8000

EXPOSE ${PORT}

CMD ["sh", "-c", "cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
