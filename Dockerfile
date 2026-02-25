ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim

# 1. Install Selenium dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 2. Create the user that was missing
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# 3. Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# 4. Copy project files
COPY . .
RUN chown -R appuser:appuser /app

USER appuser

# 5. Run the script as a module
CMD ["python3", "-m", "app.main"]