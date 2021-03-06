# Pull official base image
FROM python:3.8-slim-buster

# Create directory for app user
RUN mkdir -p /home/app

# Create app user
RUN addgroup --system app && useradd -g app app

# Create appropriate directories
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
RUN mkdir $APP_HOME/poetry

# Set work directory
WORKDIR $APP_HOME

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.0 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    ENVIRONMENT=development

# Install psycopg2 and weasyprint dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git python3-dev libpq-dev python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info && \
    apt-get clean

# Install dependencies - poetry
RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Install other dependencies
RUN poetry install

# Copy app files
COPY . .
RUN chmod +x ./entrypoint.sh

# Chown all the files to the app user
RUN chown -R app:app .

# Change to the app user
USER app

# Run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]