"""Tests for package-level exports."""

import blip8


def test_version_is_exposed() -> None:
    assert blip8.__version__
    assert blip8.__version__ != "0.0.0+unknown"


def test_everything_in_all_is_importable() -> None:
    for name in blip8.__all__:
        assert hasattr(blip8, name), name
