FROM python:3.12
MAINTAINER Nicolò Vescera <nicolo.vescera@unipg.it>

RUN mkdir -p /project/web
COPY . /project/web

WORKDIR /project/web

# set envs to activate poetry env
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/project/web/.venv \
    PATH="/project/web/.venv/bin:$PATH"

RUN pip install poetry && poetry install --no-root

EXPOSE 5000

CMD ["./run.sh"]
