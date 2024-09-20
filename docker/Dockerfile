FROM python:3.12
MAINTAINER Nicolò Vescera <nicolo.vescera@unipg.it>

RUN pip install poetry

RUN mkdir /project
COPY . /project

WORKDIR /project

# set envs to activate poetry env
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN poetry install

ENV VIRTUAL_ENV=/project/.venv \
    PATH="/project/.venv/bin:$PATH"

EXPOSE 5000

CMD ["./run.sh"]
