"""Tests for the recipe layer.

Deliberately shallow: there is no way to assert that something sounds like a
coin. These guarantee every recipe stays usable — produces sound, does not clip
or click — and fail loudly if a change to wave.py breaks them all at once.
"""

import numpy as np
import pytest

from blip8 import SAMPLE_RATE, sfx

# Listed by hand so deleting a recipe fails a test rather than quietly
# shrinking the suite.
RECIPES = [
    "blip",
    "select",
    "back",
    "coin",
    "jump",
    "powerup",
    "laser",
    "hurt",
    "explosion",
    "chime",
    "kick",
    "snare",
    "hat",
    "crash",
]


@pytest.fixture(params=RECIPES)
def sound(request):
    """Runs every test that requests `sound` once per recipe."""
    return getattr(sfx, request.param)()


def test_recipe_produces_audio(sound):
    assert isinstance(sound, np.ndarray)
    assert len(sound) > 0
    assert sound.dtype == np.float64


def test_recipe_is_actually_audible(sound):
    """Guards against a recipe that returns an array of silence."""
    assert np.max(np.abs(sound)) > 0.05


def test_recipe_will_not_clip(sound):
    """Recipes must leave headroom, since callers add them together."""
    assert np.max(np.abs(sound)) <= 1.0


def test_recipe_does_not_click(sound):
    """Starts and ends at silence, so there's no speaker snap at either edge."""
    assert abs(sound[0]) < 0.01
    assert abs(sound[-1]) < 0.01


def test_recipe_has_a_sane_duration(sound):
    """A sound effect that outlasts the action it accompanies is a bug."""
    seconds = len(sound) / SAMPLE_RATE
    assert 0.01 < seconds < 3.0


# --------------------------------------------------------------------------
# A couple of specific claims worth pinning down
# --------------------------------------------------------------------------


def test_recipes_can_be_mixed_without_clipping():
    """The documented use case, `sfx.kick() + sfx.hat()`, trimmed to the
    shorter of the two."""
    kick, hat = sfx.kick(), sfx.hat()
    overlap = min(len(kick), len(hat))
    assert np.max(np.abs(kick[:overlap] + hat[:overlap])) <= 1.0


def test_select_rises_and_back_falls():
    """Compares which half of each sound holds the higher pitch."""
    for sound, expect_rising in ((sfx.select(), True), (sfx.back(), False)):
        midpoint = len(sound) // 2
        first = _crossings(sound[:midpoint])
        second = _crossings(sound[midpoint:])
        assert (second > first) == expect_rising


def test_crash_is_a_longer_snare():
    """They share raw material and differ only in fade length."""
    assert len(sfx.crash()) > len(sfx.snare()) * 5


def _crossings(samples: np.ndarray) -> int:
    positive = samples > 0
    return int(np.count_nonzero(~positive[:-1] & positive[1:]))
