from typing import Any, Callable

import orjson
from pydantic import BaseModel


def orjson_dumps(v: Any, *, default: Callable[[Any], Any] | None) -> str:
    return orjson.dumps(v, default=default).decode()


class OrJsonMixin:
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseDBModel(BaseModel, OrJsonMixin):
    pass
