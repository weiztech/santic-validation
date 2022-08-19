from typing import List, Optional

import pytest
from pydantic import BaseModel, Field
from sanic import Sanic
from sanic.response import json, json_dumps

from santic_validation import MethodType, SanticModel, validate_schema


class BodySchema(BaseModel):
    name: str
    age: int
    list_address: List[str]
    list_ids: Optional[List[int]]


class QuerySchema(BaseModel):
    page: int


def address_number(value: str):
    return f"Number: {value}"


def make_address(value: str):
    return f"Address: {value}"


class AddressSchema(SanticModel):
    number: MethodType[int] = Field(method=address_number)
    address: MethodType[str] = Field(method=make_address)

    @property
    def address_method_params(self):
        query: QuerySchema = self._context.get("query")
        return {"value": f"{self.address} ({query.location})"}

    @property
    def number_method_params(self):
        query: QuerySchema = self._context.get("query")
        return {"value": f"{self.number} ({query.location})"}


class QueryAddressSchema(BaseModel):
    location: str


@pytest.fixture
def app():
    sanic_app = Sanic(name="TestingApp")

    @sanic_app.route("/post", methods=["POST"])
    @validate_schema(body=BodySchema, query=QuerySchema)
    async def post_handler(request, body, query):
        return json(
            {
                "body": body.dict(),
                "query": query.dict(),
            }
        )

    @sanic_app.route("/post_address", methods=["POST"])
    @validate_schema(body=AddressSchema, query=QueryAddressSchema)
    async def post_handler(request, body, query):
        return json(
            {
                "body": body.dict(),
                "query": query.dict(),
            }
        )

    @sanic_app.route("/post_address_replace", methods=["POST"])
    @validate_schema(
        body=AddressSchema,
        query=QueryAddressSchema,
        method_replace_value=True,
    )
    async def post_handler(request, body, query):
        return json(
            {
                "body": body.dict(),
                "query": query.dict(),
            }
        )

    return sanic_app


class TestValidateSchema:
    def test_positive_validate_schema(self, app):
        # Test request.json
        payload = {
            "name": "Anna",
            "age": 20,
            "list_address": ["address 1", "address 2"],
            "list_ids": [1, 2, 3],
        }
        query = {"page": 10}
        headers = {"content-type": "application/json"}

        response = app.test_client.post(
            "/post",
            data=json_dumps(payload),
            params=query,
            headers=headers,
        )[1]

        assert response.status_code == 200
        assert response.json == {
            "body": payload,
            "query": query,
        }

        # Test request.form
        payload = {
            "name": "Anna",
            "age": 20,
            "list_address": ["address 1", "address 2"],
            "list_ids": [1, 2, 3],
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = payload
        request, response = app.test_client.post(
            "/post",
            data=data,
            params=query,
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json == {
            "body": data,
            "query": query,
        }

    def test_negative_validate_schema(self, app):
        # test request.json
        payload = {"any": 1}
        headers = {"content-type": "application/json"}
        response = app.test_client.post(
            "/post",
            data=payload,
            headers=headers,
        )[1]

        assert response.status_code == 400

        # test request.form
        headers = {"content-type": "application/x-www-form-urlencoded"}
        response = app.test_client.post(
            "/post",
            data=payload,
            params={"page": 10},
            headers=headers,
        )[1]

        assert response.status_code == 400

    def test_validate_method_fields(self, app):
        # test validate methods
        data = {"address": "my-address", "number": 101}
        query = {"location": "Earth"}

        headers = {"content-type": "application/json"}
        request, response = app.test_client.post(
            "/post_address",
            data=json_dumps(data),
            params=query,
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json == {
            "body": data,
            "query": query,
        }

        headers = {"content-type": "application/x-www-form-urlencoded"}
        request, response = app.test_client.post(
            "/post_address",
            data=data,
            params=query,
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json == {
            "body": data,
            "query": query,
        }

        # test with replace value
        data = {"address": "my-address", "number": 101}
        query = {"location": "Earth"}

        headers = {"content-type": "application/json"}
        request, response = app.test_client.post(
            "/post_address_replace",
            data=json_dumps(data),
            params=query,
            headers=headers,
        )

        resp_data = data.copy()
        resp_data["address"] = f"Address: {data['address']} ({query['location']})"
        resp_data["number"] = f"Number: {data['number']} ({query['location']})"

        assert response.status_code == 200
        assert response.json == {
            "body": resp_data,
            "query": query,
        }

        data = {"address": "my-address", "number": 101}
        query = {"location": "Earth"}

        headers = {"content-type": "application/x-www-form-urlencoded"}
        request, response = app.test_client.post(
            "/post_address_replace",
            data=data,
            params=query,
            headers=headers,
        )

        resp_data = data.copy()
        resp_data["address"] = f"Address: {data['address']} ({query['location']})"
        resp_data["number"] = f"Number: {data['number']} ({query['location']})"

        assert response.status_code == 200
        assert response.json == {
            "body": resp_data,
            "query": query,
        }
