FROM python:3.12-slim

WORKDIR /www

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download ru_core_news_sm


COPY . .

#CMD ["uvicorn", "s:app", "--host", "0.0.0.0", "--port", "8000"]