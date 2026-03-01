FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY server/ ./server/
COPY demo_project/ ./demo_project/

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["python", "main.py"]
CMD ["serve"]