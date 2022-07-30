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

Installation
------------

::

 pip install santic-validation


Usage
------------

::

 from typing import Optional
 from pydantic import BaseModel
 from santic_validation import validate_schema, async_validate_by_method


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
