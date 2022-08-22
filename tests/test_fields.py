from typing import List, Optional

from pydantic import ValidationError

from santic_validation import MethodType, SanticModel


class UserSchema(SanticModel):
    name: str
    age: MethodType[int]
    ids: Optional[MethodType[List[int]]]


class TestFields:
    async def test_positive_method_type(self):
        data = {"name": "max", "age": 10}
        user = UserSchema(**data)
        res = data.copy()
        res["ids"] = None
        assert user.dict() == res
        assert user._context == {}

        user2 = UserSchema(name=data["name"], age="10", ids=["1", 2])
        res["ids"] = [1, 2]
        assert user2.dict() == res
        assert user2._context == {}

    async def test_negative_method_type(self):
        try:
            UserSchema(name="Max", age="10", ids=["AA", 2])
        except ValidationError as err:
            assert err.errors() == [
                {"loc": ("ids",), "msg": "Expected type int", "type": "type_error"}
            ]

        class UserSchema2(SanticModel):
            name: str
            age: MethodType

        try:
            UserSchema2(name="Max", age="10")
        except ValidationError as err:
            assert err.errors() == [
                {"loc": ("age",), "msg": "Value type not found", "type": "value_error"}
            ]
