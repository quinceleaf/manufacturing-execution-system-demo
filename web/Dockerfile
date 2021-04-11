# pull official base image
FROM python:3.8-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER=1 
ENV POETRY_VERSION=1.0
ENV ENVIRONMENT=production

# install psycopg2 dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y netcat-openbsd gcc git && \
    apt-get clean

# install dependencies
RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install $(test "$ENVIRONMENT" == production && echo "--no-dev") --no-interaction --no-ansi


# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]