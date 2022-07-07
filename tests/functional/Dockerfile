FROM python:3.10

RUN pip install --upgrade pip
RUN pip install poetry

ENV PYTHONPATH "${PYTHONPATH}:/app"

WORKDIR /app

COPY ./pyproject.toml ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . ./

CMD sh -c "python /app/utils/wait_for_elastic.py \
    && python /app/utils/wait_for_redis.py \
    && python -m pytest -s -p no:warnings"