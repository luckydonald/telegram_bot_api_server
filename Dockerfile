FROM tiangolo/uvicorn-gunicorn

ENV MODULE_NAME main
ENV VARIABLE_NAME app
ENV APP_MODULE main:app
ENV WORKERS_PER_CORE 1
# ENV WEB_CONCURRENCY 2  # core count
# ENV HOST
ENV PORT 80
ENV BIND 0.0.0.0:80
ENV LOG_LEVEL debug

RUN rm --recursive --force /app/ ; mkdir --parents /app/
COPY ./main.py /app/main.py
COPY ./telegram_bot_api_server /app/telegram_bot_api_server
COPY ./requirements.txt /app/requirements.txt
COPY ./requirements.freeze.txt /app/requirements.freeze.txt
RUN pip install -r requirements.txt
