# FROM tiangolo/uvicorn-gunicorn
FROM python:3.8

ENV MODULE_NAME main
ENV VARIABLE_NAME app
ENV APP_MODULE main:app
ENV WORKERS_PER_CORE 1
ENV TOTAL_WORKERS 1
# ENV HOST
ENV PORT 80
ENV BIND 0.0.0.0:80
ENV LOG_LEVEL debug


COPY ./start.sh /start.sh
COPY ./gunicorn_conf.py /gunicorn_conf.py
COPY ./start-reload.sh /start-reload.sh

EXPOSE 80

RUN chmod +x /start.sh \
    && chmod +x /start-reload.sh \
    && rm --recursive --force /app/ \
    && mkdir --parents /app/;

WORKDIR /app/
ENV PYTHONPATH=/app

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]

COPY ./main.py /app/main.py
COPY ./telegram_bot_api_server /app/telegram_bot_api_server
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements.freeze.txt /app/requirements.freeze.txt
RUN pip install uvicorn && pip install -r requirements.txt
