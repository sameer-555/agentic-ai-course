# Build from the course root:   docker build -f level-14-ship-it/Dockerfile -t ops-buddy .
# Run:                           docker run -p 8000:8000 -e ANTHROPIC_API_KEY=... ops-buddy
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml ./
COPY ops_buddy ./ops_buddy
RUN pip install --no-cache-dir .
COPY level-13-guardrails ./level-13-guardrails
COPY level-14-ship-it ./level-14-ship-it
EXPOSE 8000
CMD ["uvicorn", "app:app", "--app-dir", "level-14-ship-it", "--host", "0.0.0.0", "--port", "8000"]
