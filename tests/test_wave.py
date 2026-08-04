"""Tests for the oscillators."""

from collections.abc import Callable

import numpy as np
import pytest

from blip8 import BELL_TABLE, SAMPLE_RATE, SINE_TABLE, Samples, noise, square, triangle, wavetable

# --------------------------------------------------------------------------
# Things that must be true of ALL three oscillators
# --------------------------------------------------------------------------

OSCILLATORS = [
    ("square", lambda length: square(freq=440, length=length)),
    ("triangle", lambda length: triangle(freq=440, length=length)),
    ("noise", lambda length: noise(length=length)),
]


@pytest.mark.parametrize(("name", "osc"), OSCILLATORS)
def test_length_matches_seconds_requested(name: str, osc: Callable[..., Samples]) -> None:
    """0.25 seconds must mean exactly SAMPLE_RATE * 0.25 samples."""
    samples = osc(0.25)
    assert len(samples) == int(SAMPLE_RATE * 0.25) == 11025


@pytest.mark.parametrize(("name", "osc"), OSCILLATORS)
def test_never_exceeds_speaker_range(name: str, osc: Callable[..., Samples]) -> None:
    """Samples outside -1.0..1.0 get clipped on save and sound like crackle."""
    samples = osc(0.1)
    assert np.all(samples >= -1.0)
    assert np.all(samples <= 1.0)


@pytest.mark.parametrize(("name", "osc"), OSCILLATORS)
def test_returns_float_array(name: str, osc: Callable[..., Samples]) -> None:
    """Downstream code (save, mixing) assumes floats, not ints."""
    samples = osc(0.1)
    assert isinstance(samples, np.ndarray)
    assert samples.dtype == np.float64


# --------------------------------------------------------------------------
# square
# --------------------------------------------------------------------------


def test_square_only_has_two_values() -> None:
    """A square is either fully up or fully down, with nothing in between."""
    samples = square(freq=440, length=0.1, volume=0.4)
    assert sorted(np.unique(samples)) == [-0.4, 0.4]


def test_square_jumps_but_triangle_slides() -> None:
    """The buzzy-versus-soft difference, as a number: the gap between
    neighbouring samples is the full range for a square and tiny for a
    triangle."""
    biggest_square_step = np.max(np.abs(np.diff(square(freq=440, length=0.1))))
    biggest_triangle_step = np.max(np.abs(np.diff(triangle(freq=440, length=0.1))))

    assert biggest_square_step == pytest.approx(1.0)  # -0.5 straight to +0.5
    assert biggest_triangle_step < 0.05  # gradual


@pytest.mark.parametrize("duty", [0.125, 0.25, 0.5, 0.75])
def test_duty_is_the_fraction_of_time_spent_up(duty: float) -> None:
    """duty=0.125 should mean the wave is "up" one eighth of the time."""
    samples = square(freq=100, length=1.0, duty=duty)
    fraction_up = np.count_nonzero(samples > 0) / len(samples)
    assert fraction_up == pytest.approx(duty, abs=0.01)


def test_duty_does_not_change_pitch() -> None:
    """The whole point of the duty knob: same note, different character."""
    assert _count_cycles(square(freq=440, length=0.5, duty=0.5)) == pytest.approx(220, abs=1)
    assert _count_cycles(square(freq=440, length=0.5, duty=0.125)) == pytest.approx(220, abs=1)


# --------------------------------------------------------------------------
# triangle
# --------------------------------------------------------------------------


def test_triangle_uses_the_full_range() -> None:
    """A triangle should reach both extremes, not hover in the middle."""
    samples = triangle(freq=440, length=0.1, volume=0.5)
    assert np.max(samples) == pytest.approx(0.5, abs=0.01)
    assert np.min(samples) == pytest.approx(-0.5, abs=0.01)


def test_triangle_has_many_distinct_values() -> None:
    """The counterpart to test_square_only_has_two_values."""
    samples = triangle(freq=440, length=0.1)
    assert len(np.unique(samples)) > 50


# --------------------------------------------------------------------------
# noise
# --------------------------------------------------------------------------


def test_noise_is_different_every_call() -> None:
    """Random means random. Two crashes shouldn't be identical."""
    assert not np.array_equal(noise(length=0.1), noise(length=0.1))


def test_noise_is_centred_on_zero() -> None:
    """Averaged out, the speaker cone should sit at rest, not pushed to one
    side. An off-centre wave wastes headroom and can thump."""
    assert np.mean(noise(length=1.0)) == pytest.approx(0.0, abs=0.01)


def test_noise_has_no_pitch() -> None:
    """A pitched wave crosses zero twice per cycle; noise crosses it far more
    often than any musical note would."""
    crossings = _count_cycles(noise(length=1.0))
    assert crossings > 5000


# --------------------------------------------------------------------------
# pitch, for the two oscillators that have one
# --------------------------------------------------------------------------


@pytest.mark.parametrize("freq", [110, 220, 440, 880])
@pytest.mark.parametrize("osc", [square, triangle])
def test_freq_really_means_cycles_per_second(osc: Callable[..., Samples], freq: float) -> None:
    """freq=440 over 0.5s must produce 220 repeats. Catches a factor-of-two
    error in the phase maths."""
    samples = osc(freq=freq, length=0.5)
    assert _count_cycles(samples) == pytest.approx(freq * 0.5, abs=1)


@pytest.mark.parametrize("osc", [square, triangle])
def test_volume_scales_the_output(osc: Callable[..., Samples]) -> None:
    """volume=0.25 should be exactly half as far from rest as volume=0.5."""
    quiet = np.max(np.abs(osc(freq=440, length=0.1, volume=0.25)))
    loud = np.max(np.abs(osc(freq=440, length=0.1, volume=0.5)))
    assert quiet == pytest.approx(loud / 2, abs=0.01)


# --------------------------------------------------------------------------
# pitch sweeps — passing (start, end) instead of one frequency
# --------------------------------------------------------------------------


@pytest.mark.parametrize("osc", [square, triangle])
def test_sweep_has_the_right_length(osc: Callable[..., Samples]) -> None:
    """A glide shouldn't change how long the sound is."""
    assert len(osc(freq=(200, 1600), length=0.3)) == int(SAMPLE_RATE * 0.3)


@pytest.mark.parametrize("osc", [square, triangle])
def test_rising_sweep_speeds_up_over_time(osc: Callable[..., Samples]) -> None:
    """The defining property of a rising glide: more cycles happen in the
    second half of the sound than in the first."""
    samples = osc(freq=(110, 880), length=1.0)
    midpoint = len(samples) // 2

    first_half = _count_cycles(samples[:midpoint])
    second_half = _count_cycles(samples[midpoint:])

    assert second_half > first_half * 2


@pytest.mark.parametrize("osc", [square, triangle])
def test_falling_sweep_slows_down_over_time(osc: Callable[..., Samples]) -> None:
    """And a falling glide does the opposite — this is the laser sound."""
    samples = osc(freq=(880, 110), length=1.0)
    midpoint = len(samples) // 2

    assert _count_cycles(samples[:midpoint]) > _count_cycles(samples[midpoint:]) * 2


@pytest.mark.parametrize("osc", [square, triangle])
def test_sweep_between_identical_pitches_matches_a_steady_note(osc: Callable[..., Samples]) -> None:
    """A "glide" from 440 to 440 is just a note at 440. Sanity-checks that the
    accumulated phase maths agrees with the multiply shortcut."""
    swept = _count_cycles(osc(freq=(440, 440), length=0.5))
    steady = _count_cycles(osc(freq=440, length=0.5))
    assert swept == pytest.approx(steady, abs=1)


@pytest.mark.parametrize("osc", [square, triangle])
def test_sweep_cycle_count_matches_the_average_pitch(osc: Callable[..., Samples]) -> None:
    """Gliding evenly from 200 to 400 Hz over a second should produce about as
    many cycles as a steady 300 Hz would."""
    swept = _count_cycles(osc(freq=(200, 400), length=1.0))
    assert swept == pytest.approx(300, abs=2)


def test_sweep_still_respects_duty() -> None:
    """The duty knob and the glide shouldn't interfere with each other."""
    samples = square(freq=(200, 400), length=1.0, duty=0.25)
    fraction_up = np.count_nonzero(samples > 0) / len(samples)
    assert fraction_up == pytest.approx(0.25, abs=0.01)


# --------------------------------------------------------------------------
# wavetable — the Game Boy's user-defined voice
# --------------------------------------------------------------------------


def test_a_two_entry_table_is_exactly_a_square_wave() -> None:
    """[1.0, -1.0] is the definition of a square wave at duty 0.5, so the two
    functions must agree sample for sample, not merely sound similar."""
    from_table = wavetable([1.0, -1.0], freq=440, length=0.25)
    from_square = square(freq=440, length=0.25, duty=0.5)
    assert np.array_equal(from_table, from_square)


def test_wavetable_only_outputs_values_from_the_table() -> None:
    """It is a lookup, not a calculation."""
    table = [1.0, 0.5, 0.0, -0.5]
    samples = wavetable(table, freq=440, length=0.1, volume=1.0)
    assert set(np.unique(samples)).issubset(set(table))


def test_wavetable_length_and_volume() -> None:
    samples = wavetable(SINE_TABLE, freq=440, length=0.2, volume=0.25)
    assert len(samples) == int(SAMPLE_RATE * 0.2)
    assert np.max(np.abs(samples)) == pytest.approx(0.25, abs=0.01)


def test_wavetable_accepts_a_plain_python_list() -> None:
    """Callers should not have to build an array to define a shape."""
    assert len(wavetable([0.0, 1.0, 0.0, -1.0], freq=440, length=0.1)) > 0


def test_wavetable_takes_the_pitch_of_the_table_not_its_length() -> None:
    """A table describes the shape of one cycle; how many values it uses must
    not affect pitch."""
    short = _count_cycles(wavetable([1.0, 1.0, -1.0, -1.0], freq=440, length=0.5))
    long = _count_cycles(wavetable(SINE_TABLE, freq=440, length=0.5))
    assert short == pytest.approx(long, abs=1)


def test_wavetable_supports_sweeps_like_the_other_oscillators() -> None:
    samples = wavetable(SINE_TABLE, freq=(110, 880), length=1.0)
    midpoint = len(samples) // 2
    assert _count_cycles(samples[midpoint:]) > _count_cycles(samples[:midpoint]) * 2


@pytest.mark.parametrize(("name", "table"), [("sine", SINE_TABLE), ("bell", BELL_TABLE)])
def test_preset_tables_are_game_boy_shaped(name: str, table: Samples) -> None:
    """32 entries was the hardware's limit, and values must stay in range."""
    assert len(table) == 32
    assert np.all(np.abs(table) <= 1.0)


def test_sine_table_is_smooth() -> None:
    """A sine has no jumps between neighbouring samples."""
    samples = wavetable(SINE_TABLE, freq=100, length=0.1)
    assert np.max(np.abs(np.diff(samples))) < 0.2


# --------------------------------------------------------------------------
# helper
# --------------------------------------------------------------------------


def _count_cycles(samples: np.ndarray) -> int:
    """Count negative-to-positive crossings, which happen once per cycle."""
    positive = samples > 0
    return int(np.count_nonzero(~positive[:-1] & positive[1:]))


# --------------------------------------------------------------------------
# reproducibility
# --------------------------------------------------------------------------


def test_noise_is_reproducible_when_seeded() -> None:
    """Needed for golden-audio tests: without a seed a refactor cannot be
    distinguished from fresh randomness."""
    assert np.array_equal(noise(length=0.1, seed=42), noise(length=0.1, seed=42))


def test_different_seeds_give_different_noise() -> None:
    assert not np.array_equal(noise(length=0.1, seed=1), noise(length=0.1, seed=2))


def test_unseeded_noise_still_varies() -> None:
    assert not np.array_equal(noise(length=0.1), noise(length=0.1))
