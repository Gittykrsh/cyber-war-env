FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn pydantic openenv

EXPOSE 8000

ENV ENABLE_WEB_INTERFACE=true
CMD ["python", "-m", "server.app"]