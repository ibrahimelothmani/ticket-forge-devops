# ==========================================
# Stage 1: Build & Install Dependencies
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# Stage 2: Production Runtime
# ==========================================
FROM python:3.11-slim

WORKDIR /app

RUN useradd -u 9999 appuser && mkdir /home/appuser && chown -R appuser:appuser /home/appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY src/ ./src

RUN chown -R appuser:appuser /app
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8083

ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8083"]