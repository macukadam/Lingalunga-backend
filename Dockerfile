FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install nltk
RUN python -m nltk.downloader -d /home/celery_user/nltk_data punkt
RUN python -m nltk.downloader -d /home/celery_user/nltk_data omw
RUN python -c "import nltk; nltk.download('punkt', download_dir='/home/celery_user/nltk_data')"

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . /app/

RUN python manage.py collectstatic --noinput

# Create a non-root user and give it ownership of the app directory
RUN useradd -ms /bin/bash celery_user && \
    chown -R celery_user:celery_user /app

# Switch to the non-root user
USER celery_user

CMD ["uvicorn", "lingalunga_server.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload", "--lifespan", "on"]
