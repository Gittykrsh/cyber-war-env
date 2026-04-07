# Use correct Python version
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv

# Expose required port (important for HuggingFace)
EXPOSE 7860

# Run FastAPI app
ENV ENABLE_WEB_INTERFACE=true
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]