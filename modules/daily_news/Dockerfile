FROM contentpilot-base:latest

WORKDIR /app
ENV PYTHONPATH=/app

COPY shared /app/shared
COPY modules/daily_news /app/modules/daily_news

CMD ["python3", "modules/daily_news/main.py"]
