import pandas as pd

from src.data.validate_dataset import normalize_label, parse_sample_number


def test_parse_sample_number_requires_expected_full_format() -> None:
    assert parse_sample_number("Sample 126") == "126"
    assert parse_sample_number(" Sample 12 ") == "12"
    assert parse_sample_number("126") is None
    assert parse_sample_number("Sample 12 extra") is None


def test_normalize_label_only_collapses_whitespace() -> None:
    assert normalize_label("Supratentorial\xa0  ependymoma") == (
        "Supratentorial ependymoma"
    )
    assert normalize_label("Supratentorial ependymoma, NOS") == (
        "Supratentorial ependymoma, NOS"
    )
    assert normalize_label(pd.NA) is None

