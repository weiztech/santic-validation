from functools import wraps
from inspect import isawaitable
from typing import Dict, Optional, Type, get_args, get_origin, get_type_hints

from pydantic import ValidationError
from sanic import Request
from sanic.exceptions import SanicException

ARRAY_TYPES = {list, tuple}


def has_array_type(hint_value) -> Optional[bool]:
    if get_origin(hint_value) in ARRAY_TYPES:
        return True

    list_args = get_args(hint_value)
    for args in list_args:
        if get_origin(args) in ARRAY_TYPES:
            return True


def clean_data(schema, raw_data) -> Dict[str, any]:
    hints = get_type_hints(schema)
    data = {}

    for hint_key, hint_value in hints.items():
        is_array = has_array_type(hint_value)
        if is_array:
            value = raw_data.getlist(hint_key)
        else:
            value = raw_data.get(hint_key)

        data[hint_key] = value

    return data


def validate_schema(
    body: Optional[Type[object]] = None,
    query: Optional[Type[object]] = None,
):
    """
    Simple validation
    """

    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            if args and isinstance(args[0], Request):
                request: Request = args[0]
            elif len(args) > 1:
                request: Request = args[1]
            else:
                raise SanicException("Request could not be found")

            try:
                if query:
                    cleaned_data = clean_data(
                        query,
                        request.args,
                    )
                    kwargs["query"] = query(
                        **cleaned_data,
                    )
                if body:
                    if request.headers["content-type"] == "application/json":
                        cleaned_data = request.json
                    else:
                        cleaned_data = clean_data(
                            body,
                            request.form,
                        )

                    kwargs["body"] = body(**cleaned_data)
            except ValidationError as err:
                raise SanicException(
                    "Validation error",
                    context={
                        "detail": {
                            error["loc"][0]: error["msg"] for error in err.errors()
                        }
                    },
                    status_code=400,
                )
            retval = f(*args, **kwargs)
            if isawaitable(retval):
                retval = await retval
            return retval

        return decorated_function

    return decorator
