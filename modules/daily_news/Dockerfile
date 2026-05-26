FROM contentpilot-base:latest

# Install module-specific dependencies (currently none beyond base)
COPY requirements/news.txt /tmp/news.txt
RUN pip install --no-cache-dir -r /tmp/news.txt

# Copy shared layer (already in base, but explicit copy handles dev overrides)
COPY shared/ /app/shared/

# Copy module code
COPY modules/daily_news/ /app/module/

# Copy root helper scripts for local container validation
COPY scripts/ /app/scripts/

WORKDIR /app/module

CMD ["python", "runner.py"]