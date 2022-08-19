from inspect import iscoroutinefunction
from typing import Any, Callable, Dict, TypedDict, TypeVar, Union

from .fields import SanticModel

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


async def validate_method_fields(schema: SanticModel, replace_value=False):
    method_fields = getattr(schema, "_method_fields", None)
    if not method_fields:
        return

    for name in method_fields:
        method, params = (
            schema.__fields__[name].field_info.extra.get("method"),
            getattr(schema, f"{name}_method_params", {}),
        )
        if iscoroutinefunction(method):
            value = await method(**params)
        else:
            value = method(**params)

        if replace_value:
            setattr(schema, name, value)
