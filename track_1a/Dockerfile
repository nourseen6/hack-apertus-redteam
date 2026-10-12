FROM python:3.12-slim
WORKDIR /app
COPY findings /app/findings
COPY src /app/src
CMD ["python", "src/reproduce.py"]
