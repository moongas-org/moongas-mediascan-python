import pandas as pd
import pytest

from mediascan.utils.db._dataframe_row import optional_boolean, optional_float


@pytest.mark.parametrize("value", [None, float("nan"), pd.NA])
def test_optional_boolean_returns_none_for_missing_values(value: object) -> None:
    assert optional_boolean(value) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, False), (1, True), (1.0, True), (True, True), (False, False)],
)
def test_optional_boolean_converts_sqlite_values(
    value: object, expected: bool
) -> None:
    assert optional_boolean(value) is expected


@pytest.mark.parametrize(
    ("value", "error"),
    [(2, ValueError), (0.5, ValueError), ("1", TypeError)],
)
def test_optional_boolean_rejects_invalid_values(
    value: object, error: type[Exception]
) -> None:
    with pytest.raises(error):
        optional_boolean(value)


@pytest.mark.parametrize("value", [None, float("nan"), pd.NA])
def test_optional_float_returns_none_for_missing_values(value: object) -> None:
    assert optional_float(value) is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [(1, 1.0), (1.25, 1.25)],
)
def test_optional_float_converts_real_values(value: object, expected: float) -> None:
    result = optional_float(value)
    assert result == expected
    assert isinstance(result, float)


@pytest.mark.parametrize("value", ["1.25", True])
def test_optional_float_rejects_non_numeric_values(value: object) -> None:
    with pytest.raises(TypeError, match="Expected a float"):
        optional_float(value)
