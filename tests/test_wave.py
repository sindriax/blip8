"""Tests for the oscillators.

How do you test a *sound*? You can't assert "this sounds like a Game Boy". But
every claim in wave.py's docstrings is secretly a claim about numbers, and
numbers you can check:

    "half a second long"        → the array has SAMPLE_RATE * 0.5 items
    "square jumps, never slides" → only two distinct values ever appear
    "duty is the fraction up"    → count how many samples are positive
    "440 Hz means 440 cycles/s"  → count the cycles

Run them all with:  uv run pytest
"""

import numpy as np
import pytest

from blip8 import SAMPLE_RATE, noise, square, triangle

# pytest collects any function starting with `test_` in any file named
# `test_*.py`. No registration, no suite object — that's the whole convention.


# --------------------------------------------------------------------------
# Things that must be true of ALL three oscillators
# --------------------------------------------------------------------------

# A list of (human name, function) pairs. `parametrize` below runs the test
# once per entry, so one test function becomes three reported test cases.
OSCILLATORS = [
    ("square", lambda length: square(freq=440, length=length)),
    ("triangle", lambda length: triangle(freq=440, length=length)),
    ("noise", lambda length: noise(length=length)),
]


@pytest.mark.parametrize(("name", "osc"), OSCILLATORS)
def test_length_matches_seconds_requested(name, osc):
    """0.25 seconds must mean exactly SAMPLE_RATE * 0.25 samples."""
    samples = osc(0.25)
    assert len(samples) == int(SAMPLE_RATE * 0.25) == 11025


@pytest.mark.parametrize(("name", "osc"), OSCILLATORS)
def test_never_exceeds_speaker_range(name, osc):
    """Samples outside -1.0..1.0 get clipped on save and sound like crackle.

    np.all() is NumPy's "every item passes" — it collapses a whole array of
    True/False into one answer.
    """
    samples = osc(0.1)
    assert np.all(samples >= -1.0)
    assert np.all(samples <= 1.0)


@pytest.mark.parametrize(("name", "osc"), OSCILLATORS)
def test_returns_float_array(name, osc):
    """Downstream code (save, mixing) assumes floats, not ints."""
    samples = osc(0.1)
    assert isinstance(samples, np.ndarray)
    assert samples.dtype == np.float64


# --------------------------------------------------------------------------
# square
# --------------------------------------------------------------------------


def test_square_only_has_two_values():
    """The defining property: a square is either fully up or fully down.

    No in-between positions, ever. That's what makes it buzz, and it's what
    distinguishes it from triangle.
    """
    samples = square(freq=440, length=0.1, volume=0.4)
    assert sorted(np.unique(samples)) == [-0.4, 0.4]


def test_square_jumps_but_triangle_slides():
    """The buzzy-vs-soft difference, expressed as a number.

    np.diff() gives the gap between each pair of neighbouring samples. For a
    square that gap is the entire range (a hard jump). For a triangle it's a
    tiny step, because it ramps.
    """
    biggest_square_step = np.max(np.abs(np.diff(square(freq=440, length=0.1))))
    biggest_triangle_step = np.max(np.abs(np.diff(triangle(freq=440, length=0.1))))

    assert biggest_square_step == pytest.approx(1.0)  # -0.5 straight to +0.5
    assert biggest_triangle_step < 0.05  # gradual


@pytest.mark.parametrize("duty", [0.125, 0.25, 0.5, 0.75])
def test_duty_is_the_fraction_of_time_spent_up(duty):
    """duty=0.125 should mean the wave is "up" one eighth of the time."""
    samples = square(freq=100, length=1.0, duty=duty)
    fraction_up = np.count_nonzero(samples > 0) / len(samples)
    assert fraction_up == pytest.approx(duty, abs=0.01)


def test_duty_does_not_change_pitch():
    """The whole point of the duty knob: same note, different character."""
    assert _count_cycles(square(freq=440, length=0.5, duty=0.5)) == pytest.approx(220, abs=1)
    assert _count_cycles(square(freq=440, length=0.5, duty=0.125)) == pytest.approx(220, abs=1)


# --------------------------------------------------------------------------
# triangle
# --------------------------------------------------------------------------


def test_triangle_uses_the_full_range():
    """A triangle should reach both extremes, not hover in the middle."""
    samples = triangle(freq=440, length=0.1, volume=0.5)
    assert np.max(samples) == pytest.approx(0.5, abs=0.01)
    assert np.min(samples) == pytest.approx(-0.5, abs=0.01)


def test_triangle_has_many_distinct_values():
    """Contrast with test_square_only_has_two_values — this is the same test
    from the other side. Sliding means lots of intermediate positions."""
    samples = triangle(freq=440, length=0.1)
    assert len(np.unique(samples)) > 50


# --------------------------------------------------------------------------
# noise
# --------------------------------------------------------------------------


def test_noise_is_different_every_call():
    """Random means random. Two crashes shouldn't be identical."""
    assert not np.array_equal(noise(length=0.1), noise(length=0.1))


def test_noise_is_centred_on_zero():
    """Averaged out, the speaker cone should sit at rest, not pushed to one
    side. An off-centre wave wastes headroom and can thump."""
    assert np.mean(noise(length=1.0)) == pytest.approx(0.0, abs=0.01)


def test_noise_has_no_pitch():
    """The claim in the docstring: static has no repeating cycle.

    A pitched wave crosses zero a predictable number of times (twice per
    cycle). Noise crosses it constantly and unpredictably — far more often
    than any musical note would.
    """
    crossings = _count_cycles(noise(length=1.0))
    assert crossings > 5000


# --------------------------------------------------------------------------
# pitch, for the two oscillators that have one
# --------------------------------------------------------------------------


@pytest.mark.parametrize("freq", [110, 220, 440, 880])
@pytest.mark.parametrize("osc", [square, triangle])
def test_freq_really_means_cycles_per_second(osc, freq):
    """freq=440 over 0.5s must produce 220 repeats. This is the test that
    would catch an off-by-a-factor-of-two error in the phase math."""
    samples = osc(freq=freq, length=0.5)
    assert _count_cycles(samples) == pytest.approx(freq * 0.5, abs=1)


@pytest.mark.parametrize("osc", [square, triangle])
def test_volume_scales_the_output(osc):
    """volume=0.25 should be exactly half as far from rest as volume=0.5."""
    quiet = np.max(np.abs(osc(freq=440, length=0.1, volume=0.25)))
    loud = np.max(np.abs(osc(freq=440, length=0.1, volume=0.5)))
    assert quiet == pytest.approx(loud / 2, abs=0.01)


# --------------------------------------------------------------------------
# pitch sweeps — passing (start, end) instead of one frequency
# --------------------------------------------------------------------------


@pytest.mark.parametrize("osc", [square, triangle])
def test_sweep_has_the_right_length(osc):
    """A glide shouldn't change how long the sound is."""
    assert len(osc(freq=(200, 1600), length=0.3)) == int(SAMPLE_RATE * 0.3)


@pytest.mark.parametrize("osc", [square, triangle])
def test_rising_sweep_speeds_up_over_time(osc):
    """The defining property of a rising glide: more cycles happen in the
    second half of the sound than in the first."""
    samples = osc(freq=(110, 880), length=1.0)
    midpoint = len(samples) // 2

    first_half = _count_cycles(samples[:midpoint])
    second_half = _count_cycles(samples[midpoint:])

    assert second_half > first_half * 2


@pytest.mark.parametrize("osc", [square, triangle])
def test_falling_sweep_slows_down_over_time(osc):
    """And a falling glide does the opposite — this is the laser sound."""
    samples = osc(freq=(880, 110), length=1.0)
    midpoint = len(samples) // 2

    assert _count_cycles(samples[:midpoint]) > _count_cycles(samples[midpoint:]) * 2


@pytest.mark.parametrize("osc", [square, triangle])
def test_sweep_between_identical_pitches_matches_a_steady_note(osc):
    """A "glide" from 440 to 440 is just a note at 440. Sanity-checks that the
    accumulated phase maths agrees with the multiply shortcut."""
    swept = _count_cycles(osc(freq=(440, 440), length=0.5))
    steady = _count_cycles(osc(freq=440, length=0.5))
    assert swept == pytest.approx(steady, abs=1)


@pytest.mark.parametrize("osc", [square, triangle])
def test_sweep_cycle_count_matches_the_average_pitch(osc):
    """Gliding evenly from 200 to 400 Hz over a second should produce about as
    many cycles as a steady 300 Hz would."""
    swept = _count_cycles(osc(freq=(200, 400), length=1.0))
    assert swept == pytest.approx(300, abs=2)


def test_sweep_still_respects_duty():
    """The duty knob and the glide shouldn't interfere with each other."""
    samples = square(freq=(200, 400), length=1.0, duty=0.25)
    fraction_up = np.count_nonzero(samples > 0) / len(samples)
    assert fraction_up == pytest.approx(0.25, abs=0.01)


# --------------------------------------------------------------------------
# helper
# --------------------------------------------------------------------------


def _count_cycles(samples: np.ndarray) -> int:
    """Count how many times the wave goes from negative to positive.

    That happens exactly once per cycle, so for a pitched wave this is the
    number of repeats — a way to measure pitch without any Fourier maths.
    Leading underscore = "internal helper", and it stops pytest collecting
    this as a test.
    """
    positive = samples > 0
    # A rising edge is a False immediately followed by a True.
    return int(np.count_nonzero(~positive[:-1] & positive[1:]))
