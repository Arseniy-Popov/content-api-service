FROM python:3.10

RUN pip install --upgrade pip
RUN pip install poetry

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

WORKDIR /app

COPY ./pyproject.toml ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . ./

CMD gunicorn -c infra/gunicorn/gunicorn.conf.py main:app
# CMD gunicorn main:app