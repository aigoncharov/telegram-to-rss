FROM python:3.12-bookworm

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram_to_rss ./telegram_to_rss

ENV DATA_DIR=/data
ENV BIND=0.0.0.0:3042

CMD [ "python", "-m", "telegram_to_rss" ]