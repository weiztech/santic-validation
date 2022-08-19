from santic_validation import MethodType, SanticModel


class UserSchema(SanticModel):
    name: str
    age: MethodType[int]


class TestFields:
    async def test_positive_method_type(self):
        data = {"name": "max", "age": 10}
        user = UserSchema(**data)
        assert user.dict() == data
        assert user._context == {}

    async def test_negative_method_type(self):
        try:
            UserSchema(name="Max", age="10")
        except Exception as err:
            assert err.errors() == [
                {"loc": ("age",), "msg": "Expected type int", "type": "type_error"}
            ]

        class UserSchema2(SanticModel):
            name: str
            age: MethodType

        try:
            UserSchema2(name="Max", age="10")
        except Exception as err:
            assert err.errors() == [
                {"loc": ("age",), "msg": "Value type not found", "type": "value_error"}
            ]
