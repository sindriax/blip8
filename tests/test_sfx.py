"""Tests for the recipe layer.

These are deliberately shallow. There's no way to assert "this sounds like a
coin" — that's a judgement call for ears. What tests *can* guarantee is that
every recipe stays usable: produces sound, doesn't clip, doesn't click, and
doesn't silently disappear when someone refactors wave.py underneath it.

That last one is the real value. If a change breaks `square()`, all 14 recipes
fail at once and you know immediately.
"""

import numpy as np
import pytest

from blip8 import SAMPLE_RATE, sfx

# Every public recipe. Listed by hand rather than discovered automatically, so
# that deleting one makes a test fail instead of quietly shrinking the suite.
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
    """A pytest fixture: every test that asks for `sound` runs once per recipe.

    `request.param` is the current name. This is a tidier way to say "run this
    against all 14" than repeating the parametrize decorator each time.
    """
    return getattr(sfx, request.param)()


def test_recipe_produces_audio(sound):
    assert isinstance(sound, np.ndarray)
    assert len(sound) > 0
    assert sound.dtype == np.float64


def test_recipe_is_actually_audible(sound):
    """Guards against a recipe that technically returns an array of silence,
    which is the most likely way for one of these to break unnoticed."""
    assert np.max(np.abs(sound)) > 0.05


def test_recipe_will_not_clip(sound):
    """Every recipe must leave headroom, because users will add them together.

    If a single sound already peaked at 1.0, mixing two would distort.
    """
    assert np.max(np.abs(sound)) <= 1.0


def test_recipe_does_not_click(sound):
    """Starts and ends at silence, so there's no speaker snap at either edge."""
    assert abs(sound[0]) < 0.01
    assert abs(sound[-1]) < 0.01


def test_recipe_has_a_sane_duration(sound):
    """Nothing shorter than a tick or longer than a couple of seconds — a game
    sound effect that outlasts the action is a bug."""
    seconds = len(sound) / SAMPLE_RATE
    assert 0.01 < seconds < 3.0


# --------------------------------------------------------------------------
# A couple of specific claims worth pinning down
# --------------------------------------------------------------------------


def test_recipes_can_be_mixed_without_clipping():
    """The documented use case: `sfx.kick() + sfx.hat()`.

    Both are trimmed to the shorter length first, which is what a real mixer
    would do differently — but it proves the headroom budget works.
    """
    kick, hat = sfx.kick(), sfx.hat()
    overlap = min(len(kick), len(hat))
    assert np.max(np.abs(kick[:overlap] + hat[:overlap])) <= 1.0


def test_select_rises_and_back_falls():
    """The menu convention, asserted. Comparing which half of each sound holds
    the higher pitch, via zero crossings as a cheap pitch measure."""
    for sound, expect_rising in ((sfx.select(), True), (sfx.back(), False)):
        midpoint = len(sound) // 2
        first = _crossings(sound[:midpoint])
        second = _crossings(sound[midpoint:])
        assert (second > first) == expect_rising


def test_crash_is_a_longer_snare():
    """They share raw material and differ only in how long they take to fade."""
    assert len(sfx.crash()) > len(sfx.snare()) * 5


def _crossings(samples: np.ndarray) -> int:
    positive = samples > 0
    return int(np.count_nonzero(~positive[:-1] & positive[1:]))
