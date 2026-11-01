from math import isnan
from numbers import Integral, Real

import pandas as pd


def optional_text(value: object) -> str | None:
    if value is None or value is pd.NA or (isinstance(value, float) and isnan(value)):
        return None
    if not isinstance(value, str):
        raise TypeError(f"Expected a string or missing value, got {value!r}")
    return value


def optional_integer(value: object) -> int | None:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"Expected an integer or missing value, got {value!r}")
    if isinstance(value, Integral):
        return int(value)
    if isnan(value):
        return None
    result = int(float(value))
    if result != value:
        raise ValueError(f"Expected an integer, got {value!r}")
    return result


def optional_boolean(value: object) -> bool | None:
    """Convert SQLite BOOLEAN values, which are stored as 0/1 integers."""
    if isinstance(value, bool):
        return value
    result = optional_integer(value)
    if result is None:
        return None
    if result not in (0, 1):
        raise ValueError(f"Expected a boolean, got {value!r}")
    return bool(result)


def optional_float(value: object) -> float | None:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"Expected a float or missing value, got {value!r}")
    if isnan(value):
        return None
    return float(value)
