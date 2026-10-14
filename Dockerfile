FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installs Chromium plus every OS-level library Playwright needs for it.
RUN playwright install --with-deps chromium

COPY . .

ENV HEADLESS=true
ENV PYTHONUNBUFFERED=1

# Overridden per schedule by the ECS task's container command override,
# e.g. ["run_daily_d88_cider.py"] / ["run_daily_d94_bottles.py"] / etc.
ENTRYPOINT ["python"]
CMD ["run_daily_d88_bottles.py"]
