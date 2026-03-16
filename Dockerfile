ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim

# 1. Install Selenium dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 2. Set the "Home" for your code
# We use /app as the working directory, and copy our code there. This way, we can use relative imports in our Python code without issues.
WORKDIR /app

# 3. Install Requirements
# (Assuming requirements.txt is in your project root)
COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# 4. Copy the CONTENTS of your local 'app' folder into the Workdir
# This is the key change!
COPY ./app /app

# 5. Fix permissions
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# 6. Run the script as a module
CMD ["python3", "main.py"]