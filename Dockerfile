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

COPY ./telegram_bot_api_server /app

