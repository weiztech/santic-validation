from typing import Any, Callable, Dict, TypedDict, TypeVar, Union

Schema = TypeVar("Schema")


class MethodData(TypedDict):
    method: Callable
    params: Dict[str, str]


async def async_validate_by_method(
    schema: Schema,
    data: Dict[str, Dict[str, Union[Callable, Dict[str, str]]]],
    exceptions: Union[Any],
    skip_on_fail: bool = False,
):
    error = {}
    for field_name, method_data in data.items():
        try:
            value = await method_data["method"](**method_data["params"])
            setattr(schema, field_name, value)
        except exceptions:
            error[field_name] = "Invalid value"
            if skip_on_fail:
                return error

    return True if not error else False, error or None
