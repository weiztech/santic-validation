Sanic Pydantic Validation
=========================

.. start-badges

.. list-table::
    :widths: 15 85
    :stub-columns: 1
    
    * - Build
      - | |Tox|
    * - Package
      - | |PyPI| |PyPI version| |Code style black|

.. |Tox| image:: https://github.com/weiztech/santic-validation/actions/workflows/python-package.yml/badge.svg?branch=main
   :target: https://github.com/weiztech/santic-validation/actions/workflows/python-package.yml
.. |PyPI| image:: https://img.shields.io/pypi/v/santic-validation.svg
   :target: https://pypi.python.org/pypi/santic-validation/
.. |PyPI version| image:: https://img.shields.io/pypi/pyversions/santic-validation.svg
   :target: https://pypi.python.org/pypi/santic-validation/
.. |Code style black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

.. end-badges

Tools for help developers working with Sanic and Pydantic.

Features
--------

- validate_schema
- async_validate_by_method
- SanticModel
- `MethodType` Field

Installation
------------

::

 pip install santic-validation


Usage
------------

::

 from typing import Optional
 from pydantic import BaseModel, Field
 from santic_validation import (
     validate_schema,
     async_validate_by_method,
     SanticModel,
     MethodType,
 )
 
 
 class QueryAddressSchema(BaseModel):
    location: str


 def address_number(value: str):
    return f"Number: {value}"


 def make_address(value: str):
    return f"Address: {value}"


 class AddressSchema(SanticModel):
    number: MethodType[int] = Field(method=address_number)
    address: MethodType[str] = Field(method=make_address)

    @property
    def address_method_params(self):
        query: QueryAddressSchema = self._context.get("query")
        return {"value": f"{self.address} ({query.location})"}

    @property
    def number_method_params(self):
        query: QueryAddressSchema = self._context.get("query")
        return {"value": f"{self.number} ({query.location})"}


 class PlanetSchema(BaseModel):
    name: Optional[str]
    category: int


 sanic_app = Sanic(name="TestingApp")


 def query_category_(category_id):
     return Model.get(id=category_id)


 @sanic_app.route("/post", methods=["POST"])
 @validate_schema(body=BodySchema, query=QuerySchema)
 async def post_handler(request, body, query):

     # validate to make sure category exists
     # if exists, change the body.category value
     async_validate_by_method(
         body,
         {
             "category": {
                 "method": query_category,
                 "params": {"category_id": body.category},
             }
         },
         exceptions=(DoesNotExists,),
     )

     return Text("hello world")
 
 
 @sanic_app.route("/post_address", methods=["POST"])
 @validate_schema(
    body=AddressSchema,
    query=QueryAddressSchema,
    method_replace_value=True,
 )
 async def post_address(request, body, query):
     return json(
         {
             "body": body.dict(),
             "query": query.dict(),
         }
     )
