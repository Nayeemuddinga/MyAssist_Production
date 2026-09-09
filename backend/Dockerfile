FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN addgroup --system assist && adduser --system --ingroup assist assist && chown -R assist:assist /app
USER assist
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live')" || exit 1
CMD ["gunicorn","app.main:app","-k","uvicorn.workers.UvicornWorker","-w","2","-b","0.0.0.0:8000","--access-logfile","-","--timeout","60"]
