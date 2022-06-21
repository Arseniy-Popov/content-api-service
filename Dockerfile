FROM python:3.10

RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /app

COPY ./pyproject.toml ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . ./

CMD python src/main.py