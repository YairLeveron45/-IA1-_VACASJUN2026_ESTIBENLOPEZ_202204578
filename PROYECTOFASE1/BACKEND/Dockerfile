FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends swi-prolog \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/BACKEND

COPY BACKEND/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY BACKEND ./ 
COPY PROLOG /workspace/PROLOG

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
