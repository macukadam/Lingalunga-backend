FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install packages for connecting to PostgreSQL
RUN apt-get update && apt-get install -y libpq5

COPY . /app/

RUN python manage.py collectstatic --noinput

# Create a non-root user and give it ownership of the app directory
RUN useradd -ms /bin/bash celery_user && \
    chown -R celery_user:celery_user /app

# Switch to the non-root user
USER celery_user

CMD ["gunicorn", "--timeout", "60", "lingalunga_server.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-w", "1", "-b", "0.0.0.0:8000"]
