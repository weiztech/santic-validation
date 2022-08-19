from pydantic import BaseModel, Field, ValidationError

# isort: off
from santic_validation import (
    MethodType,
    SanticModel,
    async_validate_by_method,
    validate_method_fields,
)

# isort: on


class PlanetSchema(BaseModel):
    name: str
    age: int


class TestAsyncValidate:
    @staticmethod
    async def age_to_string(value) -> str:
        return str(value)

    async def test_positive_async_validate_by_method(self):
        schema = PlanetSchema(name="Anna", age=20)
        assert isinstance(schema.age, int)

        is_valid, errors = await async_validate_by_method(
            schema,
            {
                "age": {
                    "method": self.age_to_string,
                    "params": {"value": schema.age},
                }
            },
            exceptions=(ValidationError,),
        )

        assert is_valid
        assert errors is None
        assert isinstance(schema.age, str)

    async def test_negative_async_validate_by_method(self):
        schema = PlanetSchema(name="Anna", age=20)
        assert isinstance(schema.age, int)

        is_valid, errors = await async_validate_by_method(
            schema,
            {
                "age_test": {
                    "method": self.age_to_string,
                    "params": {"value": schema.age},
                }
            },
            exceptions=(
                ValidationError,
                ValueError,
            ),
        )

        assert is_valid is False
        assert errors == {"age_test": "Invalid value"}

    async def test_validate_method_fields(self):
        class Age(object):
            value: int

            def __init__(self, value):
                self.value = value

            @classmethod
            def to_instance(cls, age: int):
                return cls(value=age)

        class UserSchema(SanticModel):
            name: str
            age: MethodType[int] = Field(method=Age.to_instance)

            @property
            def age_method_params(self):
                return {"age": self.age}

        data = {"name": "Zack", "age": 10}
        user = UserSchema(**data)

        await validate_method_fields(user)
        assert data == user.dict()

        await validate_method_fields(user, replace_value=True)
        assert user.name == data["name"]
        assert isinstance(user.age, Age) is True

        async def multiply(value):
            return value * 2

        class PersonSchema(SanticModel):
            name: str
            age: MethodType[int] = Field(method=multiply)

            @property
            def age_method_params(self):
                return {"value": self.age}

        data = {"name": "Zack", "age": 10}
        user = PersonSchema(**data)

        await validate_method_fields(user)
        assert data == user.dict()

        data["age"] = data["age"] * 2
        await validate_method_fields(user, replace_value=True)
        assert data == user.dict()
