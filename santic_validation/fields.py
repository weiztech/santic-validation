from typing import Dict, Generic, TypeVar, Union, no_type_check

from pydantic import BaseModel, PrivateAttr
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass

ValueType = TypeVar("value")


class MethodType(Generic[ValueType]):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField, values):
        value_type = field.sub_fields[0] if field.sub_fields else None

        if not value_type:
            raise ValueError("Value type not found")

        if value_type.type_ == int:
            try:
                if isinstance(v, list):
                    v = [int(num) for num in v]
                else:
                    v = int(v)
            except ValueError:
                raise TypeError(f"Expected type {value_type.type_.__name__}")

        return v


class Meta(ModelMetaclass):
    @no_type_check  # noqa C901
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        setattr(cls, "_method_fields", [])
        for name, model_field in cls.__fields__.items():
            if model_field.type_ == MethodType:
                cls._method_fields.append(name)

        return cls


class SanticModel(BaseModel, metaclass=Meta):
    _context: Dict[Union[str, int, float], any] = PrivateAttr(default={})
