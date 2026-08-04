"""Tests for input validation.

Every case here used to succeed and produce something wrong: silence, an
inverted wave, or samples outside the range `save()` can represent. Failing
loudly at the call site beats debugging a silent sound later.
"""

import pytest

from blip8 import crunch, envelope, noise, square, triangle, wavetable


@pytest.mark.parametrize("volume", [1.01, 2.0, -0.5, -1.0])
def test_volume_outside_zero_to_one_is_rejected(volume: float) -> None:
    """volume=2.0 used to return samples peaking at 2.0, which save() then
    silently clipped. volume=-1.0 used to invert the wave."""
    with pytest.raises(ValueError, match="volume must be between"):
        square(freq=440, length=0.1, volume=volume)


@pytest.mark.parametrize("duty", [0.0, 1.0, 5.0, -1.0])
def test_duty_outside_zero_to_one_is_rejected(duty: float) -> None:
    """duty=5.0 used to hold the wave permanently high, which is silence."""
    with pytest.raises(ValueError, match="duty must be between"):
        square(freq=440, length=0.1, duty=duty)


@pytest.mark.parametrize("freq", [0, -440])
def test_freq_at_or_below_zero_is_rejected(freq: float) -> None:
    """freq=0 used to return a constant, which is silence."""
    with pytest.raises(ValueError, match="freq must be greater than 0"):
        square(freq=freq, length=0.1)


def test_freq_above_nyquist_is_rejected() -> None:
    """Above half the sample rate a wave cannot be represented at all; it
    aliases down to some other frequency."""
    with pytest.raises(ValueError, match="Nyquist"):
        square(freq=30000, length=0.1)


def test_a_sweep_validates_both_ends() -> None:
    with pytest.raises(ValueError, match="freq must be greater than 0"):
        square(freq=(440, 0), length=0.1)


def test_negative_length_is_rejected() -> None:
    """It used to return an empty array, so a typo produced no sound at all."""
    with pytest.raises(ValueError, match="length must not be negative"):
        square(freq=440, length=-1.0)


def test_zero_length_is_allowed() -> None:
    """Distinct from negative: an empty sound is a legitimate edge case, and
    melody("") relies on it."""
    assert len(square(freq=440, length=0.0)) == 0


@pytest.mark.parametrize("bits", [1, 0, -4])
def test_crunch_below_two_bits_is_rejected(bits: int) -> None:
    """bits=0 used to return pure silence rather than extreme grit."""
    with pytest.raises(ValueError, match="bits must be at least 2"):
        crunch(square(freq=440, length=0.1), bits=bits)


def test_empty_wavetable_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least one value"):
        wavetable([], freq=440, length=0.1)


def test_sustain_outside_zero_to_one_is_rejected() -> None:
    with pytest.raises(ValueError, match="sustain is a level"):
        envelope(square(freq=440, length=0.1), sustain=2.0)


def test_negative_envelope_stages_are_rejected() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        envelope(square(freq=440, length=0.1), attack=-0.1)


@pytest.mark.parametrize("volume", [0.0, 1.0])
def test_the_boundaries_are_allowed(volume: float) -> None:
    """Silence and full scale are both legitimate."""
    assert len(triangle(freq=440, length=0.1, volume=volume)) > 0
    assert len(noise(length=0.1, volume=volume)) > 0
