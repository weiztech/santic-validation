from pydantic import BaseModel, ValidationError

from santic_validation import async_validate_by_method


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
