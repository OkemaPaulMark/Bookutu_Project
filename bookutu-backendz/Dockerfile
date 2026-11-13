FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Static files are baked into the image; SECRET_KEY only needed to import settings here.
RUN SECRET_KEY=build DEBUG=False python manage.py collectstatic --noinput

RUN chmod +x deploy/start.sh
CMD ["deploy/start.sh"]
