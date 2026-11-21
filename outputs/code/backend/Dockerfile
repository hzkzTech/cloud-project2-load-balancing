FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Optional pip mirror; override with
#   docker compose build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_INDEX_URL=https://pypi.org/simple

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -i "${PIP_INDEX_URL}" -r requirements.txt

COPY app.py .

# The backend is only reachable inside the compose network; no host port is
# published.  EXPOSE is documentation only.
EXPOSE 8000

CMD ["python", "app.py"]
