FROM contentpilot-base:latest

COPY requirements/dashboard.txt /tmp/dashboard.txt
RUN pip install --no-cache-dir -r /tmp/dashboard.txt

COPY shared/ /app/shared/
COPY modules/dashboard/ /app/module/

WORKDIR /app/module

CMD ["python3", "main.py"]
