# Pull official base image
FROM python:3.8-slim-buster

# create directory for app user
RUN mkdir -p /home/app

# create app user
RUN addgroup --system app && useradd -g app app

# create appropriate directories
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
RUN mkdir $APP_HOME/poetry

# set work directory
WORKDIR $APP_HOME

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.0 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    ENVIRONMENT=development

# Install dependencies - psycopg2
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends git python3-dev libpq-dev && \
    apt-get clean

# Install dependencies - poetry
RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Install other dependencies
RUN poetry install

# copy project
COPY . .
RUN chmod +x ./entrypoint.sh

# chown all the files to the app user
RUN chown -R app:app .

# change to the app user
USER app

# Run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]