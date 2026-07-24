FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000
ENV PYTHONUNBUFFERED=1

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 month1_python_core.flask_backend_server:app
