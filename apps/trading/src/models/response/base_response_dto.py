from typing import Generic, TypeVar
from pydantic import BaseModel
from pydantic.alias_generators import to_camel

# from pydantic.generics import GenericModel

M = TypeVar("M", bound=BaseModel)


class BaseGenericResponse(BaseModel):
    status_code: int = 200

    class Config:
        alias_generator = to_camel


class BaseResponse(BaseGenericResponse, Generic[M]):
    item: M


class BaseListResponse(BaseGenericResponse, Generic[M]):
    items: list[M]
