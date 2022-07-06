FROM python:3.10

RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /tests

COPY ./pyproject.toml ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . ./