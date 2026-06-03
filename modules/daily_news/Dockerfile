FROM contentpilot-base:latest

COPY --chown=appuser:appuser requirements/news.txt /tmp/news.txt
RUN pip install --no-cache-dir -r /tmp/news.txt
RUN pip install --no-cache-dir apscheduler>=3.10.0

COPY --chown=appuser:appuser shared/ /app/shared/
COPY --chown=appuser:appuser modules/daily_news/ /app/module/
COPY --chown=appuser:appuser scripts/ /app/scripts/

USER appuser
WORKDIR /app/module

CMD ["python", "main.py"]