from typing import List, Optional

import pytest
from pydantic import BaseModel
from sanic import Sanic
from sanic.response import json, json_dumps

from santic_validation import validate_schema


class BodySchema(BaseModel):
    name: str
    age: int
    list_address: List[str]
    list_ids: Optional[List[int]]


class QuerySchema(BaseModel):
    page: int


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
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = dict(**payload, **{"list_ids": None})
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
