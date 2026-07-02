# ==========================================
# Stage 1: Build & Install Dependencies
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev

COPY requirements.txt .
# تثبيت المكتبات داخل مجلد local لنسخه مباشرة في المرحلة القادمة
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# Stage 2: Production-Ready Light Runtime
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# إنشاء مستخدم آمن غير جذر لحماية الحاوية
RUN useradd -u 8888 appuser && mkdir /home/appuser && chown -R appuser:appuser /home/appuser

# نسخ المكتبات المثبتة فقط من الـ Stage الأول
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

RUN chown -R appuser:appuser /app
USER appuser

# تفعيل الـ Path للمكتبات المنسوخة
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8082

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]