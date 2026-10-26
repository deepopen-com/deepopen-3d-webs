FROM python:3.9-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LD_DEMO_MODE=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=8090 \
    PORT=8090 \
    GRADIO_ANALYTICS_ENABLED=False \
    NO_PROXY=localhost,127.0.0.1,::1,0.0.0.0 \
    no_proxy=localhost,127.0.0.1,::1,0.0.0.0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120

WORKDIR /app


COPY requirements-web.txt /app/requirements-web.txt
RUN pip install --no-cache-dir -r /app/requirements-web.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY web_app.py /app/web_app.py
COPY webui /app/webui
COPY examples /app/examples
COPY assets /app/assets

RUN mkdir -p /app/outputs /app/results /app/data

EXPOSE 8090

CMD ["python", "web_app.py"]
