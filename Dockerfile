FROM python:3.14.5
WORKDIR /usr/local/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
# Copy in the source code
COPY . .

# Setup an app user so the container doesn't run as the root user
RUN addgroup --system appgroup \
    && adduser \
        --system \
        --ingroup appgroup \
        appuser

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8080"]