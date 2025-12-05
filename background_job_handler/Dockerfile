FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt update && \
    apt install -y --no-install-recommends \
        cron \
        build-essential \
        python3-dev \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY article_rating_calculator/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY article_rating_calculator/main.py /app/main.py

COPY article_rating_calculator/crontab.txt /etc/cron.d/rating-job


RUN chmod 0644 /etc/cron.d/rating-job && \
    crontab /etc/cron.d/rating-job


RUN touch /var/log/cron.log

CMD ["cron", "-f"]